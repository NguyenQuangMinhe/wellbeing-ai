import logging
import httpx
from app.classifier.crisis_keywords import detect_crisis, CRISIS_RESPONSE_MESSAGE
from app.classifier.stage_gate import evaluate_gate
from app.classifier.boundary_responses import detect_boundary, BOUNDARY_RESPONSE_MESSAGE
from app.classifier.intent_classifier import classify_intent
from app.classifier.output_check import check_output
from app.llm.generator import generate_response
from app.rag.retriever import assemble_prompt
from app.storage.history_store import (
    add_entry, is_session_locked, set_session_locked, init_db, get_session_stage, set_session_stage, get_history, 
    increment_turn_count, get_last_reminder_turn, set_last_reminder_turn,
)
from app.models.schemas import ChatRequest, ChatResponse
from app.classifier.language_check import NON_ENGLISH_RESPONSE_MESSAGE, is_non_english

logger = logging.getLogger(__name__)

GUARDRAIL_FALLBACK_MESSAGE = (
    "Unfortunately, I am unable to help with that request, I can help "
    "reflect on thoughts and feelings but cannot provide diagnosis, medication or crisis support"
)
TIMEOUT_MESSAGE = "Response is taking longer than expected, we weren't able to respond"
MODEL_UNAVAILABLE_MESSAGE = "We couldn't generate a response right now. Please try again later, sorry for the inconvenience."
SESSION_LOCKED_MESSAGE = "This session has been ended for your safety. Please reach out to a crisis service directly, or start a new conversation."


# Over-reliance reminders. First reminder once a session reaches RELIANCE_REMINDER_THRESHOLD turns (20), then again every 
# RELIANCE_REMINDER_PERIOD turns after that (20, 30, 40, ...). 
# MAX_HISTORY_TURNS (retriever.py) already treats 10 turns as the "recent context" window, so this sits above normal usage 
# while still catching a long single-use session.
RELIANCE_REMINDER_THRESHOLD = 20
RELIANCE_REMINDER_PERIOD = 10

async def handle_message(request: ChatRequest) -> ChatResponse:
    # function executed for every incoming chat message, running each stage of system flow in sequence, or halting when unsafe to continue

    session_id = request.session_id
    user_message = request.message

    # Preliminary Stage: Check session lock
    logger.info("Stage: session_lock_check | session=%s", session_id)
    if is_session_locked(session_id):
        logger.info("Session %s is locked - terminating without processing", session_id)
        response = ChatResponse(
            type = "crisis",
            message = SESSION_LOCKED_MESSAGE,
            risk_level = "high",
            end_session = True,
            stage = get_session_stage(session_id),
        )
        add_entry(session_id, user_message, response.message, response.type, response.risk_level)
        return response

     # Stage 0: Read current conversation stage
    current_stage = get_session_stage(session_id)
    logger.info("Stage: stage_read | session=%s | stage=%s", session_id, current_stage)
    #increment and evaluate the reminder counter for this turn
    turn_count = increment_turn_count(session_id)
    last_reminder_turn = get_last_reminder_turn(session_id)
    show_reminder = (
        turn_count >= RELIANCE_REMINDER_THRESHOLD
        and (turn_count - last_reminder_turn) >= RELIANCE_REMINDER_PERIOD
    )

    #Stage 1.1: Crisis keyword check 
    logger.info("Stage: crisis_keywords | session=%s", session_id)
    if detect_crisis(user_message):
        logger.info("Crisis keyword match for session %s - short-circuiting", session_id)
        set_session_locked(session_id)
        response = ChatResponse(
            type = "crisis",
            message = CRISIS_RESPONSE_MESSAGE,
            risk_level = "high",
            end_session = True,
            stage = current_stage,
        )
        add_entry(session_id, user_message, response.message, response.type, response.risk_level)
        return response

    #Stage 1.15: Non-english check
    logger.info("Stage: non_english_check | session=%s", session_id)
    if is_non_english(user_message):
        logger.info("Non-english message detected for session %s - short-circuiting", session_id)
        response = ChatResponse(
            type = "non-english",
            message = NON_ENGLISH_RESPONSE_MESSAGE,
            risk_level = "low",
            end_session = False,
            stage = current_stage,
        )
        return response


    #Stage 1.2: Boundary Check
    logger.info("Stage: boundary_check | session=%s", session_id)
    if detect_boundary(user_message):
        logger.info("Boundary match for session %s", session_id)
        response = ChatResponse(
            type="boundary",
            message = BOUNDARY_RESPONSE_MESSAGE,
            risk_level = "low",
            end_session = False,
            stage = current_stage,
        )
        add_entry(session_id, user_message, response.message, response.type, response.risk_level)
        return response 

    # Stage 2: Intent Classification
    logger.info("Stage: intent_classification | session=%s", session_id)
    try:
        classification = classify_intent(user_message)
    except httpx.ReadTimeout:
        logger.error("Stage: intent_classification | session=%s | TIMEOUT - Ollama did not respond in time", session_id)
        response = ChatResponse(
            type = "error",
            message = TIMEOUT_MESSAGE,
            risk_level = "low",
            end_session = False,
            stage = current_stage,
        )
        add_entry(session_id, user_message, response.message, response.type, response.risk_level)
        return response
    except httpx.ConnectError:
        logger.error("Stage: intent_classification | session=%s | MODEL UNAVAILABLE - could not reach Ollama", session_id)
        response = ChatResponse(
            type = "error",
            message = MODEL_UNAVAILABLE_MESSAGE,
            risk_level = "low",
            end_session = False,
            stage = current_stage,
        )
        add_entry(session_id, user_message, response.message, response.type, response.risk_level)
        return response
    risk_level = classification["risk_level"]
    logger.info("Session %s classified as risk_level=%s", session_id, risk_level)

    #Stage 3: Prompt Assembly (RAG + conversational history + system prompt)
    logger.info("Stage: prompt_assembly | session=%s", session_id)
    prompt = assemble_prompt(session_id, user_message, risk_level, current_stage, show_reminder)
    print(f"[DEBUG] Moderate-risk instruction in prompt: {'classified as moderate risk' in prompt}")

    #Stage 4: Generation
    logger.info("Stage: generation | session=%s", session_id)
    try:
        generated_text = generate_response(prompt)
    except httpx.ReadTimeout:
        logger.error("Stage: generation | session=%s | TIMEOUT - Ollama did not respond in time", session_id)
        response = ChatResponse(
            type = "error",
            message = TIMEOUT_MESSAGE,
            risk_level = risk_level,
            end_session = False,
            stage = current_stage,
        )
        add_entry(session_id, user_message, response.message, response.type, response.risk_level)
        return response
    except httpx.ConnectError:
        logger.error("Stage: generation | session=%s | MODEL UNAVAILABLE - could not reach Ollama", session_id)
        response = ChatResponse(
            type ="error",
            message = MODEL_UNAVAILABLE_MESSAGE,
            risk_level = risk_level,
            end_session = False,
            stage = current_stage
        )
        add_entry(session_id, user_message, response.message, response.type, response.risk_level)
        return response

    #Stage 5: Output Guardrail
    logger.info("Stage: output_guardrail | session=%s", session_id)
    try:
        guardrail_result = check_output(generated_text)
    except httpx.ReadTimeout:
        logger.error("Stage: output_guardrail | session=%s | TIMEOUT - Ollama did not respond in time", session_id)
        response = ChatResponse(
            type = "error",
            message = TIMEOUT_MESSAGE,
            risk_level = risk_level,
            end_session = False,
            stage = current_stage,
        )
        add_entry(session_id, user_message, response.message, response.type, response.risk_level)
        return response
    except httpx.ConnectError:
        logger.error("Stage: output_guardrail | session=%s | MODEL UNAVAILABLE - could not reach Ollama", session_id)
        response = ChatResponse(
            type = "error",
            message = MODEL_UNAVAILABLE_MESSAGE,
            risk_level = risk_level,
            end_session = False,
            stage = current_stage
        )
        add_entry(session_id, user_message, response.message, response.type, response.risk_level)
        return response

    if guardrail_result["verdict"] == "unsafe":
        logger.info("Guardrail flagged unsafe output for session %s - routing to fallback", session_id)
        logger.error("Stage: output_guardrail | session=%s | UNSAFE output discarded, unsafe text not shown to user", session_id)
        response = ChatResponse(
            type = "error",
            message = GUARDRAIL_FALLBACK_MESSAGE,
            risk_level = risk_level,
            end_session = False,
            stage = current_stage,
        )
    else:
        history = get_history(session_id)
        previous_user_message = None
        for entry in reversed(history):
            if not detect_decline(entry["user_message"]) and not detect_close(entry["user_message"]):
                previous_user_message = entry["user_message"]
                break
        new_stage = evaluate_gate(current_stage, user_message, previous_user_message)
        if new_stage != current_stage:
            logger.info("Stage: gate_check | session=%s | advancing %s -> %s", session_id, current_stage, new_stage)
            set_session_stage(session_id, new_stage)
        if show_reminder:
            logger.info("Reliance reminder shown for session %s at turn %s", session_id, turn_count)
            set_last_reminder_turn(session_id, turn_count)
        response = ChatResponse(
            type = "normal",
            message = generated_text,
            risk_level = risk_level,
            end_session = False,
            stage = new_stage,
            reminder = show_reminder,
        )
    add_entry(session_id, user_message, response.message, response.type, response.risk_level)
    return response


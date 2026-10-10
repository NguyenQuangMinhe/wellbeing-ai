import uuid
from unittest.mock import patch

import pytest
import httpx

from app.control_plane import handle_message, GUARDRAIL_FALLBACK_MESSAGE
from app.models.schemas import ChatRequest
from app.storage.history_store import init_db, get_history, is_session_locked
from app.classifier.language_check import NON_ENGLISH_RESPONSE_MESSAGE, is_non_english

UNSAFE_MARKER = "UNSAFE-MARKER-TEXT-12345"

@pytest.mark.live
@pytest.mark.asyncio
async def test_unsafe_text_never_appears_in_response_or_history():
    # Forces the model's generated resposne to return an unsafe guardrail verdict
    # Confirms generated response not returned to user or used to populated stored session histopry
    init_db()
    session_id = f"test-{uuid.uuid4()}"
    request = ChatRequest(
        session_id=session_id,
        message="I've been feeling stressed about an upcoming deadline",
    )

    with patch("app.control_plane.generate_response") as mock_generate, \
         patch("app.control_plane.check_output") as mock_check:
        mock_generate.return_value = UNSAFE_MARKER
        mock_check.return_value = {"verdict": "unsafe", "Llamaguard_response": "unsafe\ns1"}
        response = await handle_message(request)

    print(f"\ntype: {response.type}")
    print(f"risk_level: {response.risk_level}")
    print(f"end_session: {response.end_session}")
    print(f"message: {response.message}")

    assert response.message == GUARDRAIL_FALLBACK_MESSAGE
    assert response.type == "error"
    assert UNSAFE_MARKER not in response.message

    history = get_history(session_id)
    print(f"stored history entry: {history[0]['system_message']}")

    assert len(history) == 1
    assert UNSAFE_MARKER not in history[0]["system_message"]


@pytest.mark.asyncio
async def test_crisis_writes_history_and_locks_session():
    # tests for crisis message accurately recorded in session history
    # tests for crisis message setting session lock
    # tests follow up prompts in same-session do not reach the LLM
    init_db()
    session_id = f"test-{uuid.uuid4()}"

    crisis_response = await handle_message(
        ChatRequest(session_id=session_id, message="I might hurt myself")
    )

    print(f"\ncrisis type: {crisis_response.type}")
    print(f"crisis risk_level: {crisis_response.risk_level}")
    print(f"crisis end_session: {crisis_response.end_session}")
    print(f"session locked after crisis: {is_session_locked(session_id)}")

    history = get_history(session_id)
    print(f"history rows after crisis: {len(history)}")
    print(f"history row: response_type={history[0]['response_type']}, "
          f"risk_level={history[0]['risk_level']}")

    assert crisis_response.type == "crisis"
    assert crisis_response.risk_level == "high"
    assert crisis_response.end_session is True
    assert is_session_locked(session_id) is True

    assert len(history) == 1
    assert history[0]["response_type"] == "crisis"
    assert history[0]["risk_level"] == "high"

    with patch("app.control_plane.generate_response") as mock_generate:
        follow_up = await handle_message(
            ChatRequest(session_id=session_id, message="Actually, I'm fine now")
        )
        mock_generate.assert_not_called()

    print(f"follow-up type: {follow_up.type}")
    print(f"follow-up end_session: {follow_up.end_session}")

    assert follow_up.type == "crisis"
    assert follow_up.risk_level == "high"
    assert follow_up.end_session is True

@pytest.mark.asyncio
async def test_locked_session_follow_up_is_recorded_in_history():
    
    # test every conversation outcome written to history including a locked-session termination. 
    init_db()
    session_id = f"test-{uuid.uuid4()}"

    await handle_message(ChatRequest(session_id=session_id, message="I might hurt myself"))
    await handle_message(ChatRequest(session_id=session_id, message="Actually, I'm fine now"))

    assert len(get_history(session_id)) == 2

@pytest.mark.asyncio
async def test_generation_timeout_returns_error_variant():
    init_db()
    session_id = f"test-{uuid.uuid4()}"
    request = ChatRequest(session_id=session_id, message="I've been feeling stressed about an upcoming deadline")

    with patch("app.control_plane.classify_intent") as mock_classify, \
         patch("app.control_plane.assemble_prompt") as mock_assemble, \
         patch("app.control_plane.generate_response") as mock_generate:
        mock_classify.return_value = {"risk_level": "low", "Llamaguard_response": "safe"}
        mock_assemble.return_value = "a fake assembled prompt"
        mock_generate.side_effect = httpx.ReadTimeout("simulated timeout")
        response = await handle_message(request)

    assert response.type == "error"
    assert response.message == "Response is taking longer than expected, we weren't able to respond"
    assert response.message != ""

    history = get_history(session_id)
    assert len(history) == 1
    assert history[0]["response_type"] == "error"


@pytest.mark.asyncio
async def test_generation_model_unavailable_returns_error_variant():
    init_db()
    session_id = f"test-{uuid.uuid4()}"
    request = ChatRequest(session_id=session_id, message="I've been feeling stressed about an upcoming deadline")

    with patch("app.control_plane.classify_intent") as mock_classify, \
         patch("app.control_plane.assemble_prompt") as mock_assemble, \
         patch("app.control_plane.generate_response") as mock_generate:
        mock_classify.return_value = {"risk_level": "low", "Llamaguard_response": "safe"}
        mock_assemble.return_value = "a fake assembled prompt"
        mock_generate.side_effect = httpx.ConnectError("simulated connection failure")
        response = await handle_message(request)

    assert response.type == "error"
    assert response.message == "We couldn't generate a response right now. Please try again later, sorry for the inconvenience."
    assert response.message != ""

    history = get_history(session_id)
    assert len(history) == 1
    assert history[0]["response_type"] == "error"




@pytest.mark.asyncio
async def test_classification_model_unavailable_returns_error_variant():
    init_db()
    session_id = f"test-{uuid.uuid4()}"
    request = ChatRequest(session_id=session_id, message="I've been feeling stressed about an upcoming deadline")

    with patch("app.control_plane.classify_intent") as mock_classify:
        mock_classify.side_effect = httpx.ConnectError("simulated connection failure")
        response = await handle_message(request)

    assert response.type == "error"
    assert response.message == "We couldn't generate a response right now. Please try again later, sorry for the inconvenience."
    assert response.message != ""

    history = get_history(session_id)
    assert len(history) == 1
    assert history[0]["response_type"] == "error"


@pytest.mark.asyncio 
async def test_guardrail_timeout_returns_error_variant():
    init_db()
    session_id = f"test-{uuid.uuid4()}"
    request = ChatRequest(session_id=session_id, message="I've been feeling stressed about an upcoming deadline")

    with patch("app.control_plane.classify_intent") as mock_classify, \
         patch("app.control_plane.assemble_prompt") as mock_assemble, \
         patch("app.control_plane.generate_response") as mock_generate, \
         patch("app.control_plane.check_output") as mock_check:
        mock_classify.return_value = {"risk_level": "low", "Llamaguard_response": "safe"}
        mock_assemble.return_value = "a fake assembled prompt"
        mock_generate.return_value = "a normal generated reply"
        mock_check.side_effect = httpx.ReadTimeout("simulated timeout")
        response = await handle_message(request)

    assert response.type == "error"
    assert response.message == "Response is taking longer than expected, we weren't able to respond"
    assert response.message != ""

    history = get_history(session_id)
    assert len(history) == 1
    assert history[0]["response_type"] == "error"


@pytest.mark.asyncio
async def test_guardrail_model_unavailable_returns_error_variant():
    init_db()
    session_id = f"test-{uuid.uuid4()}"
    request = ChatRequest(session_id=session_id, message="I've been feeling stressed about an upcoming deadline")

    with patch("app.control_plane.classify_intent") as mock_classify, \
         patch("app.control_plane.assemble_prompt") as mock_assemble, \
         patch("app.control_plane.generate_response") as mock_generate, \
         patch("app.control_plane.check_output") as mock_check:
        mock_classify.return_value = {"risk_level": "low", "Llamaguard_response": "safe"}
        mock_assemble.return_value = "a fake assembled prompt"
        mock_generate.return_value = "a normal generated reply"
        mock_check.side_effect = httpx.ConnectError("simulated connection failure")
        response = await handle_message(request)

    assert response.type == "error"
    assert response.message == "We couldn't generate a response right now. Please try again later, sorry for the inconvenience."
    assert response.message != ""

    history = get_history(session_id)
    assert len(history) == 1
    assert history[0]["response_type"] == "error"


@pytest.mark.live
@pytest.mark.asyncio
async def test_short_non_english_message_not_blocked():
    # Confirms a short non-English message, which is too short for reliable detection, is not blocked and proceeds to generation.
    init_db()
    session_id = f"test-{uuid.uuid4()}"
    request = ChatRequest(session_id=session_id, message="im stressed")

    response = await handle_message(request)

    assert response.type != "error" or response.message != NON_ENGLISH_RESPONSE_MESSAGE


@pytest.mark.asyncio
async def test_long_non_english_message_blocked():
    # confirms a non-english message is identified and returned language limitation error message rather than proceeding to response generation.
    init_db()
    session_id = f"test-{uuid.uuid4()}"
    request = ChatRequest(
        session_id=session_id,
        message="Je me sens vraiment stressé à propos d'un délai qui approche au travail",
    )

    response = await handle_message(request)

    assert response.type == "error"
    assert response.message == NON_ENGLISH_RESPONSE_MESSAGE

    history = get_history(session_id)
    assert len(history) == 1
    assert history[0]["response_type"] == "error"
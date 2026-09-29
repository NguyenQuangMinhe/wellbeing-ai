import asyncio

from app.classifier.crisis_keywords import detect_crisis, CRISIS_RESPONSE_MESSAGE
from app.classifier.boundary_responses import detect_boundary, BOUNDARY_RESPONSE_MESSAGE
from app.storage.history_store import add_entry, delete_history, get_history, init_db, set_session_locked, is_session_locked
import logging

from app.llm.prompt_builder import build_prompt
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.control_plane import handle_message
from app.models.schemas import ChatRequest, ChatResponse
from app.storage.history_store import delete_history, init_db

# Makes the stage-level INFO logs from control_plane.py visible in terminal
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["POST", "DELETE", "GET"],
    allow_headers=["*"],
)

def end_response(session_id: str, user_message: str, response: ChatResponse) -> ChatResponse:
    add_entry(session_id, user_message, response.message, response.type, response.risk_level)
    if response.end_session:
        set_session_locked(session_id, True)
    return response

@app.on_event("startup")
async def startup():
    init_db()

@app.post("/api/message", response_model=ChatResponse)
async def handle_message(request: ChatRequest) -> ChatResponse:
    # Delay testing
    #await asyncio.sleep(10)  
    try: 
        # Session lock check first
        if is_session_locked(request.session_id):
            response = ChatResponse(
                type="crisis",
                message=CRISIS_RESPONSE_MESSAGE,
                risk_level="high",
                end_session=True,
            )
            add_entry(request.session_id, request.message, response.message, response.type, response.risk_level)
            return response

        # First tier, is risk_level and crisis can be considered only label
        if detect_crisis(request.message):
            response = ChatResponse(type="crisis", message=CRISIS_RESPONSE_MESSAGE, risk_level="high", end_session=True)
            return end_response(request.session_id, request.message, response)
        if detect_boundary(request.message):
            response = ChatResponse(type="boundary", message=BOUNDARY_RESPONSE_MESSAGE, risk_level="medium", end_session=False)
            return end_response(request.session_id, request.message, response)
        # TODO: intent

        # Prompt from session historuy + new message
        # TODO: not yet sent to LLM
        prompt = build_prompt(request.session_id, request.message)

        
        # Stub - classifier/RAG/LLM not wired up yet
        response = ChatResponse(
            type="normal",
            message=f"(stub, prompt assembled with {len(prompt)} chars) I heard: {request.message}",
            risk_level="low",
            end_session=False,
        )
        return end_response(request.session_id, request.message, response) # hasnt handled risks yet (low default) + stub response type
    except Exception:
        logger.exception("Unhandled error processing message for session %s", request.session_id)
        response = ChatResponse(
            type="error",
            message="We couldn’t generate a response right now. Please try again later, sorry for the inconvenience.",
            risk_level="low",
            end_session=False,
        )
        add_entry(request.session_id, request.message, response.message, response.type, response.risk_level)
        return response

# Named post_message so it doesn't shadow the handle_message imported above.
@app.post("/api/message", response_model=ChatResponse)
async def post_message(request: ChatRequest) -> ChatResponse:
    try:
        return await handle_message(request)
    except Exception:
        logger.exception("Unhandled error processing message for session %s", request.session_id)
        return ChatResponse(
            type="error",
            message="We couldn’t generate a response right now. Please try again later, sorry for the inconvenience.",
            risk_level="low",
            end_session=False,
        )


@app.delete("/api/history/{session_id}")
async def clear_history(session_id: str):
    deleted = delete_history(session_id)
    return {"deleted": deleted}

@app.get("/api/history/{session_id}")
async def read_history(session_id: str):
    return get_history(session_id)

@app.get("/health")
async def health():
    return {"status": "ok"}
import asyncio

from app.classifier.crisis_keywords import detect_crisis, CRISIS_RESPONSE_MESSAGE
from app.classifier.boundary_responses import detect_boundary, BOUNDARY_RESPONSE_MESSAGE
from app.storage.history_store import add_entry, delete_history, init_db, set_session_locked, is_session_locked
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.models.schemas import ChatRequest, ChatResponse
from app.llm.prompt_builder import build_prompt

import logging

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
    await asyncio.sleep(10)  
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
        return ChatResponse(
            type="error",
            message="Something went wrong on our end. Please try again in a moment.",
            risk_level="low",
            end_session=False,
        )

@app.delete("/api/history/{session_id}")
async def clear_history(session_id: str):
    deleted = delete_history(session_id)
    return {"deleted": deleted}

@app.get("/health")
async def health():
    return {"status": "ok"}
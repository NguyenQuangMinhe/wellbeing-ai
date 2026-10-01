import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.control_plane import handle_message
from app.models.schemas import ChatRequest, ChatResponse
from app.storage.history_store import delete_history, get_history, init_db, is_session_locked

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


@app.on_event("startup")
async def startup():
    init_db()


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

@app.get("/api/session/{session_id}/status")
async def get_session_status(session_id: str):
    locked = is_session_locked(session_id)
    return {"locked": locked}

@app.get("/health")
async def health():
    return {"status": "ok"}
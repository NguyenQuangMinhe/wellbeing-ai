from app.classifier.crisis_keywords import detect_crisis, CRISIS_RESPONSE_MESSAGE
from app.storage.history_store import add_entry, delete_history, init_db
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.models.schemas import ChatRequest, ChatResponse

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
async def handle_message(request: ChatRequest) -> ChatResponse:
    add_entry(request.session_id, "user", request.message, "low") # hasnt handled risks yet (low default)

    # First tier
    if detect_crisis(request.message):
        response = ChatResponse(type="crisis", message=CRISIS_RESPONSE_MESSAGE, risk_level="high", end_session=True)
        add_entry(request.session_id, "system", response.message, response.risk_level)
        return response
    # TODO: boundary
    # TODO: intent

    
    # Stub - classifier/RAG/LLM not wired up yet
    return ChatResponse(
        type="normal",
        message=f"(stub) I heard: {request.message}",
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
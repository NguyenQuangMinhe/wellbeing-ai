from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.models.schemas import ChatRequest, ChatResponse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["POST"],
    allow_headers=["*"],
)


@app.post("/api/message", response_model=ChatResponse)
async def handle_message(request: ChatRequest) -> ChatResponse:
    # Stub — no classifier, RAG, or LLM wired up yet.
    return ChatResponse(
        type="normal",
        message=f"(stub) I heard: {request.message}",
        risk_level="low",
        end_session=False,
    )


@app.get("/health")
async def health():
    return {"status": "ok"}
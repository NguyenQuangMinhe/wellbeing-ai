from pydantic import BaseModel
from typing import Literal


class ChatRequest(BaseModel):
    session_id: str
    message: str


class ChatResponse(BaseModel):
    type: Literal["normal", "crisis", "error", "boundary"]
    message: str
    risk_level: Literal["low", "medium", "high"]
    end_session: bool
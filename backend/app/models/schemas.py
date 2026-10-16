from pydantic import BaseModel, Field
from typing import Literal


class ChatRequest(BaseModel):
    session_id: str
    message: str = Field(..., min_length=1)


class ChatResponse(BaseModel):
    type: Literal["normal", "crisis", "non-english", "error", "boundary"]
    message: str
    risk_level: Literal["low", "medium", "high"]
    end_session: bool

class FeedbackRequest(BaseModel):
    message_id: str
    message_text: str
    category: list[str] = Field(min_length=1)
    additional: str = Field(default="", max_length=1000)
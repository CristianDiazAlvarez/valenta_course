from typing import Optional, List, Any
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from pydantic import BaseModel

class ChatSession(SQLModel, table=True):
    session_id: str = Field(primary_key=True, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    messages: List["ChatMessage"] = Relationship(back_populates="session")

class ChatMessage(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: str = Field(foreign_key="chatsession.session_id", index=True)
    role: str  # 'user' o 'assistant'
    content: str
    standalone_question: Optional[str] = None
    sources_json: Optional[str] = None  # JSON serializado (lista de fuentes)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    session: Optional[ChatSession] = Relationship(back_populates="messages")

# Schemas para respuestas API
class ChatMessageRead(BaseModel):
    id: int
    session_id: str
    role: str
    content: str
    standalone_question: Optional[str] = None
    sources: Optional[Any] = None
    created_at: datetime

    class Config:
        from_attributes = True

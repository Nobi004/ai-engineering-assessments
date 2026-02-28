from sqlmodel import SQLModel, Field, JSON, Column
from datetime import datetime
from uuid import UUID, uuid4
from pydantic import BaseModel
from typing import Literal
from enum import Enum

class Company(SQLModel, table=True):
    __tablename__ = "companies"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    company_id: str = Field(index=True, unique=True)  # e.g. "acme-corp"
    name: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ChatRole(str, Enum):
    user = "user"
    assistant = "assistant"

class ChatMessage(SQLModel, table=True):
    __tablename__ = "rag_chat_history"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    session_id: UUID
    company_id: str
    role: ChatRole
    content: str
    confidence: float | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class RAGResponse(BaseModel):
    answer: str
    confidence: float
    sources: list[str]
    refusal: bool


class ChatRequest(BaseModel):
    query: str
    company_id: str = "acme-corp"
    session_id: UUID | None = None
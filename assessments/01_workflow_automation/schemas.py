from sqlmodel import SQLModel, Field, JSON, Column
from pydantic import BaseModel, field_validator
from datetime import datetime
from uuid import UUID, uuid4
from typing import Literal, Any

class LeadFields(BaseModel):
    name: str | None = None
    email: str | None = None
    company: str | None = None
    phone: str | None = None
    budget: float | None = None
    message_summary: str | None = None

    @field_validator("email")
    @classmethod
    def validate_email(cls, v):
        if v and "@" not in v:
            raise ValueError("Invalid email")
        return v

class IntentClassification(BaseModel):
    intent: Literal["sales", "support", "partnership", "unknown"]
    confidence: float

class WorkflowLead(SQLModel, table=True):
    __tablename__ = "workflow_leads"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    raw_input: dict = Field(sa_column=Column(JSON))
    intent: str
    confidence: float
    extracted_fields: dict = Field(sa_column=Column(JSON))
    ai_response: str | None = None
    status: Literal["processed", "fallback", "failed"] = "processed"
    request_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class WorkflowResponse(BaseModel):
    lead_id: UUID
    intent: str
    confidence: float
    extracted_fields: LeadFields
    ai_response: str
    status: str
    execution_trace: dict
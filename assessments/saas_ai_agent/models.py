# assessments/03_saas_ai_agent/models.py
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID, uuid4

class Tenant(SQLModel, table=True):
    __tablename__ = "saas_tenants"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(index=True)
    slug: str = Field(unique=True, index=True)           # e.g. "acme-corp"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    settings: dict = Field(default_factory=dict, sa_column=Field(sa_type="JSON"))  # tone, crm_webhook_url, etc.

class SocialConnection(SQLModel, table=True):
    __tablename__ = "saas_social_connections"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    tenant_id: UUID = Field(foreign_key="saas_tenants.id")
    platform: str                                     # twitter, instagram, facebook, linkedin
    account_id: str
    access_token: str                                 # encrypted in real system
    refresh_token: Optional[str] = None
    expires_at: Optional[datetime] = None

class Lead(SQLModel, table=True):
    __tablename__ = "saas_leads"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    tenant_id: UUID = Field(foreign_key="saas_tenants.id")
    source_platform: str
    source_id: str                                    # tweet id / dm id / comment id
    username: str
    content: str
    intent: Optional[str] = None
    tags: list[str] = Field(default_factory=list, sa_column=Field(sa_type="JSON"))
    confidence: float = 0.0
    reply_text: Optional[str] = None
    crm_synced: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
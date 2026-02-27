# assessments/01_workflow_automation/schemas.py (SQLModel models)
class WorkflowLead(SQLModel, table=True):
    __tablename__ = "workflow_leads"          # assessment-prefixed for clarity
    id: UUID = Field(primary_key=True, default_factory=uuid4)
    raw_input: dict = Field(sa_column=Column(JSON))
    intent: str                               # "sales", "support", "partnership", "unknown"
    confidence: float
    extracted_fields: dict = Field(sa_column=Column(JSON))   # validated Pydantic model dumped
    ai_response: str | None
    status: Literal["pending", "processed", "failed", "fallback"] = "pending"
    error_trace: dict | None = Field(sa_column=Column(JSON), default=None)
    request_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow})

class WorkflowStepLog(SQLModel, table=True):
    __tablename__ = "workflow_step_logs"
    id: UUID = Field(primary_key=True)
    lead_id: UUID = Field(foreign_key="workflow_leads.id")
    step_name: str                            # "intent_classification", "field_extraction"...
    llm_model: str
    tokens_in: int
    tokens_out: int
    duration_ms: float
    success: bool
    error: str | None
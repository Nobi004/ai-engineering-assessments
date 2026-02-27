# Assessment 1: AI Agent Workflow Automation (n8n + LLM)

**What this implements:**
- FastAPI endpoint `/api/01-workflow/leads`
- LLM intent classification (JSON mode + confidence)
- Structured field extraction with Pydantic validation
- Retry logic (tenacity 3× exponential backoff)
- SQLite persistence with full audit
- Structured logging (structlog + request_id)
- Fallback regex + generic response
- Exact replica of n8n workflow (Webhook → LLM Intent → IF → LLM Extract → Validate → SQLite → LLM Reply → Respond)

**Run locally:**
See Setup Instructions above.

**n8n node-by-node mapping:**
1. Webhook → FastAPI endpoint
2. Set (request_id) → middleware
3. OpenAI Intent → `structured_call`
4. IF confidence >= 0.7 → code in service
5. OpenAI Extractor → `structured_call`
6. Function (validation) → Pydantic
7. SQLite → SQLModel transaction
8. OpenAI Response → final LLM call
9. Respond → API JSON
10. Error branch → fallback + status="fallback"

Ready for Assessment 2.
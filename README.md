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

# Assessment 2: Company-Specific RAG Chatbot

**Production features implemented:**
- FAISS vector store with metadata filtering (company_id)
- RecursiveCharacterTextSplitter (800 tokens + 120 overlap)
- text-embedding-3-small embeddings
- Similarity threshold 0.45 + refusal logic
- Grounded prompt with exact refusal sentence
- Persistent chat memory in SQLite
- Confidence scoring from max cosine similarity
- Ingestion script (supports .txt, .pdf)

**How to test:**
1. Run ingest script (creates Acme Corp knowledge base)
2. Open Streamlit 8502
3. Ask: "What is your pricing?" → should answer correctly
4. Ask: "What is the weather in Dhaka?" → refusal with confidence 0

**API usage:**
The `/api/02-rag/chat` endpoint accepts a POST with the user query.  You can
provide the question either as a JSON body or as a URL query parameter:

```bash
# JSON body (used by Streamlit app)
curl -X POST http://localhost:8000/api/02-rag/chat \
     -H "Content-Type: application/json" \
     -d '{"query": "tell me about the company"}'

# query string (will also work)
curl -X POST "http://localhost:8000/api/02-rag/chat?query=tell+me+about+the+company"
```

Leaving `query` out produces a `422` error (field required).

Changing `company_id` or including `session_id` is also supported via the
same body/parameters.

**Multi-company ready:** Just change `company_id` and ingest new docs. Single index, zero leakage.

Ready for Assessment 3.
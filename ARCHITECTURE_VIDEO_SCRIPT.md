# AI Engineering Assessments — Video Script

Duration: ~8–12 minutes
Format: Narration + on-screen captions + code/demo screens + B-roll diagrams
Purpose: Explain the full project architecture, demos, and talking points for interviewers.

---

## 00:00–00:20 — Opening (Title + Hook)
- On screen: Project title and subtitle
  - "AI Engineering Assessments — Workflow Automation · RAG Chatbot · SaaS Agent"
- Narration:
  - "Hi — in this video we'll walk through a compact, production-oriented AI engineering project that demonstrates three core capabilities: workflow automation, a retrieval-augmented chatbot, and a multi-tenant SaaS AI agent design. You'll see architecture, implementation highlights, a short demo, and interviewer talking points."
- B-roll: quick montage of code, diagrams, and demo UI.

## 00:20–01:10 — Project Overview (High level)
- On screen: Project folder tree (shortened) and architecture block diagram.
- Narration:
  - "The repo contains three assessments under `assessments/`: `01_workflow_automation`, `02_rag_chatbot`, and `03_saas_ai_agent`. The backend runs on FastAPI, demos use Streamlit, core utilities live in `core/`, and data and FAISS indexes are in `data/`.
  - The goals: demonstrate reliable LLM integration, grounded retrieval via FAISS, and an extensible agent architecture suitable for multi-tenant SaaS." 
- On screen caption: Key technologies — FastAPI, OpenAI LLMs, FAISS, SQLModel/SQLite, Streamlit.

## 01:10–02:30 — Assessment 1: Workflow Automation
- On screen: `assessments/01_workflow_automation/` file list and a simple flow diagram.
- Narration:
  - "This module shows how to use LLMs for intent classification and structured field extraction. Incoming lead JSON is classified, confidence is checked, then fields are extracted and validated with Pydantic before persistence."
- Key points to show on screen:
  - Intent classification with JSON-mode responses.
  - Retry strategy with exponential backoff.
  - Audit trail in database and structured logging with `structlog`.
- Demo command (screencast suggestion): run a sample request to the API and show the structured JSON response.

```bash
curl -X POST http://localhost:8000/api/01-workflow/leads \
  -H "Content-Type: application/json" \
  -d '{"name": "Alice", "message":"Interested in partnership"}'
```

## 02:30–04:10 — Assessment 2: RAG Chatbot
- On screen: `assessments/02_rag_chatbot/` with `ingest.py`, `services.py`, router.
- Narration:
  - "This assessment demonstrates Retrieval-Augmented Generation: documents are chunked and embedded using `text-embedding-3-small`, stored in FAISS, and queries are answered by retrieving top-k chunks then generating grounded responses."
- Show reasoning points:
  - Chunking strategy (800 token chunks, 120 overlap)
  - Per-tenant FAISS metadata filtering (company isolation)
  - Similarity threshold + explicit refusal sentence to avoid hallucination
  - Optional rewrite pass to make answers friendly
- Demo commands to run locally:

```bash
# Ingest documents for acme-corp
python -c "from assessments.rag_chatbot.services import RAGService; import asyncio; asyncio.run(RAGService.ingest_documents('acme-corp'))"

# Query (body style)
curl -X POST http://localhost:8000/api/02-rag/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "Tell me about Acme Corp", "company_id": "acme-corp"}'
```

- On-screen highlight: sources attribution and confidence score returned alongside answers.

## 04:10–06:00 — Assessment 3: SaaS AI Agent Design
- On screen: `assessments/03_saas_ai_agent/design.md` and architecture diagram (B-roll).
- Narration:
  - "This part is a design exercise for a scalable, multi-tenant SaaS platform providing AI agents (Reply Agent, Lead Qualifier, Entity Extractor). It covers tenant isolation, webhook handling, agent interfaces, and operational considerations like caching and queues."
- Talking points for interviewers:
  - Tenant isolation strategies (request-scoped tenant_id, RLS, encryption keys)
  - Agent interface patterns and asynchronous processing
  - Webhook retry/queue/DLQ patterns
  - Cost control: batching, caching, fallback to smaller models

## 06:00–07:20 — Cross-Cutting Concerns & Observability
- On screen: `core/` file list and short code snippets for logging and error handling.
- Narration:
  - "Cross-cutting concerns include structured logging with correlation IDs, metrics (LLM latency, token usage), and tracing for distributed flows. Error handling uses retries, circuit breakers, and graceful fallbacks."
- Show example log line and the circuit-breaker pattern briefly.

## 07:20–08:30 — Demo Walkthrough (Short live demo)
- On screen: Streamlit demo (`streamlit_apps/02_rag_app.py`) showing ingestion and chat.
- Narration & steps:
  - "Start the backend with `uvicorn backend.main:app --reload` and the Streamlit UI with `streamlit run streamlit_apps/02_rag_app.py`. Ingest company docs, then ask the chat UI a question and watch the grounded answer and sources appear." 
- Commands to show in captions:

```bash
uvicorn backend.main:app --reload
streamlit run streamlit_apps/02_rag_app.py
```

## 08:30–09:30 — Interviewer Guide & Key Questions
- On screen: bullet list of interview topics (from `ARCHITECTURE_GUIDE.md`):
  - RAG hallucination prevention, tenant isolation, scaling to large numbers of tenants, cost/latency trade-offs, security and compliance.
- Narration: call out a few strong questions:
  - "How would you migrate FAISS to production storage?"
  - "How would you enforce tenant isolation at DB level?"
  - "How to reduce LLM costs while keeping quality?"

## 09:30–10:00 — Closing & Next Steps
- Narration:
  - "If you'd like, we can record a longer demo deep-dive on any of the assessments — or provide a ready-to-run demo VM, Docker files, and a CI pipeline. Check the repo's `LOCAL_SETUP.md` for quick start steps."
- On screen: links/paths to `README.md`, `LOCAL_SETUP.md`, and `ARCHITECTURE_GUIDE.md`.

---

## Production Recording Tips
- Record in sections; capture terminal + browser demos separately to avoid accidental secrets appearing on camera.
- Add on-screen captions for commands and file paths.
- Use the project's architecture diagrams as B-roll while narrating design decisions.
- For code snippets, show small focused excerpts (3–8 lines) and zoom in.

## Assets to Prepare
- Screen capture of `streamlit_apps/02_rag_app.py` in action
- Terminal commands for `uvicorn` and ingestion script
- Architecture PNGs from `assessments/03_saas_ai_agent/` (use in B-roll)
- Short prerecorded clip of LLM calls (optional)

---

File created: `ARCHITECTURE_VIDEO_SCRIPT.md`

If you'd like I can also: 
- produce a bullet-point shot list for camera and B-roll, or
- export this into speaker cue cards (one per slide/scene).

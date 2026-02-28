# Assessment 3 – AI Agent SaaS Platform  
**Multi-tenant Web-based Social Media Automation & Lead Management System**

**February 2026**

## Objective

Design a production-oriented SaaS platform that allows companies (tenants) to:

- Connect social media business accounts (Facebook Pages, Instagram Business, X/Twitter, LinkedIn Pages, etc.)
- Receive real-time incoming messages, comments and mentions via webhooks
- Generate AI-powered, context-aware automated replies
- Automatically qualify and tag leads (hot / warm / cold / support ticket / spam / …)
- Extract structured contact & intent data
- Synchronize enriched leads to the tenant’s CRM system (HubSpot, Salesforce, Pipedrive, custom webhook, etc.)

Goal: Save time for social media managers, increase response speed 24/7 and improve lead quality.

## Key Design Goals

- Strong multi-tenancy with strict data isolation
- Asynchronous processing (fast webhook acknowledgment)
- Cost-aware LLM usage
- Production-grade resilience & observability
- Realistic local demo constraints

## High-Level Architecture

```mermaid
graph TD
    A[Company User<br>Dashboard] -->|HTTPS + JWT| B[Frontend<br>Next.js / React]
    C[Social Platforms<br>Meta / X / LinkedIn] -->|Webhook POST| D[Backend API<br>FastAPI]
    D --> E[Event Queue<br>Redis / RabbitMQ]
    E --> F[Background Workers<br>Celery / RQ]
    F --> G[AI Agent Supervisor<br>LangGraph]
    G --> H[Specialized Agents<br>Intent • Qualifier • Extractor • Replier • Retriever]
    H --> I[Vector Store<br>PGVector / Pinecone]
    H --> J[Relational DB<br>PostgreSQL<br>tenant_id everywhere]
    F --> K[CRM Sync Worker<br>Retry + DLQ]
    K --> L[CRM Systems<br>HubSpot / Salesforce / Webhook]
    M[Observability<br>OTel + Prometheus + Loki] -.-> D & F & G
Core AI Agents (LangGraph style)















































AgentPrimary ResponsibilityTypical ModelOutputSupervisor / RouterDecide execution path & parallelismgpt-4o-miniPlanIntent & SentimentClassify: sales / support / complaint / spam / …gpt-4o-miniLabel + confidence + urgencyLead QualifierScore 0–100 + hot / warm / cold / vertical tagsgpt-4o-miniScore + tagsEntity ExtractorName, email, phone, company, product intereststructured outputPydantic objectReply GeneratorCreate natural, on-brand reply (or skip)Claude 3.5 / GPT-4oReply text ≤ 280 charsKnowledge RetrieverRAG over company-specific docs & tone examplesembedding + vector dbContext chunks
Data Flow – Incoming Message → Reply + CRM Sync

Social platform → webhook POST (signature verified)
FastAPI → immediate 200 OK + enqueue event (idempotency key = message ID)
Worker picks event → loads tenant config & vector index
Supervisor routes → parallel agent execution
Reply generated → posted via platform API (if confidence ≥ threshold)
Lead record created / updated → queued for CRM sync
CRM worker pushes data (retry + dead-letter on failure)
Dashboard updated via WebSocket or polling

Multi-tenancy & Isolation

tenant_id (UUID) mandatory on every relevant table
Vector store queries filtered by {"tenant_id": "..."}
Cache keys prefixed with tenant slug
Rate limits, quotas and token metering applied per tenant
Recommended: PostgreSQL Row Level Security (RLS)

Authentication & Authorization

























FlowMechanismUser loginEmail magic link / Google / Microsoft / SSOSocial account connectionOAuth 2.0 Authorization Code + PKCEAPI & frontend callsShort-lived JWT + HttpOnly refresh tokenData accesstenant_id filter + RLS
Security & Privacy Highlights

Social access/refresh tokens encrypted at rest
PII fields (email, phone) encrypted or pseudonymized where possible
Full audit trail of AI-generated replies & CRM pushes
GDPR/CCPA support: data export & tenant deletion endpoints
Automatic webhook secret rotation
Per-tenant rate limiting & circuit breakers

Cost Optimization





























ApproachExpected impactgpt-4o-mini / flash for triage & extraction70–90% cost reductionPremium model only for final high-confidence replies+20–50% savingSemantic cache for frequent questions & tone20–60%Early exit for spam / low-value messagesvariableBatch CRM sync (every 5–15 min)infrastructure cost
Resilience & Recovery Patterns

































Failure scenarioHandlingWebhook signature invalid401 → platform retryLLM rate limit / timeouttenacity retries → static fallback replySocial API 5xxExponential backoff + dead-letter queueCRM repeated failureMark lead sync_failed + notify adminMalformed messageValidation → skip + structured logQueue backlog growingAuto-scale workers + engineering alert
Observability Stack





























ComponentPurposeStructured loggingstructlog / loguru → JSONDistributed tracingOpenTelemetry → Jaeger / TempoMetricsPrometheus – leads, replies, cost, latencyDashboardsGrafana – usage trends, error rates, queue depthAlertsSlack / email on critical thresholds
Local Demo Implementation Notes
For assessment / portfolio purposes the following simplifications are typical:

SQLite + FAISS instead of PostgreSQL + PGVector
Fake webhook endpoint (POST /api/03-saas/webhooks/{tenant_slug}/{platform})
Mock “connect account” button (dummy tokens)
Sequential or simple parallel agent flow
Streamlit dashboard instead of full Next.js frontend
In-memory tasks or fastapi.BackgroundTasks instead of Redis queue

These choices allow the complete system to run locally without external credentials.
Folder Structure (reference)
textassessments/03_saas_ai_agent/
├── agents/                     # LangGraph nodes / chains
│   ├── supervisor.py
│   ├── intent.py
│   ├── qualifier.py
│   ├── extractor.py
│   └── reply.py
├── routers/
│   ├── auth.py
│   ├── webhook.py
│   ├── dashboard.py
│   └── crm.py
├── models.py                   # SQLModel tables
├── schemas.py
├── services.py
├── prompts.py
├── background/
│   └── crm_sync.py
└── streamlit_dashboard.py      # local demo UI
Summary – Why this design is credible

Separates fast webhook acknowledgment from slow AI processing
Enforces tenant isolation at every layer
Uses proven agent orchestration patterns
Keeps per-interaction cost realistic (~$0.001–$0.01)
Provides clear observability & resilience story
Supports incremental rollout (one platform → many)

Questions, feedback and deeper dives welcome.
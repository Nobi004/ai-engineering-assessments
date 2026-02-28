# AI Engineering Assessments - Architecture Guide & Interview Reference

**Document Purpose:** Comprehensive technical architecture overview for interviewers and stakeholders. This document maps the full project structure, key design decisions, and exploration points for technical discussions.

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Project Landscape](#project-landscape)
3. [Assessment 1: Workflow Automation](#assessment-1-workflow-automation)
4. [Assessment 2: RAG Chatbot](#assessment-2-rag-chatbot)
5. [Assessment 3: SaaS Platform Design](#assessment-3-saas-platform-design)
6. [Cross-Cutting Architecture](#cross-cutting-architecture)
7. [Technology Stack](#technology-stack)
8. [Key Discussion Points](#key-discussion-points)
9. [Demo Workflow](#demo-workflow)
10. [Interview Questions & Exploration Areas](#interview-questions--exploration-areas)

---

## Executive Summary

This project demonstrates **three progressive AI engineering challenges** showcasing practical skills in:

- **LLM Integration**: Structured output parsing, intent classification, prompt engineering
- **Retrieval-Augmented Generation**: Vector stores, similarity search, grounded responses
- **System Design**: Multi-tenant architecture, scalable SaaS patterns, security considerations

**Core Achievement:** Complete end-to-end implementations with production-ready patterns (error handling, logging, persistence, validation).

```
┌─────────────────────────────────────────────────────────────────┐
│                    FastAPI Backend (Port 8000)                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Assessment 1     │  Assessment 2      │  Assessment 3   │  │
│  │  Workflow API     │  RAG Chat API      │  SaaS API       │  │
│  └──────────────────────────────────────────────────────────┘  │
│         ↓                    ↓                    ↓             │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │         Core Services Layer (LLM, Embeddings, DB)        │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
         ↓                    ↓                    ↓
    SQLite DB          FAISS Index          PostgreSQL
   (Leads/Chat)       (Company Docs)      (Multi-tenant)
```

---

## Project Landscape

### Directory Structure

```
pyproject.toml
README.md
requirements.txt
assessments/
  01_workflow_automation/
    __init__.py
    routers.py
    schemas.py
    services.py
    prompts/
  02_rag_chatbot/
    __init__.py
    ingest.py
    routers.py
    schemas.py
    services.py
    prompts/
  03_saas_ai_agent/
    __init__.py
    design.md
    agents/
    auth/
    crm/
    tenants/
    webhooks/
backend/
  __init__.py
  main.py
  middleware.py
  __pycache__/
core/
  __init__.py
  config.py
  database.py
  embedding_client.py
  exceptions.py
  llm_client.py
  logger.py
  vector_store.py
data/
  faiss_indexes/
    rag_index.faiss
  uploads/
logs/
streamlit_apps/
  01_workflow_app.py
  02_rag_app.py
```

---

## Assessment 1: Workflow Automation

### Problem Statement

Build an **AI-powered lead processing pipeline** that mimics n8n workflow:
1. Classify incoming lead intent (Sales, Support, Partnership)
2. Extract structured fields (name, email, phone, budget)
3. Persist to database with confidence scoring
4. Handle low-confidence cases with fallback rules

### Architecture

```
Lead Input (JSON)
    ↓
[LLM] Intent Classification (JSON mode)
    ↓
Confidence Threshold Check (> 0.7)
    ├─ Yes → Field Extraction (Pydantic validation)
    │         ↓
    │      [LLM] Extract structured fields
    │         ↓
    │      SQLite Persistence (audit trail)
    │         ↓
    │      Response with intent + fields
    │
    └─ No  → Regex Fallback (generic extraction)
            ↓
         Return with low_confidence=true
```

### Key Technical Components

**1. Intent Classification**
```python
# Using LLM with JSON mode for deterministic output
prompt: "Classify the following lead intent..."
response_format: {"type": "json_object"}
output: {"intent": "Sales", "confidence": 0.92}
```

**2. Robust Error Handling**
```python
# Retry strategy with tenacity (3× exponential backoff)
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
async def classify_intent(lead: LeadInput) -> IntentResult
```

**3. Audit Trail**
- Every lead processing logged with `request_id` for traceability
- Structured logging with `structlog` (JSON format)
- Timestamp, confidence, classification, extraction all recorded

### Database Schema

```sql
-- Leads table (SQLite)
CREATE TABLE leads (
    id UUID PRIMARY KEY,
    intent VARCHAR(50),           -- Sales | Support | Partnership
    name VARCHAR(255),
    email VARCHAR(255),
    phone VARCHAR(20),
    budget DECIMAL(10, 2),
    confidence FLOAT,              -- Classification confidence
    raw_response TEXT,             -- LLM response (debugging)
    processed_at TIMESTAMP,
    request_id UUID                -- Traceability
);
```

### Interview Discussion Points

- **Q: How would you handle concurrent lead processing at scale?**
  - A: Async/await pattern, message queues (Celery/RabbitMQ), rate limiting
  
- **Q: What if the LLM API fails?**
  - A: Retry strategy (exponential backoff), fallback regex extraction, circuit breaker pattern
  
- **Q: How do you validate extracted data?**
  - A: Pydantic models with field validators, regex patterns for email/phone, business logic checks
  
- **Q: Cost optimization for LLM calls?**
  - A: Batch processing, caching intent patterns, fine-tuned smaller models for simple cases

---

## Assessment 2: RAG Chatbot

### Problem Statement

Build a **company-specific chatbot** that:
1. Ingests company documents (TXT, PDF)
2. Retrieves relevant context for user queries
3. Generates grounded responses (no hallucination)
4. Maintains conversation history
5. Provides confidence scores and source attribution

### Architecture

```
Company Documents (Upload)
    ↓
[Chunking] RecursiveCharacterTextSplitter (800 tokens, 120 overlap)
    ↓
[Embeddings] text-embedding-3-small (OpenAI)
    ↓
FAISS Vector Store (In-memory index + SQLModel metadata)
    ↓
Query from User
    ↓
[Embedding] Same model for consistency
    ↓
[Retrieval] Similarity search (top-k with metadata filtering)
    ├─ Confidence threshold check (> 0.45)
    │
    ├─ Yes → [Context Assembly]
    │         ├─ Retrieved chunks
    │         ├─ Previous chat history
    │         └─ System prompt
    │         ↓
    │      [LLM Generation] Grounded response
    │         ↓
    │      [Optional Rewrite] Friendliness pass
    │         ↓
    │      Response + Confidence + Sources
    │
    └─ No  → Refusal: "I don't have information..."
```

### Key Technical Components

**1. Vector Store with Metadata Filtering**
```python
# FAISS index keyed by company_id for multi-tenancy
vector_store.add_documents(
    documents=chunks,
    company_id="acme-corp",           # Tenant isolation
    metadata={"source": "file.txt"}
)

# Retrieval with metadata filtering
results = vector_store.similarity_search(
    query_embedding,
    company_id="acme-corp",            # Only this company's docs
    k=4,
    threshold=0.45
)
```

**2. Dual-Pass Generation for Quality**
```python
# Pass 1: Generate grounded answer
answer = await llm.generate(context, query, system_prompt)

# Pass 2: Rewrite for friendliness (optional)
if answer quality:
    rewrite_prompt = "Make this warm and conversational..."
    friendly_answer = await llm.generate(answer, rewrite_prompt)
```

**3. Conversation Memory**
```python
# SQLModel persistence
class ChatMessage(SQLModel, table=True):
    id: UUID
    session_id: UUID
    company_id: str
    role: ChatRole  # user | assistant
    content: str
    confidence: float
    sources: list[str]  # For attribution
    created_at: datetime
```

### Database Schema

```sql
-- Chat history (SQLite)
CREATE TABLE chat_message (
    id UUID PRIMARY KEY,
    session_id UUID,               -- Conversation grouping
    company_id VARCHAR(100),       -- Multi-tenant
    role VARCHAR(20),              -- user | assistant
    content TEXT,                  -- Message body
    confidence FLOAT,              -- Generation confidence
    sources TEXT,                  -- JSON array of source files
    created_at TIMESTAMP
);
```

### Interview Discussion Points

- **Q: How do you prevent hallucinations?**
  - A: Similarity threshold (0.45), exact refusal message, grounding in context, optional rewrite pass
  
- **Q: Handling document updates?**
  - A: Invalidate FAISS index, re-chunk and re-embed, update metadata with version info
  
- **Q: Scaling to thousands of companies?**
  - A: Vector store per company (sharding), lazy loading, distributed FAISS, PostgreSQL for metadata
  
- **Q: Why text-embedding-3-small vs larger models?**
  - A: Good quality-cost tradeoff, 1536 dimensions, optimized for retrieval, consistent with GPT models
  
- **Q: How do you handle context window limits?**
  - A: Ranked retrieval (top-k), summarization of older messages, sliding window approach

---

## Assessment 3: SaaS Platform Design

### Problem Statement

Design a **scalable AI agent SaaS platform** featuring:
1. Multi-tenant architecture with strict isolation
2. Multiple AI agents (Reply Generator, Lead Qualifier, Entity Extractor)
3. Integration with external services (CRM, social media)
4. Webhook event processing
5. Authentication & authorization patterns
6. Cost optimization and monitoring

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (Next.js)                    │
│              Multi-tenant Dashboard UI                   │
└─────────────────────────────────────────────────────────┘
                         ↓ HTTP/WebSocket
┌─────────────────────────────────────────────────────────┐
│                   API Gateway / Auth                      │
│         JWT Validation, Rate Limiting, Request ID         │
└─────────────────────────────────────────────────────────┘
                         ↓
         ┌───────────────┼───────────────┐
         ↓               ↓               ↓
    ┌─────────┐   ┌─────────────┐   ┌────────────┐
    │ Reply   │   │   Lead      │   │  Entity    │
    │ Agent   │   │ Qualifier   │   │ Extractor  │
    │         │   │             │   │            │
    │[GPT-4]  │   │  [GPT-3.5]  │   │[GPT-3.5]   │
    └─────────┘   └─────────────┘   └────────────┘
         ↓               ↓               ↓
         └───────────────┼───────────────┘
                         ↓
         ┌───────────────┼───────────────┐
         ↓               ↓               ↓
    ┌─────────┐   ┌─────────────┐   ┌────────────┐
    │   CRM   │   │  Database   │   │   Cache    │
    │ Webhook │   │ (PostgreSQL)│   │  (Redis)   │
    │ Handler │   │ (Tenanted)  │   │            │
    └─────────┘   └─────────────┘   └────────────┘
         ↓
    ┌─────────────────────────┐
    │ External Integrations   │
    │ - Slack                 │
    │ - HubSpot CRM          │
    │ - LinkedIn/Twitter     │
    │ - Zapier               │
    └─────────────────────────┘
```

### Key Technical Components

**1. Multi-Tenancy Isolation**
```python
# Request context includes tenant_id
class RequestContext:
    tenant_id: UUID
    user_id: UUID
    permissions: list[str]

# Every query scoped to tenant
async def get_leads(context: RequestContext):
    # WHERE clause automatically filters by context.tenant_id
    return db.query(Lead).filter(Lead.tenant_id == context.tenant_id).all()
```

**2. Agent Architecture**
```python
# Agent interface
class AIAgent(ABC):
    @abstractmethod
    async def process(self, context: Context, input: AgentInput) -> AgentOutput:
        pass

# Implementations
class ReplyAgent(AIAgent):
    """Generates email replies based on context"""
    async def process(self, context, message) -> str:
        prompt = f"Given: {message.thread_context}\nGenerate a professional reply..."
        return await llm.generate(prompt)

class LeadQualifier(AIAgent):
    """Scores lead quality"""
    async def process(self, context, lead) -> QualificationScore:
        prompt = f"Score this lead: {lead.to_json()}"
        return parse_score(await llm.generate(prompt))
```

**3. Webhook Event Processing**
```python
# Incoming webhook from CRM
@router.post("/webhooks/crm/contact.updated")
async def on_contact_updated(event: WebhookPayload):
    # Extract tenant from event
    tenant_id = extract_tenant(event)
    
    # Queue async processing
    await task_queue.enqueue(
        process_contact_update,
        tenant_id=tenant_id,
        contact_id=event.data.id
    )
    
    return {"status": "received"}

# Async worker processes
async def process_contact_update(tenant_id: UUID, contact_id: str):
    context = RequestContext(tenant_id=tenant_id)
    contact = await crm_client.get_contact(contact_id)
    
    # Run through agents
    qualified_score = await lead_qualifier.process(context, contact)
    
    # Write results back to CRM
    await crm_client.update_contact(contact_id, {
        "ai_score": qualified_score.value
    })
```

**4. Security & Authentication**
```python
# JWT token with tenant claim
def create_access_token(user_id: UUID, tenant_id: UUID):
    payload = {
        "sub": str(user_id),
        "tenant": str(tenant_id),
        "iat": datetime.now(),
        "exp": datetime.now() + timedelta(hours=8)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

# Middleware validates token
@app.middleware("http")
async def tenant_middleware(request: Request, call_next):
    token = extract_token(request.headers)
    claims = jwt.decode(token, SECRET_KEY)
    
    request.state.tenant_id = UUID(claims["tenant"])
    request.state.user_id = UUID(claims["sub"])
    
    return await call_next(request)
```

### Database Schema (Multi-tenant)

```sql
-- All tables include tenant_id for isolation
CREATE TABLE tenant (
    id UUID PRIMARY KEY,
    name VARCHAR(255),
    subscription_tier VARCHAR(50),    -- starter | pro | enterprise
    created_at TIMESTAMP
);

CREATE TABLE lead (
    id UUID PRIMARY KEY,
    tenant_id UUID REFERENCES tenant(id),
    name VARCHAR(255),
    email VARCHAR(255),
    ai_score FLOAT,                   -- Qualification score
    qualified_at TIMESTAMP,
    created_at TIMESTAMP
);

CREATE TABLE crm_sync (
    id UUID PRIMARY KEY,
    tenant_id UUID REFERENCES tenant(id),
    external_platform VARCHAR(50),    -- hubspot | salesforce
    last_sync TIMESTAMP,
    sync_status VARCHAR(50)           -- pending | success | failed
);

-- Audit table
CREATE TABLE audit_log (
    id UUID PRIMARY KEY,
    tenant_id UUID REFERENCES tenant(id),
    action VARCHAR(255),
    resource_type VARCHAR(100),
    resource_id UUID,
    performed_by UUID,
    created_at TIMESTAMP
);
```

### Interview Discussion Points

- **Q: How do you ensure complete tenant isolation?**
  - A: RLS policies, filtered queries, audit logging, separate encryption keys, network segmentation
  
- **Q: Handling webhook failures?**
  - A: Message queue (RabbitMQ), retry with backoff, DLQ for failed events, alerting
  
- **Q: Scaling agents for 10,000 concurrent requests?**
  - A: Agent pooling, load balancing, horizontal scaling, request queuing, LLM rate limit management
  
- **Q: Cost control for high API usage?**
  - A: Token counting, batching, smaller models for simple tasks, caching, usage alerts per tenant
  
- **Q: How do you handle agent hallucination?**
  - A: Grounding in CRM data, validation before CRM update, confidence thresholds, human review for high-impact changes

---

## Cross-Cutting Architecture

### 1. Logging & Monitoring

**Structured Logging**
```python
# Using structlog for consistent JSON output
import structlog

logger = structlog.get_logger()

# Every operation logged with context
logger.info(
    "chat_completed",
    company_id="acme-corp",
    confidence=0.92,
    response_tokens=150,
    latency_ms=1234,
    request_id="req-123"
)
```

**Metrics to Track**
- LLM API latency (p50, p95, p99)
- Token usage per model
- Vector store query time
- Error rates by type
- Confidence score distributions
- User engagement (chats per session, repeat users)

### 2. Error Handling & Resilience

**Exception Hierarchy**
```python
class AppException(Exception):
    """Base exception"""
    pass

class LLMException(AppException):
    """LLM API failures"""
    pass

class ValidationException(AppException):
    """Input validation failures"""
    pass

class AuthorizationException(AppException):
    """Permission denied"""
    pass
```

**Circuit Breaker Pattern**
```python
@circuit_breaker(
    failure_threshold=5,
    recovery_timeout=60,
    expected_exception=LLMException
)
async def call_llm(prompt: str):
    return await llm_client.generate(prompt)
```

### 3. Performance Optimization

**Caching Strategy**
```python
# Cache company documents (invalidated on upload)
@cache(ttl=3600)
async def get_company_chunks(company_id: str):
    return vector_store.get_chunks(company_id)

# Cache intent patterns (rarely change)
@cache(ttl=86400)
async def get_intent_patterns():
    return load_intent_patterns()
```

**Batch Processing**
```python
# Process multiple leads together for efficiency
async def process_leads_batch(leads: list[LeadInput]):
    embeddings = await embedding_client.batch_embed([l.text for l in leads])
    intents = await llm_client.batch_classify([l.text for l in leads])
    # ... persist all at once
```

---

## Technology Stack

### Language & Framework

| Component | Tech | Rationale |
|-----------|------|-----------|
| Backend | FastAPI | Async support, Pydantic validation, OpenAPI docs |
| Async Runtime | asyncio | Built-in Python async, integrates with FastAPI |
| Frontend (Demo) | Streamlit | Rapid prototyping, interactive widgets |
| Frontend (Production) | Next.js 14+ | Server components, TypeScript, performance |

### LLM & Embeddings

| Component | Provider | Model | Rationale |
|-----------|----------|-------|-----------|
| LLM (General) | OpenAI | GPT-4, GPT-3.5-turbo | Quality, reliability, JSON mode support |
| Embeddings | OpenAI | text-embedding-3-small | 1536 dims, good quality-cost ratio |
| Intent Classification | OpenAI | GPT-3.5 with JSON mode | Structured output, lower cost |

### Data & Storage

| Component | Tech | Use Case |
|-----------|------|----------|
| Vector Store | FAISS | In-memory similarity search, indexed retrieval |
| Metadata Store | SQLModel + SQLite | Local dev, chat history, audit logs |
| Production DB | PostgreSQL | Multi-tenant data, transactions, ACID |
| Cache | Redis | Session data, rate limiting, embeddings cache |
| File Storage | Local / S3 | Document uploads, index persistence |

### Infrastructure & DevOps

| Component | Tech | Purpose |
|-----------|------|---------|
| Server | Uvicorn | ASGI server for FastAPI |
| Process Manager | Supervisor / systemd | Long-running background workers |
| Task Queue | Celery + RabbitMQ | Async job processing |
| Logging | structlog + CloudWatch | Structured logs, centralized aggregation |
| Monitoring | Prometheus + Grafana | Metrics, dashboards, alerts |

---

## Key Discussion Points

### 1. Design Trade-offs

**FAISS vs PostgreSQL pgvector**
- ✅ FAISS: Fast, flexible, good for research/prototyping
- ✅ pgvector: Integrated storage, better for production at scale
- 🎯 Decision: FAISS for assessment (proves understanding), production would use pgvector

**Synchronous vs Asynchronous Processing**
- ✅ Async: Better concurrency, resource efficiency, non-blocking I/O
- ✅ Sync: Simpler debugging, easier to understand
- 🎯 Decision: Async everywhere (matches modern Python best practices)

**Document Chunking Strategy**
- ✅ RecursiveCharacterTextSplitter: Preserves document structure, good for mixed content
- ✅ Fixed-size chunks: Simpler, more predictable
- 🎯 Decision: Recursive with overlap (better context preservation)

### 2. Scalability Considerations

**From 10 to 10,000 Users**
1. Load balancing (Nginx, HAProxy)
2. Horizontal scaling of FastAPI instances
3. Database read replicas
4. Cache layer (Redis)
5. CDN for static assets
6. Queue-based processing for heavy operations

**LLM API Cost at Scale**
- Token counting for budget tracking
- Batching requests where possible
- Fine-tuned models for commodity tasks
- Fallback to smaller models for simple queries

### 3. Security Hardening

- Input validation (Pydantic models + custom validators)
- Output sanitization (XSS prevention for chat)
- Rate limiting per tenant/user
- SQL injection prevention (SQLModel ORM)
- CORS configuration (restrict origins)
- HTTPS enforcement
- API key rotation strategies

### 4. Observability

**Logging**
- Request ID correlation across services
- Structured JSON logs for parsing
- Different log levels (DEBUG, INFO, WARNING, ERROR)
- Sensitive data masking (PII redaction)

**Tracing**
- Distributed tracing for multi-service flows
- Request latency breakdown per component
- Error attribution (which service failed?)

**Metrics**
- Business metrics (leads processed, chat sessions, etc.)
- Technical metrics (API latency, error rates, queue depth)
- Resource metrics (CPU, memory, disk, network)

---

## Demo Workflow

### End-to-End User Journey

```
User Flow (3 Assessment Demos)
│
├─ Assessment 1: Workflow Automation
│  │
│  ├─ Upload JSON lead: {"name": "John", "message": "I need sales support"}
│  │
│  ├─ [Backend Process]
│  │   ├─ LLM classifies intent: "Sales" (confidence: 0.95)
│  │   ├─ LLM extracts fields: {name, email, phone, budget}
│  │   ├─ Validates output with Pydantic
│  │   └─ Persists to SQLite with audit trail
│  │
│  └─ Response: {"intent": "Sales", "confidence": 0.95, fields: {...}}
│
├─ Assessment 2: RAG Chatbot
│  │
│  ├─ System ingests "about_company.txt"
│  │   ├─ Chunks text (800 tokens, 120 overlap)
│  │   ├─ Embeds with text-embedding-3-small
│  │   └─ Stores in FAISS + SQLite metadata
│  │
│  ├─ User asks: "What are your projects?"
│  │
│  ├─ [Backend Process]
│  │   ├─ Embeds query
│  │   ├─ Similarity search in FAISS
│  │   ├─ Retrieves top-4 chunks (confidence > 0.45)
│  │   ├─ Assembles context with chat history
│  │   ├─ LLM generates grounded response
│  │   ├─ Optional rewrite for friendliness
│  │   └─ Persists chat message with sources
│  │
│  └─ Response: {answer: "Hey there!...", sources: [...], confidence: 0.92}
│
└─ Assessment 3: SaaS Design Review
   │
   ├─ Architecture walkthrough
   │   ├─ Multi-tenancy strategy
   │   ├─ Agent design patterns
   │   ├─ Webhook event handling
   │   └─ Security model
   │
   └─ Discussion points for interviewers
```

### Quick Test Commands

```bash
# Assessment 1: Lead Classification
curl -X POST http://localhost:8000/api/01-workflow/leads \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Alice Johnson",
    "message": "Interested in partnership opportunities"
  }'

# Assessment 2: RAG Chat (Query parameter format)
curl -X POST "http://localhost:8000/api/02-rag/chat?query=What%20projects%20are%20you%20working%20on" \
  -H "Content-Type: application/json"

# Assessment 2: RAG Chat (Body format)
curl -X POST http://localhost:8000/api/02-rag/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Tell me about Acme Corp",
    "company_id": "acme-corp"
  }'

# API Documentation (auto-generated)
# OpenAPI: http://localhost:8000/openapi.json
# Interactive: http://localhost:8000/docs (Swagger UI)

# Streamlit Demo
streamlit run streamlit_apps/02_rag_app.py
# Access: http://localhost:8501
```

---

## Interview Questions & Exploration Areas

### Tier 1: Foundational Understanding

**Q1: Explain the overall architecture and how the three assessments connect.**
- Expected Answer Should Cover:
  - Backend FastAPI with three independent routers
  - Shared core services (LLM, embeddings, database)
  - Different use cases but similar patterns
  - Discussion of scalability from assessment 1 → 3

**Q2: What's the purpose of each assessment?**
- Expected Coverage:
  - Assessment 1: Structured LLM output parsing, data extraction
  - Assessment 2: RAG, retrieval-augmented generation, grounded responses
  - Assessment 3: System design at scale, multi-tenancy, agents

**Q3: Walk me through a request from client to database.**
- Expected Details:
  - HTTP request received by FastAPI
  - Request validation with Pydantic
  - Service layer orchestration
  - LLM API calls
  - Database persistence
  - Response serialization

### Tier 2: Technical Depth

**Q4: How do you prevent the LLM from hallucinating in the RAG system?**
- Expected Approaches:
  - Similarity threshold (0.45 cutoff)
  - Grounding context in actual documents
  - Exact refusal message when no match found
  - Confidence scoring
  - Optional human review layer

**Q5: Describe your multi-tenancy implementation in Assessment 3.**
- Key Points:
  - Row-level security policies in database
  - Request context includes tenant_id
  - Every query filtered by tenant
  - Separate encryption keys per tenant
  - Audit logging of access

**Q6: How would you scale this to handle 1 million daily active users?**
- Discussion Areas:
  - Horizontal scaling of FastAPI instances
  - Load balancing strategy
  - Database sharding (by company/tenant)
  - Cache layer (Redis)
  - Message queue for async processing
  - LLM API rate limit management
  - Cost optimization strategies

### Tier 3: Production Readiness

**Q7: What happens when OpenAI API rate limits are hit?**
- Expected Handling:
  - Retry strategy with exponential backoff
  - Circuit breaker pattern
  - Fallback mechanisms
  - Queue-based processing
  - User communication (graceful degradation)

**Q8: How do you monitor and debug issues in production?**
- Observability Strategy:
  - Structured logging with request IDs
  - Distributed tracing
  - Metrics dashboards
  - Alert thresholds
  - Error tracking (Sentry)
  - Performance profiling

**Q9: What security vulnerabilities should you be concerned about?**
- Areas to Address:
  - SQL injection (mitigation: ORM)
  - LLM prompt injection (input sanitization)
  - Data leakage between tenants (tenant isolation)
  - API key exposure (environment variables, secrets manager)
  - Rate limiting and DDoS protection
  - PII in logs (masking, redaction)

### Tier 4: Design Discussions

**Q10: Justify your choice of FAISS over PostgreSQL pgvector.**
- Discussion Points:
  - FAISS: Fast, in-memory, good for research
  - pgvector: Persistent, built-in SQL, production-grade
  - Trade-offs: Performance vs. durability
  - Migration path to pgvector

**Q11: Why use LangChain vs. direct OpenAI API calls?**
- Considerations:
  - Abstraction over model providers
  - Built-in chains and patterns
  - Flexibility for future model switching
  - Tool use and agents support
  - Overhead and complexity trade-off

**Q12: How would you implement A/B testing for different prompt versions?**
- Approach:
  - Tenant-level feature flags
  - Request context includes experiment ID
  - Route to different prompt versions
  - Track metrics by variant
  - Statistical significance testing

### Bonus: Follow-up Explorations

- **Cost Analysis**: Calculate token costs for typical workflows
- **Latency Analysis**: Where are the bottlenecks? (LLM API? Vector search? DB?)
- **Alternative Architectures**: Event-driven? CQRS? GraphQL?
- **Testing Strategy**: Unit tests? Integration tests? E2E tests?
- **Documentation**: API docs? Architecture diagrams? Runbooks?
- **Deployment**: CI/CD pipeline? Blue-green deployment? Rollback strategy?

---

## Architecture Decision Records (ADRs)

### ADR-001: FastAPI over Django/Flask

**Decision**: Use FastAPI for the backend

**Rationale**:
- Native async/await support (critical for LLM API calls)
- Automatic OpenAPI documentation
- Pydantic validation built-in
- Superior performance (similar to Go frameworks)
- Better suited for I/O-heavy workloads

**Consequences**:
- Requires Python 3.8+
- Learning curve for async patterns
- Smaller ecosystem than Django

---

### ADR-002: FAISS over pgvector for Initial Implementation

**Decision**: Use FAISS for vector store in assessments

**Rationale**:
- Speed (in-memory, no network overhead)
- Flexibility (can implement custom operators)
- Good for demonstrating RAG concepts
- Lower operational complexity for demo

**Consequences**:
- Not persistent (requires serialize/deserialize)
- Single-machine limitation
- Production version would need pgvector

---

### ADR-003: Double-Pass LLM for Response Quality

**Decision**: Optional rewrite pass after initial generation

**Rationale**:
- Improves friendliness without changing grounding
- Can be toggled per request
- Cost is acceptable (+1 API call)
- Demonstrates prompt engineering sophistication

**Consequences**:
- Doubles LLM API calls
- Adds ~1-2 seconds latency
- Risk of rewrite degrading correctness

---

## Key Metrics & Success Criteria

### Assessment 1 Success Metrics

- ✅ Lead intent classification accuracy > 90%
- ✅ Field extraction confidence scores > 0.85
- ✅ Error handling for 100% of failure modes
- ✅ API response time < 2 seconds (99th percentile)
- ✅ Audit trail captures all processing details

### Assessment 2 Success Metrics

- ✅ Relevance of retrieved documents > 0.45 similarity
- ✅ Hallucination rate < 5% (all responses grounded)
- ✅ Source attribution accuracy 100%
- ✅ Response time < 3 seconds for typical queries
- ✅ Conversation context maintained across turns

### Assessment 3 Success Metrics

- ✅ Complete system design documented
- ✅ Multi-tenancy patterns clearly defined
- ✅ Agent architecture scalable to 10K+ concurrent
- ✅ Security model addresses major threats
- ✅ Cost analysis and optimization strategies identified

---

## Next Steps & Future Enhancements

### Phase 2: Production Readiness
- [ ] Migrate to PostgreSQL + pgvector for persistence
- [ ] Implement Redis caching layer
- [ ] Add Celery for async job processing
- [ ] Deploy with Docker and Kubernetes
- [ ] Set up CI/CD pipeline (GitHub Actions)

### Phase 3: Frontend Development
- [ ] Build Next.js dashboard for Assessment 3 SaaS
- [ ] Implement real-time WebSocket chat
- [ ] Add data visualization and analytics
- [ ] Create admin panel for tenant management

### Phase 4: Advanced Features
- [ ] Fine-tuned models for specific domains
- [ ] Multi-language support
- [ ] Voice input/output integration
- [ ] Advanced analytics and reporting
- [ ] Custom agent training per tenant

### Phase 5: Enterprise Features
- [ ] SSO / SAML integration
- [ ] Audit logging and compliance reports
- [ ] Custom SLA management
- [ ] Dedicated support tiers
- [ ] On-premises deployment option

---

## Appendix: Key Concepts Reference

### Retrieval-Augmented Generation (RAG)
Process of retrieving relevant documents and using them as context for LLM generation, reducing hallucination and improving grounding.

### Multi-Tenancy
Architectural pattern where single application instance serves multiple customers (tenants), with strict data isolation.

### Vector Embeddings
Numerical representation of text, enabling semantic similarity search. Used for document retrieval in RAG systems.

### Prompt Engineering
Art of designing effective prompts to guide LLM behavior toward desired outputs.

### FAISS (Facebook AI Similarity Search)
Library for efficient similarity search and clustering of dense vectors.

### JSON Mode
OpenAI API feature that forces responses to be valid JSON, enabling reliable structured output extraction.

---

## Questions for Interviewers to Ask

1. **"Walk me through your debugging process when the RAG system starts returning hallucinated answers."**
   - Tests: Root cause analysis, observability thinking, systematic problem-solving

2. **"How would you optimize costs if token usage doubles overnight?"**
   - Tests: Business acumen, system understanding, optimization mindset

3. **"Describe how you'd handle a data leak where one tenant saw another's documents."**
   - Tests: Security awareness, incident response, system thinking

4. **"What would you change about this architecture if you had to support 100x more data?"**
   - Tests: Scalability thinking, trade-off analysis, system design maturity

5. **"Show me the most complex piece of code you wrote and explain it."**
   - Tests: Communication, technical depth, code quality awareness

---

## Document History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-28 | Initial architecture guide created |
| | | Three assessments documented |
| | | Interview questions framework established |

---

**Document Created**: February 28, 2026
**Last Updated**: February 28, 2026
**Author**: AI Engineering Assessment Team
**Status**: Active - Use for interviews and technical discussions

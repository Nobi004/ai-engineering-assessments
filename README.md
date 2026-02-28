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

# AI Engineering Assessment – Part 3  
**AI Agent SaaS Platform**  
**Multi-tenant Web-based Social Media Automation & Lead Management System**

**Objective**  
Design and describe a production-grade SaaS platform where companies can connect their social media business pages/accounts, receive AI-powered automated replies, auto-tag incoming leads (hot / warm / cold), and synchronize qualified leads with their CRM system.

**Date of design**  
February 2026

**Tech stack orientation**  
- Backend: FastAPI (Python)  
- Frontend: Next.js 14+ / React Server Components (or Streamlit for quick demo)  
- AI orchestration: LangGraph (LangChain ecosystem)  
- Database: PostgreSQL + PGVector (or SQLite + FAISS for local demo)  
- Queue: Redis / Celery or RQ  
- Auth: OAuth 2.0 + JWT (Auth0 / Clerk / self-hosted)  
- Observability: OpenTelemetry, Prometheus, structured logging (structlog)

## Table of Contents

- [Product Overview](#product-overview)
- [Key Features](#key-features)
- [System Architecture Diagram](#system-architecture-diagram)
- [Core Components & AI Agents](#core-components--ai-agents)
- [Critical Data Flows](#critical-data-flows)
- [Authentication & Authorization](#authentication--authorization)
- [Multi-tenancy & Data Isolation](#multi-tenancy--data-isolation)
- [Security & Privacy](#security--privacy)
- [Cost Optimization Strategies](#cost-optimization-strategies)
- [Failure Modes & Recovery Patterns](#failure-modes--recovery-patterns)
- [Observability & Monitoring](#observability--monitoring)
- [Local Demo Implementation Notes](#local-demo-implementation-notes)
- [Future Scaling Path](#future-scaling-path)

## Product Overview

Companies sign up → connect social media business accounts (Facebook Pages, Instagram Business, X/Twitter, LinkedIn Pages, etc.) → the system listens for incoming messages, comments, mentions → AI agents analyze, reply automatically when appropriate, qualify leads, and push structured data to the company's CRM.

Goal: Save time for social media & community managers while improving response speed and lead quality.

## Key Features

- Connect & manage multiple social media accounts per tenant
- Real-time incoming message processing via webhooks
- AI-generated context-aware auto-replies
- Lead intent classification & qualification (hot / warm / cold)
- Automatic tagging & entity extraction (name, email, company, interest…)
- CRM integration (HubSpot, Salesforce, Pipedrive, custom webhook)
- Tenant dashboard: leads overview, reply history, usage & cost tracking
- Usage-based billing foundation (token consumption tracking)

## System Architecture Diagram

```mermaid
graph TD
    A[Company User<br>Browser / Mobile] -->|HTTPS + JWT| B[CDN / Load Balancer]
    B --> C[Frontend<br>Next.js / React]
    C -->|API calls / WS| D[Backend API<br>FastAPI]
    
    E[Social Platforms<br>FB/IG/X/LI] -->|Webhook POST| F[Webhook Receiver<br>FastAPI]
    F --> G[Event Queue<br>Redis / RabbitMQ]
    
    G --> H[Background Workers<br>Celery / RQ]
    H --> I[AI Agent Supervisor<br>LangGraph]
    
    I --> J[Specialized Agents<br>• Intent & Sentiment<br>• Lead Qualifier<br>• Entity Extractor<br>• Reply Generator<br>• Knowledge Retriever]
    
    J --> K[Vector Store<br>PGVector / Pinecone / Weaviate]
    J --> L[Relational DB<br>PostgreSQL<br>Tenants • Leads • Connections]
    
    H --> M[CRM Sync Worker<br>Retry + Dead-letter]
    M --> N[CRM Systems<br>HubSpot / Salesforce / Webhook]
    
    O[Observability<br>OTel + Prometheus + Loki / Grafana] -.-> D & H & I
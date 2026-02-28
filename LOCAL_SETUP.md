# AI Agent SaaS Platform - Local Setup Guide

This guide walks you through setting up and running the AI Agent SaaS Platform locally for development and testing.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Backend Setup](#backend-setup)
4. [Database Setup](#database-setup)
5. [Running the Backend](#running-the-backend)
6. [Running the Frontend](#running-the-frontend)
7. [Testing the System](#testing-the-system)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements
- **OS**: Windows, macOS, or Linux
- **Python**: 3.10 or higher
- **Node.js**: 16+ (for frontend)
- **Git**: For cloning the repository
- **OpenAI API Key**: Required for AI features

### Required Services
- **PostgreSQL 14+** (or SQLite for local dev)
- **Redis 6+** (for queue management)
- **Docker** (optional, for containerized setup)

### API Keys Needed
- OpenAI API Key (`OPENAI_API_KEY`)
- Social Media Platform Credentials (Facebook, Instagram, Twitter, LinkedIn)

---

## Environment Setup

### Step 1: Clone the Repository

```bash
git clone https://github.com/Nobi004/ai-engineering-assessments.git
cd "ai-engineering-assessments"
```

### Step 2: Create Python Virtual Environment

**On Windows:**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**On macOS/Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Step 3: Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

Create a `.env` file in the project root:

```bash
# API Keys
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4

# Database
DATABASE_URL=sqlite:///./app.db
# For PostgreSQL: postgresql://user:password@localhost:5432/saas_db

# Redis (for queue)
REDIS_URL=redis://localhost:6379/0

# Social Media API Keys (optional for local testing)
FACEBOOK_ACCESS_TOKEN=your-token
INSTAGRAM_ACCESS_TOKEN=your-token
TWITTER_API_KEY=your-key
LINKEDIN_ACCESS_TOKEN=your-token

# JWT Settings
JWT_SECRET=your-secret-key-here
JWT_ALGORITHM=HS256

# Application Settings
DEBUG=True
ENVIRONMENT=development
ALLOWED_HOSTS=localhost,127.0.0.1
```

---

## Backend Setup

### Step 1: Install Dependencies

```bash
# Ensure virtual environment is activated
pip install fastapi uvicorn sqlmodel psycopg2-binary redis celery langchain openai
```

### Step 2: Initialize Database

```bash
# For SQLite (default for local dev)
python -c "from core.database import init_db; init_db()"
```

### Step 3: Create Database Tables

```bash
# Using SQLAlchemy/SQLModel
python -m alembic upgrade head
```

---

## Database Setup

### Option A: SQLite (Easiest for Local Dev)

SQLite is already configured. No additional setup needed.

```bash
# Database file will be created at: ./app.db
```

### Option B: PostgreSQL (Production-like Setup)

```bash
# Install PostgreSQL if not already installed
# Windows: https://www.postgresql.org/download/windows/
# macOS: brew install postgresql
# Linux: sudo apt-get install postgresql

# Start PostgreSQL
pg_ctl start

# Create database
createdb saas_db

# Update DATABASE_URL in .env
DATABASE_URL=postgresql://user:password@localhost:5432/saas_db

# Run migrations
python -m alembic upgrade head
```

### Option C: Docker Setup (Recommended for Production-like Environment)

```bash
# Start PostgreSQL in Docker
docker run --name saas-postgres \
  -e POSTGRES_USER=admin \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=saas_db \
  -p 5432:5432 \
  -d postgres:14

# Start Redis in Docker
docker run --name saas-redis \
  -p 6379:6379 \
  -d redis:7
```

---

## Running the Backend

### Start FastAPI Server

**Terminal 1: Backend API**

```bash
# Navigate to project root
cd D:\End\ to\ End\ projects\Assesment_mysoft_heaven

# Activate virtual environment
.\.venv\Scripts\Activate.ps1  # Windows
# or
source .venv/bin/activate  # macOS/Linux

# Start Uvicorn server
uvicorn backend.main:app --reload --port 8000
```

**Expected Output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started server process [PID]
INFO:     Application startup complete.
```

### Start Background Workers (Optional)

**Terminal 2: Celery Worker** (for processing AI tasks)

```bash
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Start Celery worker
celery -A assessments.rag_chatbot.tasks worker --loglevel=info
```

### Start Redis Server (If Using Celery)

**Terminal 3: Redis**

```bash
# Start Redis (if not in Docker)
redis-server

# Or start Redis CLI to monitor
redis-cli
```

---

## Running the Frontend

### Option A: Streamlit (Quick Demo)

```bash
# Terminal 4: Streamlit App
cd streamlit_apps

# Activate virtual environment
..\.venv\Scripts\Activate.ps1

# Start Streamlit
streamlit run 02_rag_app.py
```

**Access at:** http://localhost:8501

### Option B: React/Next.js Frontend (For Production)

```bash
# Terminal 4: Next.js Frontend
cd frontend  # (if exists)

# Install dependencies
npm install

# Start development server
npm run dev
```

**Access at:** http://localhost:3000

---

## Testing the System

### 1. API Health Check

```bash
curl http://localhost:8000/health
```

**Expected Response:**
```json
{"status": "healthy"}
```

### 2. Test RAG Chat Endpoint

```bash
# Test with query parameter
curl -X POST "http://localhost:8000/api/02-rag/chat?query=tell+me+about+the+company"

# Or with JSON body
curl -X POST http://localhost:8000/api/02-rag/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "What are your projects?", "company_id": "acme-corp"}'
```

### 3. Ingest Sample Documents

```bash
python assessments/rag_chatbot/ingest.py --company-id acme-corp
```

### 4. Check Database

**SQLite:**
```bash
sqlite3 app.db
> .tables
> SELECT * FROM companies;
```

**PostgreSQL:**
```bash
psql -U admin -d saas_db
# psql> \dt  (list tables)
# psql> SELECT * FROM companies;
```

### 5. Interactive Python Testing

```bash
python -c "
import asyncio
from assessments.rag_chatbot.services import RAGService
from uuid import uuid4

async def test():
    resp = await RAGService.chat('acme-corp', 'What does your company do?', uuid4())
    print(resp)

asyncio.run(test())
"
```

---

## Troubleshooting

### Issue: `ModuleNotFoundError: No module named 'assessments'`

**Solution:**
```bash
# Add project root to PYTHONPATH
set PYTHONPATH=%cd%  # Windows
export PYTHONPATH=$(pwd)  # macOS/Linux

# Or run from project root
cd D:\End\ to\ End\ projects\Assesment_mysoft_heaven
```

### Issue: OpenAI API Key Not Found

**Solution:**
```bash
# Verify .env file exists in project root
# Check that OPENAI_API_KEY is set correctly
# Test the key:
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('OPENAI_API_KEY'))"
```

### Issue: Database Connection Failed

**Solution:**
```bash
# For SQLite:
rm app.db  # Delete old database
python -c "from core.database import init_db; init_db()"  # Recreate

# For PostgreSQL:
# Ensure PostgreSQL service is running
# Verify DATABASE_URL in .env is correct
```

### Issue: Redis Connection Refused

**Solution:**
```bash
# Start Redis server
redis-server

# Or install via package manager
# Windows: choco install redis
# macOS: brew install redis
# Linux: sudo apt-get install redis-server
```

### Issue: Port Already in Use

**Solution:**
```bash
# Use a different port
uvicorn backend.main:app --port 8001

# Or find and kill process using port
# Windows: netstat -ano | findstr :8000
# macOS/Linux: lsof -i :8000
```

### Issue: Virtual Environment Not Activating

**Solution:**
```bash
# Windows - If script execution is disabled:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then activate
.\.venv\Scripts\Activate.ps1
```

---

## Project Structure

```
Assesment_mysoft_heaven/
├── assessments/
│   ├── 01_workflow_automation/
│   ├── 02_rag_chatbot/
│   └── 03_saas_ai_agent/
├── backend/
│   ├── main.py
│   └── middleware.py
├── core/
│   ├── config.py
│   ├── database.py
│   ├── llm_client.py
│   └── vector_store.py
├── streamlit_apps/
│   └── 02_rag_app.py
├── .env
├── requirements.txt
└── README.md
```

---

## Quick Start (TL;DR)

```bash
# 1. Clone and navigate
git clone https://github.com/Nobi004/ai-engineering-assessments.git
cd Assesment_mysoft_heaven

# 2. Setup Python
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 3. Install and configure
pip install -r requirements.txt
# Create .env with OPENAI_API_KEY

# 4. Start backend
uvicorn backend.main:app --reload

# 5. In new terminal, start frontend
cd streamlit_apps
streamlit run 02_rag_app.py

# 6. Access
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
# Streamlit: http://localhost:8501
```

---

## Next Steps

After local setup:

1. **Test the API endpoints** using the auto-generated Swagger UI at `http://localhost:8000/docs`
2. **Ingest documents** using the RAG chatbot setup
3. **Configure social media webhooks** for production use
4. **Set up CRM integrations** (HubSpot, Salesforce, etc.)
5. **Deploy to cloud** (AWS, GCP, Azure)

---

## Support & Documentation

- **API Docs:** http://localhost:8000/docs
- **Main README:** See [../README.md](../../README.md)
- **System Design:** See [assessment3.md](./assessment3.md)
- **Architecture Diagrams:** See [architecture_diagram.png](./architecture_diagram.png)

---

## Useful Commands

```bash
# View all database tables
python -c "from core.database import get_session; from core.database import Base; from sqlalchemy import inspect; inspector = inspect(Base.metadata); print([t.name for t in inspector.get_tables()])"

# Test async function
python -c "import asyncio; from assessments.rag_chatbot.services import RAGService; asyncio.run(RAGService.ingest_documents('test-company'))"

# Run tests
pytest tests/ -v

# Generate API documentation
python -m pydantic_core --version
```

---

**Last Updated:** February 28, 2026  
**Version:** 1.0

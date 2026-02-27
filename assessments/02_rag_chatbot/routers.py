from fastapi import APIRouter
from assessments.02_rag_chatbot.services import RAGService
from assessments.02_rag_chatbot.schemas import RAGResponse
from uuid import uuid4, UUID

router = APIRouter(prefix="/api/02-rag", tags=["Assessment 2"])

@router.post("/ingest")
async def ingest(company_id: str = "acme-corp"):
    count = await RAGService.ingest_documents(company_id)
    return {"status": "success", "chunks_ingested": count, "company_id": company_id}

@router.post("/chat", response_model=RAGResponse)
async def chat(query: str, company_id: str = "acme-corp", session_id: UUID = None):
    if session_id is None:
        session_id = uuid4()
    return await RAGService.chat(company_id, query, session_id)
from fastapi import APIRouter
from assessments.rag_chatbot.services import RAGService
from assessments.rag_chatbot.schemas import RAGResponse, ChatRequest
from uuid import uuid4, UUID

router = APIRouter(prefix="/api/02-rag", tags=["Assessment 2"])

@router.post("/ingest")
async def ingest(company_id: str = "acme-corp"):
    count = await RAGService.ingest_documents(company_id)
    return {"status": "success", "chunks_ingested": count, "company_id": company_id}

from fastapi import Body, Query, HTTPException

@router.post("/chat", response_model=RAGResponse)
async def chat(
    query: str | None = Query(None),
    company_id: str = Query("acme-corp"),
    session_id: UUID | None = Query(None),
    req: ChatRequest | None = Body(None),
):
    # merge body and query parameters; body takes precedence
    if req is not None:
        query = req.query
        company_id = req.company_id
        session_id = req.session_id

    if not query:
        # mimic FastAPI missing-field error structure for consistency
        raise HTTPException(status_code=422, detail=[
            {"loc": ["query"], "msg": "Field required", "type": "value_error.missing"}
        ])

    if session_id is None:
        session_id = uuid4()

    return await RAGService.chat(company_id, query, session_id)
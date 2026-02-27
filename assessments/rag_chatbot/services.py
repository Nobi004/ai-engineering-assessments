from langchain_core.messages import SystemMessage, HumanMessage
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader, TextLoader, PyPDFLoader
from core.llm_client import LLMClient
from core.vector_store import VectorStoreManager
from core.embedding_client import embedding_client
from core.logger import logger
from assessments.rag_chatbot.schemas import RAGResponse
from core.database import AsyncSessionLocal
from sqlmodel import select
import structlog
from uuid import uuid4

llm_client = LLMClient()
logger = structlog.get_logger()

class RAGService:
    THRESHOLD = 0.45
    CHUNK_SIZE = 800
    CHUNK_OVERLAP = 120

    PROMPT = """You are a precise assistant for {company_name}.
Answer STRICTLY using ONLY the provided context.
If the answer is not in the context, reply EXACTLY:
"I don't have information about that in our company documents."

Context:
{context}

Previous conversation:
{chat_history}"""

    @staticmethod
    async def ingest_documents(company_id: str, docs_path: str = "data/uploads/02_rag/company_docs"):
        vectorstore = VectorStoreManager.get_vectorstore()
        splitter = RecursiveCharacterTextSplitter(chunk_size=RAGService.CHUNK_SIZE, chunk_overlap=RAGService.CHUNK_OVERLAP)

        loader = DirectoryLoader(
            docs_path,
            glob="**/*.*",
            loader_cls=PyPDFLoader if docs_path.endswith(".pdf") else TextLoader,
            show_progress=True,
        )
        docs = loader.load()

        for doc in docs:
            doc.metadata["company_id"] = company_id
            doc.metadata["source"] = doc.metadata.get("source", "unknown")

        chunks = splitter.split_documents(docs)
        vectorstore.add_documents(chunks)
        VectorStoreManager.save()

        logger.info("documents_ingested", company_id=company_id, chunks=len(chunks))
        return len(chunks)

    @staticmethod
    async def chat(company_id: str, query: str, session_id: UUID) -> RAGResponse:
        vectorstore = VectorStoreManager.get_vectorstore()
        retriever = vectorstore.as_retriever(
            search_type="similarity_score_threshold",
            search_kwargs={"k": 6, "score_threshold": RAGService.THRESHOLD, "filter": {"company_id": company_id}}
        )

        docs = await retriever.ainvoke(query)
        max_score = max((doc.metadata.get("score", 0) for doc in docs), default=0) if docs else 0
        confidence = round(max_score, 3)

        if not docs:
            return RAGResponse(answer="I don't have information about that in our company documents.", confidence=0, sources=[], refusal=True)

        context = "\n\n".join([doc.page_content for doc in docs])
        sources = list({doc.metadata.get("source", "unknown") for doc in docs})

        # Simple memory (last 6 messages)
        async with AsyncSessionLocal() as session:
            history = await session.exec(
                select(ChatMessage).where(ChatMessage.session_id == session_id).order_by(ChatMessage.created_at.desc()).limit(6)
            )
            history = history.all()[::-1]
            chat_history = "\n".join([f"{msg.role}: {msg.content}" for msg in history])

        full_prompt = RAGService.PROMPT.format(company_name=company_id, context=context, chat_history=chat_history or "No previous messages.")
        
        response = await llm_client.llm.ainvoke([
            SystemMessage(content=full_prompt),
            HumanMessage(content=query)
        ])

        answer = response.content.strip()

        # Save to history
        async with AsyncSessionLocal() as session:
            session.add(ChatMessage(session_id=session_id, company_id=company_id, role="user", content=query))
            session.add(ChatMessage(session_id=session_id, company_id=company_id, role="assistant", content=answer, confidence=confidence))
            await session.commit()

        return RAGResponse(
            answer=answer,
            confidence=confidence,
            sources=sources,
            refusal="don't have information" in answer.lower()
        )
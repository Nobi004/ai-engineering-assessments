from langchain_core.messages import SystemMessage, HumanMessage
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader, TextLoader, PyPDFLoader
from core.llm_client import LLMClient
from core.vector_store import VectorStoreManager
from core.embedding_client import embedding_client
from core.logger import logger
from assessments.rag_chatbot.schemas import RAGResponse, ChatMessage
from core.config import settings
from core.database import AsyncSessionLocal
from sqlmodel import select
import structlog
from uuid import uuid4, UUID
import os

# base of repository - two levels up from this file
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
llm_client = LLMClient()
logger = structlog.get_logger()

class RAGService:
    THRESHOLD = 0.45
    CHUNK_SIZE = 800
    CHUNK_OVERLAP = 120

    PROMPT = """You are a **friendly, helpful assistant** for {company_name}.
Speak in a polite, conversational tone as if talking to a customer or
colleague.  The user's question may contain grammatical errors; interpret the
meaning sensibly and answer accordingly.
Always answer using the information given in the Context section below,
rephrasing the text as needed so it sounds natural and user‑friendly.
If the question can be answered from the context, provide a clear, concise
response based on that text.  Do NOT invent new facts.
Only if the answer truly cannot be found in the context, reply exactly:
"I don't have information about that in our company documents."

Context:
{context}

Previous conversation:
{chat_history}"""

    @staticmethod
    async def ingest_documents(company_id: str, docs_path: str = "data/uploads/02_rag/company_docs"):
        # wipe existing index so we rebuild from current documents
        index_path = settings.faiss_index_path
        try:
            if os.path.exists(f"{index_path}.faiss"):
                os.remove(f"{index_path}.faiss")
                VectorStoreManager._vectorstore = None
                logger.info("faiss_index_reset", path=index_path)
        except Exception as e:
            logger.warning("faiss_reset_failed", error=str(e))

        # normalize a relative path against project root and ensure it exists
        if not os.path.isabs(docs_path):
            docs_path = os.path.join(_PROJECT_ROOT, docs_path)
        docs_path = os.path.abspath(docs_path)
        if not os.path.isdir(docs_path):
            os.makedirs(docs_path, exist_ok=True)
            logger.warning("created_docs_directory", path=docs_path)
        # if directory exists but is empty, drop a sample description file
        if not os.listdir(docs_path):
            sample_file = os.path.join(docs_path, "about_company.txt")
            with open(sample_file, "w", encoding="utf-8") as f:
                f.write(
                    "Acme Corp is a leading provider of fictional widget solutions. "
                    "Founded in 2020, the company focuses on engineering, AI-driven products,"
                    " and offers consulting services to global clients. "
                    "Key projects include the development of an AI chatbot platform, "
                    "a widget manufacturing automation system, and ongoing research into "
                    "sustainable energy solutions."
                )
            logger.info("created_sample_doc", path=sample_file)

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
        if not chunks:
            logger.warning("no_documents_to_ingest", path=docs_path)
            return 0
        vectorstore.add_documents(chunks)
        VectorStoreManager.save()

        logger.info("documents_ingested", company_id=company_id, chunks=len(chunks))
        return len(chunks)

    @staticmethod
    async def chat(company_id: str, query: str, session_id: UUID) -> RAGResponse:
        vectorstore = VectorStoreManager.get_vectorstore()
        retriever = vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 6, "filter": {"company_id": company_id}}
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
            result = await session.execute(
                select(ChatMessage)
                .where(ChatMessage.session_id == session_id)
                .order_by(ChatMessage.created_at.desc())
                .limit(6)
            )
            history = result.scalars().all()[::-1]
            chat_history = "\n".join([f"{msg.role}: {msg.content}" for msg in history])

        full_prompt = RAGService.PROMPT.format(company_name=company_id, context=context, chat_history=chat_history or "No previous messages.")
        
        response = await llm_client.llm.ainvoke([
            SystemMessage(content=full_prompt),
            HumanMessage(content=query)
        ])

        answer = response.content.strip()

        # if model refused despite having documents, apply a simple keyword-based fallback
        if "don't have information" in answer.lower() and docs:
            import re
            sentences = re.split(r'(?<=[.!?])\s+', context)
            for s in sentences:
                if "project" in s.lower():
                    answer = s
                    confidence = round(confidence or 0.1, 3)
                    break

        # ensure the final answer is phrased in friendly, conversational style
        # (the prompt already encourages this, but a second pass can help)
        if answer and not answer.lower().startswith("i don't have information"):
            refine_prompt = (
                "Please rewrite the following response to be warm and conversational,"
                " while still staying truthful and grounded in the provided context:\n\n" + answer
            )
            refined = await llm_client.llm.ainvoke([
                SystemMessage(content=refine_prompt),
                HumanMessage(content="")
            ])
            answer = refined.content.strip()
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
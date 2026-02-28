from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from core.embedding_client import embedding_client
from core.config import settings
import os
import structlog

logger = structlog.get_logger()

class VectorStoreManager:
    _vectorstore = None
    
    @classmethod
    def get_vectorstore(cls):
        if cls._vectorstore is None:
            index_path = settings.faiss_index_path
            try:
                # attempt to load any existing index; if it fails we fall back to creation
                cls._vectorstore = FAISS.load_local(
                    index_path,
                    embedding_client.get_embeddings(),
                    allow_dangerous_deserialization=True,
                )
                logger.info("faiss_index_loaded")
            except Exception as e:
                logger.warning("faiss_load_failed", error=str(e))
                # create a fresh (empty) index and persist it
                cls._vectorstore = FAISS.from_texts([""], embedding_client.get_embeddings())
                cls._vectorstore.save_local(index_path)
                logger.info("faiss_index_created_empty")
        return cls._vectorstore

    @classmethod
    def save(cls):
        if cls._vectorstore:
            cls._vectorstore.save_local(settings.faiss_index_path)
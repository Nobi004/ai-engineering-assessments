from langchain_openai import OpenAIEmbeddings
from core.config import settings
import structlog

logger = structlog.get_logger()

class EmbeddingClient:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(
            model=settings.embedding_model,
            dimensions=settings.embedding_dimensions,
            openai_api_key=settings.openai_api_key,
        )
    
    def get_embeddings(self):
        return self.embeddings

# Singleton
embedding_client = EmbeddingClient()
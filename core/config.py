import os
from pydantic_settings import BaseSettings, SettingsConfigDict

# ensure the .env is loaded from the project root (not the current working dir)
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
env_path = os.path.join(base_dir, ".env")

class LLMSettings(BaseSettings):
    model: str = "gpt-4o-mini"

class Settings(BaseSettings):
    openai_api_key: str
    llm: LLMSettings = LLMSettings()
    log_level: str = "INFO"
    db_url: str = "sqlite+aiosqlite:///data/sqlite.db"

    # embedding configuration (used by RAG service)
    embedding_model: str = "text-embedding-3-small"
    embedding_dimensions: int = 1536

    # local FAISS index path (without extension)
    faiss_index_path: str = "data/faiss_indexes/rag_index"

    model_config = SettingsConfigDict(
        env_file=env_path,
        env_file_encoding="utf-8",
        extra="ignore",
        env_nested_delimiter="_",
    )

settings = Settings()
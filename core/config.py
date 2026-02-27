from pydantic_settings import BaseSettings, SettingsConfigDict

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
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        env_nested_delimiter="_",
    )

settings = Settings()
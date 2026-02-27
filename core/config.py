from pydantic_settings import BaseSettings, SettingsConfigDict

class LLMSettings(BaseSettings):
    model: str = "gpt-4o-mini"

class Settings(BaseSettings):
    openai_api_key: str
    llm: LLMSettings = LLMSettings()
    log_level: str = "INFO"
    db_url: str = "sqlite+aiosqlite:///data/sqlite.db"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        env_nested_delimiter="_",
    )

settings = Settings()
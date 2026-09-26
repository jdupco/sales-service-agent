# src\sales_service_agent\config.py

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Supabase & PostgreSQL
    SUPABASE_URL: str
    SUPABASE_KEY: str
    PGVECTOR_CONNECTION_STRING: str

    # NVIDIA API (Nemotron Embeddings)
    NVIDIA_API_KEY: str
    NVIDIA_API_BASE: str
    EMBEDDING_MODEL_NAME: str

    # OpenCode API (DeepSeek LLM)
    OPENCODE_API_KEY: str
    OPENCODE_API_BASE: str
    LLM_MODEL_NAME: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()

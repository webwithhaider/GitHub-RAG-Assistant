"""Application configuration loaded from environment variables."""
from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # --- App ---
    APP_NAME: str = "Codebase RAG Assistant"
    ENVIRONMENT: str = "development"
    ALLOWED_ORIGINS: str = "http://localhost:3000"

    # --- Storage ---
    REPOSITORIES_DIR: str = "./repositories"
    MAX_REPO_SIZE_MB: int = 500

    # --- Vector DB ---
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_API_KEY: Optional[str] = None
    QDRANT_COLLECTION_PREFIX: str = "repo_"

    # --- Embeddings ---
    EMBEDDING_PROVIDER: str = "bge"  # "bge" | "openai"
    EMBEDDING_MODEL: str = "BAAI/bge-m3"
    OPENAI_API_KEY: Optional[str] = None

    # --- LLM ---
    LLM_PROVIDER: str = "groq"  # "groq" | "openai"
    LLM_MODEL: str = "openai/gpt-oss-120b"
    GROQ_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None

    # --- Reranker ---
    RERANKER_MODEL: str = "BAAI/bge-reranker-v2-m3"

    # --- Auth (not enforced yet, ready for future use) ---
    SECRET_KEY: str = "change-me"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    @property
    def allowed_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()

"""
Configuration management for RAG System.

Uses Pydantic Settings for type-safe configuration loading from environment variables.
All settings are validated at startup.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
from pathlib import Path


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_RELOAD: bool = True

    # OpenRouter Configuration
    OPENROUTER_API_KEY: str = "test-key"  # Default for testing
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"

    # Embedding Configuration
    EMBEDDING_MODEL: str = "text-embedding-3-large"
    EMBEDDING_DIMENSIONS: int = 3072
    # OpenAI Configuration (Removed - using OpenRouter)
    # OPENAI_API_KEY: Optional[str] = None

    # Vector Database
    VECTOR_DB_PATH: str = "data/vectors"

    # Document Storage
    DOCUMENT_STORAGE_PATH: str = "data/documents"

    # Chunking Strategy
    CHUNK_SIZE: int = 512
    CHUNK_OVERLAP: int = 50

    # RAG Configuration
    DEFAULT_MODEL: str = "meta-llama/llama-3-70b-instruct"
    MAX_RETRIEVAL_CHUNKS: int = 5

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "data/logs/app.log"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    def _ensure_directories(self) -> None:
        """Create required directories if they don't exist."""
        dirs = [
            self.VECTOR_DB_PATH,
            self.DOCUMENT_STORAGE_PATH,
            Path(self.LOG_FILE).parent
        ]
        for dir_path in dirs:
            Path(dir_path).mkdir(parents=True, exist_ok=True)


# Global settings instance - create without .env for tests
try:
    settings = Settings()
    settings._ensure_directories()
except Exception:
    # Fallback for testing without .env
    settings = Settings(_env_file=None)

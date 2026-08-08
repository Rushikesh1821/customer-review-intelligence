import os
from functools import lru_cache
from pathlib import Path
from typing import List, Optional
from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Base directory definitions
BASE_DIR = Path(__file__).resolve().parent.parent
ROOT_DIR = BASE_DIR.parent

# Load environment variables from .env file at root or backend directory
env_path = BASE_DIR / ".env"
if not env_path.exists():
    env_path = ROOT_DIR / ".env"
load_dotenv(dotenv_path=env_path)


def _get_list_env(key: str, default: List[str]) -> List[str]:
    val = os.getenv(key)
    if not val:
        return default
    return [item.strip() for item in val.split(",") if item.strip()]


def _resolve_path(env_key: str, relative_backend_path: str, relative_root_path: str) -> Path:
    val = os.getenv(env_key)
    if val:
        return Path(val)
    backend_p = BASE_DIR / relative_backend_path
    if backend_p.exists():
        return backend_p
    return ROOT_DIR / relative_root_path


class Settings(BaseModel):
    """
    Application settings model powered by Pydantic v2.
    Loads values from environment variables with production defaults.
    """

    # General App Info
    APP_NAME: str = Field(default_factory=lambda: os.getenv("APP_NAME", "Customer Review Intelligence Platform"))
    APP_VERSION: str = Field(default_factory=lambda: os.getenv("APP_VERSION", "1.0.0"))
    DEBUG: bool = Field(default_factory=lambda: os.getenv("DEBUG", "false").lower() == "true")

    # Server Configuration
    HOST: str = Field(default_factory=lambda: os.getenv("HOST", "0.0.0.0"))
    PORT: int = Field(default_factory=lambda: int(os.getenv("PORT", "8000")))
    CORS_ORIGINS: List[str] = Field(
        default_factory=lambda: _get_list_env(
            "CORS_ORIGINS",
            [
                "http://localhost:3000",
                "http://localhost:5173",
                "http://127.0.0.1:3000",
                "http://127.0.0.1:5173",
            ],
        )
    )

    # Gemini API Configuration
    GEMINI_API_KEY: str = Field(default_factory=lambda: os.getenv("GEMINI_API_KEY", ""))
    GEMINI_MODEL: str = Field(default_factory=lambda: os.getenv("GEMINI_MODEL", "gemini-2.5-flash"))

    # Machine Learning Models Paths
    SENTIMENT_MODEL_PATH: Path = Field(
        default_factory=lambda: _resolve_path("SENTIMENT_MODEL_PATH", "models/sentiment_model.pkl", "models/sentiment_model.pkl")
    )
    TFIDF_VECTORIZER_PATH: Path = Field(
        default_factory=lambda: _resolve_path("TFIDF_VECTORIZER_PATH", "models/tfidf_vectorizer.pkl", "models/tfidf_vectorizer.pkl")
    )

    # Vector DB / Chroma Settings
    CHROMA_DB_DIR: Path = Field(
        default_factory=lambda: _resolve_path("CHROMA_DB_DIR", "vector_db", "vector_db")
    )
    CHROMA_COLLECTION_NAME: str = Field(
        default_factory=lambda: os.getenv("CHROMA_COLLECTION_NAME", "all_customer_reviews")
    )
    EMBEDDING_MODEL_NAME: str = Field(
        default_factory=lambda: os.getenv("EMBEDDING_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2")
    )

    # RAG Settings
    RAG_TOP_K: int = Field(default_factory=lambda: int(os.getenv("RAG_TOP_K", "5")))
    RAG_MAX_TOKENS: int = Field(default_factory=lambda: int(os.getenv("RAG_MAX_TOKENS", "1000")))

    # Database
    DATABASE_URL: Optional[str] = Field(
        default_factory=lambda: os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/review_db")
    )


@lru_cache()
def get_settings() -> Settings:
    """
    Singleton accessor function for application settings.
    Uses LRU cache to prevent re-instantiating settings repeatedly.
    """
    return Settings()


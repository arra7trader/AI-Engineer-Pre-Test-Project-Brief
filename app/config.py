from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Local RAG Chatbot"
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000

    ollama_base_url: str = "http://127.0.0.1:11434"
    ollama_chat_model: str = "qwen2.5:1.5b"
    ollama_embedding_model: str = "nomic-embed-text"

    chroma_persist_directory: str = "./data/chroma"
    chroma_collection_name: str = "documents"

    chunk_size: int = 1000
    chunk_overlap: int = 200
    retrieval_k: int = 4

    upload_dir: str = "./data/uploads"
    allowed_content_types: tuple[str, ...] = ("application/pdf",)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()

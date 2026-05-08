from typing import Literal

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: Literal["healthy", "degraded"]
    llm_status: Literal["connected", "disconnected"]
    vector_db_status: Literal["connected", "disconnected"]


class IngestResponse(BaseModel):
    message: str
    chunks_created: int
    filename: str


class ChatRequest(BaseModel):
    query: str = Field(..., min_length=3, description="Question to ask about ingested documents.")


class ChatResponse(BaseModel):
    answer: str
    sources: list[str]

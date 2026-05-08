from contextlib import asynccontextmanager

from fastapi import FastAPI, File, UploadFile

from app.config import get_settings
from app.models import ChatRequest, ChatResponse, HealthResponse, IngestResponse
from app.services.rag_service import RagService

settings = get_settings()
rag_service = RagService(settings)


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    return HealthResponse(**rag_service.get_health())


@app.post("/ingest", response_model=IngestResponse)
async def ingest_document(file: UploadFile = File(...)) -> IngestResponse:
    result = await rag_service.ingest_pdf(file)
    return IngestResponse(**result)


@app.post("/chat", response_model=ChatResponse)
def chat_with_documents(payload: ChatRequest) -> ChatResponse:
    result = rag_service.answer_question(payload.query)
    return ChatResponse(**result)

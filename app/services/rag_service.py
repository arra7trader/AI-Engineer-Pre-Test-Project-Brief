from __future__ import annotations

from pathlib import Path
from typing import Any

import requests
from chromadb.config import Settings as ChromaSettings
from fastapi import HTTPException, UploadFile, status
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config import Settings


RAG_PROMPT = ChatPromptTemplate.from_template(
    """Anda adalah asisten yang hanya menjawab berdasarkan konteks dokumen.

Jika jawaban tidak tersedia di konteks, katakan dengan jujur bahwa informasi tidak ditemukan.
Jawab dalam Bahasa Indonesia yang ringkas dan jelas.

Konteks:
{context}

Pertanyaan:
{question}
"""
)


class RagService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        Path(self.settings.upload_dir).mkdir(parents=True, exist_ok=True)
        Path(self.settings.chroma_persist_directory).mkdir(parents=True, exist_ok=True)

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.settings.chunk_size,
            chunk_overlap=self.settings.chunk_overlap,
        )
        self.embeddings = OllamaEmbeddings(
            model=self.settings.ollama_embedding_model,
            base_url=self.settings.ollama_base_url,
        )
        self.llm = ChatOllama(
            model=self.settings.ollama_chat_model,
            base_url=self.settings.ollama_base_url,
            temperature=0,
        )
        self.vector_store = Chroma(
            collection_name=self.settings.chroma_collection_name,
            embedding_function=self.embeddings,
            persist_directory=self.settings.chroma_persist_directory,
            client_settings=ChromaSettings(
                anonymized_telemetry=False,
                is_persistent=True,
                persist_directory=self.settings.chroma_persist_directory,
            ),
        )

    def get_health(self) -> dict[str, str]:
        llm_status = "connected" if self._check_ollama() else "disconnected"
        vector_status = "connected" if self._check_vector_store() else "disconnected"
        app_status = "healthy" if llm_status == "connected" and vector_status == "connected" else "degraded"
        return {
            "status": app_status,
            "llm_status": llm_status,
            "vector_db_status": vector_status,
        }

    async def ingest_pdf(self, file: UploadFile) -> dict[str, Any]:
        self._validate_upload(file)

        destination = Path(self.settings.upload_dir) / file.filename
        with destination.open("wb") as buffer:
            buffer.write(await file.read())

        pages = PyPDFLoader(str(destination)).load()
        if not pages:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="PDF tidak mengandung teks yang dapat diproses.",
            )

        chunks = self.text_splitter.split_documents(pages)
        if not chunks:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Dokumen gagal dipecah menjadi chunk.",
            )

        prepared_chunks = [self._enrich_metadata(chunk, file.filename) for chunk in chunks]
        self.vector_store.add_documents(prepared_chunks)

        return {
            "message": "Dokumen berhasil diproses",
            "chunks_created": len(prepared_chunks),
            "filename": file.filename,
        }

    def answer_question(self, query: str) -> dict[str, Any]:
        docs = self.vector_store.similarity_search(query, k=self.settings.retrieval_k)
        if not docs:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Belum ada dokumen yang relevan di vector store. Silakan ingest PDF terlebih dahulu.",
            )

        context = self._build_context(docs)
        prompt = RAG_PROMPT.format_messages(context=context, question=query)
        response = self.llm.invoke(prompt)

        sources = []
        for doc in docs:
            page = doc.metadata.get("page_label") or f"halaman {doc.metadata.get('page', 0) + 1}"
            source = f"{doc.metadata.get('source_file', 'dokumen')} - {page}"
            if source not in sources:
                sources.append(source)

        return {
            "answer": response.content,
            "sources": sources,
        }

    def _check_ollama(self) -> bool:
        try:
            response = requests.get(f"{self.settings.ollama_base_url}/api/tags", timeout=5)
            response.raise_for_status()
            return True
        except requests.RequestException:
            return False

    def _check_vector_store(self) -> bool:
        try:
            self.vector_store._collection.count()
            return True
        except Exception:
            return False

    def _validate_upload(self, file: UploadFile) -> None:
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nama file tidak ditemukan.",
            )

        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File harus berformat PDF.",
            )

        if file.content_type and file.content_type not in self.settings.allowed_content_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Content-Type file tidak valid untuk PDF.",
            )

    def _enrich_metadata(self, document: Document, filename: str) -> Document:
        metadata = dict(document.metadata)
        page_number = metadata.get("page", 0) + 1
        metadata["source_file"] = filename
        metadata["page_label"] = f"halaman {page_number}"
        return Document(page_content=document.page_content, metadata=metadata)

    def _build_context(self, docs: list[Document]) -> str:
        context_blocks = []
        for idx, doc in enumerate(docs, start=1):
            source_file = doc.metadata.get("source_file", "dokumen")
            page_label = doc.metadata.get("page_label", "halaman tidak diketahui")
            context_blocks.append(
                f"[Konteks {idx} | {source_file} | {page_label}]\n{doc.page_content}"
            )
        return "\n\n".join(context_blocks)

# Local RAG Chatbot

Implementasi proyek sesuai `prd.md`: chatbot RAG berbasis dokumen PDF yang berjalan penuh secara lokal menggunakan `FastAPI`, `LangChain`, `ChromaDB`, dan `Ollama`.

## Fitur Utama

- Upload dokumen PDF melalui endpoint REST.
- Parsing PDF dan chunking teks otomatis.
- Pembuatan embedding lokal menggunakan model embedding dari Ollama.
- Penyimpanan vektor ke `ChromaDB` lokal.
- Retrieval dokumen relevan dan generation jawaban melalui LLM lokal.
- Kontainerisasi dengan `Dockerfile` dan `docker-compose.yml`.

## Arsitektur Singkat

Alur sistem:

1. Client mengunggah PDF ke endpoint `POST /ingest`.
2. API mengekstrak teks PDF, memecahnya menjadi chunks, lalu membuat embeddings.
3. Embeddings disimpan ke ChromaDB lokal.
4. Client mengirim pertanyaan ke endpoint `POST /chat`.
5. API melakukan similarity search ke ChromaDB.
6. Konteks hasil retrieval dikirim ke Ollama untuk menghasilkan jawaban.

Komponen utama:

- `FastAPI`: layer REST API.
- `LangChain`: orkestrasi loader, chunking, vector store, dan LLM.
- `ChromaDB`: vector database lokal.
- `Ollama`: inference untuk chat model dan embedding model.

## Struktur Proyek

```text
.
|-- app/
|   |-- config.py
|   |-- main.py
|   |-- models.py
|   `-- services/
|       `-- rag_service.py
|-- .env.example
|-- .gitignore
|-- Dockerfile
|-- docker-compose.yml
|-- prd.md
|-- README.md
`-- requirements.txt
```

## Tech Stack

- Python 3.11
- FastAPI
- LangChain
- ChromaDB
- Ollama
- Docker & Docker Compose

## Persiapan Lokal

1. Copy file environment:

```bash
cp .env.example .env
```

2. Buat virtual environment lalu install dependency:

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

Untuk Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

3. Pastikan Ollama sudah aktif dan model tersedia:

```bash
ollama pull qwen2.5:1.5b
ollama pull nomic-embed-text
```

Jika Ollama berjalan di host lokal, sesuaikan `OLLAMA_BASE_URL` di `.env`.

## Menjalankan Aplikasi Tanpa Docker

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Swagger UI tersedia di:

- [http://localhost:8000/docs](http://localhost:8000/docs)

## Menjalankan dengan Docker Compose

1. Copy environment:

```bash
cp .env.example .env
```

2. Jalankan seluruh stack:

```bash
docker compose up --build
```

Service yang dijalankan:

- `ollama`: server model lokal.
- `ollama-init`: menarik chat model dan embedding model.
- `api`: FastAPI RAG service.

Endpoint API:

- [http://localhost:8000/health](http://localhost:8000/health)
- [http://localhost:8000/docs](http://localhost:8000/docs)

## Konfigurasi Environment

Variabel penting di `.env`:

```env
APP_NAME=Local RAG Chatbot
APP_ENV=development
APP_HOST=0.0.0.0
APP_PORT=8000
OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_CHAT_MODEL=qwen2.5:1.5b
OLLAMA_EMBEDDING_MODEL=nomic-embed-text
CHROMA_PERSIST_DIRECTORY=./data/chroma
CHROMA_COLLECTION_NAME=documents
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
RETRIEVAL_K=4
UPLOAD_DIR=./data/uploads
```

## Spesifikasi Endpoint

### `GET /health`

Memeriksa status API, koneksi Ollama, dan vector database.

Contoh response:

```json
{
  "status": "healthy",
  "llm_status": "connected",
  "vector_db_status": "connected"
}
```

### `POST /ingest`

Upload file PDF sebagai `multipart/form-data`.

Contoh `curl`:

```bash
curl -X POST "http://localhost:8000/ingest" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@sample.pdf"
```

Contoh response:

```json
{
  "message": "Dokumen berhasil diproses",
  "chunks_created": 45,
  "filename": "sample.pdf"
}
```

### `POST /chat`

Kirim pertanyaan berbasis dokumen yang sudah di-ingest.

Contoh `curl`:

```bash
curl -X POST "http://localhost:8000/chat" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d "{\"query\":\"Apa kesimpulan dari dokumen tersebut?\"}"
```

Contoh response:

```json
{
  "answer": "Kesimpulan dokumen adalah ...",
  "sources": [
    "sample.pdf - halaman 1",
    "sample.pdf - halaman 3"
  ]
}
```

## Catatan Implementasi

- Loader PDF menggunakan `PyPDFLoader`.
- Chunking memakai `RecursiveCharacterTextSplitter`.
- Retrieval memakai `similarity_search` ke ChromaDB.
- Prompt dirancang agar model hanya menjawab dari konteks dokumen.
- Sumber jawaban dikembalikan dalam format `nama_file - halaman N`.

## Bukti Pengujian

Hasil pengujian runtime yang sudah dijalankan tersimpan di [docs/test-results.md](D:/AI Engineer Pre-Test — Project Brief/docs/test-results.md:1).

Untuk submission final, Anda juga bisa melampirkan screenshot hasil pengujian Postman atau terminal `curl` pada repository, misalnya di folder `docs/`:

- `docs/health-check.png`
- `docs/ingest-success.png`
- `docs/chat-response.png`

Jika ingin, contoh skenario yang bisa diuji:

1. `GET /health` setelah semua service menyala.
2. `POST /ingest` dengan satu file PDF yang berisi teks.
3. `POST /chat` dengan pertanyaan yang jawabannya memang ada di PDF.

## Checklist Kesesuaian PRD

- Pipeline RAG end-to-end tersedia.
- LLM lokal menggunakan Ollama.
- Vector store lokal menggunakan ChromaDB.
- Tiga endpoint wajib tersedia: `/health`, `/ingest`, `/chat`.
- Tersedia `Dockerfile` dan `docker-compose.yml`.
- Tersedia `README.md` dengan setup, run, arsitektur, dan panduan pengujian.

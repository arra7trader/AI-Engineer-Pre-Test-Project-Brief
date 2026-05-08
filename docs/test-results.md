# Test Results

Tanggal pengujian: `2026-05-08`

## Local Runtime Validation

### `GET /health`

```json
{"status":"healthy","llm_status":"connected","vector_db_status":"connected"}
```

### `POST /ingest`

```json
{"message":"Dokumen berhasil diproses","chunks_created":1,"filename":"sample.pdf"}
```

### `POST /chat`

```json
{"answer":"Sistem harus berjalan on-premise, mendukung upload PDF, menyediakan endpoint health, ingest, serta chat. Teknologi utama yang dipakai adalah Python, LangChain, FastAPI, ChromaDB, dan Ollama.","sources":["sample.pdf - halaman 1"]}
```

## Docker Validation

- `docker build -t local-rag-api-test .` berhasil.
- `docker compose up -d --build` berhasil.
- `docker compose ps` menunjukkan service `api` dan `ollama` aktif.
- Setelah server lokal dimatikan, endpoint Docker tetap merespons sukses untuk `health`, `ingest`, dan `chat`.
- Log container API bersih dari warning telemetry setelah `posthog` dipin ke versi kompatibel.

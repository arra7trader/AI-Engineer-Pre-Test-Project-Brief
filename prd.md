Product Requirements Document (PRD)
Nama Proyek: RAG Chatbot dengan Local LLM (On-Premise Ready)
Peran: Junior AI Engineer
Tenggat Waktu: Selasa, 12 Mei 2026 — 23:59 WIB

1. Ringkasan Eksekutif
Proyek ini bertujuan untuk membangun sistem chatbot berbasis Retrieval-Augmented Generation (RAG) yang sepenuhnya berjalan di lingkungan lokal (on-premise). Sistem ini memungkinkan pengguna untuk mengunggah dokumen PDF, mengekstrak informasinya, dan mengajukan pertanyaan terkait isi dokumen tersebut. Sistem tidak menggunakan API cloud pihak ketiga (seperti OpenAI) demi menjaga privasi data, dan dibungkus dalam container Docker agar mudah di-deploy.

2. Tujuan Proyek
Membangun pipeline RAG end-to-end (Ingestion & Retrieval).

Mengimplementasikan LLM lokal menggunakan arsitektur yang efisien.

Menyediakan antarmuka REST API yang siap diintegrasikan.

Memastikan portabilitas aplikasi menggunakan Docker.

3. Ruang Lingkup (Scope)
In-Scope:

Pemrosesan file PDF (Parsing dan Chunking).

Pembuatan embeddings dan penyimpanan ke Vector Database lokal.

Penggunaan LLM lokal via Ollama untuk text generation.

Pembuatan REST API dengan FastAPI.

Kontainerisasi menggunakan Docker.

Out-of-Scope:

Pembuatan Frontend/User Interface (UI).

Penggunaan model cloud berbayar (OpenAI, Anthropic, dll).

Sistem Autentikasi/Otorisasi (Login/JWT).

Skalabilitas terdistribusi (Kubernetes, dll).

4. Teknologi yang Disarankan (Tech Stack)
Bahasa Pemrograman: Python 3.9+

Framework API: FastAPI

Orkestrasi LLM: LangChain

Local LLM Engine: Ollama (Model: Llama 3 8B / Mistral 7B / Qwen)

Vector Database: ChromaDB atau Qdrant (Local mode)

Deployment: Docker & Docker Compose

5. Kebutuhan Fungsional & Pipeline
Sistem harus mengimplementasikan alur kerja berikut:

A. Fase Ingestion (Persiapan Dokumen)

Upload PDF: Menerima file PDF melalui endpoint API.

Chunking: Memecah teks dokumen menjadi potongan-potongan kecil (chunks) yang dapat dicerna oleh LLM.

Embedding: Mengubah teks chunks menjadi representasi vektor numerik.

Vector Store: Menyimpan vektor ke dalam database lokal (ChromaDB/Qdrant) untuk pencarian berbasis kemiripan (similarity search).

B. Fase Retrieval & Generation (Tanya Jawab)

Menerima Pertanyaan: Menerima query dari pengguna via API.

Retrieve: Mencari konteks yang paling relevan dari Vector Database berdasarkan pertanyaan.

Generate: Menggabungkan pertanyaan dan konteks relevan ke dalam prompt, lalu mengirimkannya ke model lokal (Ollama) untuk menghasilkan jawaban.

6. Spesifikasi REST API
Sistem harus mengekspos tiga endpoints minimal:

GET /health
Deskripsi: Mengecek status health check dari aplikasi dan koneksi ke Ollama/Vector DB.

Response (200 OK): {"status": "healthy", "llm_status": "connected"}

POST /ingest
Deskripsi: Mengunggah dan memproses dokumen PDF ke dalam Vector Store.

Payload: multipart/form-data (File PDF)

Response (200 OK): {"message": "Dokumen berhasil diproses", "chunks_created": 45}

POST /chat
Deskripsi: Mengirimkan pertanyaan untuk dijawab oleh LLM berdasarkan dokumen yang sudah di-ingest.

Payload (JSON): {"query": "Apa kesimpulan dari dokumen tersebut?"}

Response (200 OK): {"answer": "[Jawaban dari LLM]", "sources": ["halaman 1", "halaman 3"]}

7. Kriteria Penerimaan (Deliverables)
Proyek dianggap selesai dan berhasil jika memenuhi syarat berikut:

Terdapat script RAG pipeline lengkap sesuai urutan.

LLM yang digunakan murni berjalan secara lokal via Ollama.

Vector store menggunakan basis data lokal (ChromaDB atau Qdrant).

FastAPI berjalan lancar dengan 3 endpoint wajib (/chat, /ingest, /health).

Terdapat Dockerfile (dan idealnya docker-compose.yml untuk mem-bundling Ollama & FastAPI) yang bisa di-build dan di-run tanpa error.

Terdapat README.md yang komprehensif, mencakup:

Cara setup proyek.

Cara menjalankan (run) proyek.

Penjelasan singkat mengenai arsitektur yang digunakan.

Screenshot hasil pengujian menggunakan Postman / cURL.

Diserahkan melalui tautan GitHub Repository publik/privat sesuai instruksi form.
# ReadMe Backend

FastAPI backend that powers the ReadMe desktop app. It runs entirely on an Azure Linux VM (or any Linux host) and keeps parsing, TTS, annotations, and caching local to the machine.

## Features
- PDF/EPUB/TXT/DOCX ingestion with PyMuPDF, pdfplumber, ebooklib, and docx2txt.
- Structured chapter/paragraph JSON stored under `/var/readme_cache/books/<uuid>/text.json`.
- Coqui/TTS-based speech synthesis using the Tacotron2 DDC voice, with cached output in `/var/readme_tts`.
- SQLite metadata + annotations stored under `~/readme/db/readme.db`.
- REST API for the Electron client:
  - `POST /api/books/import` – upload a document and receive structured text + metadata.
  - `GET /api/books` / `GET /api/books/{book_id}` – list books or fetch structure for one.
  - `POST /api/books/{book_id}/progress` – persist reader location.
  - `POST /api/tts` / `GET /api/audio/{filename}` – create and stream audio.
  - `POST /api/annotate` / `GET /api/annotations/{book_id}` – manage notes.

## Getting Started
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

The directories defined in `app/config.py` are created on import, so ensure the user running the service has permissions to `/var/readme_cache` and `/var/readme_tts`.

### Running the API
```bash
uvicorn app.main:app --host 0.0.0.0 --port 5000
```

On Azure, wrap the process with systemd (not yet committed here) so it auto-starts on boot and recovers on failure.

### Configuration
All settings can be overridden via environment variables prefixed with `README_`. For example:

```bash
export README_STORAGE_ROOT=/data/readme_cache
export README_TTS_ROOT=/data/readme_tts
export README_DB_PATH=/data/readme.db
export README_COQUI_MODEL=tts_models/en/ljspeech/tacotron2-DDC
export README_COQUI_API_URL=http://localhost:5002/api/tts
export README_COQUI_API_TIMEOUT=60
```

### API Usage Tips
- Uploads are limited to the extensions in `SUPPORTED_EXTENSIONS` inside `app/api/routes/books.py`.
- Keep payload sizes under ~200 MB per the PRD to avoid OOM during ingestion.
- Use `/api/audio/{filename}` to stream generated WAVs after calling `/api/tts`.

### Containerized Coqui
Set `README_COQUI_API_URL` when you want Coqui to run in a separate container (instead of importing the Python package in-process). When configured, the backend POSTs `{"text": "..."}` to that URL and expects JSON containing either an `audio_path`, an `audio_base64` field, or an `audio_url`. If the container writes directly into `/var/readme_tts`, just share the volume with the backend and return the absolute `audio_path`. Otherwise return `audio_base64` so the backend can persist the WAV locally.

Example Coqui container (replace the image/tag if you maintain your own):

```bash
docker pull ghcr.io/coqui-ai/tts-cpu
docker run --rm -p 5002:5002 \
  -v /var/readme_tts:/var/readme_tts \
  ghcr.io/coqui-ai/tts-cpu \
  tts-server --model_name tts_models/en/ljspeech/tacotron2-DDC --use_cuda 0
```

With the container running you can point the backend at it:

```bash
export README_COQUI_API_URL=http://localhost:5002/api/tts
uvicorn app.main:app --host 0.0.0.0 --port 5000
```

## Next Steps
- Add real chapter detection + cover extraction during ingestion.
- Implement the summarization endpoint (`/api/summarize`) when local models are finalized.
- Wire up authentication + bearer tokens if the VM ever exposes the API directly.

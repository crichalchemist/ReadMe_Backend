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
```

### API Usage Tips
- Uploads are limited to the extensions in `SUPPORTED_EXTENSIONS` inside `app/api/routes/books.py`.
- Keep payload sizes under ~200 MB per the PRD to avoid OOM during ingestion.
- Use `/api/audio/{filename}` to stream generated WAVs after calling `/api/tts`.

## Next Steps
- Add real chapter detection + cover extraction during ingestion.
- Implement the summarization endpoint (`/api/summarize`) when local models are finalized.
- Wire up authentication + bearer tokens if the VM ever exposes the API directly.

from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from ...config import settings

router = APIRouter()


@router.get("/audio/{filename}")
def stream_audio(filename: str):
    safe_name = Path(filename).name
    audio_path = settings.tts_root / safe_name
    if not audio_path.exists():
        raise HTTPException(status_code=404, detail="Audio file not found")
    media_type = "audio/wav" if settings.audio_format == "wav" else "audio/mpeg"
    return FileResponse(audio_path, media_type=media_type, filename=safe_name)

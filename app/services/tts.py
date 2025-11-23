import uuid
from pathlib import Path
from threading import Lock

from TTS.api import TTS

from ..config import settings


class CoquiTTSService:
    def __init__(self) -> None:
        self._model = None
        self._lock = Lock()

    def _load_model(self) -> None:
        if self._model is None:
            self._model = TTS(settings.coqui_model)

    def synthesize(self, text: str) -> Path:
        if not text.strip():
            raise ValueError("Text cannot be empty")
        with self._lock:
            self._load_model()
            filename = f"{uuid.uuid4()}.{settings.audio_format}"
            output_path = settings.tts_root / filename
            self._model.tts_to_file(text=text, file_path=str(output_path))
            return output_path


tts_service = CoquiTTSService()

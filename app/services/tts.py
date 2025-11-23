import base64
import uuid
from pathlib import Path
from threading import Lock
from typing import Optional

import httpx
from TTS.api import TTS

from ..config import settings


class CoquiTTSService:
    def __init__(self) -> None:
        self._model: Optional[TTS] = None
        self._lock = Lock()
        self._remote_url = settings.coqui_api_url
        self._remote_client: Optional[httpx.Client] = None

    def _get_filename(self) -> str:
        return f"{uuid.uuid4()}.{settings.audio_format}"

    def _load_model(self) -> None:
        if self._model is None:
            self._model = TTS(settings.coqui_model)

    def _get_remote_client(self) -> httpx.Client:
        if self._remote_client is None:
            self._remote_client = httpx.Client(timeout=settings.coqui_api_timeout)
        return self._remote_client

    def _synthesize_local(self, text: str) -> Path:
        with self._lock:
            self._load_model()
            output_path = settings.tts_root / self._get_filename()
            self._model.tts_to_file(text=text, file_path=str(output_path))
            return output_path

    def _write_bytes(self, audio_bytes: bytes) -> Path:
        output_path = settings.tts_root / self._get_filename()
        output_path.write_bytes(audio_bytes)
        return output_path

    def _synthesize_remote(self, text: str) -> Path:
        client = self._get_remote_client()
        response = client.post(self._remote_url, json={"text": text})
        response.raise_for_status()
        payload = response.json()

        remote_path = payload.get("audio_path")
        if remote_path:
            return Path(remote_path)

        audio_base64 = payload.get("audio_base64")
        if audio_base64:
            audio_bytes = base64.b64decode(audio_base64)
            return self._write_bytes(audio_bytes)

        audio_url = payload.get("audio_url")
        if audio_url:
            audio_response = client.get(audio_url)
            audio_response.raise_for_status()
            return self._write_bytes(audio_response.content)

        raise RuntimeError("Remote Coqui response did not provide audio data")

    def synthesize(self, text: str) -> Path:
        if not text.strip():
            raise ValueError("Text cannot be empty")
        if self._remote_url:
            return self._synthesize_remote(text=text.strip())
        return self._synthesize_local(text=text.strip())


tts_service = CoquiTTSService()

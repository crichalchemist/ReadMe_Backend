import uuid
from pathlib import Path
import httpx

from ..config import settings


class TTSService:
    def __init__(self):
        self.tts_url = "http://tts:5002/api/tts"  # docker service name
        self.output_dir = Path(settings.tts_output_path)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    async def synthesize(self, text: str):
        """
        Sends text to the Coqui-TTS Docker microservice and returns
        the path to the generated WAV file.
        """

        params = {"text": text}

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.get(self.tts_url, params=params)
            response.raise_for_status()

        # Save WAV data
        output_path = self.output_dir / f"tts_{uuid.uuid4()}.wav"
        output_path.write_bytes(response.content)

        return str(output_path)


tts_service = TTSService()

from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "ReadMe Backend"
    api_prefix: str = "/api"
    storage_root: Path = Path("/var/readme_cache")
    tts_root: Path = Path("/var/readme_tts")
    db_path: Path = Path.home() / "readme" / "db" / "readme.db"
    audio_format: str = "wav"
    coqui_model: str = "tts_models/en/ljspeech/tacotron2-DDC"
    coqui_api_url: Optional[str] = None
    coqui_api_timeout: int = 30

    class Config:
        env_prefix = "README_"
        env_file = ".env"


settings = Settings()

# ensure important directories exist at import time
settings.storage_root.mkdir(parents=True, exist_ok=True)
settings.tts_root.mkdir(parents=True, exist_ok=True)
settings.db_path.parent.mkdir(parents=True, exist_ok=True)

from pathlib import Path
from pydantic import BaseSettings


class Settings(BaseSettings):
    # Basic app metadata
    app_name: str = "ReadMe Backend"
    api_prefix: str = "/api"

    # Database settings (SQLite by default)
    db_url: str = "sqlite:///./readme.db"

    # Storage directories
    storage_root: Path = Path("/var/readme_storage")
    books_path: Path = storage_root / "books"
    audio_path: Path = storage_root / "audio"
    cache_path: Path = storage_root / "cache"

    # TTS output directory (Coqui XTTS writes WAV files here)
    tts_output_path: Path = storage_root / "tts_output"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Create global settings instance
settings = Settings()

# Ensure directories exist
for path in [
    settings.storage_root,
    settings.books_path,
    settings.audio_path,
    settings.cache_path,
    settings.tts_output_path,
]:
    path.mkdir(parents=True, exist_ok=True)

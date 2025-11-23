import json
from pathlib import Path
from typing import Any, Dict

import aiofiles
from fastapi import UploadFile

from ..config import settings


class StorageService:
    def __init__(self) -> None:
        self.base_books_dir = settings.storage_root / "books"

    def book_dir(self, book_id: str) -> Path:
        path = self.base_books_dir / book_id
        path.mkdir(parents=True, exist_ok=True)
        return path

    def text_path(self, book_id: str) -> Path:
        return self.book_dir(book_id) / "text.json"

    def uploads_dir(self) -> Path:
        path = settings.storage_root / "uploads"
        path.mkdir(parents=True, exist_ok=True)
        return path

    def cover_path(self, book_id: str) -> Path:
        return self.book_dir(book_id) / "cover.jpg"

    async def save_upload_file(self, upload_file: UploadFile) -> Path:
        dest = self.uploads_dir() / upload_file.filename
        async with aiofiles.open(dest, "wb") as buffer:
            while True:
                chunk = await upload_file.read(1024 * 1024)
                if not chunk:
                    break
                await buffer.write(chunk)
        await upload_file.close()
        return dest

    def save_text_json(self, book_id: str, payload: Dict[str, Any]) -> Path:
        path = self.text_path(book_id)
        with path.open("w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        return path

    def load_text_json(self, book_id: str) -> Dict[str, Any]:
        path = self.text_path(book_id)
        if not path.exists():
            raise FileNotFoundError(f"Missing structured text for {book_id}")
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)


storage_service = StorageService()

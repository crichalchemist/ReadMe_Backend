from datetime import datetime
from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel, Field


class Chapter(BaseModel):
    chapter_id: str
    title: str
    paragraphs: List[str]


class BookStructure(BaseModel):
    book_id: str
    title: str
    chapters: List[Chapter]


class BookMetadata(BaseModel):
    id: str = Field(alias="book_id")
    title: str
    filename: str
    created_at: datetime
    content_path: Path

    class Config:
        populate_by_name = True


class BookListResponse(BaseModel):
    items: List[BookMetadata]


class BookDetailResponse(BaseModel):
    book: BookMetadata
    structure: BookStructure


BookImportResponse = BookDetailResponse


class TTSRequest(BaseModel):
    text: str


class TTSResponse(BaseModel):
    audio_path: Path


class AnnotationRequest(BaseModel):
    book_id: str
    location: str
    note: str


class AnnotationResponse(BaseModel):
    id: str
    book_id: str
    location: str
    note: str
    created_at: datetime


class AnnotationListResponse(BaseModel):
    items: List[AnnotationResponse]


class ProgressUpdate(BaseModel):
    chapter_id: Optional[str] = None
    paragraph_index: Optional[int] = None

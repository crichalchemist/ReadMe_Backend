import uuid
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.concurrency import run_in_threadpool

from ...database import get_session
from ...schemas import (
    BookDetailResponse,
    BookListResponse,
    BookStructure,
    ProgressUpdate,
)
from ...services.books import book_service
from ...services.ingestion import ingestion_service
from ...services.storage import storage_service
from ..utils import serialize_book

router = APIRouter()

SUPPORTED_EXTENSIONS = {".pdf", ".epub", ".txt", ".docx", ".md"}


@router.post("/books/import", response_model=BookDetailResponse)
async def import_book(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename missing")
    suffix = Path(file.filename).suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {suffix}")

    stored_path = await storage_service.save_upload_file(file)
    book_id = str(uuid.uuid4())

    try:
        structure = await run_in_threadpool(
            ingestion_service.ingest,
            stored_path,
            book_id,
            Path(file.filename).stem,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    text_path = storage_service.save_text_json(book_id, structure)

    with get_session() as session:
        book = book_service.create_book(
            session,
            title=structure["title"],
            filename=file.filename,
            content_path=text_path,
        )

    return BookDetailResponse(book=serialize_book(book), structure=BookStructure(**structure))


@router.get("/books", response_model=BookListResponse)
def list_books():
    with get_session() as session:
        books = book_service.list_books(session)
    items = [serialize_book(book) for book in books]
    return BookListResponse(items=items)


@router.get("/books/{book_id}", response_model=BookDetailResponse)
def get_book(book_id: str):
    with get_session() as session:
        book = book_service.get_book(session, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    structure = storage_service.load_text_json(book_id)
    return BookDetailResponse(book=serialize_book(book), structure=BookStructure(**structure))


@router.post("/books/{book_id}/progress", response_model=ProgressUpdate)
def update_progress(book_id: str, payload: ProgressUpdate):
    with get_session() as session:
        book = book_service.get_book(session, book_id)
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")
        progress = book_service.upsert_progress(
            session,
            book_id,
            chapter_id=payload.chapter_id,
            paragraph_index=payload.paragraph_index,
        )
    return ProgressUpdate(chapter_id=progress.chapter_id, paragraph_index=progress.paragraph_index)


@router.get("/books/{book_id}/progress", response_model=ProgressUpdate)
def read_progress(book_id: str):
    with get_session() as session:
        book = book_service.get_book(session, book_id)
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")
        progress = book_service.get_progress(session, book_id)
    if not progress:
        return ProgressUpdate(chapter_id=None, paragraph_index=None)
    return ProgressUpdate(chapter_id=progress.chapter_id, paragraph_index=progress.paragraph_index)

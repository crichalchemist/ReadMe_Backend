from pathlib import Path

from ..schemas import BookMetadata
from ..models import Book


def serialize_book(book: Book) -> BookMetadata:
    return BookMetadata(
        book_id=book.id,
        title=book.title,
        filename=book.filename,
        created_at=book.created_at,
        content_path=Path(book.content_path),
    )

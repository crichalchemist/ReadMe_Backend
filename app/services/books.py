import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import Annotation, Book, Progress


class BookService:
    def create_book(
        self,
        session: Session,
        *,
        title: str,
        filename: str,
        content_path: Path,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Book:
        book = Book(
            title=title,
            filename=filename,
            content_path=str(content_path),
            metadata=json.dumps(metadata or {}),
        )
        session.add(book)
        session.commit()
        session.refresh(book)
        return book

    def list_books(self, session: Session) -> List[Book]:
        result = session.execute(select(Book).order_by(Book.created_at.desc()))
        return result.scalars().all()

    def get_book(self, session: Session, book_id: str) -> Book | None:
        return session.get(Book, book_id)

    def upsert_progress(
        self,
        session: Session,
        book_id: str,
        *,
        chapter_id: Optional[str],
        paragraph_index: Optional[int],
    ) -> Progress:
        progress = session.execute(select(Progress).where(Progress.book_id == book_id)).scalar_one_or_none()
        if progress:
            progress.chapter_id = chapter_id
            progress.paragraph_index = paragraph_index
        else:
            progress = Progress(book_id=book_id, chapter_id=chapter_id, paragraph_index=paragraph_index)
            session.add(progress)
        session.commit()
        session.refresh(progress)
        return progress

    def get_progress(self, session: Session, book_id: str) -> Progress | None:
        return session.execute(select(Progress).where(Progress.book_id == book_id)).scalar_one_or_none()

    def get_annotations(self, session: Session, book_id: str) -> List[Annotation]:
        result = session.execute(select(Annotation).where(Annotation.book_id == book_id).order_by(Annotation.created_at))
        return result.scalars().all()


book_service = BookService()

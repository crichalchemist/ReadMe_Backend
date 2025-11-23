from fastapi import APIRouter, HTTPException

from ...database import get_session
from ...schemas import AnnotationListResponse, AnnotationRequest, AnnotationResponse
from ...services.annotations import annotation_service
from ...services.books import book_service

router = APIRouter()


@router.post("/annotate", response_model=AnnotationResponse)
def create_annotation(payload: AnnotationRequest):
    with get_session() as session:
        book = book_service.get_book(session, payload.book_id)
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")
        annotation = annotation_service.create(session, payload.book_id, payload.location, payload.note)
    return AnnotationResponse(
        id=annotation.id,
        book_id=annotation.book_id,
        location=annotation.location,
        note=annotation.note,
        created_at=annotation.created_at,
    )


@router.get("/annotations/{book_id}", response_model=AnnotationListResponse)
def list_annotations(book_id: str):
    with get_session() as session:
        book = book_service.get_book(session, book_id)
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")
        annotations = book_service.get_annotations(session, book_id)
    items = [
        AnnotationResponse(
            id=a.id,
            book_id=a.book_id,
            location=a.location,
            note=a.note,
            created_at=a.created_at,
        )
        for a in annotations
    ]
    return AnnotationListResponse(items=items)

from sqlalchemy.orm import Session

from ..models import Annotation


class AnnotationService:
    def create(self, session: Session, book_id: str, location: str, note: str) -> Annotation:
        annotation = Annotation(book_id=book_id, location=location, note=note)
        session.add(annotation)
        session.commit()
        session.refresh(annotation)
        return annotation


annotation_service = AnnotationService()

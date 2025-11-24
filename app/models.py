import uuid
from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from .database import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


class Book(Base):
    __tablename__ = "books"

    id = Column(String, primary_key=True, default=generate_uuid, unique=True)
    title = Column(String, nullable=False)
    author = Column(String, nullable=True)
    filename = Column(String, nullable=False)
    content_path = Column(String, nullable=False)
    cover_path = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # FIXED: SQLAlchemy reserves "metadata"
    extra_metadata = Column(Text, nullable=True)

    annotations = relationship(
        "Annotation",
        back_populates="book",
        cascade="all, delete-orphan"
    )

    progress = relationship(
        "Progress",
        back_populates="book",
        uselist=False,
        cascade="all, delete-orphan"
    )


class Annotation(Base):
    __tablename__ = "annotations"

    id = Column(String, primary_key=True, default=generate_uuid)
    book_id = Column(String, ForeignKey("books.id"), nullable=False, index=True)
    location = Column(String, nullable=False)
    note = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    book = relationship("Book", back_populates="annotations")


class Progress(Base):
    __tablename__ = "progress"

    id = Column(Integer, primary_key=True, autoincrement=True)
    book_id = Column(String, ForeignKey("books.id"), nullable=False, unique=True)
    chapter_id = Column(String, nullable=True)
    paragraph_index = Column(Integer, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow,
                        nullable=False, onupdate=datetime.utcnow)

    book = relationship("Book", back_populates="progress")

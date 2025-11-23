import json
import re
from pathlib import Path
from typing import List

import docx2txt
import fitz
import pdfplumber
from ebooklib import epub
from bs4 import BeautifulSoup


class DocumentIngestionService:
    def __init__(self) -> None:
        self.paragraph_re = re.compile(r"\s*\n\s*\n")

    def ingest(self, file_path: Path, book_id: str, title: str | None = None) -> dict:
        text = self._extract_text(file_path)
        paragraphs = self._split_paragraphs(text)
        chapters = self._build_chapters(paragraphs)

        return {
            "book_id": book_id,
            "title": title or file_path.stem,
            "chapters": chapters,
        }

    def _extract_text(self, file_path: Path) -> str:
        suffix = file_path.suffix.lower()
        if suffix == ".pdf":
            return self._extract_pdf(file_path)
        if suffix == ".epub":
            return self._extract_epub(file_path)
        if suffix in {".txt", ".md"}:
            return file_path.read_text(encoding="utf-8", errors="ignore")
        if suffix in {".docx"}:
            return docx2txt.process(str(file_path)) or ""
        raise ValueError(f"Unsupported file type: {suffix}")

    def _extract_pdf(self, file_path: Path) -> str:
        text_parts: List[str] = []
        try:
            with fitz.open(file_path) as doc:
                for page in doc:
                    text_parts.append(page.get_text("text"))
        except Exception:  # PyMuPDF failed; try pdfplumber
            with pdfplumber.open(file_path) as doc:
                for page in doc.pages:
                    text_parts.append(page.extract_text() or "")
        return "\n".join(text_parts)

    def _extract_epub(self, file_path: Path) -> str:
        book = epub.read_epub(str(file_path))
        texts: List[str] = []
        for item in book.get_items():
            if item.get_type() == epub.EpubHtml:
                soup = BeautifulSoup(item.get_body_content(), "html.parser")
                texts.append(soup.get_text(separator="\n"))
        return "\n".join(texts)

    def _split_paragraphs(self, text: str) -> List[str]:
        raw_paragraphs = [p.strip() for p in self.paragraph_re.split(text) if p.strip()]
        if not raw_paragraphs:
            raw_paragraphs = [line.strip() for line in text.splitlines() if line.strip()]
        return raw_paragraphs

    def _build_chapters(self, paragraphs: List[str]) -> List[dict]:
        if not paragraphs:
            return []
        chunk_size = 40
        chapters = []
        for index in range(0, len(paragraphs), chunk_size):
            chunk = paragraphs[index : index + chunk_size]
            chapter_id = str(len(chapters) + 1)
            chapter_title = f"Chapter {chapter_id}"
            chapters.append(
                {
                    "chapter_id": chapter_id,
                    "title": chapter_title,
                    "paragraphs": chunk,
                }
            )
        return chapters


ingestion_service = DocumentIngestionService()

from __future__ import annotations

import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from docx import Document as DocxDocument
from pypdf import PdfReader

from app.core.logger import get_logger

logger = get_logger(__name__)


class DocumentParseError(Exception):
    """Raised when a document cannot be parsed."""


class DocumentParser:
    """Parse PDF, DOCX, and TXT documents into chunked text."""

    MAX_CHUNK_SIZE = 500
    CHUNK_OVERLAP = 100

    @classmethod
    def parse_file(cls, file_path: str | Path, file_type: str) -> dict[str, Any]:
        path = Path(file_path)
        normalized_type = file_type.lower().lstrip(".")

        if normalized_type == "pdf":
            return cls._parse_pdf(path)
        if normalized_type in {"doc", "docx"}:
            return cls._parse_docx(path)
        if normalized_type == "txt":
            return cls._parse_txt(path)

        raise ValueError(f"Unsupported file type: {file_type}")

    @classmethod
    def _parse_pdf(cls, file_path: Path) -> dict[str, Any]:
        try:
            reader = PdfReader(str(file_path))
            page_text = [cls._normalize_text(page.extract_text() or "") for page in reader.pages]
            content = "\n\n".join(text for text in page_text if text).strip()
            metadata = reader.metadata or {}

            result = {
                "content": content,
                "chunks": cls.chunk_text(content),
                "metadata": {
                    "title": cls._metadata_value(metadata, "title", "/Title"),
                    "author": cls._metadata_value(metadata, "author", "/Author"),
                    "date": cls._normalize_date(
                        cls._metadata_value(metadata, "creation_date", "/CreationDate")
                        or cls._metadata_value(metadata, "modification_date", "/ModDate")
                    ),
                    "pages": len(reader.pages),
                },
                "source": "pdf",
            }
            logger.info(
                "document_parsed",
                file_type="pdf",
                path=str(file_path),
                pages=result["metadata"]["pages"],
                chunks=len(result["chunks"]),
            )
            return result
        except Exception as exc:
            logger.warning("document_parse_failed", file_type="pdf", path=str(file_path), error=str(exc))
            raise DocumentParseError(f"Unable to parse PDF file: {file_path.name}") from exc

    @classmethod
    def _parse_docx(cls, file_path: Path) -> dict[str, Any]:
        try:
            document = DocxDocument(str(file_path))
            paragraphs = [cls._normalize_text(paragraph.text) for paragraph in document.paragraphs]
            content = "\n\n".join(paragraph for paragraph in paragraphs if paragraph).strip()
            properties = document.core_properties

            result = {
                "content": content,
                "chunks": cls.chunk_text(content),
                "metadata": {
                    "title": (properties.title or "").strip(),
                    "author": (properties.author or "").strip(),
                    "date": cls._normalize_date(properties.created or properties.modified),
                    "paragraphs": len([paragraph for paragraph in paragraphs if paragraph]),
                },
                "source": "docx",
            }
            logger.info(
                "document_parsed",
                file_type="docx",
                path=str(file_path),
                paragraphs=result["metadata"]["paragraphs"],
                chunks=len(result["chunks"]),
            )
            return result
        except Exception as exc:
            logger.warning("document_parse_failed", file_type="docx", path=str(file_path), error=str(exc))
            raise DocumentParseError(f"Unable to parse DOCX file: {file_path.name}") from exc

    @classmethod
    def _parse_txt(cls, file_path: Path) -> dict[str, Any]:
        try:
            text = file_path.read_text(encoding="utf-8-sig")
            normalized_text = cls._normalize_text(text)
            stat = file_path.stat()

            result = {
                "content": normalized_text,
                "chunks": cls.chunk_text(normalized_text),
                "metadata": {
                    "title": file_path.stem,
                    "author": "",
                    "date": datetime.fromtimestamp(stat.st_mtime, tz=UTC).isoformat(),
                    "size_bytes": stat.st_size,
                },
                "source": "txt",
            }
            logger.info(
                "document_parsed",
                file_type="txt",
                path=str(file_path),
                size_bytes=result["metadata"]["size_bytes"],
                chunks=len(result["chunks"]),
            )
            return result
        except Exception as exc:
            logger.warning("document_parse_failed", file_type="txt", path=str(file_path), error=str(exc))
            raise DocumentParseError(f"Unable to parse text file: {file_path.name}") from exc

    @classmethod
    def chunk_text(
        cls,
        text: str,
        chunk_size: int | None = None,
        overlap: int | None = None,
    ) -> list[str]:
        normalized_text = cls._normalize_text(text)
        if not normalized_text:
            return []

        max_tokens = chunk_size or cls.MAX_CHUNK_SIZE
        overlap_tokens = overlap or cls.CHUNK_OVERLAP
        units = cls._split_units(normalized_text, max_tokens)

        chunks: list[str] = []
        current_units: list[str] = []
        current_tokens = 0

        for unit in units:
            unit_tokens = cls._estimate_tokens(unit)
            if unit_tokens > max_tokens:
                if current_units:
                    chunks.append(cls._join_units(current_units))
                    overlap_text = cls._extract_overlap_text(chunks[-1], overlap_tokens)
                    current_units = [overlap_text] if overlap_text else []
                    current_tokens = cls._estimate_tokens(overlap_text) if overlap_text else 0

                chunks.extend(cls._chunk_large_unit(unit, max_tokens, overlap_tokens))
                overlap_text = cls._extract_overlap_text(chunks[-1], overlap_tokens)
                current_units = [overlap_text] if overlap_text else []
                current_tokens = cls._estimate_tokens(overlap_text) if overlap_text else 0
                continue

            if current_units and current_tokens + unit_tokens > max_tokens:
                chunk = cls._join_units(current_units)
                chunks.append(chunk)
                overlap_text = cls._extract_overlap_text(chunk, overlap_tokens)
                current_units = [overlap_text] if overlap_text else []
                current_tokens = cls._estimate_tokens(overlap_text) if overlap_text else 0

            current_units.append(unit)
            current_tokens += unit_tokens

        if current_units:
            final_chunk = cls._join_units(current_units)
            if not chunks or final_chunk != chunks[-1]:
                chunks.append(final_chunk)

        logger.info("text_chunked", chunk_count=len(chunks), estimated_tokens=cls._estimate_tokens(normalized_text))
        return chunks

    @staticmethod
    def _normalize_text(text: str) -> str:
        normalized = text.replace("\r\n", "\n").replace("\r", "\n")
        normalized = re.sub(r"[ \t]+", " ", normalized)
        normalized = re.sub(r"\n{3,}", "\n\n", normalized)
        return normalized.strip()

    @classmethod
    def _split_units(cls, text: str, max_tokens: int) -> list[str]:
        paragraphs = [part.strip() for part in re.split(r"\n{2,}", text) if part.strip()]
        if not paragraphs:
            paragraphs = [text]

        units: list[str] = []
        for paragraph in paragraphs:
            if cls._estimate_tokens(paragraph) <= max_tokens:
                units.append(paragraph)
                continue

            sentences = [part.strip() for part in re.split(r"(?<=[.!?])\s+", paragraph) if part.strip()]
            if not sentences:
                units.append(paragraph)
            else:
                units.extend(sentences)
        return units

    @staticmethod
    def _join_units(units: list[str]) -> str:
        return "\n\n".join(unit.strip() for unit in units if unit.strip()).strip()

    @staticmethod
    def _estimate_tokens(text: str) -> int:
        if not text:
            return 0
        return max(1, len(re.findall(r"\S+", text)))

    @classmethod
    def _chunk_large_unit(cls, unit: str, chunk_size: int, overlap: int) -> list[str]:
        words = unit.split()
        if not words:
            return []

        chunks: list[str] = []
        start = 0
        step = max(1, chunk_size - overlap)
        while start < len(words):
            chunk_words = words[start : start + chunk_size]
            if not chunk_words:
                break
            chunks.append(" ".join(chunk_words))
            if start + chunk_size >= len(words):
                break
            start += step
        return chunks

    @classmethod
    def _extract_overlap_text(cls, text: str, overlap_tokens: int) -> str:
        if overlap_tokens <= 0:
            return ""
        words = text.split()
        if not words:
            return ""
        return " ".join(words[-overlap_tokens:])

    @staticmethod
    def _metadata_value(metadata: Any, attribute_name: str, dict_key: str) -> str:
        attr_value = getattr(metadata, attribute_name, None)
        if attr_value:
            return str(attr_value).strip()
        if hasattr(metadata, "get"):
            value = metadata.get(dict_key)
            if value:
                return str(value).strip()
        return ""

    @classmethod
    def _normalize_date(cls, value: Any) -> str:
        if value is None or value == "":
            return ""
        if isinstance(value, datetime):
            if value.tzinfo is None:
                return value.replace(tzinfo=UTC).isoformat()
            return value.astimezone(UTC).isoformat()
        if isinstance(value, str):
            pdf_match = re.fullmatch(
                r"D:(\d{4})(\d{2})?(\d{2})?(\d{2})?(\d{2})?(\d{2})?.*",
                value,
            )
            if pdf_match:
                year = int(pdf_match.group(1))
                month = int(pdf_match.group(2) or 1)
                day = int(pdf_match.group(3) or 1)
                hour = int(pdf_match.group(4) or 0)
                minute = int(pdf_match.group(5) or 0)
                second = int(pdf_match.group(6) or 0)
                return datetime(year, month, day, hour, minute, second, tzinfo=UTC).isoformat()
            try:
                return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC).isoformat()
            except ValueError:
                pass
            return value.strip()
        return str(value)

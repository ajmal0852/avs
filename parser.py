from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import Any, BinaryIO, Union

from docx import Document
from pypdf import PdfReader

MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024


PathLike = Union[str, Path]
FileInput = Union[PathLike, bytes, bytearray, BinaryIO, Any]


def _normalize_text(text: str) -> str:
    """Collapse odd whitespace and keep output UTF-8 safe."""
    normalized = " ".join(text.split())
    return normalized.encode("utf-8", errors="ignore").decode("utf-8")


def _get_file_extension(file_input: FileInput) -> str:
    if isinstance(file_input, (str, Path)):
        return Path(file_input).suffix.lower()

    filename = getattr(file_input, "name", "")
    if filename:
        return Path(str(filename)).suffix.lower()

    return ""


def _read_binary_content(file_input: FileInput) -> bytes:
    if isinstance(file_input, bytes):
        content = file_input
    elif isinstance(file_input, bytearray):
        content = bytes(file_input)
    elif isinstance(file_input, (str, Path)):
        content = Path(file_input).read_bytes()
    elif hasattr(file_input, "read"):
        raw = file_input.read()
        if isinstance(raw, str):
            content = raw.encode("utf-8")
        else:
            content = bytes(raw)
    else:
        raise TypeError("Unsupported file input type.")

    if len(content) > MAX_FILE_SIZE_BYTES:
        raise ValueError("File size exceeds the 5 MB limit.")

    return content


def parse_pdf(file_input: FileInput) -> str:
    """Extract and normalize raw text from a PDF file."""
    try:
        content = _read_binary_content(file_input)
        reader = PdfReader(BytesIO(content))

        pages: list[str] = []
        for page in reader.pages:
            page_text = page.extract_text() or ""
            if page_text:
                pages.append(page_text)

        return _normalize_text("\n".join(pages))
    except Exception as exc:
        raise ValueError(f"Failed to parse PDF file: {exc}") from exc


def parse_docx(file_input: FileInput) -> str:
    """Extract and normalize raw text from a DOCX file."""
    try:
        content = _read_binary_content(file_input)
        document = Document(BytesIO(content))

        paragraphs = [paragraph.text for paragraph in document.paragraphs if paragraph.text]
        return _normalize_text("\n".join(paragraphs))
    except Exception as exc:
        raise ValueError(f"Failed to parse DOCX file: {exc}") from exc


def extract_text(file_input: FileInput) -> str:
    """Detect the file type and extract text with the appropriate parser."""
    extension = _get_file_extension(file_input)

    if extension == ".pdf":
        return parse_pdf(file_input)

    if extension == ".docx":
        return parse_docx(file_input)

    raise ValueError("Unsupported file type. Only PDF and DOCX files are supported.")
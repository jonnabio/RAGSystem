"""PDF document processor using PyMuPDF."""

import fitz  # PyMuPDF
from typing import Dict, Any
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class PDFProcessor:
    """
    PDF document processor for text extraction and metadata.

    Uses PyMuPDF (fitz) for reliable PDF parsing.
    """

    def extract_text(self, file_path: str) -> str:
        """
        Extract all text from PDF document.

        Args:
            file_path: Path to PDF file

        Returns:
            Extracted text content

        Raises:
            FileNotFoundError: If file doesn't exist
            RuntimeError: If PDF is corrupted or unreadable
        """
        if not Path(file_path).exists():
            raise FileNotFoundError(f"PDF file not found: {file_path}")

        try:
            doc = fitz.open(file_path)
            text_parts = []

            for page_num, page in enumerate(doc, start=1):
                try:
                    page_text = page.get_text()
                    if page_text.strip():
                        text_parts.append(page_text)
                except Exception as e:
                    logger.warning(f"Error extracting text from page {page_num}: {e}")
                    continue

            doc.close()

            if not text_parts:
                logger.warning(f"No text extracted from {file_path}")
                return ""

            return "\\n\\n".join(text_parts)

        except fitz.FileDataError as e:
            raise RuntimeError(f"Corrupted or invalid PDF file: {e}")
        except Exception as e:
            raise RuntimeError(f"Error processing PDF: {e}")

    def extract_metadata(self, file_path: str) -> Dict[str, Any]:
        """
        Extract PDF metadata.

        Args:
            file_path: Path to PDF file

        Returns:
            Dictionary containing PDF metadata
        """
        if not Path(file_path).exists():
            raise FileNotFoundError(f"PDF file not found: {file_path}")

        try:
            doc = fitz.open(file_path)

            # Get metadata and page count
            metadata = {
                "page_count": doc.page_count,
                "format": "PDF",
                **doc.metadata  # Merge PDF metadata dict
            }

            doc.close()

            # Clean up None values
            metadata = {k: v for k, v in metadata.items() if v is not None}

            return metadata

        except Exception as e:
            logger.error(f"Error extracting PDF metadata: {e}")
            return {"format": "PDF", "error": str(e)}

    def get_page_count(self, file_path: str) -> int:
        """
        Get number of pages in PDF.

        Args:
            file_path: Path to PDF file

        Returns:
            Number of pages
        """
        try:
            doc = fitz.open(file_path)
            count = doc.page_count
            doc.close()
            return count
        except Exception as e:
            logger.error(f"Error getting page count: {e}")
            return 0

"""Text chunking strategies for RAG."""

from typing import List, Dict, Any
from src.features.documents.domain.entities import Chunk
from datetime import datetime
import uuid
import re


class ChunkingStrategy:
    """
    Smart text chunking with overlap for better context preservation.

    Implements word-based chunking with configurable size and overlap.
    Preserves sentence boundaries when possible.
    """

    def __init__(self, chunk_size: int = 512, overlap: int = 50):
        """
        Initialize chunking strategy.

        Args:
            chunk_size: Target number of words per chunk
            overlap: Number of words to overlap between chunks
        """
        if chunk_size <= 0:
            raise ValueError("chunk_size must be positive")
        if overlap < 0:
            raise ValueError("overlap cannot be negative")
        if overlap >= chunk_size:
            raise ValueError("overlap must be less than chunk_size")

        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_text(
        self,
        text: str,
        document_id: str,
        metadata: Dict[str, Any] = None
    ) -> List[Chunk]:
        """
        Split text into overlapping chunks.

        Args:
            text: Text to chunk
            document_id: ID of source document
            metadata: Optional metadata to attach to chunks

        Returns:
            List of Chunk entities
        """
        if not text or not text.strip():
            return []

        metadata = metadata or {}

        # Clean and normalize text
        text = self._clean_text(text)

        # Split into words while preserving some structure
        words = text.split()

        if len(words) <= self.chunk_size:
            # Text fits in one chunk
            return [self._create_chunk(
                text=text,
                document_id=document_id,
                chunk_index=0,
                metadata=metadata
            )]

        chunks = []
        start = 0

        while start < len(words):
            # Get chunk words
            end = min(start + self.chunk_size, len(words))
            chunk_words = words[start:end]
            chunk_text = " ".join(chunk_words)

            # Try to end at sentence boundary if not last chunk
            if end < len(words):
                chunk_text = self._adjust_to_sentence_boundary(chunk_text)

            # Create chunk entity
            chunks.append(self._create_chunk(
                text=chunk_text,
                document_id=document_id,
                chunk_index=len(chunks),
                metadata={**metadata, "word_count": len(chunk_words)}
            ))

            # Break if we reached the end of the text
            if end == len(words):
                break

            # Move start position with overlap
            start = end - self.overlap

            # Prevent infinite loop (safety guard)
            if start >= end:
                break

        return chunks

    def _clean_text(self, text: str) -> str:
        """Clean and normalize text."""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove leading/trailing whitespace
        text = text.strip()
        return text

    def _adjust_to_sentence_boundary(self, text: str) -> str:
        """Try to end chunk at a sentence boundary."""
        # Look for sentence endings
        sentence_endings = ['. ', '! ', '? ', '.\n', '!\n', '?\n']

        # Find last sentence ending
        last_pos = -1
        for ending in sentence_endings:
            pos = text.rfind(ending)
            if pos > last_pos and pos > len(text) * 0.7:  # At least 70% through
                last_pos = pos

        if last_pos > 0:
            return text[:last_pos + 1].strip()

        return text

    def _create_chunk(
        self,
        text: str,
        document_id: str,
        chunk_index: int,
        metadata: Dict[str, Any]
    ) -> Chunk:
        """Create a Chunk entity."""
        return Chunk(
            id=str(uuid.uuid4()),
            document_id=document_id,
            chunk_index=chunk_index,
            text=text,
            metadata=metadata,
            created_at=datetime.utcnow()
        )

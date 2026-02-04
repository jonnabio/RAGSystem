"""Unit tests for document domain entities."""

import pytest
from datetime import datetime
from src.features.documents.domain.entities import (
    Document,
    Chunk,
    DocumentType,
    DocumentStatus
)


class TestDocumentEntity:
    """Tests for Document entity."""

    def test_create_document_with_defaults(self):
        """Should create document with default values."""
        doc = Document(
            filename="test.pdf",
            file_path="/path/to/test.pdf",
            document_type=DocumentType.PDF,
            size_bytes=1024
        )

        assert doc.id is not None
        assert doc.filename == "test.pdf"
        assert doc.document_type == DocumentType.PDF
        assert doc.processed is False
        assert doc.status == DocumentStatus.UPLOADED
        assert doc.chunk_count == 0
        assert isinstance(doc.uploaded_at, datetime)

    def test_create_document_with_all_fields(self):
        """Should create document with all fields specified."""
        doc = Document(
            id="custom-id",
            filename="report.docx",
            file_path="/docs/report.docx",
            document_type=DocumentType.DOCX,
            size_bytes=2048,
            processed=True,
            status=DocumentStatus.COMPLETED,
            chunk_count=10,
            metadata={"author": "John Doe"}
        )

        assert doc.id == "custom-id"
        assert doc.processed is True
        assert doc.status == DocumentStatus.COMPLETED
        assert doc.chunk_count == 10
        assert doc.metadata == {"author": "John Doe"}

    def test_document_type_enum(self):
        """Should validate document types."""
        assert DocumentType.PDF == "pdf"
        assert DocumentType.DOCX == "docx"
        assert DocumentType.TXT == "txt"

    def test_document_status_enum(self):
        """Should validate document statuses."""
        assert DocumentStatus.UPLOADED == "uploaded"
        assert DocumentStatus.PROCESSING == "processing"
        assert DocumentStatus.COMPLETED == "completed"
        assert DocumentStatus.FAILED == "failed"


class TestChunkEntity:
    """Tests for Chunk entity."""

    def test_create_chunk_with_defaults(self):
        """Should create chunk with default values."""
        chunk = Chunk(
            document_id="doc-123",
            chunk_index=0,
            text="Sample text chunk"
        )

        assert chunk.id is not None
        assert chunk.document_id == "doc-123"
        assert chunk.chunk_index == 0
        assert chunk.text == "Sample text chunk"
        assert chunk.embedding is None
        assert chunk.metadata == {}
        assert isinstance(chunk.created_at, datetime)

    def test_create_chunk_with_embedding(self):
        """Should create chunk with embedding vector."""
        embedding = [0.1] * 3072
        chunk = Chunk(
            document_id="doc-456",
            chunk_index=5,
            text="Text with embedding",
            embedding=embedding
        )

        assert chunk.embedding == embedding
        assert len(chunk.embedding) == 3072

    def test_create_chunk_with_metadata(self):
        """Should create chunk with metadata."""
        chunk = Chunk(
            document_id="doc-789",
            chunk_index=2,
            text="Chunk with metadata",
            metadata={"page": 1, "section": "intro"}
        )

        assert chunk.metadata["page"] == 1
        assert chunk.metadata["section"] == "intro"

    def test_chunk_serialization(self):
        """Should serialize chunk to dict."""
        chunk = Chunk(
            id="chunk-1",
            document_id="doc-1",
            chunk_index=0,
            text="Test",
            metadata={"key": "value"}
        )

        data = chunk.model_dump()
        assert data["id"] == "chunk-1"
        assert data["document_id"] == "doc-1"
        assert data["text"] == "Test"
        assert data["metadata"] == {"key": "value"}

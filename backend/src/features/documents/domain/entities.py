"""Domain entities for document processing."""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
import uuid


class DocumentType(str, Enum):
    """Supported document types."""
    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"


class DocumentStatus(str, Enum):
    """Document processing status."""
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Document(BaseModel):
    """Document entity representing an uploaded file."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    filename: str
    file_path: str
    document_type: DocumentType
    size_bytes: int
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
    processed: bool = False
    status: DocumentStatus = DocumentStatus.UPLOADED
    chunk_count: int = 0
    metadata: Dict[str, Any] = Field(default_factory=dict)
    error_message: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "filename": "example.pdf",
                "file_path": "data/documents/example.pdf",
                "document_type": "pdf",
                "size_bytes": 1024000,
                "uploaded_at": "2026-02-02T00:00:00Z",
                "processed": True,
                "status": "completed",
                "chunk_count": 50
            }
        }


class Chunk(BaseModel):
    """Text chunk entity with optional embedding."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    document_id: str
    chunk_index: int
    text: str
    embedding: Optional[List[float]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "chunk-123",
                "document_id": "doc-456",
                "chunk_index": 0,
                "text": "This is a sample text chunk from the document.",
                "metadata": {"page": 1, "section": "introduction"},
                "created_at": "2026-02-02T00:00:00Z"
            }
        }

"""Document processing service - application layer."""

from typing import Optional, List
from pathlib import Path
import uuid
import logging
from datetime import datetime

from src.features.documents.domain.entities import Document, DocumentType, DocumentStatus, Chunk
from src.features.documents.infrastructure.pdf_processor import PDFProcessor
from src.features.documents.infrastructure.word_processor import WordProcessor
from src.features.rag.domain.chunking import ChunkingStrategy
from src.features.rag.domain.interfaces import IEmbeddingService, IVectorStore
from src.features.documents.application.redaction_service import RedactionService

logger = logging.getLogger(__name__)


class DocumentService:
    """
    Document processing service.

    Orchestrates the full document pipeline:
    Upload → Extract → Chunk → Embed → Store
    """

    def __init__(
        self,
        pdf_processor: PDFProcessor,
        word_processor: WordProcessor,
        chunking_strategy: ChunkingStrategy,
        embedding_service: IEmbeddingService,
        vector_store: IVectorStore,
        storage_path: str,
        redaction_service: Optional[RedactionService] = None
    ):
        """
        Initialize document service with dependencies.

        Args:
            pdf_processor: PDF text extractor
            word_processor: Word document text extractor
            chunking_strategy: Text chunking strategy
            embedding_service: Embedding generation service
            vector_store: Vector database
            storage_path: Path to store uploaded documents
            redaction_service: Optional PII redaction service
        """
        self.processors = {
            DocumentType.PDF: pdf_processor,
            DocumentType.DOCX: word_processor,
        }
        self.chunking = chunking_strategy
        self.embeddings = embedding_service
        self.vector_store = vector_store
        self.storage_path = Path(storage_path)
        self.redaction_service = redaction_service

        # Ensure storage directory exists
        self.storage_path.mkdir(parents=True, exist_ok=True)

    def calculate_hash(self, file_path: str) -> str:
        """
        Calculate SHA-256 hash of a file.
        """
        import hashlib
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            # Read and update hash string value in blocks of 4K
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    async def process_document(
        self,
        file_path: str,
        document_type: DocumentType,
        original_filename: Optional[str] = None,
        tenant_id: str = "default",
        content_hash: Optional[str] = None
    ) -> Document:
        """
        Main pipeline: Extract → Chunk → Embed → Store.

        Args:
            file_path: Path to uploaded file
            document_type: Type of document
            original_filename: Original filename (if different from file_path)

        Returns:
            Processed Document entity

        Raises:
            ValueError: If document type not supported
            RuntimeError: If processing fails
        """
        doc_id = str(uuid.uuid4())
        filename = original_filename or Path(file_path).name

        logger.info(f"Processing document: {filename} (type: {document_type})")

        # Create document entity
        document = Document(
            id=doc_id,
            tenant_id=tenant_id,
            content_hash=content_hash,
            filename=filename,
            file_path=file_path,
            document_type=document_type,
            size_bytes=Path(file_path).stat().st_size,
            uploaded_at=datetime.utcnow(),
            status=DocumentStatus.PROCESSING
        )

        try:
            # Step 1: Extract text and metadata
            processor = self.processors.get(document_type)
            if not processor:
                raise ValueError(f"Unsupported document type: {document_type}")

            text = processor.extract_text(file_path)
            metadata = processor.extract_metadata(file_path)

            if not text or not text.strip():
                raise RuntimeError("No text extracted from document")

            logger.info(f"Extracted {len(text)} characters from {filename}")

            # Step 1.5: PII Redaction
            if self.redaction_service:
                text, redacted_types = self.redaction_service.redact_text(text)
                if redacted_types:
                    metadata["pii_redacted"] = redacted_types
                    logger.info(f"Redacted PII types: {redacted_types}")

            # Step 2: Chunk text
            chunks = self.chunking.chunk_text(
                text=text,
                document_id=doc_id,
                metadata={**metadata, "filename": filename}
            )

            # Step 2.5: Assign tenant to chunks
            for chunk in chunks:
                chunk.tenant_id = tenant_id

            logger.info(f"Created {len(chunks)} chunks from {filename}")

            # Step 3: Generate embeddings
            chunk_texts = [chunk.text for chunk in chunks]
            embeddings = await self.embeddings.generate_embeddings_large_batch(chunk_texts)

            # Attach embeddings to chunks
            for chunk, embedding in zip(chunks, embeddings):
                chunk.embedding = embedding

            logger.info(f"Generated embeddings for {len(chunks)} chunks")

            # Step 4: Store in vector database
            await self.vector_store.add_chunks(chunks)

            logger.info(f"Stored {len(chunks)} chunks in vector database")

            # Update document entity
            document.processed = True
            document.status = DocumentStatus.COMPLETED
            document.chunk_count = len(chunks)
            document.metadata = metadata

            logger.info(f"Successfully processed document: {filename}")

            return document

        except Exception as e:
            logger.error(f"Error processing document {filename}: {e}")
            document.status = DocumentStatus.FAILED
            document.error_message = str(e)
            raise RuntimeError(f"Document processing failed: {e}")

    async def delete_document(self, document_id: str, tenant_id: str = "default") -> None:
        """
        Delete document and all its chunks.

        Args:
            document_id: Document ID to delete
            tenant_id: Tenant context
        """
        logger.info(f"Deleting document: {document_id}")

        try:
            # Delete from vector store
            await self.vector_store.delete_document(document_id, tenant_id=tenant_id)

            logger.info(f"Successfully deleted document: {document_id}")

        except Exception as e:
            logger.error(f"Error deleting document {document_id}: {e}")
            raise RuntimeError(f"Failed to delete document: {e}")

    async def get_document_chunks(self, document_id: str) -> List[Chunk]:
        """
        Get all chunks for a document.

        Args:
            document_id: Document ID

        Returns:
            List of chunks
        """
        try:
            chunks = await self.vector_store.get_document_chunks(document_id)
            logger.info(f"Retrieved {len(chunks)} chunks for document {document_id}")
            return chunks

        except Exception as e:
            logger.error(f"Error retrieving chunks for {document_id}: {e}")
            return []

"""Domain interfaces and entities for RAG."""

from typing import Protocol, List, Optional, Dict, Any
from pydantic import BaseModel
from src.features.documents.domain.entities import Chunk


class SearchResult(BaseModel):
    """Result from vector similarity search."""

    chunk: Chunk
    score: float
    rank: int
    metadata: Dict[str, Any] = {}

    class Config:
        json_schema_extra = {
            "example": {
                "chunk": {
                    "id": "chunk-123",
                    "document_id": "doc-456",
                    "chunk_index": 5,
                    "text": "Relevant text snippet..."
                },
                "score": 0.92,
                "rank": 1
            }
        }


class Message(BaseModel):
    """Chat message."""

    role: str  # 'user', 'assistant', 'system'
    content: str

    class Config:
        json_schema_extra = {
            "example": {
                "role": "user",
                "content": "What is the main topic of the document?"
            }
        }


class LLMResponse(BaseModel):
    """Response from LLM."""

    content: str
    model: str
    tokens_used: int
    cost: Optional[float] = None
    finish_reason: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "content": "The main topic is...",
                "model": "meta-llama/llama-3-70b-instruct",
                "tokens_used": 150,
                "cost": 0.0015
            }
        }


class IEmbeddingService(Protocol):
    """Protocol for embedding generation services."""

    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for single text.

        Args:
            text: Text to embed

        Returns:
            Embedding vector (typically 3072 dimensions)
        """
        ...

    async def generate_embeddings_batch(
        self,
        texts: List[str]
    ) -> List[List[float]]:
        """
        Generate embeddings for multiple texts (batch processing).

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        ...


class IVectorStore(Protocol):
    """Protocol for vector storage and similarity search."""

    async def add_chunks(self, chunks: List[Chunk]) -> None:
        """
        Add chunks to vector store.

        Args:
            chunks: List of chunks with embeddings
        """
        ...

    async def search(
        self,
        query_embedding: List[float],
        limit: int = 5,
        filters: Optional[Dict[str, Any]] = None,
        table_name: Optional[str] = None,
        tenant_id: Optional[str] = None
    ) -> List[SearchResult]:
        """
        Search for similar chunks using vector similarity.

        Args:
            query_embedding: Query vector
            limit: Maximum number of results
            filters: Optional metadata filters
            table_name: Specialized table to search in

        Returns:
            List of search results, ranked by similarity
        """
        ...

    async def search_keyword(
        self,
        query: str,
        limit: int = 5,
        filters: Optional[Dict[str, Any]] = None,
        table_name: Optional[str] = None,
        tenant_id: Optional[str] = None
    ) -> List[SearchResult]:
        """
        Search for chunks using keyword matching (FTS).

        Args:
            query: Text query
            limit: Maximum number of results
            filters: Optional metadata filters
            table_name: Specialized table to search in

        Returns:
            List of search results, ranked by relevance
        """
        ...

    async def delete_document(
        self,
        document_id: str,
        table_name: Optional[str] = None,
        tenant_id: Optional[str] = None
    ) -> None:
        """
        Delete all chunks for a document.

        Args:
            document_id: ID of document to delete
        """
        ...

    async def get_document_chunks(self, document_id: str) -> List[Chunk]:
        """
        Get all chunks for a document.

        Args:
            document_id: Document ID

        Returns:
            List of chunks
        """
        ...


class ILLMClient(Protocol):
    """Protocol for LLM client implementations."""

    async def generate(
        self,
        messages: List[Message],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> LLMResponse:
        """
        Generate response from LLM.

        Args:
            messages: Conversation messages
            model: Model identifier
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate

        Returns:
            LLM response
        """
        ...

    async def get_available_models(self) -> List[Dict[str, Any]]:
        """
        Get list of available models.

        Returns:
            List of model information dicts
        """
        ...

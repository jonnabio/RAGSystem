"""LanceDB vector store implementation."""

import lancedb
from typing import List, Optional, Dict, Any
from pathlib import Path
import logging
from src.features.documents.domain.entities import Chunk
from src.features.rag.domain.interfaces import SearchResult
import asyncio

logger = logging.getLogger(__name__)


class LanceDBVectorStore:
    """
    LanceDB-based vector store for semantic search.

    Provides CRUD operations and similarity search on document chunks.
    """

    def __init__(self, db_path: str, table_name: str = "chunks"):
        """
        Initialize LanceDB vector store.

        Args:
            db_path: Path to LanceDB database directory
            table_name: Name of the table for chunks
        """
        self.db_path = Path(db_path)
        self.table_name = table_name
        self.db = None
        self.table = None

        # Ensure directory exists
        self.db_path.mkdir(parents=True, exist_ok=True)

    async def initialize(self) -> None:
        """Initialize database connection and table."""
        await asyncio.to_thread(self._initialize_sync)

    def _initialize_sync(self) -> None:
        """Synchronous initialization."""
        try:
            self.db = lancedb.connect(str(self.db_path))

            # Check if table exists
            table_names = self.db.table_names()

            if self.table_name in table_names:
                self.table = self.db.open_table(self.table_name)
                logger.info(f"Opened existing table '{self.table_name}'")
            else:
                logger.info(f"Table '{self.table_name}' will be created on first add")

        except Exception as e:
            logger.error(f"Error initializing LanceDB: {e}")
            raise RuntimeError(f"Failed to initialize vector store: {e}")

    async def add_chunks(self, chunks: List[Chunk]) -> None:
        """
        Add chunks to vector store.

        Args:
            chunks: List of chunks with embeddings

        Raises:
            ValueError: If chunks don't have embeddings
        """
        if not chunks:
            return

        # Validate all chunks have embeddings
        for chunk in chunks:
            if not chunk.embedding:
                raise ValueError(f"Chunk {chunk.id} missing embedding")

        # Convert chunks to LanceDB format
        data = []
        for chunk in chunks:
            data.append({
                "id": chunk.id,
                "document_id": chunk.document_id,
                "chunk_index": chunk.chunk_index,
                "text": chunk.text,
                "vector": chunk.embedding,
                "metadata": chunk.metadata,
                "created_at": chunk.created_at.isoformat()
            })

        await asyncio.to_thread(self._add_data_sync, data)
        logger.info(f"Added {len(chunks)} chunks to vector store")

    def _add_data_sync(self, data: List[Dict[str, Any]]) -> None:
        """Synchronous data addition."""
        try:
            if self.table is None:
                # Create table with first batch
                self.table = self.db.create_table(self.table_name, data=data)
            else:
                # Add to existing table
                self.table.add(data)
        except Exception as e:
            logger.error(f"Error adding data to LanceDB: {e}")
            raise RuntimeError(f"Failed to add chunks: {e}")

    async def search(
        self,
        query_embedding: List[float],
        limit: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """
        Search for similar chunks using vector similarity.

        Args:
            query_embedding: Query vector
            limit: Maximum number of results
            filters: Optional metadata filters (e.g., {"document_id": "doc-123"})

        Returns:
            List of search results, ranked by similarity score
        """
        if not query_embedding:
            raise ValueError("Query embedding cannot be empty")

        if self.table is None:
            logger.warning("No table exists, returning empty results")
            return []

        results = await asyncio.to_thread(
            self._search_sync,
            query_embedding,
            limit,
            filters
        )

        return results

    def _search_sync(
        self,
        query_embedding: List[float],
        limit: int,
        filters: Optional[Dict[str, Any]]
    ) -> List[SearchResult]:
        """Synchronous search."""
        try:
            # Perform vector search
            query = self.table.search(query_embedding).limit(limit)

            # Apply filters if provided
            if filters:
                filter_str = " AND ".join([
                    f"{k} = '{v}'" if isinstance(v, str) else f"{k} = {v}"
                    for k, v in filters.items()
                ])
                query = query.where(filter_str)

            results = query.to_list()

            # Convert to SearchResult objects
            search_results = []
            for rank, result in enumerate(results, start=1):
                chunk = Chunk(
                    id=result["id"],
                    document_id=result["document_id"],
                    chunk_index=result["chunk_index"],
                    text=result["text"],
                    embedding=result["vector"],
                    metadata=result.get("metadata", {})
                )

                search_results.append(SearchResult(
                    chunk=chunk,
                    score=float(result.get("_distance", 0.0)),
                    rank=rank
                ))

            logger.info(f"Found {len(search_results)} similar chunks")
            return search_results

        except Exception as e:
            logger.error(f"Error searching LanceDB: {e}")
            return []

    async def delete_document(self, document_id: str) -> None:
        """
        Delete all chunks for a document.

        Args:
            document_id: Document ID to delete
        """
        if self.table is None:
            logger.warning("No table exists, nothing to delete")
            return

        await asyncio.to_thread(self._delete_sync, document_id)
        logger.info(f"Deleted chunks for document {document_id}")

    def _delete_sync(self, document_id: str) -> None:
        """Synchronous delete."""
        try:
            self.table.delete(f"document_id = '{document_id}'")
        except Exception as e:
            logger.error(f"Error deleting from LanceDB: {e}")
            raise RuntimeError(f"Failed to delete document chunks: {e}")

    async def get_document_chunks(self, document_id: str) -> List[Chunk]:
        """
        Get all chunks for a document.

        Args:
            document_id: Document ID

        Returns:
            List of chunks
        """
        if self.table is None:
            return []

        chunks = await asyncio.to_thread(self._get_chunks_sync, document_id)
        return chunks

    def _get_chunks_sync(self, document_id: str) -> List[Chunk]:
        """Synchronous chunk retrieval."""
        try:
            results = self.table.search().where(
                f"document_id = '{document_id}'"
            ).to_list()

            chunks = []
            for result in results:
                chunks.append(Chunk(
                    id=result["id"],
                    document_id=result["document_id"],
                    chunk_index=result["chunk_index"],
                    text=result["text"],
                    embedding=result["vector"],
                    metadata=result.get("metadata", {})
                ))

            return chunks

        except Exception as e:
            logger.error(f"Error retrieving chunks: {e}")
            return []

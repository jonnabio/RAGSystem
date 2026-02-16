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

    def __init__(self, db_path: str, default_table_name: str = "technical_docs"):
        """
        Initialize LanceDB vector store.

        Args:
            db_path: Path to LanceDB database directory
            default_table_name: Default table name to use if none specified
        """
        self.db_path = Path(db_path)
        self.default_table_name = default_table_name
        self.db = None
        self._tables = {}  # Cache for opened tables

        # Ensure directory exists
        self.db_path.mkdir(parents=True, exist_ok=True)

    async def initialize(self) -> None:
        """Initialize database connection and table."""
        await asyncio.to_thread(self._initialize_sync)

    def _initialize_sync(self) -> None:
        """Synchronous initialization."""
        try:
            self.db = lancedb.connect(str(self.db_path))
            logger.info(f"Connected to LanceDB at {self.db_path}")
        except Exception as e:
            logger.error(f"Error initializing LanceDB: {e}")
            raise RuntimeError(f"Failed to initialize vector store: {e}")

    async def add_chunks(self, chunks: List[Chunk], table_name: Optional[str] = None) -> None:
        """
        Add chunks to vector store.

        Args:
            chunks: List of chunks with embeddings
            table_name: Name of the table (defaults to technical_docs)

        Raises:
            ValueError: If chunks don't have embeddings
        """
        logger.info(f"Adding {len(chunks)} chunks to vector store (table={table_name or self.default_table_name})")
        if not chunks:
            return

        # Validate all chunks have embeddings
        for chunk in chunks:
            if not chunk.embedding:
                raise ValueError(f"Chunk {chunk.id} missing embedding")

        # Convert chunks to LanceDB format
        data = []

        # Fixed set of allowed metadata fields based on existing schema
        ALLOWED_METADATA_FIELDS = {
            "author", "creationDate", "creator", "filename", "format",
            "keywords", "modDate", "page_count", "producer",
            "subject", "title", "trapped", "word_count"
        }

        for chunk in chunks:
            # Sanitize metadata: only keep allowed fields
            sanitized_metadata = {
                k: v for k, v in chunk.metadata.items()
                if k in ALLOWED_METADATA_FIELDS
            }

            # Ensure all allowed fields are present (default to empty string or 0)
            for field in ALLOWED_METADATA_FIELDS:
                if field not in sanitized_metadata:
                    if field in ["page_count", "word_count"]:
                        sanitized_metadata[field] = 0
                    else:
                        sanitized_metadata[field] = ""

            data.append({
                "id": chunk.id,
                "tenant_id": chunk.tenant_id,
                "document_id": chunk.document_id,
                "chunk_index": chunk.chunk_index,
                "text": chunk.text,
                "vector": chunk.embedding,
                "metadata": sanitized_metadata,
                "created_at": chunk.created_at.isoformat()
            })

        target_table = table_name or self.default_table_name
        await asyncio.to_thread(self._add_data_sync, data, target_table)
        logger.info(f"Added {len(chunks)} chunks to table '{target_table}'")

    def _add_data_sync(self, data: List[Dict[str, Any]], table_name: str) -> None:
        """Synchronous data addition."""
        try:
            if table_name not in self.db.table_names():
                logger.info(f"Creating new table '{table_name}'")
                table = self.db.create_table(table_name, data=data)
                self._tables[table_name] = table
            else:
                table = self._tables.get(table_name) or self.db.open_table(table_name)

                # Check for schema mismatch (specifically missing tenant_id or created_at)
                existing_cols = table.schema.names
                data_cols = data[0].keys() if data else []
                missing_in_vdb = [c for c in data_cols if c not in existing_cols]

                if missing_in_vdb:
                    logger.warning(f"Schema mismatch: missing columns {missing_in_vdb} in table '{table_name}'. Dropping and recreating table to evolve schema.")
                    # In a production app, we would migrate. Here, we recreate for simplicity.
                    self.db.drop_table(table_name)
                    table = self.db.create_table(table_name, data=data)
                else:
                    table.add(data)

                self._tables[table_name] = table
        except Exception as e:
            logger.error(f"Error adding data to LanceDB: {e}")
            if "not found in target schema" in str(e):
                logger.error("Schema mismatch detected. You may need to use the 'Reset Database' button in Settings.")
            raise RuntimeError(f"Failed to add chunks: {e}")


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
            limit: Maximum number of results
            filters: Optional metadata filters
            table_name: Specialized table to search in
            tenant_id: Optional[str] = None
        """
        if not query_embedding:
            raise ValueError("Query embedding cannot be empty")

        # Enforce tenant isolation if provided
        final_filters = filters or {}
        if tenant_id:
            final_filters["tenant_id"] = tenant_id

        target_table = table_name or self.default_table_name

        if target_table not in self.db.table_names():
            logger.warning(f"Table '{target_table}' does not exist, searching in '{self.default_table_name}'")
            target_table = self.default_table_name
            if target_table not in self.db.table_names():
                return []

        results = await asyncio.to_thread(
            self._search_sync,
            query_embedding,
            limit,
            final_filters,
            target_table
        )

        return results

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
            tenant_id: Optional[str] = None
        """
        if not query:
            return []

        # Enforce tenant isolation if provided
        final_filters = filters or {}
        if tenant_id:
            final_filters["tenant_id"] = tenant_id

        target_table = table_name or self.default_table_name

        if target_table not in self.db.table_names():
            logger.warning(f"Table '{target_table}' does not exist, FTS search skipped.")
            return []

        results = await asyncio.to_thread(
            self._search_keyword_sync,
            query,
            limit,
            final_filters,
            target_table
        )

        return results

    def _search_keyword_sync(
        self,
        query: str,
        limit: int,
        filters: Optional[Dict[str, Any]],
        table_name: str
    ) -> List[SearchResult]:
        """Synchronous keyword search."""
        try:
            table = self._tables.get(table_name) or self.db.open_table(table_name)
            self._tables[table_name] = table

            # Create FTS index if it doesn't exist
            try:
                table.create_fts_index("text")
            except Exception:
                pass

            # FTS search
            search_query = table.search(query).limit(limit)

            # Apply filters if provided
            if filters:
                filter_str = " AND ".join([
                    f"{k} = '{v}'" if isinstance(v, str) else f"{k} = {v}"
                    for k, v in filters.items()
                ])
                search_query = search_query.where(filter_str)

            results = search_query.to_list()

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
                    score=float(result.get("score", 0.0)),  # FTS score if available
                    rank=rank
                ))

            logger.info(f"Found {len(search_results)} FTS matches")
            return search_results

        except Exception as e:
            logger.error(f"Error searching LanceDB FTS: {e}")
            return []

    def _search_sync(
        self,
        query_embedding: List[float],
        limit: int,
        filters: Optional[Dict[str, Any]],
        table_name: str
    ) -> List[SearchResult]:
        """Synchronous search."""
        try:
            table = self._tables.get(table_name) or self.db.open_table(table_name)
            self._tables[table_name] = table

            # Create FTS index if it doesn't exist
            try:
                table.create_fts_index("text")
            except Exception:
                pass

            # Default to vector search
            query = table.search(query_embedding).limit(limit)

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

    async def delete_document(
        self,
        document_id: str,
        table_name: Optional[str] = None,
        tenant_id: Optional[str] = None
    ) -> None:
        """
        Delete all chunks for a document.

        Args:
            document_id: Document ID to delete
            table_name: Specialized table to delete from
            tenant_id: Optional tenant ID validation
        """
        target_table = table_name or self.default_table_name
        if target_table not in self.db.table_names():
            return

        delete_filter = f"document_id = '{document_id}'"
        if tenant_id:
            delete_filter += f" AND tenant_id = '{tenant_id}'"

        await asyncio.to_thread(self._delete_sync, delete_filter, target_table)
        logger.info(f"Deleted chunks for document {document_id} from table '{target_table}'")

    def _delete_sync(self, delete_filter: str, table_name: str) -> None:
        """Synchronous delete."""
        try:
            table = self._tables.get(table_name) or self.db.open_table(table_name)
            table.delete(delete_filter)
        except Exception as e:
            logger.error(f"Error deleting from LanceDB: {e}")
            raise RuntimeError(f"Failed to delete document chunks: {e}")

    async def get_document_chunks(self, document_id: str, table_name: Optional[str] = None) -> List[Chunk]:
        """
        Get all chunks for a document.

        Args:
            document_id: Document ID
            table_name: Specialized table to search in

        Returns:
            List of chunks
        """
        target_table = table_name or self.default_table_name
        if target_table not in self.db.table_names():
            return []

        chunks = await asyncio.to_thread(self._get_chunks_sync, document_id, target_table)
        return chunks

    def _get_chunks_sync(self, document_id: str, table_name: str) -> List[Chunk]:
        """Synchronous chunk retrieval."""
        try:
            table = self._tables.get(table_name) or self.db.open_table(table_name)
            results = table.search().where(
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

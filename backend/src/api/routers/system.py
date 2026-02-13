"""System diagnostics and architecture visualization router."""

from fastapi import APIRouter
from typing import Dict, Any
import httpx
import logging

from src.config import settings
from src.shared.pipeline_events import pipeline_tracker

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/system", tags=["system"])


@router.get("/info")
async def system_info() -> Dict[str, Any]:
    """Return system configuration for the Architect's View."""
    return {
        "chunking": {
            "chunk_size": settings.CHUNK_SIZE,
            "chunk_overlap": settings.CHUNK_OVERLAP,
            "strategy": "word-based with sentence boundary adjustment",
        },
        "embedding": {
            "model": settings.EMBEDDING_MODEL,
            "dimensions": settings.EMBEDDING_DIMENSIONS,
            "provider": "OpenRouter",
        },
        "vector_database": {
            "engine": "LanceDB",
            "path": settings.VECTOR_DB_PATH,
            "index_type": "IVF-PQ (automatic)",
            "search_method": "Vector Similarity (L2 distance)",
        },
        "llm": {
            "default_model": settings.DEFAULT_MODEL,
            "provider": "OpenRouter",
            "max_retrieval_chunks": settings.MAX_RETRIEVAL_CHUNKS,
        },
    }


@router.get("/stats")
async def system_stats() -> Dict[str, Any]:
    """Return aggregate storage and usage statistics."""
    try:
        import src.main

        # Access globals cleanly
        documents_db = getattr(src.main, "documents_db", {})
        _vector_store = getattr(src.main, "_vector_store", None)

        total_chunks = 0
        vdb_connected = False

        if _vector_store and hasattr(_vector_store, "db") and _vector_store.db:
            vdb_connected = True
            try:
                table_name = getattr(_vector_store, "default_table_name", "technical_docs")
                # Use list_tables() if available, fallback to table_names()
                tables = []
                if hasattr(_vector_store.db, "list_tables"):
                    tables = _vector_store.db.list_tables()
                elif hasattr(_vector_store.db, "table_names"):
                    tables = _vector_store.db.table_names()

                if table_name in tables:
                     tbl = _vector_store.db.open_table(table_name)
                     # Use count_rows() or fallback to len()
                     if hasattr(tbl, "count_rows"):
                         total_chunks = tbl.count_rows()
                     else:
                         total_chunks = len(tbl)
            except Exception as e:
                logger.warning(f"Error reading chunks count: {e}")

        return {
            "documents_indexed": len(documents_db),
            "total_chunks": total_chunks,
            "vector_db_status": "connected" if vdb_connected else "disconnected",
        }
    except Exception as e:
        logger.error(f"Error in system_stats: {e}")
        return {
            "documents_indexed": 0,
            "total_chunks": 0,
            "vector_db_status": "error",
            "error": str(e)
        }




@router.get("/health")
async def system_health() -> Dict[str, Any]:
    """Check connectivity to external services."""
    openrouter_status = "unknown"
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(
                "https://openrouter.ai/api/v1/models",
                headers={"Authorization": f"Bearer {settings.OPENROUTER_API_KEY}"},
            )
            openrouter_status = "connected" if resp.status_code == 200 else f"error ({resp.status_code})"
    except Exception as e:
        openrouter_status = f"unreachable ({e})"

    from src.main import _vector_store
    vdb_status = "connected" if (_vector_store and _vector_store.db) else "disconnected"

    return {
        "openrouter": openrouter_status,
        "vector_database": vdb_status,
        "status": "healthy" if openrouter_status == "connected" and vdb_status == "connected" else "degraded",
    }


@router.get("/events")
async def pipeline_events(limit: int = 10):
    """Return recent pipeline runs for live visualization."""
    runs = pipeline_tracker.get_runs(limit=limit)
    return {"runs": [r.model_dump() for r in runs]}

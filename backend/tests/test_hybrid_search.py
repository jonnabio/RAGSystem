
import asyncio
import os
import shutil
import logging
from src.features.rag.infrastructure.lancedb_store import LanceDBVectorStore
from src.features.documents.domain.entities import Chunk
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_hybrid_search():
    # Setup
    test_db_path = "backend/data/test_vectors_hybrid"
    if os.path.exists(test_db_path):
        shutil.rmtree(test_db_path)

    store = LanceDBVectorStore(test_db_path)
    await store.initialize()

    # Create dummy chunks
    # Chunk 1: "Apple" mentioned
    chunk1 = Chunk(
        id="c1", document_id="d1", chunk_index=0,
        text="The quick brown fox jumps over the lazy dog. Apple.",
        embedding=[0.1]*3072, metadata={"filename": "test1.txt"}
    )
    # Chunk 2: "Banana" mentioned
    chunk2 = Chunk(
        id="c2", document_id="d1", chunk_index=1,
        text="The quick brown fox jumps over the lazy dog. Banana.",
        embedding=[0.2]*3072, metadata={"filename": "test1.txt"}
    )
    # Chunk 3: Both "Apple" and "Banana"
    chunk3 = Chunk(
        id="c3", document_id="d2", chunk_index=0,
        text="Apple and Banana are fruits.",
        embedding=[0.3]*3072, metadata={"filename": "test2.txt"}
    )

    await store.add_chunks([chunk1, chunk2, chunk3])

    # Test 1: Keyword Search for "Apple"
    logger.info("Testing Keyword Search for 'Apple'...")
    results_apple = await store.search_keyword("Apple", limit=5)
    found_ids = [r.chunk.id for r in results_apple]
    assert "c1" in found_ids
    assert "c3" in found_ids
    assert "c2" not in found_ids
    logger.info("✅ Keyword Search 'Apple' passed.")

    # Test 2: Keyword Search for "Banana"
    logger.info("Testing Keyword Search for 'Banana'...")
    results_banana = await store.search_keyword("Banana", limit=5)
    found_ids = [r.chunk.id for r in results_banana]
    assert "c2" in found_ids
    assert "c3" in found_ids
    assert "c1" not in found_ids
    logger.info("✅ Keyword Search 'Banana' passed.")

    # Test 3: Vector Search (Mock check)
    logger.info("Testing Vector Search...")
    results_vector = await store.search([0.1]*3072, limit=1)
    assert len(results_vector) == 1
    assert results_vector[0].chunk.id == "c1" # Should match closest embedding
    logger.info("✅ Vector Search passed.")

    # Cleanup
    if os.path.exists(test_db_path):
        shutil.rmtree(test_db_path)

    logger.info("🎉 All Hybrid Search tests passed!")

if __name__ == "__main__":
    asyncio.run(test_hybrid_search())

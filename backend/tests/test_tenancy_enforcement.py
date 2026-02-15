
import asyncio
import os
import shutil
import logging
from typing import List, Optional, Dict, Any
from unittest.mock import AsyncMock, MagicMock

from src.features.rag.infrastructure.lancedb_store import LanceDBVectorStore
from src.features.documents.domain.entities import Chunk
from src.features.chat.application.chat_service import ChatService, ChatRequest
from src.features.rag.domain.interfaces import IVectorStore, IEmbeddingService, ILLMClient, SearchResult, Message, LLMResponse

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_store_tenancy_enforcement():
    # Setup
    test_db_path = "backend/data/test_vectors_tenancy"
    if os.path.exists(test_db_path):
        shutil.rmtree(test_db_path)

    store = LanceDBVectorStore(test_db_path)
    await store.initialize()

    # Create chunks with different tenants
    chunk_a1 = Chunk(
        id="c1", document_id="d1", chunk_index=0, tenant_id="TenantA",
        text="Tenant A data one.", embedding=[0.1]*3072, metadata={"filename": "docA.txt"}
    )
    chunk_a2 = Chunk(
        id="c2", document_id="d1", chunk_index=1, tenant_id="TenantA",
        text="Tenant A data two.", embedding=[0.2]*3072, metadata={"filename": "docA.txt"}
    )
    chunk_b1 = Chunk(
        id="c3", document_id="d2", chunk_index=0, tenant_id="TenantB",
        text="Tenant B data one.", embedding=[0.1]*3072, metadata={"filename": "docB.txt"}
    )

    await store.add_chunks([chunk_a1, chunk_a2, chunk_b1])

    # Test 1: Search for TenantA
    logger.info("Testing Vector Search for TenantA...")
    results_a = await store.search([0.1]*3072, limit=5, tenant_id="TenantA")
    ids_a = [r.chunk.id for r in results_a]
    assert "c1" in ids_a
    assert "c2" in ids_a
    assert "c3" not in ids_a
    logger.info("✅ TenantA isolation passed.")

    # Test 2: Search for TenantB
    logger.info("Testing Vector Search for TenantB...")
    results_b = await store.search([0.1]*3072, limit=5, tenant_id="TenantB")
    ids_b = [r.chunk.id for r in results_b]
    assert "c3" in ids_b
    assert "c1" not in ids_b
    assert "c2" not in ids_b
    logger.info("✅ TenantB isolation passed.")

    # Cleanup
    if os.path.exists(test_db_path):
        shutil.rmtree(test_db_path)

async def test_chat_service_propagation():
    logger.info("Testing ChatService tenant propagation...")

    # Mock dependencies
    embedding_service = AsyncMock(spec=IEmbeddingService)
    embedding_service.generate_embedding.return_value = [0.1] * 3072

    vector_store = AsyncMock(spec=IVectorStore)
    vector_store.search.return_value = []
    vector_store.search_keyword.return_value = []

    llm_client = AsyncMock(spec=ILLMClient)
    llm_client.generate.return_value = LLMResponse(
        content="Answer", model="test-model", tokens_used=10, cost=0.0
    )

    chat_service = ChatService(
        embedding_service=embedding_service,
        vector_store=vector_store,
        llm_client=llm_client
    )

    # Test request with specific tenant
    tenant_id = "tenant-xyz"
    request = ChatRequest(query="test query", model="test-model", tenant_id=tenant_id)

    await chat_service.chat(request)

    # Verify calls
    # Check search call
    vector_store.search.assert_called()
    call_args = vector_store.search.call_args
    assert call_args.kwargs.get("tenant_id") == tenant_id, \
        f"Expected tenant_id='{tenant_id}' in search, got {call_args.kwargs.get('tenant_id')}"

    # Check keyword search call
    vector_store.search_keyword.assert_called()
    call_args_kw = vector_store.search_keyword.call_args
    assert call_args_kw.kwargs.get("tenant_id") == tenant_id, \
        f"Expected tenant_id='{tenant_id}' in search_keyword, got {call_args_kw.kwargs.get('tenant_id')}"

    logger.info("✅ ChatService propagation passed.")

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(test_store_tenancy_enforcement())
    loop.run_until_complete(test_chat_service_propagation())
    loop.close()

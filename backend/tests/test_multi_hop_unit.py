
import pytest
from unittest.mock import AsyncMock, MagicMock
from src.features.chat.application.chat_service import ChatService, ChatRequest
from src.features.rag.application.query_decomposition_service import QueryDecompositionService
from src.features.rag.domain.interfaces import SearchResult, Chunk, LLMResponse

async def test_multi_hop_decomposition():
    # Setup Mocks
    mock_embeddings = AsyncMock()
    mock_embeddings.generate_embedding.return_value = [0.1] * 1536

    mock_vector_store = AsyncMock()
    mock_vector_store.search.return_value = []

    mock_llm = AsyncMock()
    mock_llm.generate.return_value = LLMResponse(
        content="Final answer", model="test", tokens_used=10
    )

    mock_decomposer = AsyncMock()
    mock_decomposer.decompose_query.return_value = ["sub-query 1", "sub-query 2"]

    service = ChatService(
        embedding_service=mock_embeddings,
        vector_store=mock_vector_store,
        llm_client=mock_llm,
        query_decomposer=mock_decomposer
    )

    # Mock Data
    chunk1 = Chunk(id="c1", tenant_id="default", document_id="d1", text="Chunk 1", chunk_index=0, metadata={"filename": "doc1.txt"})
    chunk2 = Chunk(id="c2", tenant_id="default", document_id="d1", text="Chunk 2", chunk_index=1, metadata={"filename": "doc1.txt"})

    # IMPORTANT: We need distinct objects for metadata to avoid shared reference issues during mocking if that was the cause
    # But here we explicitly set individual metadata dicts

    result1 = SearchResult(chunk=chunk1, score=0.9, rank=1, metadata={"retrieval_methods": ["vector"]})
    result2 = SearchResult(chunk=chunk2, score=0.8, rank=1, metadata={"retrieval_methods": ["keyword"]})

    service._hybrid_search = AsyncMock(side_effect=[
        ([result1], {"vector_count": 1, "keyword_count": 0}),
        ([result2], {"vector_count": 0, "keyword_count": 1})
    ])

    # Execute
    request = ChatRequest(query="Complex query", model="test-model")
    response = await service.chat(request)

    # Verify
    s1 = next(s for s in response.sources if s["chunk_id"] == "c1")
    s2 = next(s for s in response.sources if s["chunk_id"] == "c2")

    print("\nDEBUG s1 methods:", s1["metadata"].get("retrieval_methods"))
    print("DEBUG s2 methods:", s2["metadata"].get("retrieval_methods"))

    assert "vector" in s1["metadata"]["retrieval_methods"]
    assert "multi-hop" in s1["metadata"]["retrieval_methods"]

    assert "keyword" in s2["metadata"]["retrieval_methods"]
    assert "multi-hop" in s2["metadata"]["retrieval_methods"]

    print("✅ Multi-Hop Test Passed!")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_multi_hop_decomposition())

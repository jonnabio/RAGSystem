"""Chat service - RAG query and response generation."""

from typing import List, Dict, Any, Optional, TYPE_CHECKING
import logging
from datetime import datetime

from src.features.rag.domain.interfaces import (
    Message,
    LLMResponse,
    SearchResult,
    IEmbeddingService,
    IVectorStore,
    ILLMClient
)
from src.features.rag.application.query_decomposition_service import QueryDecompositionService
from src.features.rag.application.router_service import QueryRouter
from pydantic import BaseModel

if TYPE_CHECKING:
    from src.features.rag.application.reranking_service import RerankingService

logger = logging.getLogger(__name__)


class ChatRequest(BaseModel):
    """Chat request from user."""
    query: str
    model: str
    conversation_history: List[Message] = []
    max_context_chunks: int = 5
    temperature: float = 0.7


class PipelineStep(BaseModel):
    """A single step in the RAG pipeline."""
    step: str
    label: str
    duration_ms: float
    details: Optional[Dict[str, Any]] = None


class ChatResponse(BaseModel):
    """Chat response with sources and metadata."""
    answer: str
    model: str
    sources: List[Dict[str, Any]]
    confidence: float
    tokens_used: int
    cost: Optional[float] = None
    retrieval_time_ms: float
    generation_time_ms: float
    pipeline_steps: List[PipelineStep] = []
    debug_info: Optional[Dict[str, Any]] = None


class ChatService:
    """
    RAG-based chat service.

    Handles query embedding, retrieval, context assembly, and response generation.
    """

    def __init__(
        self,
        embedding_service: IEmbeddingService,
        vector_store: IVectorStore,
        llm_client: ILLMClient,
        reranking_service: Optional['RerankingService'] = None,
        router_service: Optional['QueryRouter'] = None,
        query_decomposer: Optional['QueryDecompositionService'] = None
    ):
        """
        Initialize chat service.

        Args:
            embedding_service: Service for generating query embeddings
            vector_store: Vector database for retrieval
            llm_client: LLM client for generation
            reranking_service: Service for reranking (optional)
            router_service: Service for query routing (optional)
            query_decomposer: Service for breaking down complex queries (optional)
        """
        self.embeddings = embedding_service
        self.vector_store = vector_store
        self.llm = llm_client
        self.reranker = reranking_service
        self.router = router_service
        self.decomposer = query_decomposer

    async def chat(self, request: ChatRequest) -> ChatResponse:
        """
        Process chat request and generate response.

        Pipeline:
        1. Embed query
        2. Retrieve relevant chunks (Hybrid/Vector)
        3. Rerank (if enabled)
        4. Assemble context
        5. Generate response
        6. Calculate confidence
        """
        import time

        logger.info(f"Processing chat request: {request.query[:50]}...")
        pipeline_steps: List[PipelineStep] = []

        # Step 1: Embed query
        step_start = time.time()
        retrieval_start = step_start

        query_embedding = await self.embeddings.generate_embedding(request.query)
        embed_time = (time.time() - step_start) * 1000
        pipeline_steps.append(PipelineStep(
            step="embedding", label="Embedding query", duration_ms=round(embed_time, 1)
        ))

        # Step 2: Route query (Phase 4)
        target_index = "technical_docs"
        if self.router:
            step_start = time.time()
            try:
                route_selection = await self.router.route_query(request.query)
                target_index = route_selection.index_name
                route_time = (time.time() - step_start) * 1000
                pipeline_steps.append(PipelineStep(
                    step="routing",
                    label=f"Routing → {target_index.replace('_', ' ').title()}",
                    duration_ms=round(route_time, 1),
                    details={
                        "index": target_index,
                        "reason": route_selection.reason,
                        "confidence": f"{route_selection.confidence:.2%}"
                    }
                ))
            except Exception as e:
                logger.error(f"Routing step failed: {e}")

        # Step 3: Retrieve relevant chunks
        # Step 3: Retrieval (Multi-hop / Decomposition)
        step_start = time.time()
        initial_k = 20 if self.reranker else request.max_context_chunks

        # Check for decomposition
        sub_queries = [request.query]
        if self.decomposer:
            decomp_start = time.time()
            sub_queries = await self.decomposer.decompose_query(request.query)
            if len(sub_queries) > 1:
                pipeline_steps.append(PipelineStep(
                    step="routing", # Re-using routing color for decomposition
                    label=f"Decomposition → {len(sub_queries)} sub-queries",
                    duration_ms=round((time.time() - decomp_start) * 1000, 1),
                    details={"sub_queries": sub_queries}
                ))

        # Prepare embeddings for all queries
        embeddings_map = {request.query: query_embedding}
        if len(sub_queries) > 1:
            for sq in sub_queries:
                if sq not in embeddings_map:
                    # We await sequentially for simplicity, but could be parallelized
                    embeddings_map[sq] = await self.embeddings.generate_embedding(sq)

        # Execute parallel searches
        import asyncio
        search_tasks = []
        for sq in sub_queries:
            search_tasks.append(
                self._hybrid_search(
                    query=sq,
                    query_embedding=embeddings_map[sq],
                    table_name=target_index,
                    limit=initial_k
                )
            )

        results_list = await asyncio.gather(*search_tasks)

        # Deduplicate and merge results
        unique_chunks = {}
        hybrid_stats = {"vector_count": 0, "keyword_count": 0}

        for res_set, stats_set in results_list:
            hybrid_stats["vector_count"] += stats_set.get("vector_count", 0)
            hybrid_stats["keyword_count"] += stats_set.get("keyword_count", 0)

            for r in res_set:
                if r.chunk.id not in unique_chunks:
                    unique_chunks[r.chunk.id] = r
                else:
                    # Keep max score
                    if r.score > unique_chunks[r.chunk.id].score:
                        unique_chunks[r.chunk.id] = r

                    # Merge retrieval methods metadata (e.g. vector, keyword)
                    existing_methods = set(unique_chunks[r.chunk.id].metadata.get("retrieval_methods", []))
                    new_methods = set(r.metadata.get("retrieval_methods", []))
                    unique_chunks[r.chunk.id].metadata["retrieval_methods"] = list(existing_methods | new_methods)

                if len(sub_queries) > 1:
                    methods = unique_chunks[r.chunk.id].metadata.setdefault("retrieval_methods", [])
                    if "multi-hop" not in methods:
                        methods.append("multi-hop")

        search_results = list(unique_chunks.values())
        search_results.sort(key=lambda x: x.score, reverse=True)

        retrieval_step_time = (time.time() - step_start) * 1000
        pipeline_steps.append(PipelineStep(
            step="retrieval",
            label=f"retrieved {len(search_results)} chunks (merged)",
            duration_ms=round(retrieval_step_time, 1),
            details={
                "candidates": len(search_results),
                "vector_hits": hybrid_stats["vector_count"],
                "keyword_hits": hybrid_stats["keyword_count"],
                "sources": len(sub_queries)
            }
        ))

        if not search_results:
            logger.warning("No relevant chunks found for query")
            return self._create_no_results_response(request, (time.time() - retrieval_start) * 1000)

        # Step 3: Rerank
        if self.reranker:
            step_start = time.time()
            logger.info("Reranking results...")
            chunks_to_rerank = [r.chunk for r in search_results]
            reranked_chunks = self.reranker.rerank(
                query=request.query,
                documents=chunks_to_rerank,
                top_k=request.max_context_chunks
            )
            final_results = []
            for i, chunk in enumerate(reranked_chunks, start=1):
                final_results.append(SearchResult(
                    chunk=chunk,
                    score=chunk.metadata.get("reranker_score", 0.99 - (i * 0.01)),
                    rank=i
                ))
            search_results = final_results
            rerank_time = (time.time() - step_start) * 1000
            pipeline_steps.append(PipelineStep(
                step="reranking",
                label=f"Reranking → Top {len(search_results)}",
                duration_ms=round(rerank_time, 1)
            ))
            logger.info(f"Reranking complete. Top {len(search_results)} kept.")

        retrieval_time = (time.time() - retrieval_start) * 1000

        logger.info(f"Retrieved {len(search_results)} relevant chunks")

        # Step 4: Assemble context
        context = self._assemble_context(search_results)

        # Step 5: Generate response
        step_start = time.time()
        generation_start = step_start

        messages = self._build_messages(
            query=request.query,
            context=context,
            conversation_history=request.conversation_history
        )

        llm_response = await self.llm.generate(
            messages=messages,
            model=request.model,
            temperature=request.temperature,
            max_tokens=1000
        )

        generation_time = (time.time() - generation_start) * 1000
        pipeline_steps.append(PipelineStep(
            step="generation",
            label=f"Generating with {request.model.split('/')[-1]}",
            duration_ms=round(generation_time, 1),
            details={"tokens": llm_response.tokens_used}
        ))

        # Step 6: Calculate confidence
        confidence = self._calculate_confidence(search_results, llm_response)

        # Build response
        sources = [
            {
                "chunk_id": result.chunk.id,
                "document_id": result.chunk.document_id,
                "text": result.chunk.text[:200] + "..." if len(result.chunk.text) > 200 else result.chunk.text,
                "score": result.score,
                "rank": result.rank,
                "metadata": {
                    **result.chunk.metadata,
                    "retrieval_methods": result.metadata.get("retrieval_methods", [])
                }
            }
            for result in search_results
        ]

        response = ChatResponse(
            answer=llm_response.content,
            model=request.model,
            sources=sources,
            confidence=confidence,
            tokens_used=llm_response.tokens_used,
            cost=llm_response.cost,
            retrieval_time_ms=retrieval_time,
            generation_time_ms=generation_time,
            pipeline_steps=pipeline_steps,
            debug_info={
                "final_prompt": [m.model_dump() for m in messages],
                "system_prompt": messages[0].content if messages else "",
                "user_query": request.query,
                "context_used": context
            }
        )

        logger.info(
            f"Generated response: {len(llm_response.content)} chars, "
            f"confidence: {confidence:.2f}, "
            f"retrieval: {retrieval_time:.0f}ms, "
            f"generation: {generation_time:.0f}ms"
        )
        return response

    def _assemble_context(self, search_results: List[SearchResult]) -> str:
        """
        Assemble context from search results.

        Args:
            search_results: Retrieved chunks

        Returns:
            Formatted context string
        """
        context_parts = []

        for result in search_results:
            chunk = result.chunk
            metadata_str = ""

            if "filename" in chunk.metadata:
                metadata_str = f" (from {chunk.metadata['filename']})"

            context_parts.append(
                f"[Document {result.rank}]{metadata_str}:\\n{chunk.text}"
            )

        return "\\n\\n".join(context_parts)

    def _build_messages(
        self,
        query: str,
        context: str,
        conversation_history: List[Message]
    ) -> List[Message]:
        """
        Build message list for LLM.

        Args:
            query: User query
            context: Retrieved context
            conversation_history: Previous messages

        Returns:
            List of messages
        """
        messages = []

        # System prompt
        system_prompt = (
            "You are a helpful AI assistant that answers questions based on provided documents. "
            "Use the context below to answer the user's question accurately. "
            "If the answer cannot be found in the context, say so. "
            "Always cite which document your answer comes from.\\n\\n"
            f"CONTEXT:\\n{context}"
        )

        messages.append(Message(role="system", content=system_prompt))

        # Add conversation history (limit to last 5 exchanges)
        if conversation_history:
            messages.extend(conversation_history[-10:])

        # Add current query
        messages.append(Message(role="user", content=query))

        return messages

    def _calculate_confidence(
        self,
        search_results: List[SearchResult],
        llm_response: LLMResponse
    ) -> float:
        """
        Calculate confidence score for the response.

        Based on:
        - Average similarity score of retrieved chunks
        - Number of chunks retrieved
        - LLM finish reason

        Args:
            search_results: Retrieved chunks
            llm_response: LLM response

        Returns:
            Confidence score (0.0 - 1.0)
        """
        if not search_results:
            return 0.0

        # Average similarity score
        avg_score = sum(r.score for r in search_results) / len(search_results)

        # Normalize score (assuming distance metric, lower is better)
        # This may need adjustment based on actual LanceDB scoring
        normalized_score = max(0.0, 1.0 - avg_score)

        # Penalize if we have very few results
        result_count_factor = min(1.0, len(search_results) / 3.0)

        # Penalize if LLM didn't finish properly
        finish_penalty = 1.0
        if llm_response.finish_reason and llm_response.finish_reason != "stop":
            finish_penalty = 0.8

        confidence = normalized_score * result_count_factor * finish_penalty

        return min(1.0, max(0.0, confidence))

    def _create_no_results_response(
        self,
        request: ChatRequest,
        retrieval_time: float
    ) -> ChatResponse:
        """Create response when no relevant documents found."""
        return ChatResponse(
            answer="I cannot answer this question based on the provided documents. Please try rephrasing your question or upload relevant documents.",
            model=request.model,
            sources=[],
            confidence=0.0,
            tokens_used=0,
            cost=0.0,
            retrieval_time_ms=retrieval_time,
            generation_time_ms=0.0
        )

    async def _hybrid_search(
        self,
        query: str,
        query_embedding: List[float],
        table_name: str,
        limit: int
    ) -> tuple[List[SearchResult], Dict[str, Any]]:
        """Execute parallel vector and keyword search and fuse results."""
        import asyncio

        # Run vector and keyword search in parallel
        vector_task = self.vector_store.search(
            query_embedding=query_embedding,
            limit=limit,
            table_name=table_name
        )

        keyword_task = self.vector_store.search_keyword(
            query=query,
            limit=limit,
            table_name=table_name
        )

        vector_results, keyword_results = await asyncio.gather(vector_task, keyword_task)

        logger.info(f"Hybrid retrieval: {len(vector_results)} vector, {len(keyword_results)} keyword results")

        fused_results = self._rrf_fusion(vector_results, keyword_results, limit)

        # Calculate visualization stats
        stats = {
            "vector_count": len(vector_results),
            "keyword_count": len(keyword_results),
            "total_fused": len(fused_results),
            "vector_ids": [r.chunk.id for r in vector_results],
            "keyword_ids": [r.chunk.id for r in keyword_results]
        }

        # Propagate method metadata to results
        for res in fused_results:
            methods = []
            if res.chunk.id in stats["vector_ids"]:
                methods.append("vector")
            if res.chunk.id in stats["keyword_ids"]:
                methods.append("keyword")
            res.metadata["retrieval_methods"] = methods

        return fused_results, stats

    def _rrf_fusion(
        self,
        vector_results: List[SearchResult],
        keyword_results: List[SearchResult],
        limit: int,
        k: int = 60
    ) -> List[SearchResult]:
        """Combines results using Reciprocal Rank Fusion."""
        fused_scores = {}
        chunks_map = {}

        # Process Vector Results
        for rank, result in enumerate(vector_results):
            if result.chunk.id not in chunks_map:
                chunks_map[result.chunk.id] = result.chunk

            # score = 1 / (k + rank)
            # rank is 0-indexed here from enumerate
            fused_scores[result.chunk.id] = fused_scores.get(result.chunk.id, 0.0) + (1.0 / (k + rank + 1))

        # Process Keyword Results
        for rank, result in enumerate(keyword_results):
            if result.chunk.id not in chunks_map:
                chunks_map[result.chunk.id] = result.chunk

            fused_scores[result.chunk.id] = fused_scores.get(result.chunk.id, 0.0) + (1.0 / (k + rank + 1))

        # Sort by fused score
        # x is chunk_id
        sorted_ids = sorted(fused_scores.keys(), key=lambda x: fused_scores[x], reverse=True)

        final_results = []
        for i, chunk_id in enumerate(sorted_ids[:limit], start=1):
            final_results.append(SearchResult(
                chunk=chunks_map[chunk_id],
                score=fused_scores[chunk_id],
                rank=i
            ))

        return final_results

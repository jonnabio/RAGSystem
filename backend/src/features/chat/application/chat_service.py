"""Chat service - RAG query and response generation."""

from typing import List, Dict, Any, Optional
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
from pydantic import BaseModel

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
        reranking_service: Optional['RerankingService'] = None
    ):
        """
        Initialize chat service.

        Args:
            embedding_service: Service for generating query embeddings
            vector_store: Vector database for retrieval
            llm_client: LLM client for generation
            reranking_service: Service for reranking (optional)
        """
        self.embeddings = embedding_service
        self.vector_store = vector_store
        self.llm = llm_client
        self.reranker = reranking_service

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

        # Step 2: Retrieve relevant chunks
        step_start = time.time()
        initial_k = 20 if self.reranker else request.max_context_chunks

        search_results = await self.vector_store.search(
            query_embedding=query_embedding,
            limit=initial_k
        )
        retrieval_step_time = (time.time() - step_start) * 1000
        pipeline_steps.append(PipelineStep(
            step="retrieval", label=f"Retrieving {initial_k} candidates",
            duration_ms=round(retrieval_step_time, 1),
            details={"candidates": len(search_results)}
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
                "metadata": result.chunk.metadata
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
            pipeline_steps=pipeline_steps
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

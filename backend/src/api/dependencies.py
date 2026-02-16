from typing import Optional
import logging
from src.config import settings
from src.features.documents.infrastructure.pdf_processor import PDFProcessor
from src.features.documents.infrastructure.word_processor import WordProcessor
from src.features.documents.application.document_service import DocumentService
from src.features.chat.application.chat_service import ChatService
from src.features.rag.domain.chunking import ChunkingStrategy
from src.features.rag.infrastructure.embedding_service import OpenAIEmbeddingService
from src.features.rag.infrastructure.lancedb_store import LanceDBVectorStore
from src.features.rag.infrastructure.openrouter_client import OpenRouterClient
from src.features.rag.application.router_service import QueryRouter
from src.features.rag.application.query_decomposition_service import QueryDecompositionService
from src.features.documents.application.redaction_service import RedactionService

logger = logging.getLogger(__name__)

# Global services (singleton pattern)
_document_service: Optional[DocumentService] = None
_chat_service: Optional[ChatService] = None
_vector_store: Optional[LanceDBVectorStore] = None
_openrouter_client: Optional[OpenRouterClient] = None


async def get_document_service() -> DocumentService:
    """Get or create document service instance."""
    global _document_service, _vector_store

    if _document_service is None:
        # Initialize vector store
        if _vector_store is None:
            _vector_store = LanceDBVectorStore(settings.VECTOR_DB_PATH)
            await _vector_store.initialize()

        # Initialize services
        pdf_processor = PDFProcessor()
        word_processor = WordProcessor()
        chunking_strategy = ChunkingStrategy(
            chunk_size=settings.CHUNK_SIZE,
            overlap=settings.CHUNK_OVERLAP
        )

        # Use OpenRouter for embeddings (Single Provider)
        embedding_service = OpenAIEmbeddingService(
            api_key=settings.OPENROUTER_API_KEY,
            base_url=settings.OPENROUTER_BASE_URL,
            model=settings.EMBEDDING_MODEL
        )

        # Initialize Redaction Service
        redaction_service = RedactionService()

        _document_service = DocumentService(
            pdf_processor=pdf_processor,
            word_processor=word_processor,
            chunking_strategy=chunking_strategy,
            embedding_service=embedding_service,
            vector_store=_vector_store,
            storage_path=settings.DOCUMENT_STORAGE_PATH,
            redaction_service=redaction_service
        )

    return _document_service


async def get_chat_service() -> ChatService:
    """Get or create chat service instance."""
    global _chat_service, _vector_store, _openrouter_client

    if _chat_service is None:
        # Initialize vector store if needed
        if _vector_store is None:
            _vector_store = LanceDBVectorStore(settings.VECTOR_DB_PATH)
            await _vector_store.initialize()

        # Initialize services
        # Use OpenRouter for embeddings (Single Provider)
        embedding_service = OpenAIEmbeddingService(
            api_key=settings.OPENROUTER_API_KEY,
            base_url=settings.OPENROUTER_BASE_URL,
            model=settings.EMBEDDING_MODEL
        )

        if _openrouter_client is None:
            _openrouter_client = OpenRouterClient(
                api_key=settings.OPENROUTER_API_KEY,
                base_url=settings.OPENROUTER_BASE_URL
            )

        # Initialize Reranking Service
        reranking_service = None
        try:
            from src.features.rag.application.reranking_service import RerankingService
            reranking_service = RerankingService()
        except Exception as e:
            logger.warning(f"Reranking not available: {e}")

        # Initialize Query Router (Phase 4)
        router_service = QueryRouter(llm_client=_openrouter_client)

        # Initialize Query Decomposer (Phase 5)
        decomposition_service = QueryDecompositionService(llm_client=_openrouter_client)

        _chat_service = ChatService(
            embedding_service=embedding_service,
            vector_store=_vector_store,
            llm_client=_openrouter_client,
            reranking_service=reranking_service,
            router_service=router_service,
            query_decomposer=decomposition_service
        )

    return _chat_service

async def get_openrouter_client() -> OpenRouterClient:
    global _openrouter_client
    if _openrouter_client is None:
        _openrouter_client = OpenRouterClient(
            api_key=settings.OPENROUTER_API_KEY,
            base_url=settings.OPENROUTER_BASE_URL
        )
    return _openrouter_client

async def cleanup_services():
    global _openrouter_client
    if _openrouter_client:
        await _openrouter_client.close()

import logging
from typing import List
from sentence_transformers import CrossEncoder
from src.features.documents.domain.entities import Chunk
from src.config import settings

logger = logging.getLogger(__name__)

class RerankingService:
    """
    Service for reranking retrieved documents using a Cross-Encoder model.
    """

    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        """
        Initialize the Reranking Service.

        Args:
            model_name: Hugging Face model ID for the Cross-Encoder.
        """
        self.model_name = model_name
        self._model = None
        logger.info(f"RerankingService initialized with model: {model_name}")

    def _get_model(self):
        """Lazy load the model to avoid overhead on startup if not used."""
        if self._model is None:
            logger.info(f"Loading Cross-Encoder model: {self.model_name}...")
            try:
                self._model = CrossEncoder(self.model_name)
                logger.info("Cross-Encoder model loaded successfully.")
            except Exception as e:
                logger.error(f"Failed to load Cross-Encoder model: {e}")
                raise RuntimeError(f"Could not load reranker model: {e}")
        return self._model

    def rerank(self, query: str, documents: List[Chunk], top_k: int = 5) -> List[Chunk]:
        """
        Rerank a list of documents based on relevance to the query.

        Args:
            query: The user's search query.
            documents: List of retrieved Chunks to rerank.
            top_k: Number of top results to return.

        Returns:
            Top-k chunks sorted by relevance score.
        """
        if not documents:
            return []

        model = self._get_model()

        # Prepare pairs for the Cross-Encoder
        # [('Query', 'Document Text'), ...]
        pairs = [[query, doc.text] for doc in documents]

        # Predict scores
        scores = model.predict(pairs)

        # Attach scores to documents (temporarily, or in metadata)
        # We'll create a list of (score, doc) tuples and sort them
        scored_docs = sorted(
            zip(scores, documents),
            key=lambda x: x[0],
            reverse=True
        )

        # Select top-k
        top_docs = []
        for score, doc in scored_docs[:top_k]:
            # Optional: We could store the reranker score in metadata for debugging
            doc.metadata["reranker_score"] = float(score)
            top_docs.append(doc)

        logger.info(f"Reranked {len(documents)} documents, returning top {top_k}")
        return top_docs

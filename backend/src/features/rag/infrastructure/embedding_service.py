"""OpenAI embedding service implementation."""

from typing import List
import openai
from openai import AsyncOpenAI
import logging

logger = logging.getLogger(__name__)


class OpenAIEmbeddingService:
    """
    OpenAI embedding service using text-embedding-3-large model.

    Implements batch processing and error handling.
    """

    def __init__(self, api_key: str, model: str = "text-embedding-3-large", base_url: str = None):
        """
        Initialize embedding service.

        Args:
            api_key: OpenAI API key (or compatible)
            model: Embedding model name
            base_url: Optional API base URL (e.g. for OpenRouter)
        """
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        self.model = model
        self.max_batch_size = 100  # OpenAI limit

    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for single text.

        Args:
            text: Text to embed

        Returns:
            Embedding vector (3072 dimensions for text-embedding-3-large)

        Raises:
            RuntimeError: If API call fails
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")

        try:
            print(f"DEBUG: Generating embedding for text (len={len(text)}) using model={self.model} base_url={self.client.base_url}")
            response = await self.client.embeddings.create(
                model=self.model,
                input=text.strip()
            )
            print("DEBUG: Embedding received successfully")

            embedding = response.data[0].embedding
            logger.debug(f"Generated embedding with {len(embedding)} dimensions")

            return embedding

        except openai.APIError as e:
            print(f"DEBUG: API Error: {e}")
            logger.error(f"OpenAI API error: {e}")
            raise RuntimeError(f"Failed to generate embedding: {e}")
        except Exception as e:
            print(f"DEBUG: Unexpected Error: {e}")
            logger.error(f"Unexpected error: {e}")
            raise RuntimeError(f"Embedding generation failed: {e}")

    async def generate_embeddings_batch(
        self,
        texts: List[str]
    ) -> List[List[float]]:
        """
        Generate embeddings for multiple texts (batch processing).

        Args:
            texts: List of texts to embed (max 100 at a time)

        Returns:
            List of embedding vectors

        Raises:
            ValueError: If batch size exceeds limit
            RuntimeError: If API call fails
        """
        if not texts:
            return []

        # Clean texts
        cleaned_texts = [t.strip() for t in texts if t and t.strip()]

        if not cleaned_texts:
            raise ValueError("No valid texts to embed")

        if len(cleaned_texts) > self.max_batch_size:
            raise ValueError(
                f"Batch size {len(cleaned_texts)} exceeds maximum {self.max_batch_size}"
            )

        try:
            print(f"DEBUG: Batch embedding request for {len(cleaned_texts)} items using {self.model} at {self.client.base_url}")
            response = await self.client.embeddings.create(
                model=self.model,
                input=cleaned_texts
            )
            print("DEBUG: Batch embedding success")

            embeddings = [item.embedding for item in response.data]
            logger.debug(f"Generated {len(embeddings)} embeddings")

            return embeddings

        except openai.APIError as e:
            print(f"DEBUG: Batch API Error: {e}")
            logger.error(f"OpenAI API error: {e}")
            raise RuntimeError(f"Failed to generate batch embeddings: {e}")
        except Exception as e:
            print(f"DEBUG: Batch Unexpected Error: {e}")
            logger.error(f"Unexpected error: {e}")
            raise RuntimeError(f"Batch embedding generation failed: {e}")

    async def generate_embeddings_large_batch(
        self,
        texts: List[str],
        batch_size: int = 100
    ) -> List[List[float]]:
        """
        Generate embeddings for large batches by chunking.

        Args:
            texts: List of texts (can exceed 100)
            batch_size: Size of each batch

        Returns:
            List of all embeddings
        """
        all_embeddings = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            embeddings = await self.generate_embeddings_batch(batch)
            all_embeddings.extend(embeddings)

            logger.info(f"Processed batch {i//batch_size + 1}, total embeddings: {len(all_embeddings)}")

        return all_embeddings

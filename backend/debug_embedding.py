
import asyncio
import os
from src.config import settings
from src.features.rag.infrastructure.embedding_service import OpenAIEmbeddingService
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)

async def test_embedding():
    print("Testing Embedding Service...")
    print(f"API Key: {settings.OPENROUTER_API_KEY[:5]}... (len={len(settings.OPENROUTER_API_KEY)})")
    print(f"Base URL: {settings.OPENROUTER_BASE_URL}")
    print(f"Model: {settings.EMBEDDING_MODEL}")

    service = OpenAIEmbeddingService(
        api_key=settings.OPENROUTER_API_KEY,
        base_url=settings.OPENROUTER_BASE_URL,
        model=settings.EMBEDDING_MODEL
    )

    text = "This is a test sentence for embedding generation."

    try:
        print("Sending request...")
        embedding = await service.generate_embedding(text)
        print(f"Success! Generated embedding with {len(embedding)} dimensions.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_embedding())

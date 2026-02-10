import asyncio
import logging
from src.main import get_chat_service, startup_event
from src.features.chat.application.chat_service import ChatRequest

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def run_smoke_test():
    """Run a simple smoke test for the RAG pipeline with reranking."""
    print("--- Starting Smoke Test ---")

    # 1. Initialize services
    await startup_event()
    chat_service = await get_chat_service()

    if chat_service.reranker:
        print("✅ RerankingService is enabled.")
    else:
        print("❌ RerankingService is NOT enabled.")
        return

    # 2. Simulate a query
    # We assume some documents are already in the DB from previous runs.
    # If not, this test might return "No results", which is still a valid pipeline execution.
    query = "What is the chunking strategy?"

    print(f"Querying: '{query}'")

    request = ChatRequest(
        query=query,
        model="openai/gpt-3.5-turbo", # Dummy model for logic check
        max_context_chunks=3
    )

    try:
        response = await chat_service.chat(request)
        print("\n--- Response Recieved ---")
        print(f"Answer: {response.answer[:100]}...")
        print(f"Sources: {len(response.sources)}")
        for i, src in enumerate(response.sources):
            print(f"  {i+1}. [Score: {src['score']:.4f}] {src['text'][:50]}...")

        print("\n✅ Smoke Test Passed: Pipeline executed successfully.")

    except Exception as e:
        print(f"\n❌ Smoke Test Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(run_smoke_test())

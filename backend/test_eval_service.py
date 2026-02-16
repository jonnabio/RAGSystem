import asyncio
import os
import sys

# Add src to path
sys.path.append(os.path.abspath("src"))

from src.features.rag.application.evaluation_service import EvaluationService
from src.config import settings

async def test_evaluation_load():
    print(f"Current working directory: {os.getcwd()}")
    try:
        service = EvaluationService()
        print(f"Golden dataset path: {service.golden_dataset_path}")
        if service.golden_dataset_path.exists():
            print("Golden dataset found!")
        else:
            print("Golden dataset still NOT found!")

        # Test initialization of models
        print("Initializing LLM and Embeddings...")
        print(f"LLM: {service.llm.model_name if hasattr(service.llm, 'model_name') else 'N/A'}")

    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_evaluation_load())

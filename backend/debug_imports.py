try:
    import torch
    print(f"✅ torch imported: {torch.__version__}")
except ImportError as e:
    print(f"❌ torch import failed: {e}")

try:
    import sentence_transformers
    print(f"✅ sentence_transformers imported: {sentence_transformers.__version__}")
except ImportError as e:
    print(f"❌ sentence_transformers import failed: {e}")

try:
    from src.features.rag.application.reranking_service import RerankingService
    print("✅ RerankingService imported successfully")
except Exception as e:
    print(f"❌ RerankingService import failed: {e}")

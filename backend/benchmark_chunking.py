
import time
from src.features.rag.domain.chunking import ChunkingStrategy
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)

def benchmark():
    print("Starting Chunking Benchmark...")

    # Create dummy text of ~40k chars
    words = ["word"] * 8000
    text = " ".join(words)
    print(f"Generated text with {len(text)} characters.")

    strategy = ChunkingStrategy(chunk_size=512, overlap=50)

    start_time = time.time()
    print("Chunking...")
    chunks = strategy.chunk_text(text, "test-doc")
    end_time = time.time()

    duration = end_time - start_time
    print(f"Chunking complete.")
    print(f"Chunks created: {len(chunks)}")
    print(f"Time taken: {duration:.4f} seconds")

    if duration > 1.0:
        print("WARNING: Chunking is suspiciously slow!")
    else:
        print("Performance looks OK.")

if __name__ == "__main__":
    benchmark()

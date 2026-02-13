"""End-to-end test using the actual DOCX processing pipeline."""
import sys
import os
import asyncio
import logging

# Setup logging to see everything
logging.basicConfig(level=logging.DEBUG, format='%(name)s - %(levelname)s - %(message)s')
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from src.features.documents.infrastructure.word_processor import WordProcessor
from src.features.rag.domain.chunking import ChunkingStrategy
from src.features.rag.infrastructure.lancedb_store import LanceDBVectorStore
import json

# Step 1: Extract metadata from actual DOCX
wp = WordProcessor()
docx_path = "../stress_test.docx"
if not os.path.exists(docx_path):
    docx_path = "data/documents/"
    # Find the first .docx file
    import glob
    docx_files = glob.glob("data/documents/*.docx")
    if docx_files:
        docx_path = docx_files[0]
    else:
        print("No DOCX files found!")
        sys.exit(1)

print(f"Testing with DOCX: {docx_path}")

metadata = wp.extract_metadata(docx_path)
print(f"\n=== WordProcessor.extract_metadata() ===")
print(f"Keys: {list(metadata.keys())}")
print(f"Full metadata: {json.dumps(metadata, default=str, indent=2)}")

# Check for 'created' field
if 'created' in metadata:
    print(f"\n⚠️ WARNING: 'created' field found in metadata: {metadata['created']}")
else:
    print(f"\n✅ No 'created' field in metadata")

# Step 2: Chunk text with metadata
text = wp.extract_text(docx_path)
chunker = ChunkingStrategy(chunk_size=512, overlap=50)
chunks = chunker.chunk_text(text=text, document_id="test-doc", metadata={**metadata, "filename": "test.docx"})

print(f"\n=== ChunkingStrategy.chunk_text() ===")
print(f"Number of chunks: {len(chunks)}")
if chunks:
    print(f"First chunk metadata keys: {list(chunks[0].metadata.keys())}")
    print(f"First chunk metadata: {json.dumps(chunks[0].metadata, default=str, indent=2)}")
    if 'created' in chunks[0].metadata:
        print(f"\n⚠️ WARNING: 'created' field found in chunk metadata!")
    else:
        print(f"\n✅ No 'created' field in chunk metadata")

# Step 3: Test add_chunks with these REAL chunks (using fake embeddings)
for chunk in chunks[:2]:  # Just test first 2 chunks
    chunk.embedding = [0.1] * 3072

async def test():
    import shutil
    test_dir = "data/vectors_e2e_test"
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)

    store = LanceDBVectorStore(test_dir)
    await store.initialize()
    try:
        await store.add_chunks(chunks[:2])
        print(f"\n✅ add_chunks with real DOCX metadata succeeded!")
    except Exception as e:
        print(f"\n❌ add_chunks with real DOCX metadata FAILED: {e}")
        import traceback
        traceback.print_exc()

asyncio.run(test())

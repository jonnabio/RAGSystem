"""Direct test of LanceDBVectorStore.add_chunks - bypasses uvicorn."""
import sys
import os
import asyncio
import logging

# Setup logging to see everything
logging.basicConfig(level=logging.DEBUG, format='%(name)s - %(levelname)s - %(message)s')

# Ensure correct path
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from src.features.rag.infrastructure.lancedb_store import LanceDBVectorStore
from src.features.documents.domain.entities import Chunk
from datetime import datetime
import inspect

print(f"LanceDBVectorStore loaded from: {inspect.getfile(LanceDBVectorStore)}")
print(f"add_chunks source first line: {inspect.getsource(LanceDBVectorStore.add_chunks).split(chr(10))[0]}")

# Check specific lines for ENTRY_SENTINEL
source = inspect.getsource(LanceDBVectorStore.add_chunks)
if "ENTRY_SENTINEL" in source:
    print("✅ ENTRY_SENTINEL found in source")
else:
    print("❌ ENTRY_SENTINEL NOT found in source!")

# Check _add_data_sync
sync_source = inspect.getsource(LanceDBVectorStore._add_data_sync)
if "_ADD_DATA_SYNC" in sync_source:
    print("✅ _ADD_DATA_SYNC found in source")
else:
    print("❌ _ADD_DATA_SYNC NOT found in sync source!")
    print(f"First 5 lines of _add_data_sync: {sync_source.split(chr(10))[:5]}")

# Check the bytecode
import dis
print("\n=== BYTECODE of add_chunks (first 20 instructions) ===")
instructions = list(dis.get_instructions(LanceDBVectorStore.add_chunks))
for i, instr in enumerate(instructions[:20]):
    print(f"  {instr}")

# Create a test chunk
chunk = Chunk(
    id="test-id",
    document_id="test-doc-id",
    chunk_index=0,
    text="Test chunk text",
    metadata={"created": "should-be-filtered", "filename": "test.docx"},
    embedding=[0.1] * 3072,
    created_at=datetime.utcnow()
)

# Initialize store and try adding
async def test():
    store = LanceDBVectorStore("data/vectors_test")
    await store.initialize()
    try:
        await store.add_chunks([chunk])
        print("✅ add_chunks succeeded!")
    except Exception as e:
        print(f"❌ add_chunks failed: {e}")

asyncio.run(test())

# Skill: Vector Database Operations (LanceDB)

> Procedural knowledge for working with LanceDB vector database including
> table creation, embedding storage, similarity search, and optimization.

---

## Purpose

Effectively use LanceDB for storing and retrieving vector embeddings in the
RAG System with optimal performance and scalability.

---

## Prerequisites

- [ ] Review ADR-005 (LanceDB Vector Storage)
- [ ] Understanding of LanceDB architecture (columnar, disk-based)
- [ ] Familiarity with embedding dimensions (e.g., 3072 for text-embedding-3-large)
- [ ] Knowledge of distance metrics (L2, cosine, dot product)

---

## Procedures

### 1. Database Initialization

```markdown
Step 1: Setup LanceDB connection

- Import lancedb library
- Define database path (local directory)
- Create database connection
- Verify connection successful

Step 2: Create table schema

- Define table name (e.g., "document_chunks")
- Specify vector column (embedding)
- Add metadata columns (document_id, chunk_index, etc.)
- Set vector dimensions

Step 3: Configure indexing

- Choose index type (IVF for large datasets)
- Set number of partitions (for IVF)
- Build index after data load
- Verify index creation

Step 4: Validate setup

- Test write operation
- Test search operation
- Check table stats
- Verify performance
```

### 2. Storing Embeddings

```markdown
Embedding storage workflow:

Step 1: Prepare data batch

- Collect chunk texts
- Generate embeddings (batch)
- Prepare metadata records
- Validate dimensions

Step 2: Structure records
Format: {
"vector": [0.123, 0.456, ...], # embedding
"text": "chunk text",
"document_id": "doc-123",
"chunk_index": 0,
"metadata": {...}
}

Step 3: Insert into table

- Use table.add() for batch insert
- Handle duplicate checks (if needed)
- Commit transaction
- Handle errors gracefully

Step 4: Verify insertion

- Check record count
- Validate a sample record
- Verify embedding dimensions
- Check metadata integrity
```

### 3. Vector Similarity Search

```markdown
Search workflow:

Step 1: Prepare query

- Generate query embedding
- Validate dimensions match
- Set search parameters (limit, filters)

Step 2: Execute search

- Call table.search(query_vector)
- Set limit (k results)
- Apply metadata filters if needed
- Use appropriate distance metric

Step 3: Process results

- Extract vector + metadata
- Calculate similarity scores
- Sort by relevance
- Apply post-filtering

Step 4: Return formatted results

- Include chunk text
- Include metadata
- Include similarity score
- Format for consumption
```

### 4. Filtering and Queries

```markdown
Advanced querying:

Metadata filtering:

- Filter by document_id
- Filter by date range
- Filter by custom metadata
- Combine multiple filters

Examples:

# Search in specific documents

results = table.search(query_embedding)
.where("document_id IN ['doc-1', 'doc-2']")
.limit(5)
.to_list()

# Search with date filter

results = table.search(query_embedding)
.where("created_at > '2026-01-01'")
.limit(10)
.to_list()

# Combined filters

results = table.search(query_embedding)
.where("document_id = 'doc-1' AND chunk_index < 10")
.limit(5)
.to_list()
```

### 5. Index Optimization

```markdown
Optimizing for performance:

Step 1: Create IVF index

- Decide on number of partitions (sqrt(num_rows) typical)
- Create index with table.create_index()
- Wait for index build to complete
- Verify index exists

Step 2: Tune search parameters

- Set nprobes (partitions to search)
- Balance speed vs. accuracy
- Higher nprobes = slower but more accurate

Step 3: Monitor performance

- Track search latency
- Monitor memory usage
- Check index hit rate
- Optimize as needed

Step 4: Rebuild index periodically

- After large data additions
- If performance degrades
- On schema changes
```

---

## Patterns

### Table Creation

```python
import lancedb
import pyarrow as pa

# Connect to database
db = lancedb.connect("./lancedb_data")

# Define schema
schema = pa.schema([
    pa.field("vector", pa.list_(pa.float32(), 3072)),  # embedding dimension
    pa.field("text", pa.string()),
    pa.field("document_id", pa.string()),
    pa.field("chunk_index", pa.int32()),
    pa.field("page_number", pa.int32()),
    pa.field("created_at", pa.timestamp('us')),
    pa.field("metadata", pa.string()),  # JSON string
])

# Create table
table = db.create_table(
    "document_chunks",
    schema=schema,
    mode="overwrite"  # or "create" for new table
)
```

### Batch Insert

```python
from typing import List, Dict
import numpy as np

async def store_embeddings_batch(
    table: lancedb.table.Table,
    chunks: List[Dict],
    embeddings: List[np.ndarray]
):
    # Prepare records
    records = []
    for chunk, embedding in zip(chunks, embeddings):
        records.append({
            "vector": embedding.tolist(),
            "text": chunk["text"],
            "document_id": chunk["document_id"],
            "chunk_index": chunk["chunk_index"],
            "page_number": chunk.get("page_number", 0),
            "created_at": chunk["created_at"],
            "metadata": json.dumps(chunk.get("metadata", {}))
        })

    # Insert batch
    table.add(records)

    return len(records)
```

### Vector Search

```python
from typing import List, Optional

def search_similar_chunks(
    table: lancedb.table.Table,
    query_embedding: np.ndarray,
    k: int = 5,
    document_ids: Optional[List[str]] = None,
    score_threshold: float = 0.7
) -> List[Dict]:
    # Build query
    query = table.search(query_embedding.tolist()).limit(k)

    # Apply filters
    if document_ids:
        filter_expr = f"document_id IN {document_ids}"
        query = query.where(filter_expr)

    # Execute search
    results = query.to_list()

    # Filter by score threshold
    filtered_results = []
    for result in results:
        # LanceDB returns L2 distance, convert to similarity
        # similarity = 1 / (1 + distance)
        distance = result.get("_distance", 0)
        similarity = 1 / (1 + distance)

        if similarity >= score_threshold:
            filtered_results.append({
                "text": result["text"],
                "document_id": result["document_id"],
                "chunk_index": result["chunk_index"],
                "page_number": result["page_number"],
                "similarity": similarity,
                "metadata": json.loads(result["metadata"])
            })

    return filtered_results
```

### Creating IVF Index

```python
def create_search_index(
    table: lancedb.table.Table,
    num_partitions: int = None,
    num_sub_vectors: int = 16
):
    # Auto-calculate partitions if not provided
    if num_partitions is None:
        row_count = table.count_rows()
        num_partitions = max(1, int(np.sqrt(row_count)))

    # Create IVF-PQ index
    table.create_index(
        metric="L2",  # or "cosine"
        num_partitions=num_partitions,
        num_sub_vectors=num_sub_vectors,
        accelerator="cpu"  # or "cuda" if available
    )

    print(f"Index created with {num_partitions} partitions")
```

### Delete Documents

```python
def delete_document_chunks(
    table: lancedb.table.Table,
    document_id: str
):
    # Delete all chunks for a document
    table.delete(f"document_id = '{document_id}'")

    # Optionally compact table
    table.compact_files()
```

---

## Configuration

### Database Path Structure

```
project_root/
└── lancedb_data/           # Database directory
    └── document_chunks.lance/  # Table directory
        ├── data_*.lance    # Data files
        ├── _indices/       # Index files
        └── _versions/      # Version metadata
```

### Performance Tuning

```python
# Small dataset (<10K vectors)
INDEX_TYPE = None  # No index needed
SEARCH_NPROBES = None

# Medium dataset (10K-100K vectors)
INDEX_TYPE = "IVF"
NUM_PARTITIONS = 100
SEARCH_NPROBES = 10  # Search 10 partitions

# Large dataset (>100K vectors)
INDEX_TYPE = "IVF_PQ"
NUM_PARTITIONS = 256
NUM_SUB_VECTORS = 16  # Compression
SEARCH_NPROBES = 20
```

### Memory Management

```python
# For large datasets, use batch processing
BATCH_SIZE = 1000  # Insert in batches

# Limit search results
MAX_SEARCH_RESULTS = 100

# Enable table compaction periodically
if table.count_rows() > 10000:
    table.compact_files()  # Optimize storage
```

---

## Quality Checks

### After Database Setup

- [ ] **Connection**
  - [ ] Database path created
  - [ ] Connection successful
  - [ ] Table created
  - [ ] Schema correct

- [ ] **Data Integrity**
  - [ ] Embeddings stored correctly
  - [ ] Metadata preserved
  - [ ] No data loss
  - [ ] Dimensions consistent

- [ ] **Search Quality**
  - [ ] Returns relevant results
  - [ ] Scores make sense
  - [ ] Filters work correctly
  - [ ] Performance acceptable

- [ ] **Indexing**
  - [ ] Index created
  - [ ] Search uses index
  - [ ] Performance improved
  - [ ] Accuracy maintained

---

## Troubleshooting

### Slow Search Performance

**Symptoms**: Search takes >1 second

**Diagnosis**:

1. Check if index exists: `table.list_indices()`
2. Check table size: `table.count_rows()`
3. Profile search query
4. Monitor CPU/memory usage

**Solutions**:

- Create IVF index if >10K vectors
- Increase nprobes (slower but more accurate)
- Add metadata filters to narrow search
- Consider upgrading hardware

### High Memory Usage

**Symptoms**: Memory grows over time

**Diagnosis**:

1. Check table file size
2. Monitor Python memory usage
3. Review batch sizes

**Solutions**:

- Compact table files: `table.compact_files()`
- Reduce batch size for inserts
- Clear old data periodically
- Use compression (IVF-PQ index)

### Inaccurate Search Results

**Symptoms**: Retrieved chunks not relevant

**Diagnosis**:

1. Verify embedding model consistency
2. Check distance metric (L2 vs. cosine)
3. Review nprobes setting
4. Inspect query embeddings

**Solutions**:

- Use same embedding model for query and docs
- Try different distance metric
- Increase nprobes for better recall
- Normalize embeddings if using cosine
- Re-index if data changed significantly

---

## Best Practices

### 1. Distance Metrics

```markdown
Use L2 (Euclidean) when:

- Embeddings are normalized
- Magnitude matters
- Default for most embedding models

Use Cosine when:

- Only direction matters (not magnitude)
- Embeddings vary in scale
- Explicitly recommended by embedding model

Use Dot Product when:

- Model outputs are calibrated
- Explicitly optimized for dot product
```

### 2. Indexing Strategy

```markdown
No index:

- < 10K vectors
- Fast enough without index
- Saves memory

IVF:

- 10K - 1M vectors
- Good balance of speed/accuracy
- Moderate memory usage

IVF-PQ:

- > 1M vectors
- Compressed storage
- Slight accuracy tradeoff
```

### 3. Metadata Design

```markdown
Store as structured data:
✅ document_id (for filtering)
✅ chunk_index (for ordering)
✅ created_at (for time-based queries)
✅ page_number (for citations)

Store as JSON string:
✅ Custom metadata (flexible schema)
✅ Document properties (author, title, etc.)
✅ Chunk-specific data (headers, tags)
```

### 4. Batch Operations

```markdown
Always batch inserts:

- Insert 100-1000 records at a time
- Reduces overhead
- Better performance

Batch searches when possible:

- Submit multiple queries together
- Amortize connection costs
- Better throughput
```

---

## Testing

### Unit Tests

```python
import pytest
import numpy as np

def test_store_and_retrieve():
    db = lancedb.connect(":memory:")  # In-memory for tests
    table = db.create_table("test_table", schema=test_schema)

    # Insert test embedding
    test_embedding = np.random.rand(3072).astype(np.float32)
    table.add([{
        "vector": test_embedding.tolist(),
        "text": "test chunk",
        "document_id": "test-doc",
        "chunk_index": 0
    }])

    # Search
    results = table.search(test_embedding.tolist()).limit(1).to_list()

    assert len(results) == 1
    assert results[0]["text"] == "test chunk"
    assert results[0]["document_id"] == "test-doc"

def test_metadata_filtering():
    # ... setup table ...

    results = table.search(query_embedding) \
        .where("document_id = 'doc-1'") \
        .limit(5) \
        .to_list()

    assert all(r["document_id"] == "doc-1" for r in results)
```

---

## Migration Considerations

### Backup Strategy

```python
import shutil

# Backup database directory
def backup_database(db_path: str, backup_path: str):
    shutil.copytree(db_path, backup_path)

# Restore from backup
def restore_database(backup_path: str, db_path: str):
    shutil.rmtree(db_path)
    shutil.copytree(backup_path, db_path)
```

### Schema Evolution

```python
# Add new column to existing table
def add_column_to_table(table: lancedb.table.Table):
    # LanceDB doesn't support ALTER TABLE
    # Need to recreate table with new schema

    # 1. Export existing data
    old_data = table.to_pandas()

    # 2. Add new column
    old_data['new_column'] = default_value

    # 3. Create new table with updated schema
    new_table = db.create_table("document_chunks_v2", old_data, mode="overwrite")

    # 4. Rename tables (manual step)
```

---

## Common Pitfalls

1. **Dimension mismatch** - Query embedding has different dimensions than stored
2. **Wrong distance metric** - Using L2 when cosine is appropriate (or vice versa)
3. **No index on large dataset** - >10K vectors without index causes slowness
4. **Filter after search** - Apply filters in WHERE clause, not after results
5. **Not normalizing embeddings** - Required for cosine similarity
6. **Too many partitions** - IVF with too many partitions wastes memory
7. **Ignoring compaction** - Table files grow indefinitely
8. **Schema changes** - LanceDB doesn't support ALTER, need migration

---

## Invocation

```markdown
"Apply the vector database operations skill from .ace/skills/vector-database-lancedb.md
for [table creation | embedding storage | similarity search | indexing].
Follow LanceDB best practices and optimize for the RAG System use case."
```

---

_Skill Version: 1.0 - LanceDB Specific_

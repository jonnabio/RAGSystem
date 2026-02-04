# ADR-005: LanceDB for Local Vector Storage

> **Status:** Accepted  
> **Date:** 2026-02-02  
> **Supersedes:** None  
> **Related:** ADR-002, ADR-003

---

## Context

The RAG system requires a vector database to:

- Store document embeddings (3072-dimensional vectors from OpenAI)
- Perform semantic similarity search
- Support metadata filtering
- Scale to thousands of documents initially

Requirements from DISCUSS phase:

- **Local deployment** (Phase 1) - no cloud dependencies
- **Low operational overhead** - no server management
- **Fast similarity search** - sub-second query times
- **Persistence** - data survives restarts
- **Future cloud migration** - shouldn't block Phase 3

---

## Decision

We will use **LanceDB** as the vector database for the RAG system.

### Key Characteristics

- **Serverless**: Embedded database, runs in-process
- **Disk-based**: Persistent storage on local filesystem
- **Fast**: Uses Lance columnar format optimized for vectors
- **Simple**: No server to manage, just a directory path
- **Python-native**: Excellent Python integration

### Storage Architecture

```
data/
└── vectors/
    ├── documents.lance/      # Main document vectors
    │   ├── data/
    │   └── _indices/
    └── metadata.db           # Optional: SQLite for complex queries
```

---

## Alternatives Considered

### Alternative 1: Pinecone

**Approach**: Managed cloud vector database

- **Pros:**
  - Production-ready, highly scalable
  - Excellent performance
  - Managed service (no ops)
  - Great documentation

- **Cons:**
  - ❌ **Cloud dependency** (violates Phase 1 requirement)
  - Monthly costs ($70+/month minimum)
  - Data stored in cloud
  - Network latency for queries

- **Why Rejected:** Phase 1 requires local deployment

### Alternative 2: ChromaDB

**Approach**: Open-source embedded vector database

- **Pros:**
  - Open-source, active community
  - Good documentation
  - Local and server modes
  - Python-first design

- **Cons:**
  - More complex setup (persistent storage configuration)
  - Heavier dependencies
  - Slower than LanceDB for large datasets
  - Less mature Lance format

- **Why Rejected:** LanceDB offers better performance with simpler setup

### Alternative 3: Weaviate

**Approach**: Open-source cloud-native vector database

- **Pros:**
  - Feature-rich (hybrid search, modules)
  - Good scaling characteristics
  - GraphQL API
  - Multi-tenancy support

- **Cons:**
  - Requires Docker orchestration
  - Overkill for local deployment
  - Complex configuration
  - Higher resource usage

- **Why Rejected:** Too heavy for Phase 1 local deployment

### Alternative 4: FAISS + Custom Persistence

**Approach**: FAISS for search, custom code for persistence

- **Pros:**
  - Extremely fast (Meta's battle-tested library)
  - Maximum control
  - Minimal dependencies

- **Cons:**
  - Manual persistence implementation
  - No built-in metadata storage
  - Lower-level API
  - More code to maintain

- **Why Rejected:** LanceDB wraps FAISS-like performance with persistence

### Alternative 5: PostgreSQL with pgvector

**Approach**: Use PostgreSQL extension for vectors

- **Pros:**
  - Familiar SQL interface
  - Mature database ecosystem
  - ACID transactions
  - Rich query capabilities

- **Cons:**
  - Slower than specialized vector DBs
  - Requires PostgreSQL server
  - Not optimized for high-dimensional vectors
  - More ops overhead

- **Why Rejected:** Performance and operational overhead

---

## Consequences

### Positive

- ✅ **Zero Infrastructure**: No server to deploy/manage
- ✅ **Local Data**: All data stays on local filesystem
- ✅ **Fast Development**: Simple API, quick setup
- ✅ **Good Performance**: Columnar format optimized for vectors
- ✅ **Python-Native**: Excellent integration with FastAPI
- ✅ **Persistent**: Automatic persistence to disk
- ✅ **Cost**: Completely free, no cloud fees

### Negative

- ❌ **Single-Machine Scaling**: Limited to single machine in Phase 1
- ❌ **Less Mature**: Newer than alternatives (less battle-tested)
- ❌ **Limited Query Features**: Simpler query API than Weaviate
- ❌ **Community Size**: Smaller community than ChromaDB/Pinecone

### Neutral

- ⚪ **Migration Path**: Can migrate to Pinecone/Weaviate later if needed
- ⚪ **Disk Space**: Storage grows with document corpus
- ⚪ **Backup**: Just backup the directory

---

## Implementation Details

### Installation

```bash
pip install lancedb
```

### Schema Definition

```python
# backend/src/features/rag/domain/schemas.py
from pydantic import BaseModel
from typing import List

class DocumentChunk(BaseModel):
    id: str
    document_id: str
    chunk_index: int
    text: str
    embedding: List[float]  # 3072-dimensional from OpenAI
    metadata: dict
    created_at: str
```

### Database Initialization

```python
# backend/src/features/rag/infrastructure/vector_store.py
import lancedb
from pathlib import Path

class LanceDBVectorStore:
    def __init__(self, db_path: str = "data/vectors"):
        self.db_path = Path(db_path)
        self.db_path.mkdir(parents=True, exist_ok=True)
        self.db = lancedb.connect(str(self.db_path))
        self._init_tables()

    def _init_tables(self):
        """Initialize document chunks table"""
        if "documents" not in self.db.table_names():
            # Create empty table with schema
            self.db.create_table(
                "documents",
                schema=DocumentChunk.schema()
            )
```

### Insert Operation

```python
async def add_chunks(self, chunks: List[DocumentChunk]):
    """Add document chunks to vector store"""
    table = self.db.open_table("documents")

    # Convert Pydantic models to dict
    data = [chunk.dict() for chunk in chunks]

    # Insert into LanceDB
    table.add(data)

    # Optional: Create index for faster search
    if len(table) > 1000:
        table.create_index(
            metric="cosine",
            num_partitions=256,
            num_sub_vectors=96
        )
```

### Search Operation

```python
async def search(
    self,
    query_embedding: List[float],
    limit: int = 5,
    filters: dict = None
) -> List[DocumentChunk]:
    """Semantic search for relevant chunks"""
    table = self.db.open_table("documents")

    # Perform vector search
    results = (
        table.search(query_embedding)
        .limit(limit)
        .to_pandas()
    )

    # Convert back to Pydantic models
    return [
        DocumentChunk(**row.to_dict())
        for _, row in results.iterrows()
    ]
```

### Metadata Filtering

```python
async def search_with_filters(
    self,
    query_embedding: List[float],
    document_ids: List[str] = None,
    limit: int = 5
) -> List[DocumentChunk]:
    """Search with metadata filtering"""
    table = self.db.open_table("documents")

    query = table.search(query_embedding).limit(limit)

    # Add filters if provided
    if document_ids:
        query = query.where(f"document_id IN {document_ids}")

    results = query.to_pandas()
    return [DocumentChunk(**row.to_dict()) for _, row in results.iterrows()]
```

---

## Performance Considerations

### Indexing Strategy

- No index needed for < 1,000 chunks (linear search is fast enough)
- Create IVF index at 1,000+ chunks
- Rebuild index periodically as data grows

### Query Optimization

- Use `limit` to control result size
- Pre-filter on metadata when possible
- Cache embeddings for frequent queries

### Storage Optimization

- Compress old documents (rarely accessed)
- Archive deleted documents (don't immediately purge)
- Monitor disk usage

---

## Compliance

### Security (`.ace/standards/security.md`)

- ✅ Local storage - no data leaves machine
- ✅ Filesystem permissions for data directory
- ✅ No credentials needed (local access)
- ✅ Encrypt embedding data if PII present

### Testing Requirements

- Unit tests for CRUD operations
- Integration tests with real LanceDB
- Performance tests for search latency
- Stress tests for large datasets

### Monitoring

- Track database size
- Monitor query latency
- Alert on disk space issues

---

## Migration Path

### Phase 1 → Phase 2 (Multi-User)

- Keep LanceDB, add PostgreSQL for user/session metadata
- Implement file locking for concurrent access

### Phase 2 → Phase 3 (Cloud)

Option A: Migrate to Pinecone

```python
# Export from LanceDB
chunks = lancedb_store.export_all()

# Import to Pinecone
pinecone_store.batch_upsert(chunks)
```

Option B: Keep LanceDB, use cloud storage

- Deploy LanceDB with cloud-attached storage (EBS, Cloud Disk)
- Scale horizontally with load balancer

---

## Risks & Mitigation

| Risk                         | Impact | Mitigation                                     |
| ---------------------------- | ------ | ---------------------------------------------- |
| **Data Corruption**          | High   | Regular backups, checksum verification         |
| **Disk Space Exhaustion**    | Medium | Monitoring, cleanup policies, quotas           |
| **Slow Search at Scale**     | Medium | Indexing strategy, query optimization          |
| **Concurrent Access Issues** | Low    | File locking, single-writer pattern in Phase 1 |
| **Migration Complexity**     | Medium | Export utilities, test migration early         |

---

## Operational Procedures

### Backup

```bash
# Simple: Copy directory
cp -r data/vectors/ backups/vectors-$(date +%Y%m%d)/

# Better: Use rsync
rsync -av data/vectors/ backups/vectors/
```

### Restore

```bash
# Restore from backup
cp -r backups/vectors-20260202/ data/vectors/
```

### Monitoring

```python
# Check database health
db = lancedb.connect("data/vectors")
table = db.open_table("documents")

print(f"Total chunks: {len(table)}")
print(f"Disk size: {get_directory_size('data/vectors')} MB")
```

---

## References

- [LanceDB Documentation](https://lancedb.github.io/lancedb/)
- [Lance Columnar Format](https://github.com/lancedb/lance)
- ADR-002 - Technology Stack
- ADR-003 - Layered Architecture
- `.ace/standards/architecture.md`

---

_ADR-005 - LanceDB for Local Vector Storage - ACE Framework v2.1_

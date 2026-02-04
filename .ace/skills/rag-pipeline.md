# Skill: RAG Pipeline Implementation

> Procedural knowledge for implementing Retrieval-Augmented Generation (RAG)
> systems including document processing, vector storage, and LLM integration.

---

## Purpose

Build robust RAG pipelines that accurately process documents, generate embeddings,
perform semantic search, and integrate with Large Language Models for
context-aware responses.

---

## Prerequisites

- [ ] Review ADR-002 (RAG Technology Stack)
- [ ] Review ADR-004 (OpenRouter Multi-Model LLM)
- [ ] Review ADR-005 (LanceDB Vector Storage)
- [ ] Understand chunking strategy (chunk_size, overlap)
- [ ] Access to OpenRouter API key
- [ ] Familiarity with embedding models

---

## Procedures

### 1. Document Ingestion Pipeline

```markdown
Step 1: Validate input document

- Check file type (PDF, DOCX, etc.)
- Verify file size within limits
- Scan for corruption

Step 2: Extract text content

- Use appropriate processor (PyMuPDF for PDF, python-docx for Word)
- Preserve structure where possible
- Handle special characters/encoding

Step 3: Extract metadata

- Document properties (author, created date, etc.)
- Page count, word count
- Custom metadata fields

Step 4: Clean and normalize text

- Remove excessive whitespace
- Fix encoding issues
- Normalize unicode characters
- Remove artifacts (headers, footers, page numbers)
```

### 2. Text Chunking Strategy

```markdown
When chunking documents:

Step 1: Determine chunk parameters

- Chunk size: 512 tokens (default)
- Overlap: 50 tokens (10% of chunk size)
- Rationale: Balance between context and granularity

Step 2: Split text into chunks

- Use word boundaries (not character splits)
- Maintain sentence integrity where possible
- Apply overlap to preserve context

Step 3: Enrich chunk metadata

- Document ID
- Chunk index (position in document)
- Page number (if applicable)
- Section/heading (if detected)

Step 4: Validate chunks

- Check minimum length (avoid very short chunks)
- Verify no truncated sentences at boundaries
- Ensure overlap is correct
```

### 3. Embedding Generation

```markdown
Embedding workflow:

Step 1: Prepare text for embedding

- Clean whitespace
- Truncate if exceeds model's token limit
- Add any required prefixes (query vs. document)

Step 2: Generate embeddings

- Use batch API for efficiency (up to 100 texts)
- Handle rate limiting with exponential backoff
- Retry on transient errors (3 attempts)

Step 3: Validate embeddings

- Check dimensionality (e.g., 3072 for text-embedding-3-large)
- Verify no null/NaN values
- Normalize if required by vector DB

Step 4: Store with chunks

- Associate embedding with chunk ID
- Store metadata alongside
- Index for fast retrieval
```

### 4. Vector Search & Retrieval

```markdown
When performing RAG retrieval:

Step 1: Process user query

- Clean and normalize query text
- Generate query embedding using same model
- Apply any query-specific transformations

Step 2: Execute similarity search

- Set retrieval count (k=5 default)
- Apply filters if needed (document_ids, date ranges)
- Use appropriate distance metric (cosine, L2, dot product)

Step 3: Rank and filter results

- Re-rank by relevance score if needed
- Apply confidence thresholds (e.g., score > 0.7)
- Remove duplicate/overlapping chunks

Step 4: Assemble context

- Concatenate chunks in logical order
- Include source citations
- Truncate if exceeds LLM context window
- Format for LLM consumption
```

### 5. LLM Integration (RAG Generation)

```markdown
Generating responses with retrieved context:

Step 1: Build prompt structure
System message:
"You are a helpful assistant. Answer based on this context:
[RETRIEVED_CHUNKS]"

User message:
[USER_QUERY]

Step 2: Manage context window

- Calculate token count (context + history + query)
- Truncate oldest conversation turns if needed
- Prioritize recent chunks over old

Step 3: Call LLM API

- Select model (from user preference or default)
- Set temperature (0.7 for balanced creativity)
- Set max_tokens (leave room for response)
- Handle streaming if enabled

Step 4: Process response

- Extract generated text
- Parse citations if structured
- Calculate confidence score (based on chunk relevance)
- Track token usage and cost
```

---

## Patterns

### Document Processing Factory Pattern

```python
class DocumentProcessorFactory:
    @staticmethod
    def get_processor(file_type: str):
        processors = {
            'pdf': PDFProcessor(),
            'docx': WordProcessor(),
            'txt': TextProcessor(),
        }
        return processors.get(file_type)

# Usage
processor = DocumentProcessorFactory.get_processor('pdf')
text = processor.extract_text(file_path)
```

### Batch Embedding Generation

```python
async def generate_embeddings_batch(
    texts: List[str],
    batch_size: int = 100
) -> List[List[float]]:
    embeddings = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        batch_embeddings = await embedding_service.generate(batch)
        embeddings.extend(batch_embeddings)
    return embeddings
```

### Context Assembly with Citations

```python
def assemble_context(
    chunks: List[Chunk],
    max_tokens: int = 2000
) -> str:
    context_parts = []
    current_tokens = 0

    for i, chunk in enumerate(chunks):
        chunk_text = f"[Source {i+1}]: {chunk.text}"
        chunk_tokens = count_tokens(chunk_text)

        if current_tokens + chunk_tokens > max_tokens:
            break

        context_parts.append(chunk_text)
        current_tokens += chunk_tokens

    return "\n\n".join(context_parts)
```

### Confidence Score Calculation

```python
def calculate_confidence(
    search_results: List[SearchResult]
) -> float:
    if not search_results:
        return 0.0

    # Average of top 3 chunk scores
    top_scores = [r.score for r in search_results[:3]]
    return sum(top_scores) / len(top_scores)
```

---

## Configuration Guidelines

### Chunking Parameters

```python
# For technical documents (code, specs)
CHUNK_SIZE = 512  # tokens
OVERLAP = 50      # ~10% overlap

# For narrative documents (articles, books)
CHUNK_SIZE = 1024  # tokens
OVERLAP = 100      # ~10% overlap

# For short-form content (emails, messages)
CHUNK_SIZE = 256  # tokens
OVERLAP = 25      # ~10% overlap
```

### Retrieval Parameters

```python
# Conservative (high precision)
K = 3              # retrieve 3 chunks
SCORE_THRESHOLD = 0.8  # 80% similarity

# Balanced (default)
K = 5              # retrieve 5 chunks
SCORE_THRESHOLD = 0.7  # 70% similarity

# Comprehensive (high recall)
K = 10             # retrieve 10 chunks
SCORE_THRESHOLD = 0.6  # 60% similarity
```

### LLM Parameters

```python
# Factual responses (low creativity)
TEMPERATURE = 0.3
MAX_TOKENS = 512

# Balanced responses (default)
TEMPERATURE = 0.7
MAX_TOKENS = 1024

# Creative responses (high creativity)
TEMPERATURE = 0.9
MAX_TOKENS = 2048
```

---

## Quality Checks

### After Implementing RAG Pipeline

- [ ] **Document Processing**
  - [ ] Handles all specified document types
  - [ ] Extracts text accurately
  - [ ] Preserves important metadata
  - [ ] Handles corrupted files gracefully

- [ ] **Chunking**
  - [ ] Chunks are appropriate size
  - [ ] Overlap is consistent
  - [ ] No orphaned text at document end
  - [ ] Metadata attached to each chunk

- [ ] **Embeddings**
  - [ ] Correct dimensionality
  - [ ] No null/NaN values
  - [ ] Batch processing works
  - [ ] Rate limiting handled

- [ ] **Vector Search**
  - [ ] Returns relevant results
  - [ ] Ranking is correct
  - [ ] Filters work as expected
  - [ ] Performance is acceptable

- [ ] **LLM Integration**
  - [ ] Responses are coherent
  - [ ] Citations are accurate
  - [ ] Context window managed
  - [ ] Token usage tracked

- [ ] **End-to-End**
  - [ ] Upload → Process → Query works
  - [ ] Confidence scores calculated
  - [ ] Error handling comprehensive
  - [ ] Logging adequate

---

## Troubleshooting

### Poor Retrieval Quality

**Symptoms**: Irrelevant chunks returned, low confidence scores

**Diagnosis**:

1. Check embedding model alignment (same for docs and queries)
2. Verify chunk size isn't too small/large
3. Review chunking overlap
4. Inspect vector DB similarity metric

**Solutions**:

- Increase retrieval count (K)
- Adjust score threshold
- Re-chunk with different parameters
- Try different embedding model

### Token Limit Exceeded

**Symptoms**: LLM API errors about context length

**Diagnosis**:

1. Calculate total tokens (context + history + query)
2. Check chunk count and size
3. Review conversation history length

**Solutions**:

- Reduce retrieval count
- Truncate conversation history
- Use model with larger context window
- Implement sliding window for history

### Slow Performance

**Symptoms**: Long query response times

**Diagnosis**:

1. Profile each pipeline stage
2. Check embedding generation time
3. Review vector search performance
4. Monitor LLM API latency

**Solutions**:

- Batch embed queries
- Add vector search indexes
- Use faster embedding model
- Implement caching

---

## Testing Strategy

### Unit Tests

```python
# Test chunking
def test_chunking_with_overlap():
    chunker = ChunkingStrategy(chunk_size=10, overlap=2)
    text = "word " * 25
    chunks = chunker.chunk_text(text, "doc-1")

    assert len(chunks) > 1
    # Verify overlap
    assert chunks[0].text[-10:] in chunks[1].text[:20]

# Test embedding generation
async def test_generate_embeddings():
    service = OpenAIEmbeddingService(api_key="test")
    embeddings = await service.generate_embeddings_batch(["test text"])

    assert len(embeddings) == 1
    assert len(embeddings[0]) == 3072  # text-embedding-3-large
```

### Integration Tests

```python
# Test E2E RAG pipeline
async def test_rag_pipeline_end_to_end():
    # Upload document
    doc = await document_service.process_document("test.pdf", "pdf")
    assert doc.processed

    # Query
    result = await chat_service.chat(
        query="What is the main topic?",
        model="gpt-4"
    )

    assert result["response"]
    assert len(result["sources"]) > 0
    assert result["confidence"] > 0.0
```

---

## Performance Benchmarks

### Target Metrics

| Operation                         | Target   | Acceptable | Poor      |
| --------------------------------- | -------- | ---------- | --------- |
| Document Processing (1MB PDF)     | < 2s     | < 5s       | > 10s     |
| Embedding Generation (100 chunks) | < 3s     | < 8s       | > 15s     |
| Vector Search                     | < 100ms  | < 500ms    | > 1s      |
| LLM Response (no stream)          | < 3s     | < 8s       | > 15s     |
| **Total Query Time**              | **< 5s** | **< 10s**  | **> 15s** |

---

## Common Pitfalls

1. **Inconsistent embedding models** - Query and document MUST use same model
2. **Too small chunks** - Lose context, poor retrieval
3. **Too large chunks** - Exceed token limits, slow processing
4. **No overlap** - Context lost at chunk boundaries
5. **Wrong similarity metric** - Cosine vs. L2 vs. dot product matters
6. **Ignoring token limits** - LLM context window exceeded
7. **No confidence threshold** - Return irrelevant results
8. **Missing error handling** - API failures crash pipeline

---

## Advanced Techniques

### Hybrid Search (Optional for Phase 2)

```markdown
Combine vector search with keyword search:

1. Perform vector similarity search
2. Perform keyword/BM25 search
3. Merge and re-rank results
4. Improves recall for specific terms
```

### Query Expansion (Optional)

```markdown
Expand user query for better retrieval:

1. Generate query variations with LLM
2. Embed all variations
3. Retrieve using multiple embeddings
4. Deduplicate and merge results
```

### Contextual Compression (Optional)

```markdown
Compress retrieved context to fit window:

1. Retrieve more chunks than needed (k=10)
2. Use LLM to extract only relevant sentences
3. Reconstruct compressed context
4. Send to final LLM
```

---

## Invocation

```markdown
"Apply the RAG pipeline implementation skill from .ace/skills/rag-pipeline.md
for [document processing | chunking | retrieval | generation]. Follow best
practices for embeddings and vector search."
```

---

_Skill Version: 1.0 - RAG System Specific_

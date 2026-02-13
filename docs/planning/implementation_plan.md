# Implementation Plan - Advanced RAG Features

**Status**: Draft
**Role**: Architect
**Previous Plan**: UX Improvements (Completed)

## Objective

Upgrade the RAG system to detailed industry standards by implementing Hybrid Retrieval, Multi-hop RAG capabilities, and Production-grade concerns (Tenancy, Redaction, Invalidation).

---

## 1. Hybrid Retrieval & Reranking

**Problem**: Current retrieval relies solely on Dense Vector Search, which can miss exact keyword matches (e.g., specific error codes, acronyms) that don't satisfy semantic similarity.
**Solution**: specific **Hybrid Search** using `BM25` (Sparse) + `Embeddings` (Dense) with Reciprocal Rank Fusion (RRF).

### Tasks

- [ ] **Data Layer**:
  - [ ] Verify `LanceDB` FTS (Full-Text Search) index configuration in `LanceDBVectorStore`.
  - [ ] Implement `search_sparse` method using LanceDB's FTS.
- [ ] **Application Layer (`ChatService`)**:
  - [ ] Update `search_workflow` to execute both `vector_search` and `keyword_search` in parallel.
  - [ ] Implement **Reciprocal Rank Fusion (RRF)** algorithm to combine result lists.
  - [ ] Pass the unified list to the existing `RerankingService`.

---

## 2. Multi-Hop RAG (Query Decomposition)

**Problem**: Complex questions (e.g., "Compare the retry logic in the Chat Service vs the Document Service") require information from distinct disparate sources. Single-step retrieval often fails here.
**Solution**: Implement **Query Decomposition** to break complex user queries into sub-questions.

### Tasks

- [ ] **New Service**: `QueryDecompositionService`
  - [ ] Create prompt to split complex queries into atomic sub-questions.
  - [ ] Use `ILLMClient` to process the decomposition.
- [ ] **Workflow Update**:
  - [ ] Update `ChatService` to detect complexity (using `RouterService`).
  - [ ] If complex:
    - [ ] Execute `decompose(query) -> [q1, q2]`.
    - [ ] Retrieve documents for `q1` and `q2` independently.
    - [ ] Deduplicate and Rerank combined chunks.
    - [ ] Synthesize final answer.

---

## 3. Production Concerns (Security & Invalidation)

**Problem**: The system currently treats all data as a single bucket (no tenancy), has no PII protection, and allows duplicate ingestion.
**Solution**: Add Tenancy enforcement, PII scrubbing, and Content Hashing.

### Tasks

- [ ] **Tenancy**:
  - [ ] Update `Document` and `Chunk` entities to include `tenant_id`.
  - [ ] Update `LanceDBVectorStore` to enforce `tenant_id` filter on every query.
  - [ ] Update `DocumentService` to require `tenant_id` on ingestion.
- [ ] **Redaction**:
  - [ ] Create `RedactionService` (Regex-based initially) for PII (Emails, API Keys, Phones).
  - [ ] Inject `RedactionService` into `DocumentService` pipeline _before_ embedding.
- [ ] **Invalidation Strategies**:
  - [ ] Implement `content_hash` calculation (SHA256) on file upload.
  - [ ] Check for existing hash before processing.
  - [ ] Implementing "Upsert" logic: if exists, delete old chunks -> ingest new.

---

## 4. Evaluation & Quality

**Problem**: New complexity requires regression testing.
**Solution**: Expand `ragas` evaluation to cover multi-hop scenarios.

### Tasks

- [ ] Add "Comparison" and "Multi-fact" questions to `golden_dataset.json`.
- [ ] Run `EvaluationService.run_batch_evaluation` after Hybrid & Multi-hop implementation.

---

## Execution Constraints

- **Regression Guards**: Ensure existing simple queries still work with low latency.
- **Dependencies**: Use existing `LanceDB` capabilities; avoid adding `ElasticSearch` or `Pinecone` unless strictly necessary.

# RAG System Architecture Overview

This document provides a detailed architectural explanation of the **jonnabio/RAGSystem**, serving as a reference for agents, developers, and stakeholders.

## 1. System Overview

The **RAG (Retrieval-Augmented Generation) System** is designed to enhance Large Language Model (LLM) responses by retrieving relevant information from a curated knowledge base of uploaded documents (PDFs, DOCX). This "grounding" process reduces hallucinations and ensures answers are based on specific, trusted data.

### Core Philosophy

- **Ingestion**: Convert unstructured documents into searchable vector representations, handling PII redaction and duplicate detection.
- **Retrieval**: Find the most semantically relevant text chunks for a user query using Hybrid Search (Vector + Keyword) and Multi-Hop reasoning.
- **Augmentation**: Provide the retrieved chunks to the LLM as context.
- **Generation**: The LLM synthesizes an answer based _only_ on the provided context.

---

## 2. Agents (Functional Services)

In this specific implementation, "Agents" refer to the specialized functional services that autonomously handle distinct parts of the pipeline. They are orchestrated by the `pipeline_tracker` in `backend/src/shared/pipeline_events.py`.

### A. The Ingestion Agent (`DocumentService`)

- **Code Location**: `backend/src/features/documents/application/document_service.py`
- **Class**: `DocumentService`
- **Role**: Librarian & Processor
- **Responsibility**: Takes raw files, validates them, chunks the text, generates embeddings, and indexes them into the vector database.
- **New Capabilities**:
  - **Content Hashing**: Calculates SHA-256 hash of files to prevent duplicate uploads.
  - **PII Redaction**: Uses `RedactionService` to automatically mask sensitive information (Emails, Phone Numbers, SSN, Credit Cards) before storage.
  - **Tenancy**: Tags all documents and chunks with a `tenant_id` for data isolation.

### B. The Retrieval & Generation Agent (`ChatService`)

- **Code Location**: `backend/src/features/chat/application/chat_service.py`
- **Class**: `ChatService`
- **Role**: Researcher & Responder
- **Responsibility**: Interprets user queries, finds relevant information, and crafts the final response.
- **Advanced Retrieval Strategies**:
  - **Hybrid Search**: Combines **Vector Search** (semantic meaning) with **Keyword Search** (BM25 exact match) using Reciprocal Rank Fusion (RRF).
  - **Multi-Hop Retrieval**: Decomposes complex queries into sub-queries (via `QueryDecompositionService`) to find information scattered across multiple documents.
  - **Deep Visualization**: Returns detailed metadata (`retrieval_methods`) to the frontend, allowing users to see exactly how each piece of information was found (Vector, Keyword, or Multi-Hop).

### C. The External Communication Agent (`OpenRouterClient`)

- **Code Location**: `backend/src/features/rag/infrastructure/openrouter_client.py`
- **Class**: `OpenRouterClient`
- **Role**: LLM Gateway
- **Responsibility**: Manages all communication with external LLM providers (via OpenRouter), handling API keys, headers, and response parsing.

---

## 3. Data Privacy & Security (New)

The system now enforces strict data privacy and isolation protocols:

1.  **Multi-Tenancy**:
    - Every `Document` and `Chunk` is tagged with a `tenant_id`.
    - All retrieval and deletion operations in `LanceDBVectorStore` automatically filter by `tenant_id`.
    - This ensures that users can only access their own data, even within a shared vector database.

2.  **PII Redaction**:
    - **Service**: `RedactionService`
    - **Patterns**: Regex-based detection for:
      - Emails
      - Phone Numbers
      - SSNs
      - Credit Card Numbers
    - **Action**: Sensitive text is replaced with `[REDACTED: TYPE]` _before_ embedding generation. This ensures PII never enters the vector space or the LLM context.

---

## 4. The Retrieval Process (Enhanced)

The retrieval process is the heart of the RAG system. It follows a strict pipeline:

### Step 1: Query Decomposition (Multi-Hop)

- **Input**: User Query.
- **Process**: The `QueryDecompositionService` analyzes if the query is complex (e.g., comparing two documents).
- **Output**: If complex, it breaks it down into sub-queries (e.g., "Summarize Doc A" and "Summarize Doc B"). If simple, it keeps it as one.

### Step 2: Hybrid Search (Parallel)

- For each sub-query, the system executes two searches in parallel:
  1.  **Vector Search**: Using OpenAI Embeddings (`text-embedding-3-large`) and Cosine Similarity.
  2.  **Keyword Search**: Using LanceDB's Full-Text Search (FTS).
- **Fusion**: Results are combined using **Reciprocal Rank Fusion (RRF)**, boosting documents found by both methods.

### Step 3: Result Merging & Visualization

- Results from all sub-queries are merged.
- **Metadata Tagging**: Each result is tagged with how it was found (`vector`, `keyword`, `multi-hop`).
- **Frontend**: Displays badges (e.g., `[Vector]`, `[Multi-Hop]`) to give users "Glass Box" visibility into the AI's reasoning.

---

## 5. Vectors: A Deep Dive

### What is a Vector?

In the context of AI and RAG, a **Vector** (or Embedding) is a long list of numbers that represents the _semantic meaning_ of a piece of text.

- **Analogy**: Imagine a library where every book has a coordinate location (X, Y, Z).
  - Books about "Cooking" are at coordinate (10, 5, 2).
  - Books about "Recipes" are at (10, 6, 2) -> _Very close!_
  - Books about "Quantum Physics" are at (90, 80, 50) -> _Far away._

### High-Dimensional Space

- Our system uses `text-embedding-3-large`, which generates vectors with **3,072 dimensions**.
- Instead of just X, Y, Z (3 dimensions), it uses 3,072 different axes to capture nuances like:
  - Topic (Sports vs. Finance)
  - Sentiment (Happy vs. Sad)
  - Tense (Past vs. Future)
  - Entity types (Person vs. Location)

### Why Use Vectors?

Computers cannot understand "meaning" in text directly. They understand numbers. By converting text to vectors, we can mathematically calculate "relatedness." Keyword search looks for exact word matches; Vector search looks for **meaning matches**.

---

## 6. Relevant Terminology

| Term              | Definition                                                                                                                                               |
| :---------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Chunking**      | Splitting a large document into smaller, manageable text blocks. Essential because LLMs have a limit on how much text they can process (Context Window). |
| **Hybrid Search** | Combining Vector Search (semantic) and Keyword Search (exact match) to get the "best of both worlds".                                                    |
| **Multi-Hop**     | The ability to answer questions that require pieces of information from multiple different documents or sections.                                        |
| **Tenancy**       | Isolating data so that User A cannot see User B's documents.                                                                                             |
| **Redaction**     | Masking sensitive information (PII) to protect user privacy.                                                                                             |
| **Vector Store**  | A specialized database (LanceDB) designed to store and efficiently search through millions of high-dimensional vectors.                                  |

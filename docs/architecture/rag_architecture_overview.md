# RAG System Architecture Overview

This document provides a detailed architectural explanation of the **jonnabio/RAGSystem**, serving as a reference for agents, developers, and stakeholders. It is written from the perspective of a Computer Science educator to explain not just _what_ we built, but _why_ we built it that way.

## 1. System Overview

The **RAG (Retrieval-Augmented Generation) System** is designed to enhance Large Language Model (LLM) responses by retrieving relevant information from a curated knowledge base. This "grounding" process reduces hallucinations and ensures answers are based on specific, trusted data.

### Core Philosophy

1.  **Ingestion**: Convert unstructured documents (PDF, DOCX) into searchable vector representations, handling PII redaction and duplicate detection.
2.  **Retrieval**: Find the most semantically relevant text chunks using **Hybrid Search** (Vector + Keyword) and **Multi-Hop reasoning**.
3.  **Augmentation**: Provide the retrieved chunks to the LLM as verified context.
4.  **Generation**: The LLM synthesizes an answer based _only_ on the provided context.
5.  **Observability**: Provide "glass box" transparency into the AI's reasoning via the **Prompt Inspector**.

---

## 2. Agents (Functional Services)

In this implementation, "Agents" are specialized services that autonomously handle distinct parts of the pipeline.

### A. The Ingestion Agent (`DocumentService`)

- **Role**: Librarian & Processor.
- **Responsibility**: Takes raw files, validates them, chunks the text, and indexes them.
- **Key Features**:
  - **Content Hashing**: SHA-256 hashing to prevent duplicate uploads.
  - **PII Redaction**: Automatically masks sensitive info (Emails, SSN) _before_ embedding.
  - **Tenancy**: Tags all data with `tenant_id` for isolation.

### B. The Retrieval & Generation Agent (`ChatService`)

- **Role**: Researcher & Responder.
- **Responsibility**: Interprets queries, executes retrieval strategies, and crafts responses.
- **Key Features**:
  - **Query Decomposition**: Breaks complex questions into sub-queries.
  - **Hybrid Search**: Combines semantic understanding with exact keyword matching.
  - **Prompt Inspection**: Exposes the exact prompt sent to the LLM for debugging.

### C. The External Communication Agent (`OpenRouterClient`)

- **Role**: Gateway.
- **Responsibility**: Manages communication with LLM providers (Llama 3, GPT-4, etc.) via OpenRouter.

---

## 3. Advanced Retrieval Patterns (Educational)

### A. Hybrid Retrieval and Reranking

In production RAG systems, relying solely on **Vector Search** (embeddings) often fails for specific queries (e.g., searching for a specific product ID like "XJ-900").

- **Vector Search**: Excellent for _concepts_ ("devices for cleaning").
- **Keyword Search (BM25)**: Excellent for _exact matches_ ("XJ-900").

**Our Approach**: We run both searches in parallel and combine them using **Reciprocal Rank Fusion (RRF)**. RRF allows us to merge two different ranked lists without needing to normalize their scores arbitrarily.

- _Theory_: `score = 1 / (k + rank)`. This boosts items that appear near the top of _both_ lists.

### B. Multi-Index and Routing

Not all data should live in one big index. We separate concerns:

- **Technical Docs Index**: For manuals and guides.
- **Ticket Index**: For support history (future).
- **Metric Index**: For structured data (future).

**Implementation**: Our `QueryRouter` ("Step 2") analyzes the user's intent to decide _which_ index to query.

- _Example_: "How do I reset the router?" → Routes to `technical_docs`.
- _Example_: "How many tickets did we close today?" → Routes to `metrics`.

### C. Multi-Hop Reasoning

Standard RAG fails at "comparison" questions like "Does the XJ-900 have a better battery than the Y-200?". The answer lives in two different documents.
**Implementation**: Our `QueryDecompositionService` detects these complex intents and splits the query:

1.  "What is the battery life of XJ-900?"
2.  "What is the battery life of Y-200?"
    We execute both searches, finding chunks for _both_ devices, and then synthesize the final answer.

---

## 4. Quality and Evaluation

How do we know if our RAG system is actually good? We use the **Ragas** framework methodology to measure four key metrics:

1.  **Faithfulness**: Does the answer come _only_ from the retrieved context? (Prevents hallucinations).
2.  **Answer Relevancy**: Does the answer actually address the user's question?
3.  **Context Precision**: Did we retrieve relevant chunks, or just noise?
4.  **Context Recall**: Did we retrieve _all_ the necessary information?

**Current Status**: We have implemented the `EvaluationService` backend (latent) and an architecture to run these benchmarks on demand.

---

## 5. Production Concerns

Moving from prototype to production requires handling "Day 2" operations:

### A. Index Refresh and Invalidation

When a document is updated, its old chunks become "stale" (outdated).

- **Strategy**: Our system currently uses a "Replace" strategy. When a document is re-uploaded (same filename), we delete _all_ old chunks associated with that `document_id` before indexing the new ones. This ensures no "ghost" information remains.

### B. Access Control and Tenancy

In a multi-user system, User A must never see User B's documents.

- **Implementation**: Every chunk in LanceDB has a `tenant_id` column.
- **Gap Identification**: While our storage layer supports this, our current `ChatService` does not yet strictly enforce passing the `tenant_id` filter during search. This is a known improvement area for the next sprint.

### C. Redaction

We treat privacy as a first-class citizen. PII is redacted _before_ it ever reaches the embedding model or vector inputs. This "Shift Left" privacy approach ensures that even if the database leaks, personal data is not there.

---

## 6. Observability: The Architect's View

We have introduced a dedicated **Architect's View** in the frontend to provide deep visibility into the system's inner workings.

### A. Pipeline Log

Shows the exact execution path of every request:

- "Routing → Technical Docs (98% confidence)"
- "Retrieval → Found 5 chunks (3 Vector, 2 Keyword)"
- "Generation → Llama 3 (1.2s)"

### B. Prompt Inspector

A critical debugging tool that reveals:

- **System Prompt**: The exact instructions given to the persona.
- **Injected Context**: The raw text chunks retrieved from the database.
- **Full Conversation**: The complete message history sent to the API.

---

## 7. Relevant Terminology

| Term             | Definition                                                                             |
| :--------------- | :------------------------------------------------------------------------------------- |
| **Chunking**     | Splitting large documents into smaller overlapping segments (default 512 tokens).      |
| **Embedding**    | A list of numbers (vector) representing the semantic meaning of text.                  |
| **RRF**          | Reciprocal Rank Fusion - a method to combine results from different search algorithms. |
| **Tenancy**      | Isolating data so users only see what belongs to them.                                 |
| **Vector Store** | A specialized database (LanceDB) for fast similarity search.                           |

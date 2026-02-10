# RAG System Architecture Overview

This document provides a detailed architectural explanation of the **jonnabio/RAGSystem**, serving as a reference for agents, developers, and stakeholders.

## 1. System Overview

The **RAG (Retrieval-Augmented Generation) System** is designed to enhance Large Language Model (LLM) responses by retrieving relevant information from a curated knowledge base of uploaded documents (PDFs, DOCX). This "grounding" process reduces hallucinations and ensures answers are based on specific, trusted data.

### Core Philosophy

- **Ingestion**: Convert unstructured documents into searchable vector representations.
- **Retrieval**: Find the most semantically relevant text chunks for a user query.
- **Augmentation**: Provide the retrieved chunks to the LLM as context.
- **Generation**: The LLM synthesizes an answer based _only_ on the provided context.

---

## 2. Agents (Functional Services)

In this specific implementation, "Agents" refer to the specialized functional services that autonomously handle distinct parts of the pipeline. They are orchestrated by the `pipeline_tracker` in [`backend/src/shared/pipeline_events.py`](file:///c:/Users/jonna/OneDrive/Documentos/Code__Projects_Local/RAGSystem/backend/src/shared/pipeline_events.py).

### A. The Ingestion Agent (`DocumentService`)

- **Code Location**: [`backend/src/features/documents/application/document_service.py`](file:///c:/Users/jonna/OneDrive/Documentos/Code__Projects_Local/RAGSystem/backend/src/features/documents/application/document_service.py)
- **Class**: `DocumentService`
- **Role**: Librarian & Processor
- **Responsibility**: Takes raw files, validates them, chunks the text, generates embeddings, and indexes them into the vector database.
- **Key Methods**:
  - `process_document()`: Orchestrates the parsing, chunking, and embedding workflow.
  - `ChunkingStrategy` (in [`.../rag/domain/chunking.py`](file:///c:/Users/jonna/OneDrive/Documentos/Code__Projects_Local/RAGSystem/backend/src/features/rag/domain/chunking.py)): Smartly splits text into overlapping segments to preserve context.
  - `OpenAIEmbeddingService` (in [`.../rag/infrastructure/embedding_service.py`](file:///c:/Users/jonna/OneDrive/Documentos/Code__Projects_Local/RAGSystem/backend/src/features/rag/infrastructure/embedding_service.py)): Converts text chunks into vector embeddings.

### B. The Retrieval & Generation Agent (`ChatService`)

- **Code Location**: [`backend/src/features/chat/application/chat_service.py`](file:///c:/Users/jonna/OneDrive/Documentos/Code__Projects_Local/RAGSystem/backend/src/features/chat/application/chat_service.py)
- **Class**: `ChatService`
- **Role**: Researcher & Responder
- **Responsibility**: Interprets user queries, finds relevant information, and crafts the final response.
- **Key Methods**:
  - `chat()`: The main entry point for user interaction.
  - `_assemble_context()`: Concatenates retrieved text into a coherent context block.
  - Uses `LanceDBVectorStore` (in [`.../rag/infrastructure/lancedb_store.py`](file:///c:/Users/jonna/OneDrive/Documentos/Code__Projects_Local/RAGSystem/backend/src/features/rag/infrastructure/lancedb_store.py)) for the `search()` operation.

### C. The External Communication Agent (`OpenRouterClient`)

- **Code Location**: [`backend/src/features/rag/infrastructure/openrouter_client.py`](file:///c:/Users/jonna/OneDrive/Documentos/Code__Projects_Local/RAGSystem/backend/src/features/rag/infrastructure/openrouter_client.py)
- **Class**: `OpenRouterClient`
- **Role**: LLM Gateway
- **Responsibility**: Manages all communication with external LLM providers (via OpenRouter), handling API keys, headers, and response parsing.
- **Key Methods**:
  - `generate()`: Sends the formatted prompt and context to the LLM and processes the response.
  - `get_available_models()`: Fetches the list of supported models dynamically.

---

## 3. Chunking & Ingestion Strategy

Before documents can be searched, they must be broken down into smaller pieces. This process is controlled by the `ChunkingStrategy` class and configured in `config.py`.

### A. Configuration Parameters

- **Chunk Size**: `512` words.
  - _Reasoning_: Large enough to contain a complete thought or paragraph, but small enough to fit multiple chunks into the LLM's context window.
- **Overlap**: `50` words.
  - _Reasoning_: Ensures that if a sentence is split at the end of a chunk, the context remains intact in the start of the next chunk. This prevents "loss at the edges" during retrieval.

### B. The "Smart Chunking" Algorithm

The system uses a custom sliding window approach with sentence boundary detection:

1.  **Text Cleaning**: Excessive whitespace is removed to normalize the input.
2.  **Word Splitting**: The text is split into a list of words.
3.  **Sliding Window**:
    - The algorithm takes the first `512` words.
    - **Boundary Adjustment**: It checks the end of this selection for sentence terminators (`.`, `!`, `?`). if a sentence end is found within the last 30% of the chunk, it "snaps" the chunk end to that sentence boundary. This keeps sentences whole.
4.  **Overlap & Move**:
    - The window moves forward, but starts `50` words _before_ the previous chunk ended (unless it snapped to a sentence, in which case it handles overlap relative to that).
    - This creates a continuous chain of overlapping text segments.

### C. Visual Representation of Overlap

```text
[Chunk 1: ... The quick brown fox jumps over the lazy dog. The system is]
                                             [Chunk 2: The system is designed to handle...]
                                             <--- Overlap (50 words) --->
```

---

## 4. The Retrieval Process

The retrieval process is the heart of the RAG system. It follows a strict pipeline:

### Step 1: Query Embedding

- **Input**: User's natural language question (e.g., "What are the safety protocols?").
- **Process**: The question is sent to the **Embedding Model** (`text-embedding-3-large`).
- **Output**: A **Query Vector** (a list of 3,072 floating-point numbers) representing the semantic meaning of the question.

### Step 2: Vector Search

- **Input**: Query Vector.
- **Process**: The **Vector Store** (`LanceDB`) compares the Query Vector against all stored Document Chunk Vectors.
- **Mechanism**: It calculates the **Distance** (likely Cosine Similarity or Euclidean Distance) between vectors.
  - _Closer vectors = More semantically similar text._
- **Output**: The top $N$ (default 5) most similar chunks.

### Step 3: Context Assembly

- **Process**: The text content of the top 5 chunks is retrieved.
- **Formatting**: They are formatted into a single string, often with metadata (e.g., `[Document 1] (filename.pdf): <content>`).

### Step 4: Generation (The "Augmented" Part)

- **Input**: System Prompt + Context Block + User Query.
- **Process**: The LLM is instructed: "Answer the user's question using ONLY the context below."
- **Output**: A natural language answer grounded in the retrieved documents.

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

| Term               | Definition                                                                                                                                                     |
| :----------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Chunking**       | Splitting a large document into smaller, manageable text blocks. Essential because LLMs have a limit on how much text they can process (Context Window).       |
| **Overlap**        | Including a small portion of the previous chunk in the next chunk (e.g., 50 words). Ensures that context isn't lost if a sentence is split between two chunks. |
| **Embedding**      | The process of converting text into a Vector. Also refers to the Vector itself.                                                                                |
| **Vector Store**   | A specialized database (LanceDB) designed to store and efficiently search through millions of high-dimensional vectors.                                        |
| **Context Window** | The maximum amount of text (measured in tokens) an LLM can process at once. RAG is a workaround to "extend" this memory by only retrieving what is needed.     |
| **Hallucination**  | When an LLM confidently generates false information. RAG mitigates this by forcing the model to use provided sources.                                          |
| **LanceDB**        | The specific Vector Database used in this project. It is serverless and stores data on the local file system.                                                  |
| **OpenRouter**     | An API aggregator that allows the system to switch between different LLM providers (OpenAI, Anthropic, Meta, etc.) without changing code.                      |

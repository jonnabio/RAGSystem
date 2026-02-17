# Implementation Plan - Multimodal RAG (Phase 1: Images)

**Status**: Draft
**Role**: Architect
**Date**: 2026-02-16

## 1. Executive Summary

This plan outlines the first phase of transforming the text-only RAG system into a **Multimodal RAG** system, starting with **Images**.

Our strategy is "Incrementing":

1.  **Phase 1 (Current Scope): Image Description & Indexing**. We will extract images from documents, generate detailed descriptions using a Vision-Language Model (VLM), and index these descriptions as text chunks. The original images will be stored and served statically.
2.  **Phase 2 (Future)**: **Multimodal Context**. We will pass the actual image content to the Generation LLM (e.g., GPT-4o) alongside the text context.
3.  **Phase 3 (Future)**: **Multimodal Embeddings**. We will use multimodal embedding models (CLIP/SigLIP) for direct image-to-image or text-to-image retrieval.

**Outcome of Phase 1**: Users can ask questions about charts, diagrams, and photos in their PDFs (e.g., "What does the sales graph show?"), and the system will retrieve the relevant image description and display the image in the UI.

## 2. Architecture Changes

### A. Ingestion Pipeline (`DocumentService`)

**Current State**:

- `PDFProcessor.extract_text()` returns a single string.
- `ChunkingStrategy` splits the string.

**New State**:

- New `ImageProcessor` responsible for handling image data.
- `PDFProcessor` modified to extract both **Text** and **Images**.
- New `CaptioningService` (using OpenRouter/OpenAI) to generate descriptions for extracted images.
- **Data Flow**:
  1.  PDF uploaded.
  2.  Extract text blocks AND images.
  3.  Save images to `backend/data/static/images/{doc_id}_{page}_{index}.png`.
  4.  Send images to VLM -> Get Description (e.g., "A bar chart showing sales growth...").
  5.  Create a `Chunk` for the description with metadata:
      - `type`: "image"
      - `image_path`: "/static/images/..."
      - `page`: page_num
  6.  Embed and store `Chunk` in LanceDB (same as text).

### B. Storage Layer

- **FileSystem**: New directory `backend/data/static/images` to store extracted image files.
- **Vector DB**: No schema changes strictly required if we use `metadata` field, but we will formalize `chunk_type` in metadata.

### C. Retrieval & Generation (`ChatService`)

- **Retrieval**: No changes needed for Phase 1. Searching for "sales graph" will hit the description chunk.
- **Context Assembly**:
  - The `chunk.text` (description) is already added to the context.
  - **Update**: We need to append `[Image Available: /static/images/...]` to the context so the LLM knows there is a visual aid and can reference it in its answer.

### D. Frontend

- **Chat Interface**:
  - When a citation is from an "image" chunk, render the image thumbnail in the "Sources" section or inline.
  - Allow clicking to expand.

## 3. Implementation Steps

### Step 1: Foundation Setup

- Create `backend/data/static/images` directory.
- Configure `FastAPI` to mount/serve the static directory.
- Add `openai` or `httpx` logic to `LLMClient` (or new `VisionClient`) to support Image-to-Text calls (using `gpt-4o-mini` or similar cost-effective VLM).

### Step 2: PDF Image Extraction

- Modify `PDFProcessor` in `backend/src/features/documents/infrastructure/pdf_processor.py`.
- Use `fitz` (PyMuPDF) to iterate image list.
- **Constraint**: Extract only images larger than X dimensions to avoid icons/logos.

### Step 3: Captioning Service

- Create `backend/src/features/rag/application/captioning_service.py`.
- Implement `generate_caption(image_path) -> str`.
- Prompt: "Describe this image in detail for a blind user. Include all text, data points from charts, and visual relationships."

### Step 4: Pipeline Integration

- Modify `DocumentService.process_document`:
  - Integrate extraction and captioning.
  - Inject "Image Chunks" into the list of text chunks before embedding.

### Step 5: Frontend Updates

- Update `ChatInterface` to detect `metadata.image_path`.
- Render `<img>` tag.

## 4. Risks & Mitigations

- **Cost**: Calling GPT-4o for every image in a PDF can be expensive.
  - _Mitigation_: Use `gpt-4o-mini` (cheaper) and filter small images (logos, dividers).
- **Latency**: Ingestion time will increase significantly.
  - _Mitigation_: Parallelize captioning requests. Implement async background processing (already semi-async).
- **Quality**: "Describe this image" might miss specific details user cares about.
  - _Mitigation_: Prompt engineering for the VLM.

## 5. Technical Stack Selection

- **PDF Extraction**: `PyMuPDF` (already installed).
- **VLM**: `google/gemini-flash-1.5-8b` or `openai/gpt-4o-mini` via OpenRouter (Cost/Performance balance).
- **Image Storage**: Local filesystem (simplest for now).

## 6. Verification Plan

1.  **Unit Test**: `test_pdf_image_extraction` - verify images are saved.
2.  **Integration Test**: Process a PDF with a known chart. Verify a chunk exists with `type="image"` and a relevant description.
3.  **E2E**: Ask "What is in the chart?" and verify the answer is correct and source links to the image.

# Implementation Plan - UX Improvements & Debugging

## Goal

Improve the user experience for document uploads by providing visual feedback (progress bar) during the processing phase and handle potential errors more gracefully. Also verify that the OpenRouter fallback for embeddings is working correctly.

## User Review Required

> [!NOTE]
> The progress bar for uploads will be **simulated** (0-90% over time) because standard `fetch` API requests don't provide upload progress events easily without XMLHttpRequest, and the backend processing time is opaque to the frontend until completion. This is a standard UX pattern for this stack.

## Proposed Changes

### Frontend

#### [MODIFY] [documents/page.tsx](file:///c:/Users/jonna/OneDrive/Documentos/Code__Projects_Local/RAGSystem/frontend/app/documents/page.tsx)

- Implement `startProgressSimulation` helper function.
- Update `uploadFile` to use the simulation.
- ensure `uploadProgress` state is reset correctly on error or success.
- Improve error alerting to be more descriptive.

### Backend (Already Implemented)

#### [MODIFY] [src/main.py](file:///c:/Users/jonna/OneDrive/Documentos/Code__Projects_Local/RAGSystem/backend/src/main.py)

- Configured `OpenAIEmbeddingService` to use OpenRouter key/URL if OpenAI key is default/missing.

#### [MODIFY] [src/features/rag/infrastructure/embedding_service.py](file:///c:/Users/jonna/OneDrive/Documentos/Code__Projects_Local/RAGSystem/backend/src/features/rag/infrastructure/embedding_service.py)

- Updated `__init__` to accept `base_url`.
- Added debug logging.

## Verification Plan

### Manual Verification

1. **Upload Test**: Upload the PDF again.
   - **Expectation**: Progress bar fills up to 90% and waits.
   - **Expectation**: Upon completion, jumps to 100% and document appears in list.
   - **Expectation**: Backend logs show "Batch embedding success".
2. **Chat Test**: Ask a question about the document.
   - **Expectation**: System returns an answer with citations (proving embeddings worked).

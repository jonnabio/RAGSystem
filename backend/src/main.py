"""FastAPI main application."""

from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict
import logging
from pathlib import Path
import shutil
import uuid

from src.config import settings
from src.features.documents.domain.entities import Document, DocumentType, DocumentStatus
from src.features.documents.application.document_service import DocumentService
from src.features.chat.application.chat_service import ChatService, ChatRequest, ChatResponse
from src.features.rag.infrastructure.openrouter_client import OpenRouterClient
from src.features.rag.domain.interfaces import Message
from src.api.routers.system import router as system_router
from src.api.routers.feedback import router as feedback_router
from src.api.routers.evaluation import router as evaluation_router
from src.features.rag.application.router_service import QueryRouter
from src.features.rag.application.query_decomposition_service import QueryDecompositionService
from src.features.documents.application.redaction_service import RedactionService
from src.shared.pipeline_events import pipeline_tracker
from src.api.dependencies import get_document_service, get_chat_service, get_openrouter_client, cleanup_services

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(settings.LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="RAG System API",
    description="Retrieval-Augmented Generation chatbot with multi-model LLM support",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(system_router)
app.include_router(feedback_router)
app.include_router(evaluation_router)

# In-memory document storage (Phase 1 - replace with DB in Phase 2)
documents_db:  Dict[str, Document] = {}


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    logger.info("Starting RAG System API...")
    logger.info(f"Vector DB Path: {settings.VECTOR_DB_PATH}")
    logger.info(f"Document Storage: {settings.DOCUMENT_STORAGE_PATH}")

    # Pre-initialize services
    await get_document_service()
    await get_chat_service()

    logger.info("✅ RAG System API ready!")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    await cleanup_services()
    logger.info("RAG System API shutdown complete")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "RAG System API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "operational"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "documents": len(documents_db)}


# ==================== Document Endpoints ====================

@app.post("/api/documents/upload", response_model=Dict)
async def upload_document(
    file: UploadFile = File(...),
    doc_service: DocumentService = Depends(get_document_service),
    tenant_id: str = "default"
):
    """
    Upload and process a document.

    Supports PDF and DOCX files.
    """
    run_id = pipeline_tracker.start_run("ingestion", file.filename or "unknown")
    try:
        # Step 1: Validate file type
        step_id = pipeline_tracker.add_step(run_id, "validation", "Validating file type")
        filename = file.filename
        extension = Path(filename).suffix.lower()

        if extension == ".pdf":
            doc_type = DocumentType.PDF
        elif extension in [".docx", ".doc"]:
            doc_type = DocumentType.DOCX
        else:
            pipeline_tracker.fail_step(run_id, step_id, f"Unsupported: {extension}")
            pipeline_tracker.fail_run(run_id, f"Unsupported file type: {extension}")
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {extension}. Please upload PDF or DOCX files."
            )
        pipeline_tracker.complete_step(run_id, step_id, {"type": str(doc_type), "extension": extension})

        # Step 2: Save file
        step_id = pipeline_tracker.add_step(run_id, "saving", "Saving file to storage")
        file_id = str(uuid.uuid4())
        file_path = Path(settings.DOCUMENT_STORAGE_PATH) / f"{file_id}{extension}"

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        pipeline_tracker.complete_step(run_id, step_id, {"path": str(file_path)})

        logger.info(f"Saved file: {filename} -> {file_path}")

        # Step 2.5: Check for duplicates via Content Hashing
        content_hash = doc_service.calculate_hash(str(file_path))

        # Check matching hash AND tenant_id
        for existing_doc in documents_db.values():
            if existing_doc.tenant_id == tenant_id and existing_doc.content_hash == content_hash:
                logger.info(f"Duplicate document found: {existing_doc.id} (hash: {content_hash})")

                # Cleanup uploaded duplicate
                try:
                    Path(file_path).unlink(missing_ok=True)
                except Exception:
                    pass

                pipeline_tracker.complete_run(run_id, {"status": "duplicate", "original_id": existing_doc.id})

                return {
                    "id": existing_doc.id,
                    "filename": existing_doc.filename,
                    "status": "existing", # Signal frontend it's a duplicate
                    "chunk_count": existing_doc.chunk_count,
                    "size_bytes": existing_doc.size_bytes,
                    "document_type": str(existing_doc.document_type),
                    "uploaded_at": existing_doc.uploaded_at.isoformat(),
                    "metadata": existing_doc.metadata,
                    "pipeline_run_id": run_id,
                    "message": "Document already exists"
                }

        # Step 3: Process document (parsing → chunking → embedding → storing)
        step_id = pipeline_tracker.add_step(run_id, "processing", "Processing document chunks")
        try:
            document = await doc_service.process_document(
                file_path=str(file_path),
                document_type=doc_type,
                original_filename=filename,
                tenant_id=tenant_id,
                content_hash=content_hash
            )
            pipeline_tracker.complete_step(run_id, step_id, {
                "chunks_created": document.chunk_count,
                "size_bytes": document.size_bytes
            })

            # Step 4: Index complete
            step_id = pipeline_tracker.add_step(run_id, "indexing", "Document indexed in vector store")
            documents_db[document.id] = document
            pipeline_tracker.complete_step(run_id, step_id, {"document_id": document.id})

            pipeline_tracker.complete_run(run_id)
            logger.info(f"✅ Document processed: {filename} ({document.chunk_count} chunks)")

            return {
                "id": document.id,
                "filename": document.filename,
                "status": str(document.status),
                "chunk_count": document.chunk_count,
                "size_bytes": document.size_bytes,
                "document_type": str(document.document_type),
                "uploaded_at": document.uploaded_at.isoformat(),
                "metadata": document.metadata,
                "pipeline_run_id": run_id
            }
        except Exception as e:
            logger.error(f"Processing failed for {filename}: {e}")
            pipeline_tracker.fail_step(run_id, step_id, str(e))
            pipeline_tracker.fail_run(run_id, str(e))
            raise HTTPException(status_code=500, detail=f"Document processing failed: {str(e)}")

    except HTTPException:
        raise
    except Exception as e:
        pipeline_tracker.fail_run(run_id, str(e))
        logger.error(f"Error uploading document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/documents", response_model=List[Dict])
async def list_documents(tenant_id: str = "default"):
    """List all uploaded documents for a tenant."""
    return [
        {
            "id": doc.id,
            "filename": doc.filename,
            "status": doc.status,
            "chunk_count": doc.chunk_count,
            "size_bytes": doc.size_bytes,
            "document_type": doc.document_type,
            "uploaded_at": doc.uploaded_at.isoformat(),
            "metadata": doc.metadata
        }
        for doc in documents_db.values()
        if doc.tenant_id == tenant_id
    ]


@app.delete("/api/documents/{document_id}")
async def delete_document(
    document_id: str,
    doc_service: DocumentService = Depends(get_document_service),
    tenant_id: str = "default"
):
    """Delete a document and all its chunks."""
    if document_id not in documents_db:
        raise HTTPException(status_code=404, detail="Document not found")

    try:
        # Delete from vector store
        await doc_service.delete_document(document_id, tenant_id=tenant_id)

        # Remove from memory
        del documents_db[document_id]

        logger.info(f"✅ Document deleted: {document_id}")

        return {"message": "Document deleted successfully"}

    except Exception as e:
        logger.error(f"Error deleting document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Chat Endpoints ====================

@app.post("/api/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    chat_service: ChatService = Depends(get_chat_service)
):
    """
    Process a chat query using RAG.

    Returns answer with sources and confidence score.
    """
    run_id = pipeline_tracker.start_run("query", request.query[:60])
    try:
        logger.info(f"Chat request: {request.query[:50]}... (model: {request.model})")

        # Step 1: Embedding query
        step_id = pipeline_tracker.add_step(run_id, "embedding", f"Embedding query with {settings.EMBEDDING_MODEL}")
        pipeline_tracker.complete_step(run_id, step_id)

        # Step 2: Retrieval
        step_id = pipeline_tracker.add_step(run_id, "retrieval", f"Searching top {request.max_context_chunks} chunks via LanceDB")
        pipeline_tracker.complete_step(run_id, step_id)

        # Step 3: Generation
        step_id = pipeline_tracker.add_step(run_id, "generation", f"Generating response with {request.model}")

        response = await chat_service.chat(request)

        pipeline_tracker.complete_step(run_id, step_id, {
            "model": request.model,
            "tokens_used": response.tokens_used,
            "confidence": response.confidence,
            "sources_count": len(response.sources),
            "retrieval_time_ms": response.retrieval_time_ms,
            "generation_time_ms": response.generation_time_ms
        })

        pipeline_tracker.complete_run(run_id)
        logger.info(f"✅ Response generated: confidence={response.confidence:.2f}")

        return response

    except RuntimeError as e:
        error_msg = str(e)
        pipeline_tracker.fail_run(run_id, error_msg)
        if "429" in error_msg or "rate-limited" in error_msg.lower():
            logger.warning(f"Rate limit hit: {e}")
            raise HTTPException(
                status_code=429,
                detail="The AI model is temporarily rate-limited. Please wait a moment or try a different model."
            )
        logger.error(f"Error processing chat: {e}")
        raise HTTPException(status_code=500, detail=error_msg)
    except Exception as e:
        pipeline_tracker.fail_run(run_id, str(e))
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/models")
async def list_models():
    """Get list of available LLM models from OpenRouter."""
    global _openrouter_client

    client = await get_openrouter_client()

    try:
        models = await client.get_available_models()

        # Filter to show most relevant models
        featured_models = [
            m for m in models
            if any(name in m.get("id", "").lower() for name in [
                "llama", "gpt", "claude", "mistral", "gemini"
            ])
        ]

        return {"models": featured_models[:20]}  # Limit to top 20

    except Exception as e:
        logger.error(f"Error fetching models: {e}")
        # Return default models if API fails
        return {
            "models": [
                {
                    "id": "meta-llama/llama-3-70b-instruct",
                    "name": "Llama 3 70B Instruct",
                    "context_length": 8192,
                    "pricing": {"prompt": "0", "completion": "0"}
                },
                {
                    "id": "openai/gpt-4-turbo",
                    "name": "GPT-4 Turbo",
                    "context_length": 128000,
                    "pricing": {"prompt": "0.01", "completion": "0.03"}
                }
            ]
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.API_RELOAD
    )

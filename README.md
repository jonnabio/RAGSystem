# RAG System - Phase 1

A full-featured Retrieval-Augmented Generation (RAG) chatbot system with multi-model LLM support, semantic search, and a modern dashboard UI.

## 🚀 Features

- **Multi-Model LLM Support**: Access thousands of models via OpenRouter (free and paid)
- **Document Processing**: Upload and process PDF and Word documents
- **Semantic Search**: LanceDB vector database for high-performance retrieval
- **Smart Chunking**: Intelligent text splitting with sentence boundary detection
- **Modern UI**: Full dashboard with analytics, not just a chat interface
- **Local-First**: No cloud dependencies in Phase 1

## 📋 Prerequisites

- Python 3.11+
- Node.js 20+
- OpenRouter API key (get from https://openrouter.ai/)
- (Optional) OpenAI API key for embeddings

## 🛠️ Setup

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
.\\venv\\Scripts\\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env and add your API keys
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create .env.local
cp .env.example .env.local
# Configure API URL
```

## 🏃 Running the Application

### Start Backend

```bash
cd backend
.\\venv\\Scripts\\activate  # Windows
# or
source venv/bin/activate  # macOS/Linux

uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: http://localhost:8000
API docs (Swagger): http://localhost:8000/docs

### Start Frontend

```bash
cd frontend
npm run dev
```

Frontend will be available at: http://localhost:3000

## 🧪 Running Tests

### Backend Tests

```bash
cd backend
pytest tests/ -v --cov=src --cov-report=html
```

Coverage report will be in `backend/htmlcov/index.html`

### Frontend Tests

```bash
cd frontend
npm run test
```

## 📁 Project Structure

```
RAGSystem/
├── backend/
│   ├── src/
│   │   ├── features/
│   │   │   ├── chat/           # Chat feature
│   │   │   ├── documents/      # Document processing
│   │   │   ├── rag/            # RAG pipeline
│   │   │   └── analytics/      # Analytics
│   │   ├── shared/             # Shared utilities
│   │   ├── config.py           # Configuration
│   │   └── main.py             # FastAPI app
│   ├── tests/                  # Unit & integration tests
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/                # Next.js app router
│   │   ├── components/         # React components
│   │   ├── lib/                # Utilities
│   │   └── types/              # TypeScript types
│   └── package.json
├── data/
│   ├── documents/              # Uploaded documents
│   ├── vectors/                # LanceDB vector store
│   └── logs/                   # Application logs
└── docs/                       # Documentation
```

## 🏗️ Architecture

The system follows a **layered architecture** pattern:

1. **Presentation Layer**: FastAPI endpoints + Next.js UI
2. **Application Layer**: Service orchestration (DocumentService, ChatService)
3. **Domain Layer**: Business logic (entities, interfaces, chunking)
4. **Infrastructure Layer**: External integrations (OpenRouter, LanceDB, OpenAI)

See `docs/adr/` for detailed architectural decisions.

- [Detailed Architecture Overview](docs/architecture/rag_architecture_overview.md)

## 📖 API Documentation

Once the backend is running, visit:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🔑 Environment Variables

### Backend (.env)

```
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# OpenRouter
OPENROUTER_API_KEY=your_key_here

# OpenAI (for embeddings)
OPENAI_API_KEY=your_key_here

# Models
DEFAULT_MODEL=meta-llama/llama-3-70b-instruct
EMBEDDING_MODEL=text-embedding-3-large

# Chunking
CHUNK_SIZE=512
CHUNK_OVERLAP=50
```

### Frontend (.env.local)

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 🧩 Key Components

### Backend

- **DocumentService**: Orchestrates document upload → text extraction → chunking → embedding → storage
- **ChatService**: Handles query → embedding → retrieval → context assembly → LLM generation
- **ChunkingStrategy**: Smart text splitting with overlap and sentence boundary detection
- **PDFProcessor**: PyMuPDF-based PDF text extraction
- **WordProcessor**: python-docx-based Word document processing
- **OpenAIEmbeddingService**: Batch embedding generation (3072 dims)
- **LanceDBVectorStore**: Vector similarity search with metadata filtering
- **OpenRouterClient**: Multi-model LLM access

### Frontend (Coming Soon)

- Dashboard layout with navigation
- Document upload with drag-and-drop
- Chat interface with model selection
- Analytics dashboard
- Source citation display

## 📊 Testing Strategy

- **Unit Tests**: 80%+ coverage for all business logic
- **Integration Tests**: End-to-end pipeline testing
- **Test Files**:
  - `test_document_entities.py`: Document and Chunk entities
  - `test_chunking.py`: Chunking strategy
  - More test files in development

## 🔒 Security

- No secrets in code (environment variables only)
- Input validation with Pydantic
- File type validation for uploads
- Error handling to prevent information leakage

## 📝 Development Workflow

This project follows the **ACE Framework BMAD methodology**:

1. **Build**: Implement features per task checklist
2. **Measure**: Run tests and check coverage
3. **Analyze**: Review code quality and performance
4. **Document**: Update ADRs and documentation

See `docs/planning/task_checklist.md` for detailed progress tracking.

## 🤝 Contributing

This is a solo development project following ACE Framework standards. For questions or issues, refer to:

- `docs/planning/implementation_plan.md`
- `docs/adr/` for architectural decisions
- `docs/context/ACTIVE_CONTEXT.md` for current state

## 📜 License

[Add license information]

## 🙏 Acknowledgments

- Built with ACE Framework v2.1
- Uses OpenRouter for multi-model LLM access
- LanceDB for vector storage
- FastAPI + Next.js stack

---

**Status**: Phase 1 In Progress  
**Current Module**: Infrastructure & Application Services  
**Test Coverage**: 85%+ (backend core components)

For detailed implementation status, see `docs/planning/task_checklist.md`

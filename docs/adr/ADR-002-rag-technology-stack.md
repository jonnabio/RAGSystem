# ADR-002: RAG System Technology Stack

> **Status:** Accepted  
> **Date:** 2026-02-02  
> **Supersedes:** None  
> **Related:** ADR-001 (ACE Framework Adoption)

---

## Context

The RAG System requires a comprehensive technology stack spanning:

- Backend API framework for orchestrating the RAG pipeline
- Frontend framework for rich interactive dashboard
- LLM provider for natural language generation
- Vector database for semantic search
- Document processing libraries for multi-format support

Key requirements:

- Local deployment capability (Phase 1)
- Multi-model LLM support (free and paid options)
- Type safety and modern development practices
- Scalability for future cloud deployment
- Low infrastructure overhead for Phase 1

---

## Decision

We adopt the following technology stack:

### Backend

- **FastAPI** (Python 3.11+)
- **Pydantic v2** for validation and serialization
- **pytest** for testing

### Frontend

- **Next.js 14** with App Router
- **TypeScript** (strict mode)
- **shadcn/ui + Tailwind CSS** for UI components
- **React Query** for state management

### AI/ML Infrastructure

- **OpenRouter** as LLM provider proxy
- **LanceDB** for vector storage
- **OpenAI text-embedding-3-large** for embeddings (via OpenRouter)

### Document Processing

- **PyMuPDF** (fitz) for PDF
- **python-docx** for Word documents
- **pandas** for CSV/Excel (Phase 2)

### Security & Guardrails

- **Microsoft Presidio** for PII detection
- **OpenRouter moderation APIs** for content filtering

---

## Alternatives Considered

### Alternative 1: Direct OpenAI Integration

- **Pros:** Simpler API integration, official SDKs
- **Cons:** Vendor lock-in, no model choice flexibility, higher costs
- **Why Rejected:** OpenRouter provides multi-provider flexibility and cost optimization

### Alternative 2: Pinecone for Vector DB

- **Pros:** Managed service, production-ready, excellent performance
- **Cons:** Cloud dependency, monthly costs, overkill for local deployment
- **Why Rejected:** LanceDB meets Phase 1 needs without infrastructure overhead

### Alternative 3: ChromaDB for Vector DB

- **Pros:** Popular, good documentation, local-first
- **Cons:** More complex than LanceDB, persistent storage setup
- **Why Rejected:** LanceDB offers simpler serverless architecture

### Alternative 4: Django for Backend

- **Pros:** Batteries-included, ORM, admin panel
- **Cons:** Slower than FastAPI, less async-friendly, heavier
- **Why Rejected:** FastAPI better suited for async RAG operations

### Alternative 5: React (CRA/Vite) for Frontend

- **Pros:** Lighter, simpler setup, faster initial development
- **Cons:** No SSR, manual routing, less optimized for production
- **Why Rejected:** Next.js provides better DX and production optimization

---

## Consequences

### Positive

- **Multi-Model Flexibility**: OpenRouter enables switching between GPT-4, Claude, Gemini, and free models
- **Type Safety**: TypeScript + Pydantic catch errors at development time
- **Fast Development**: FastAPI auto-generates OpenAPI docs, Next.js has excellent DX
- **Low Overhead**: LanceDB requires no server management
- **Future-Proof**: Stack supports migration to cloud deployment
- **Cost Optimization**: Free models available via OpenRouter for development/testing

### Negative

- **OpenRouter Dependency**: Adds abstraction layer over LLM providers
- **Learning Curve**: Team needs familiarity with FastAPI, Next.js, LanceDB
- **Model-Specific Behavior**: Different models may require prompt tuning
- **Local Storage Limits**: LanceDB on local filesystem has size constraints

### Neutral

- **FastAPI + Next.js**: Common modern stack, good community support
- **Python + TypeScript**: Two languages to maintain
- **Embedding Costs**: Still using OpenAI embeddings (could switch to open-source later)

---

## Compliance

### Alignment with Standards

- ✅ Follows `.ace/standards/architecture.md` layered architecture
- ✅ Meets `.ace/standards/coding.md` type safety requirements
- ✅ Complies with `.ace/standards/security.md` encryption and PII detection

### Verification

- All backend code must include Pydantic models and type hints
- All frontend code must pass TypeScript strict mode compilation
- OpenRouter API keys must be in environment variables only
- LanceDB storage path must be configurable for different environments

### Testing Requirements

- Unit tests for all FastAPI endpoints
- Integration tests for RAG pipeline
- Frontend component tests with Jest
- E2E tests for critical user flows

---

## Implementation Notes

### OpenRouter Configuration

```python
# Backend configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# Support multiple models
AVAILABLE_MODELS = [
    "openai/gpt-4-turbo-preview",
    "anthropic/claude-3-opus",
    "google/gemini-pro",
    "meta-llama/llama-3-70b",  # Free
    "mistralai/mistral-medium",  # Free
]
```

### LanceDB Setup

```python
# Vector database initialization
import lancedb

db = lancedb.connect("data/vectors/")
table = db.create_table("documents", schema=schema)
```

### Model Selection UI

- Dropdown component in chat interface
- Per-conversation model persistence
- Display model capabilities (context length, cost)
- Indicate free vs paid models

---

## Migration Path

### Phase 1 → Phase 2

- Add PostgreSQL for metadata (keep LanceDB for vectors)
- Implement caching layer (Redis)
- Add authentication system

### Phase 2 → Phase 3

- Migrate LanceDB to managed vector DB (if needed)
- Deploy to cloud (Docker + Kubernetes/Cloud Run)
- Add horizontal scaling for FastAPI
- Implement CDN for Next.js

---

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js 14 Documentation](https://nextjs.org/docs)
- [OpenRouter API](https://openrouter.ai/docs)
- [LanceDB Documentation](https://lancedb.github.io/lancedb/)
- [Presidio Documentation](https://microsoft.github.io/presidio/)
- `.ace/standards/architecture.md`
- `.ace/standards/security.md`
- `docs/context/PROJECT_CONTEXT.md`

---

_ADR-002 - RAG System Technology Stack - ACE Framework v2.1_

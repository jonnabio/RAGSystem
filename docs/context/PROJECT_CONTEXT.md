# Project Context: RAG System

> This file captures key decisions and soft requirements that define how we build the system.
> Created during the DISCUSS phase of BMAD methodology.

---

## Project Overview

**Project Name**: AI-Powered RAG Chatbot System  
**Created**: 2026-02-02  
**Current Phase**: PLANNING  
**Architect**: ACE Framework v2.1

---

## Technology Stack Decisions

### Backend Stack

- **Framework**: FastAPI (Python 3.11+)
- **Validation**: Pydantic v2
- **Testing**: pytest
- **Architecture**: Layered (Presentation → Application → Domain → Infrastructure)

### Frontend Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **UI Library**: shadcn/ui + Tailwind CSS
- **State Management**: React Query + Context API
- **Testing**: Jest + React Testing Library

### AI & ML Stack

- **LLM Provider**: OpenRouter
  - **Rationale**: Enables model selection flexibility (free and paid models)
  - **Key Benefit**: Users can choose from multiple providers (OpenAI, Anthropic, Google, etc.)
  - **Implementation**: Model selection dropdown in UI
- **Vector Database**: LanceDB
  - **Rationale**: Local, serverless, fast, no infrastructure overhead
  - **Storage**: Local filesystem
- **Embeddings**: OpenAI text-embedding-3-large (3072 dimensions)
  - **Alternative**: Can add other embedding providers via OpenRouter

### Document Processing

- **PDF**: PyMuPDF (fitz)
- **Word**: python-docx
- **CSV/Excel**: pandas
- **Image (Future)**: pytesseract, PIL
- **Audio/Video (Future)**: whisper-api

### Data Storage

- **Deployment**: Local (filesystem-based)
- **Vector Storage**: LanceDB (local)
- **Document Storage**: Local filesystem
- **Metadata**: SQLite or PostgreSQL (TBD in Phase 1)
- **Configuration**: YAML/JSON files

### Security & Guardrails

- **PII Detection**: Microsoft Presidio
- **Encryption**: At rest (filesystem encryption) and in transit (HTTPS)
- **RBAC**: Simple role-based system (Phase 2)
- **Content Moderation**: OpenRouter moderation APIs

---

## Phase 1 Scope Decisions

### Document Support

- ✅ **Word documents** (.doc, .docx)
- ✅ **PDF files** (.pdf)
- ⏸️ CSV/Excel (Phase 2)
- ⏸️ Images (Phase 2)
- ⏸️ Audio/Video (Phase 3)

### User Interface

- ✅ **Full Dashboard** (not basic chat)
  - Chat interface with conversation history
  - Document management panel
  - Analytics/insights dashboard
  - Model selection interface
  - Confidence score visualization
  - Export functionality

### Data Sources

- ✅ **File Upload** (primary method in Phase 1)
- ⏸️ Cloud connectors (SharePoint, Confluence, etc.) - Phase 3
- ⏸️ REST API integration - Phase 2

### Model Selection

- ✅ **Multi-Model Support** via OpenRouter
  - Free models available (e.g., Llama, Mistral)
  - Paid models available (GPT-4, Claude, Gemini)
  - User-selectable in UI
  - Per-conversation model switching

---

## Deployment Strategy

### Phase 1: Local Development

- **Target**: Single-user local deployment
- **Storage**: Local filesystem
- **Database**: LanceDB (serverless, local)
- **Configuration**: Environment variables + config files
- **No cloud dependencies required**

### Future Phases

- Phase 2: Multi-user local network
- Phase 3: Cloud deployment (AWS/Azure/GCP)
- Phase 4: Hybrid (local + cloud connectors)

---

## Architecture Principles

Following `.ace/standards/architecture.md`:

1. **Layered Architecture**
   - Presentation (Next.js frontend)
   - Application (FastAPI services)
   - Domain (RAG pipeline, business logic)
   - Infrastructure (LanceDB, OpenRouter, file storage)

2. **Feature-Based Organization**
   - `features/chat/`
   - `features/documents/`
   - `features/rag/`
   - `features/guardrails/`
   - `features/analytics/`

3. **Separation of Concerns**
   - Business logic in domain layer
   - External APIs in infrastructure layer
   - No tight coupling between features

---

## Key Design Decisions

### 1. OpenRouter Instead of Direct OpenAI

**Decision**: Use OpenRouter as LLM proxy instead of direct OpenAI integration  
**Rationale**:

- Provides flexibility to switch between models
- Enables cost optimization (free models for testing)
- Future-proofs against vendor lock-in
- Users can choose based on task complexity

**Consequences**:

- Slightly more complex API integration
- Need model selection UI component
- Configuration management for API keys
- Model-specific prompt optimization may be needed

### 2. Local-First Deployment

**Decision**: Design for local deployment first, cloud later  
**Rationale**:

- Faster development iteration
- No cloud costs during development
- Data privacy (local data stays local)
- Easier to transition to cloud later

**Consequences**:

- Must design with future cloud migration in mind
- Storage should be abstraction-ready
- Configuration should support both local and cloud

### 3. Full Dashboard in Phase 1

**Decision**: Build complete dashboard UI from the start  
**Rationale**:

- Better UX from day one
- Enables comprehensive testing
- Demonstrates full capabilities early
- Easier to iterate on complete system

**Consequences**:

- More frontend work in Phase 1
- Longer time to first demo
- Better final product quality

---

## Non-Negotiable Constraints

From `.ace/standards/security.md`:

- ✅ No secrets in code or git
- ✅ Environment variables for API keys
- ✅ Input validation on all user inputs
- ✅ PII detection before storage
- ✅ Encrypted storage of sensitive data

From `.ace/standards/coding.md`:

- ✅ Type hints in all Python code
- ✅ TypeScript strict mode in frontend
- ✅ Unit tests for all business logic
- ✅ Integration tests for API endpoints

From `.ace/standards/architecture.md`:

- ✅ Layered architecture pattern
- ✅ Repository pattern for data access
- ✅ Dependency injection
- ✅ No circular dependencies

---

## Success Criteria

### Phase 1 Completion Criteria

1. ✅ Users can upload Word and PDF documents
2. ✅ Documents are chunked and embedded into LanceDB
3. ✅ Users can chat and receive relevant answers
4. ✅ Users can select different LLM models via OpenRouter
5. ✅ Dashboard displays conversation history
6. ✅ Analytics show confidence scores and insights
7. ✅ All tests passing (unit + integration)
8. ✅ Documentation complete
9. ✅ Walkthrough artifact demonstrates functionality

---

## Open Questions for Future Phases

- [ ] Which cloud provider for Phase 3? (AWS, Azure, GCP)
- [ ] User authentication method? (OAuth, JWT, Basic Auth)
- [ ] Database migration strategy (SQLite → PostgreSQL?)
- [ ] Multi-tenancy requirements?
- [ ] API rate limiting strategy?

---

## References

- **Specification**: `docs/specs/RAGSystem_Specs`
- **Standards**: `.ace/standards/architecture.md`, `.ace/standards/security.md`
- **ADRs**: See `docs/adr/ADR-002-*` through `ADR-006-*`

---

_Last Updated: 2026-02-02 20:11_  
_ACE Framework v2.1 - DISCUSS Phase Complete_

# ADR-003: Layered Architecture Pattern for RAG System

> **Status:** Accepted  
> **Date:** 2026-02-02  
> **Supersedes:** None  
> **Related:** ADR-001, ADR-002

---

## Context

The RAG System is a complex application with multiple concerns:

- Document processing and storage
- Vector embedding and retrieval
- LLM interaction and generation
- User interface and API
- Security and guardrails
- Analytics and monitoring

We need an architectural pattern that:

- Separates concerns clearly
- Enables independent testing of components
- Supports future scaling and cloud migration
- Maintains code organization as features grow
- Enforces dependency direction

Per `.ace/standards/architecture.md`, we must follow the layered architecture principle with dependency inversion.

---

## Decision

We adopt a **Feature-Based Layered Architecture** with 4 layers per feature:

```
┌─────────────────────────────────────────┐
│      Presentation Layer (API/UI)        │
│           (FastAPI Routes)              │
└──────────────────┬──────────────────────┘
                   │ depends on
                   ▼
┌─────────────────────────────────────────┐
│       Application Layer (Services)      │
│     (Use Cases, Orchestration)          │
└──────────────────┬──────────────────────┘
                   │ depends on
                   ▼
┌─────────────────────────────────────────┐
│        Domain Layer (Business Logic)    │
│   (Entities, Value Objects, Rules)      │
└──────────────────┬──────────────────────┘
                   │ interfaces define
                   ▼
┌─────────────────────────────────────────┐
│   Infrastructure Layer (External I/O)   │
│ (Database, OpenRouter, File System)     │
└─────────────────────────────────────────┘
```

### Directory Structure

```
backend/src/
├── features/
│   ├── chat/
│   │   ├── api/              # Controllers (Presentation)
│   │   │   └── routes.py
│   │   ├── application/      # Services (Application)
│   │   │   └── chat_service.py
│   │   ├── domain/           # Business Logic (Domain)
│   │   │   ├── entities.py
│   │   │   └── interfaces.py
│   │   └── infrastructure/   # External I/O (Infrastructure)
│   │       └── repositories.py
│   ├── documents/
│   │   ├── api/
│   │   ├── application/
│   │   ├── domain/
│   │   └── infrastructure/
│   ├── rag/                  # Core RAG pipeline
│   │   ├── application/      # Pipeline orchestration
│   │   ├── domain/
│   │   │   ├── chunking.py
│   │   │   ├── embedding.py
│   │   │   ├── retrieval.py
│   │   │   └── generation.py
│   │   └── infrastructure/
│   │       ├── vector_store.py
│   │       └── llm_client.py
│   ├── guardrails/
│   │   ├── domain/
│   │   │   ├── pii_detector.py
│   │   │   └── content_moderator.py
│   │   └── infrastructure/
│   └── analytics/
├── shared/
│   ├── kernel/               # Shared domain primitives
│   ├── infrastructure/       # Logging, config
│   └── utils/
└── main.py
```

---

## Alternatives Considered

### Alternative 1: Monolithic MVC Pattern

- **Pros:** Simpler, fewer directories, familiar pattern
- **Cons:** Poor separation, hard to test, tight coupling
- **Why Rejected:** Doesn't scale with complexity, violates ACE standards

### Alternative 2: Microservices Architecture

- **Pros:** Independent deployment, technology flexibility
- **Cons:** Overkill for Phase 1, operational complexity, distributed debugging
- **Why Rejected:** Premature for local deployment, can migrate later if needed

### Alternative 3: Hexagonal Architecture (Ports & Adapters)

- **Pros:** Excellent separation, highly testable
- **Cons:** More complex, steeper learning curve, more boilerplate
- **Why Rejected:** Layered architecture achieves similar benefits with less overhead

### Alternative 4: Flat Structure by File Type

- **Pros:** Very simple, quick to start
- **Cons:** No feature isolation, poor scalability, hard to navigate
- **Why Rejected:** Violates ACE standards, will become unmaintainable

---

## Consequences

### Positive

- **Clear Boundaries**: Each layer has explicit responsibilities
- **Testability**: Domain logic can be tested without external dependencies
- **Maintainability**: Changes in one layer don't cascade to others
- **Scalability**: Easy to add new features without affecting existing ones
- **Standards Compliance**: Directly implements `.ace/standards/architecture.md`
- **Team Understanding**: Clear structure helps onboarding

### Negative

- **More Files**: Feature-based structure creates more directories
- **Boilerplate**: Repository/service patterns require interface definitions
- **Learning Curve**: Team must understand layer responsibilities
- **Indirection**: More layers mean more files to navigate

### Neutral

- **Feature-Based**: Cross-cutting changes require touching multiple features
- **Abstraction**: Interfaces make code more abstract but more flexible

---

## Layer Responsibilities

### 1. Presentation Layer (API)

**Purpose**: Handle HTTP requests/responses, route to services

```python
# backend/src/features/chat/api/routes.py
from fastapi import APIRouter, Depends
from ..application.chat_service import ChatService

router = APIRouter()

@router.post("/chat")
async def chat(
    message: str,
    service: ChatService = Depends()
):
    """Handle chat request - Presentation layer only"""
    result = await service.process_message(message)
    return {"response": result}
```

**Rules**:

- ✅ No business logic
- ✅ Validate input (Pydantic models)
- ✅ Map domain objects to DTOs
- ❌ No direct database access
- ❌ No LLM client calls

### 2. Application Layer (Services)

**Purpose**: Orchestrate use cases, coordinate domain and infrastructure

```python
# backend/src/features/chat/application/chat_service.py
from ..domain.interfaces import IVectorStore, ILLMClient
from ..domain.entities import ChatMessage

class ChatService:
    def __init__(
        self,
        vector_store: IVectorStore,
        llm_client: ILLMClient
    ):
        self.vector_store = vector_store
        self.llm_client = llm_client

    async def process_message(self, message: str) -> str:
        """Orchestrate RAG pipeline"""
        # Retrieve context
        context = await self.vector_store.search(message)

        # Generate response
        response = await self.llm_client.generate(
            message, context
        )

        return response
```

**Rules**:

- ✅ Coordinate domain and infrastructure
- ✅ Define use case workflows
- ✅ Handle transactions
- ❌ No HTTP/request handling
- ❌ No direct external API calls

### 3. Domain Layer (Business Logic)

**Purpose**: Define business rules, entities, value objects

```python
# backend/src/features/rag/domain/chunking.py
from typing import List
from pydantic import BaseModel

class Chunk(BaseModel):
    text: str
    metadata: dict
    embedding: List[float] | None = None

class ChunkingStrategy:
    """Domain logic for document chunking"""

    def chunk_document(
        self,
        text: str,
        chunk_size: int = 512,
        overlap: int = 50
    ) -> List[Chunk]:
        """
        Business rule: Chunks must overlap for context
        continuity
        """
        # Pure business logic, no I/O
        ...
```

**Rules**:

- ✅ Pure business logic
- ✅ Define interfaces (protocols)
- ✅ No external dependencies
- ❌ No I/O operations
- ❌ No framework dependencies

### 4. Infrastructure Layer

**Purpose**: Implement external integrations

```python
# backend/src/features/rag/infrastructure/vector_store.py
from ..domain.interfaces import IVectorStore
import lancedb

class LanceDBVectorStore(IVectorStore):
    """Concrete implementation of vector store"""

    def __init__(self, db_path: str):
        self.db = lancedb.connect(db_path)

    async def search(self, query: str) -> List[Chunk]:
        # LanceDB-specific implementation
        ...
```

**Rules**:

- ✅ Implement domain interfaces
- ✅ Handle external I/O
- ✅ Manage connections
- ❌ No business logic
- ❌ No HTTP handling

---

## Dependency Rules

1. **Inward Dependencies Only**
   - Presentation → Application → Domain ← Infrastructure
   - Domain has NO outward dependencies

2. **Interface Segregation**
   - Domain defines interfaces
   - Infrastructure implements them
   - Application depends on interfaces, not implementations

3. **No Circular Dependencies**
   - Enforce with import structure
   - Use dependency injection

---

## Testing Strategy

### Unit Tests

- **Domain Layer**: Test pure business logic, no mocks needed
- **Application Layer**: Mock infrastructure interfaces
- **Infrastructure Layer**: Test external integrations (use test databases)

### Integration Tests

- Test complete feature flows (API → Service → Domain → Infrastructure)
- Use test containers for external dependencies

### E2E Tests

- Test entire RAG pipeline end-to-end
- Real LanceDB, mock OpenRouter (cost control)

---

## Compliance

### Verification Checklist

- [ ] Each feature has 4 layers (api, application, domain, infrastructure)
- [ ] Domain layer has no external dependencies
- [ ] Infrastructure implements domain interfaces
- [ ] No circular imports between features
- [ ] All business logic in domain layer
- [ ] All external I/O in infrastructure layer

### Code Reviews

- Verify layer responsibilities during PR review
- Check dependency direction with import analysis
- Ensure no business logic in presentation layer

---

## Migration Path

### Phase 1 → Phase 2

- Add `shared/kernel/` for cross-feature domain primitives
- Implement event-driven communication between features
- Add caching layer in infrastructure

### Phase 2 → Phase 3 (Microservices)

- Each feature becomes independent service
- Shared kernel becomes published library
- API gateway for routing

---

## References

- `.ace/standards/architecture.md` - Architecture standards
- ADR-002 - Technology stack
- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Domain-Driven Design](https://martinfowler.com/bliki/DomainDrivenDesign.html)

---

_ADR-003 - Layered Architecture Pattern - ACE Framework v2.1_

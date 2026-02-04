# Skills Inventory - RAG System

> Complete list of procedural knowledge skills available for the RAG System project.

---

## Purpose

This document catalogs all skills available in `.ace/skills/` for use during development.
Skills provide step-by-step procedures, patterns, and best practices for specific technical tasks.

---

## Available Skills

### Core Skills (Standard ACE Framework)

#### 1. API Design (`api-design.md`)

**Purpose**: Design and implement RESTful APIs

**Use when**:

- Creating new API endpoints
- Defining request/response formats
- Implementing authentication
- Documenting API specifications

**Key topics**:

- REST conventions (GET, POST, PUT, PATCH, DELETE)
- URL structure and naming
- Response envelopes and error handling
- Status codes and pagination
- Security checklist

---

#### 2. Code Review (`code-review.md`)

**Purpose**: Conduct thorough code reviews

**Use when**:

- Reviewing pull requests
- Ensuring code quality
- Checking for security issues
- Validating architecture adherence

**Key topics**:

- Review checklist
- Common anti-patterns
- Security considerations
- Performance issues
- Testing coverage

---

#### 3. Database Operations (`database-operations.md`)

**Purpose**: Perform safe database operations

**Use when**:

- Creating migrations
- Modifying schema
- Optimizing queries
- Managing indexes

**Key topics**:

- Migration procedures
- Schema change checklist
- Query optimization (EXPLAIN ANALYZE)
- Safe column addition/removal
- Rollback strategies

---

#### 4. Migration Logic (`migration-logic.md`)

**Purpose**: Implement data migrations and transformations

**Use when**:

- Migrating between systems
- Transforming data structures
- Backfilling data
- Version upgrades

**Key topics**:

- Migration planning
- Data validation
- Rollback procedures
- Testing strategies
- Error handling

---

#### 5. Refactoring (`refactoring.md`)

**Purpose**: Safely refactor code to improve quality

**Use when**:

- Improving code structure
- Reducing technical debt
- Extracting common patterns
- Optimizing performance

**Key topics**:

- Refactoring techniques
- Test-driven refactoring
- Extract method/class
- Dependency injection
- Before/after validation

---

#### 6. Root Cause Analysis (`root-cause-analysis.md`)

**Purpose**: Systematically debug and resolve issues

**Use when**:

- Investigating bugs
- Resolving production issues
- Understanding system failures
- Preventing recurrence

**Key topics**:

- 5 Whys technique
- Hypothesis testing
- Evidence collection
- Fix validation
- Post-mortem documentation

---

#### 7. Testing Strategy (`testing-strategy.md`)

**Purpose**: Implement comprehensive testing

**Use when**:

- Writing unit tests
- Creating integration tests
- E2E testing
- Test coverage analysis

**Key topics**:

- Test pyramid
- Unit test patterns
- Integration test setup
- Mocking strategies
- Coverage goals

---

### RAG System Specific Skills

#### 8. RAG Pipeline Implementation (`rag-pipeline.md`) ✨ **NEW**

**Purpose**: Build RAG systems with document processing and LLM integration

**Use when**:

- Implementing document ingestion
- Creating chunking strategies
- Generating embeddings
- Performing vector search
- Integrating with LLMs

**Key topics**:

- Document processing (PDF, DOCX)
- Text chunking with overlap
- Batch embedding generation
- Context assembly with citations
- Confidence score calculation
- Troubleshooting retrieval quality
- Performance benchmarks

**Specific to**: Phase 1 implementation (Modules 2-6)

---

#### 9. UI/UX Implementation (`ui-ux-implementation.md`) ✨ **NEW**

**Purpose**: Build accessible, modern UIs following the design system

**Use when**:

- Implementing components
- Creating pages
- Applying dark blue × Fiserv orange theme
- Ensuring accessibility
- Responsive design

**Key topics**:

- Tailwind CSS configuration
- Component development (Buttons, Cards, Inputs)
- Color system application (navy blues + orange)
- WCAG AA compliance
- Animation and micro-interactions
- Performance optimization
- Debugging UI issues

**Specific to**: Week 3 frontend development

---

#### 10. Vector Database Operations - LanceDB (`vector-database-lancedb.md`) ✨ **NEW**

**Purpose**: Effectively use LanceDB for vector storage and retrieval

**Use when**:

- Setting up vector database
- Storing embeddings
- Performing similarity search
- Creating indexes
- Optimizing performance

**Key topics**:

- Table creation with schema
- Batch embedding insertion
- Vector similarity search (L2, cosine)
- Metadata filtering
- IVF index creation and tuning
- Troubleshooting slow searches
- Memory management
- Backup and migration

**Specific to**: Module 3 (Vector Storage) and Module 5 (RAG Integration)

---

## Skill Usage Guide

### When to Apply a Skill

1. **Identify the task type**: Review the skill purposes above
2. **Read the skill file**: Open `.ace/skills/[skill-name].md`
3. **Follow the procedures**: Step-by-step instructions
4. **Use the patterns**: Code examples and templates
5. **Validate**: Check quality criteria at the end

### Invocation Format

Most skills include an "Invocation" section at the end. Use this format when explicitly requesting skill application:

```markdown
"Apply the [skill name] skill from .ace/skills/[filename].md
for [specific task]. Follow the [relevant section] and ensure
[quality criteria] are met."
```

Example:

```markdown
"Apply the RAG pipeline implementation skill from .ace/skills/rag-pipeline.md
for document chunking. Follow the text chunking strategy and ensure chunks
have proper overlap and metadata."
```

---

## Skill Mapping to Implementation Plan

### Week 1: Backend Foundation

| Module                  | Tasks   | Relevant Skills                               |
| ----------------------- | ------- | --------------------------------------------- |
| 1. Repository Structure | 1.1-1.3 | None (initial setup)                          |
| 2. Document Processing  | 2.1-2.3 | **rag-pipeline.md** (Document Ingestion)      |
| 3. Vector Storage       | 3.1-3.3 | **vector-database-lancedb.md** (All sections) |

### Week 2: RAG Pipeline & API

| Module               | Tasks   | Relevant Skills                                      |
| -------------------- | ------- | ---------------------------------------------------- |
| 4. Embedding Service | 4.1-4.3 | **rag-pipeline.md** (Embedding Generation)           |
| 5. RAG Integration   | 5.1-5.4 | **rag-pipeline.md** (Vector Search, LLM Integration) |
| 6. API Layer         | 6.1-6.4 | **api-design.md**, **testing-strategy.md**           |

### Week 3: Frontend & Testing

| Module                | Tasks       | Relevant Skills                             |
| --------------------- | ----------- | ------------------------------------------- |
| 7. Frontend Dashboard | 7.1-7.5     | **ui-ux-implementation.md** (All sections)  |
| Testing               | All modules | **testing-strategy.md**, **code-review.md** |

---

## Skill Development Workflow

### For Developers

1. **Before starting a task**:
   - Check if a relevant skill exists
   - Read the prerequisites section
   - Review the procedures

2. **During implementation**:
   - Follow step-by-step procedures
   - Use provided code patterns
   - Reference configuration examples

3. **After completion**:
   - Run through quality checks
   - Validate against common pitfalls
   - Document any deviations

### For QA Engineer

1. **Use testing-strategy.md** for comprehensive testing
2. **Use rag-pipeline.md** quality checks for RAG components
3. **Use ui-ux-implementation.md** accessibility checks for frontend
4. **Use code-review.md** for pull request reviews

### For Maintainer

1. **Use refactoring.md** when improving code
2. **Use root-cause-analysis.md** for bug investigation
3. **Use database-operations.md** for schema changes
4. **Use migration-logic.md** for data migrations

---

## Skill Maintenance

### Adding New Skills

When creating a new skill:

1. Use the template format (Purpose, Prerequisites, Procedures, Patterns)
2. Include concrete code examples
3. Add quality checks and validation steps
4. Document common pitfalls
5. Update this inventory file

### Updating Existing Skills

When updating a skill:

1. Increment version number
2. Document changes in changelog (if major)
3. Notify team of updates (if breaking changes)
4. Update references in other docs

---

## Quick Reference

**Need to...**

- Build REST API? → `api-design.md`
- Review code? → `code-review.md`
- Change database schema? → `database-operations.md`
- Migrate data? → `migration-logic.md`
- Refactor code? → `refactoring.md`
- Debug production issue? → `root-cause-analysis.md`
- Write tests? → `testing-strategy.md`
- Process documents? → `rag-pipeline.md` ✨
- Store embeddings? → `vector-database-lancedb.md` ✨
- Build UI components? → `ui-ux-implementation.md` ✨

---

## Summary

**Total Skills**: 10

- **Standard ACE Skills**: 7
- **RAG System Specific**: 3 ✨

**Coverage**:

- ✅ API Development
- ✅ Database Operations
- ✅ Testing & QA
- ✅ Code Quality
- ✅ RAG Pipeline Implementation ✨
- ✅ Vector Database Operations ✨
- ✅ UI/UX Development ✨

**Status**: Complete for Phase 1 implementation

---

_Skills Inventory v1.0 - RAG System_  
_Last Updated: 2026-02-02_

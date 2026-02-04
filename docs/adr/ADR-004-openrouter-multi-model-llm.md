# ADR-004: OpenRouter for Multi-Model LLM Support

> **Status:** Accepted  
> **Date:** 2026-02-02  
> **Supersedes:** None  
> **Related:** ADR-002

---

## Context

The RAG System requires LLM capabilities for:

- Natural language understanding of user queries
- Context-aware response generation
- Document summarization
- Analytics and insights generation

Key requirements identified during DISCUSS phase:

- **User must have model choice** (not locked to single provider)
- **Support both free and paid models** (cost flexibility)
- **Enable per-conversation model switching**
- **Future-proof against provider changes**

Direct integration with OpenAI/Anthropic/Google creates vendor lock-in and limits flexibility.

---

## Decision

We will use **OpenRouter** as a unified LLM proxy instead of direct provider integrations.

### Implementation Approach

1. **Single API Integration**
   - Backend uses OpenRouter API (OpenAI-compatible)
   - One API key, multiple providers accessible
   - Standardized request/response format

2. **Model Selection Architecture**

   ```python
   # Domain model
   class LLMModel(BaseModel):
       id: str                    # e.g., "openai/gpt-4-turbo"
       name: str                  # e.g., "GPT-4 Turbo"
       provider: str              # e.g., "openai"
       context_length: int        # e.g., 128000
       cost_per_token: float      # e.g., 0.00003
       is_free: bool              # True for open-source models
       capabilities: List[str]    # ["chat", "function_calling"]
   ```

3. **UI Model Selection**
   - Dropdown in chat interface
   - Filter by: free/paid, provider, capabilities
   - Display: name, cost estimate, context length
   - Per-conversation model persistence

4. **Supported Models (Phase 1)**
   - **Paid**: GPT-4 Turbo, Claude 3 Opus, Gemini Pro
   - **Free**: Llama 3 70B, Mistral Medium, Mixtral 8x7B

---

## Alternatives Considered

### Alternative 1: Direct OpenAI Integration

**Approach**: Use OpenAI SDK directly

- **Pros:**
  - Official SDK, well-documented
  - Simpler initial setup
  - Best performance (no proxy)
  - Function calling support

- **Cons:**
  - Vendor lock-in to OpenAI
  - No model choice for users
  - Higher costs (no free alternatives)
  - Hard to switch providers later

- **Why Rejected:** Conflicts with requirement for multi-model support

### Alternative 2: Multiple Direct Integrations

**Approach**: Integrate OpenAI, Anthropic, Google separately

- **Pros:**
  - Maximum control per provider
  - Best-in-class features per model
  - No proxy overhead

- **Cons:**
  - 3+ SDKs to maintain
  - Different APIs for each provider
  - Complex model switching logic
  - More API keys to manage
  - Higher development overhead

- **Why Rejected:** Too complex for Phase 1, hard to maintain

### Alternative 3: LangChain LLM Abstraction

**Approach**: Use LangChain's LLM interface

- **Pros:**
  - Provider abstraction built-in
  - Many integrations available
  - Active community

- **Cons:**
  - Heavy dependency (large library)
  - Opinionated patterns
  - Harder to customize
  - Frequent breaking changes

- **Why Rejected:** Adds unnecessary complexity, we only need LLM calls

### Alternative 4: LiteLLM

**Approach**: Use LiteLLM for provider abstraction

- **Pros:**
  - Lightweight
  - OpenAI-compatible interface
  - Local proxy option

- **Cons:**
  - Self-hosted (more infrastructure)
  - Less mature than OpenRouter
  - Requires deployment/management

- **Why Rejected:** OpenRouter is managed, simpler for Phase 1

---

## Consequences

### Positive

- ✅ **User Flexibility**: Users choose models based on task complexity
- ✅ **Cost Optimization**: Free models for testing, expensive models for production
- ✅ **Future-Proof**: Easy to add new providers as they emerge
- ✅ **Single API**: Backend only integrates with one API
- ✅ **No Vendor Lock-In**: Can switch to direct integration later
- ✅ **Rapid Prototyping**: Access to latest models without integration work

### Negative

- ❌ **Proxy Dependency**: Requires OpenRouter service availability
- ❌ **Slight Latency**: Proxy adds ~50-100ms overhead
- ❌ **Limited Control**: Can't use provider-specific features easily
- ❌ **Cost Markup**: OpenRouter adds small markup on paid models
- ❌ **Model Variations**: Different models may need prompt tuning

### Neutral

- ⚪ **API Key Management**: Still need API keys, but only one
- ⚪ **Rate Limits**: Subject to OpenRouter rate limits
- ⚪ **Model Availability**: Dependent on OpenRouter's model catalog

---

## Implementation Details

### Configuration

```python
# backend/src/config.py
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    OPENROUTER_API_KEY: str
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    OPENROUTER_SITE_URL: str = "http://localhost:3000"
    OPENROUTER_APP_NAME: str = "RAG System"

    # Default models
    DEFAULT_CHAT_MODEL: str = "meta-llama/llama-3-70b-instruct"  # Free
    DEFAULT_EMBEDDING_MODEL: str = "openai/text-embedding-3-large"

    class Config:
        env_file = ".env"
```

### LLM Client Interface (Domain Layer)

```python
# backend/src/features/rag/domain/interfaces.py
from typing import Protocol, List
from pydantic import BaseModel

class Message(BaseModel):
    role: str
    content: str

class LLMResponse(BaseModel):
    content: str
    model: str
    tokens_used: int
    cost: float

class ILLMClient(Protocol):
    async def generate(
        self,
        messages: List[Message],
        model: str,
        temperature: float = 0.7
    ) -> LLMResponse:
        """Generate response from LLM"""
        ...
```

### OpenRouter Client (Infrastructure Layer)

```python
# backend/src/features/rag/infrastructure/openrouter_client.py
import httpx
from ..domain.interfaces import ILLMClient, Message, LLMResponse

class OpenRouterClient(ILLMClient):
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url
        self.client = httpx.AsyncClient()

    async def generate(
        self,
        messages: List[Message],
        model: str,
        temperature: float = 0.7
    ) -> LLMResponse:
        response = await self.client.post(
            f"{self.base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "HTTP-Referer": settings.OPENROUTER_SITE_URL,
                "X-Title": settings.OPENROUTER_APP_NAME,
            },
            json={
                "model": model,
                "messages": [m.dict() for m in messages],
                "temperature": temperature,
            }
        )
        data = response.json()

        return LLMResponse(
            content=data["choices"][0]["message"]["content"],
            model=data["model"],
            tokens_used=data["usage"]["total_tokens"],
            cost=self._calculate_cost(data)
        )
```

### Model Selection API

```python
# backend/src/features/chat/api/routes.py
@router.get("/models")
async def get_available_models():
    """Return list of available models with metadata"""
    return {
        "models": [
            {
                "id": "openai/gpt-4-turbo-preview",
                "name": "GPT-4 Turbo",
                "provider": "OpenAI",
                "context_length": 128000,
                "is_free": False,
                "cost_estimate": "$$$"
            },
            {
                "id": "meta-llama/llama-3-70b-instruct",
                "name": "Llama 3 70B",
                "provider": "Meta",
                "context_length": 8192,
                "is_free": True,
                "cost_estimate": "Free"
            },
            # ... more models
        ]
    }
```

### Frontend Model Selector

```typescript
// frontend/src/components/chat/ModelSelector.tsx
export function ModelSelector({ onModelChange }: Props) {
  const { data: models } = useQuery('models', fetchModels);

  return (
    <Select onValueChange={onModelChange}>
      <SelectTrigger>
        <SelectValue placeholder="Select Model" />
      </SelectTrigger>
      <SelectContent>
        <SelectGroup>
          <SelectLabel>Free Models</SelectLabel>
          {models?.filter(m => m.is_free).map(model => (
            <SelectItem key={model.id} value={model.id}>
              {model.name} - {model.provider}
            </SelectItem>
          ))}
        </SelectGroup>
        <SelectSeparator />
        <SelectGroup>
          <SelectLabel>Paid Models</SelectLabel>
          {models?.filter(m => !m.is_free).map(model => (
            <SelectItem key={model.id} value={model.id}>
              {model.name} - {model.cost_estimate}
            </SelectItem>
          ))}
        </SelectGroup>
      </SelectContent>
    </Select>
  );
}
```

---

## Compliance

### Security Requirements

Per `.ace/standards/security.md`:

- ✅ API key stored in environment variables only
- ✅ Never log API responses (may contain sensitive data)
- ✅ Validate all LLM outputs before displaying
- ✅ Rate limiting to prevent abuse

### Testing Requirements

- Unit tests for OpenRouter client with mocked responses
- Integration tests with actual OpenRouter API (use free models)
- E2E tests for model switching in UI
- Cost tracking tests to prevent runaway expenses

### Monitoring Requirements

- Log model selection per request
- Track token usage per model
- Alert on unexpected costs
- Monitor OpenRouter API availability

---

## Risks & Mitigation

| Risk                    | Impact   | Mitigation                                                  |
| ----------------------- | -------- | ----------------------------------------------------------- |
| **OpenRouter Downtime** | High     | Implement fallback to direct OpenAI, cache responses        |
| **Cost Overruns**       | Medium   | Set token limits, require confirmation for expensive models |
| **Model Deprecation**   | Low      | Subscribe to OpenRouter announcements, version model IDs    |
| **Prompt Injection**    | High     | Input validation, content moderation, user warnings         |
| **API Key Exposure**    | Critical | Environment variables, never log keys, rotation policy      |

---

## Future Enhancements

### Phase 2

- Model comparison mode (same query, multiple models)
- Custom model configurations (temperature, top_p, etc.)
- Cost tracking dashboard

### Phase 3

- Local model support (Ollama integration)
- Fine-tuned model deployment
- Model performance benchmarking

---

## References

- [OpenRouter Documentation](https://openrouter.ai/docs)
- [OpenRouter Models](https://openrouter.ai/models)
- `.ace/standards/security.md` - Security standards
- ADR-002 - Technology Stack
- `docs/context/PROJECT_CONTEXT.md`

---

_ADR-004 - OpenRouter for Multi-Model LLM Support - ACE Framework v2.1_

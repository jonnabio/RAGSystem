# Implementation Plan: Educational Prompt Inspector ("Console Log")

## 🎯 Objective

Create a "Developer Console" or "Prompt Inspector" within the chat interface that reveals the exact raw inputs sent to the LLM. This is strictly for educational purposes, helping users understand how their query + retrieved documents are transformed into a prompt.

## 🎨 Design Concept: "The Glass Box"

Instead of a raw text dump, we will present the prompt as a **structured, code-like view** (similar to a VS Code window or a dark terminal) that parses the `System`, `User`, and `Context` components.

### UI Features

1.  **Terminal/Code Look**: Dark background, monospace font (Fira Code/Consolas), syntax highlighting.
2.  **Structured Breakdown**:
    - **System Message**: "You are a helpful assistant..." (Annotated: "The AI's Persona")
    - **Context Block**: The retrieved chunks. (Annotated: "Knowledge injected into the AI")
    - **User Query**: The actual question.
3.  **Collapsible Sections**: Large context blocks should be collapsible to keep the UI clean.
4.  **Copy-to-Clipboard**: Allow users to copy the full prompt to test elsewhere.

---

## 🛠 Backend Changes (Python)

### 1. Update Data Models (`src/features/rag/domain/interfaces.py`)

Update `ChatResponse` (or add a new field to `Message` metadata) to include the raw prompt messages.

```python
class ChatResponse(BaseModel):
    # ... existing fields
    debug_info: Optional[Dict[str, Any]] = None  # To hold raw_prompts, routing_decisions, etc.
```

### 2. Capture Prompt in `ChatService` (`src/features/chat/application/chat_service.py`)

In the `chat` method, capture the final `messages` list constructed before calling `llm_client.generate`.

```python
# Capture
raw_messages = [m.model_dump() for m in messages]

# Return
return ChatResponse(
    ...,
    debug_info={
        "final_prompt": raw_messages,
        "model_used": request.model
    }
)
```

---

## 🖥️ Frontend Changes (Next.js)

### 1. Create `PromptInspector` Component (`frontend/app/components/chat/PromptInspector.tsx`)

A new component that takes the `debug_info` and renders it nicely.

- **Tabs**: "Parsed View" (Pretty) vs "Raw JSON" (Actual API payload).
- **Styling**:
  - System Role: <span style="color: #ff7b72">Red/Orange</span>
  - User Role: <span style="color: #7ee787">Green</span>
  - Context: <span style="color: #a5d6ff">Blue</span>

### 2. Update `Message` Interface (`frontend/app/types/chat.ts`)

Add `debug_info` to the frontend types.

### 3. Integrate into Chat Page (`frontend/app/chat/page.tsx`)

- Add a small "Terminal" icon or "Show Prompt" button to the `PipelineStatus` bar.
- When clicked, this expands a drawer or modal showing the `PromptInspector`.

---

## 📝 Task List

### Backend

- [ ] Modify `ChatResponse` in `interfaces.py`.
- [ ] Update `ChatService.chat` to populate `debug_info` with the `messages` list.
- [ ] (Optional) Add prompts from Routing/Decomposition steps if available.

### Frontend

- [ ] Create `PromptInspector.tsx` component with "Terminal" styling.
- [ ] Add `debug_info` to TypeScript interfaces.
- [ ] Add toggle button to `PipelineStatus` or `Message` component.
- [ ] Implement Copy-to-Clipboard functionality.

---

## 📚 Educational Value

This feature demystifies "Prompt Engineering" by showing exactly:

1.  How much text (Context) is actually sent vs the user's short question.
2.  How the System Prompt instructions guide the behavior.
3.  The format (JSON/dictionary structure) required by LLM APIs.

# UI/UX Specification: RAG System Dashboard

> **Version:** 1.0  
> **Date:** 2026-02-02  
> **Status:** Approved for Phase 1  
> **Related:** ADR-002, `docs/planning/implementation_plan.md`

---

## Table of Contents

1. [Overview](#overview)
2. [Design System](#design-system)
3. [Layout Architecture](#layout-architecture)
4. [Page Specifications](#page-specifications)
5. [Component Library](#component-library)
6. [User Flows](#user-flows)
7. [Responsive Design](#responsive-design)
8. [Accessibility](#accessibility)

---

## Overview

### Vision

A **modern, professional dashboard** for AI-powered document Q&A that feels premium and state-of-the-art. The interface should be:

- 🎨 **Visually Stunning**: Modern gradients, smooth animations, glassmorphism
- ⚡ **Fast & Responsive**: Instant feedback, optimistic updates
- 🧠 **Intelligent**: Context-aware, helpful, anticipates user needs
- 📊 **Data-Rich**: Analytics, insights, confidence scores prominently displayed

### Target Users

- Knowledge workers querying document collections
- Researchers analyzing papers and reports
- Business analysts extracting insights from data
- Technical users exploring model capabilities

---

## Design System

### Color Palette

#### Dark Mode (Primary)

```css
/* Background Layers - Deep Blue Tones */
--bg-primary: #0a0e1a; /* Deep navy blue - main background */
--bg-secondary: #0f1729; /* Dark blue - cards, panels */
--bg-tertiary: #162038; /* Medium blue - elevated elements */
--bg-hover: #1a2847; /* Lighter blue - hover states */
--bg-accent: #1e3a5f; /* Blue accent - selected states */

/* Fiserv Orange Spectrum */
--orange-primary: #ff6600; /* Fiserv Orange - primary brand */
--orange-light: #ff8533; /* Light orange - hover, highlights */
--orange-dark: #cc5200; /* Dark orange - pressed states */
--orange-subtle: #ff660033; /* Transparent orange - backgrounds */
--orange-glow: #ff660066; /* Orange glow - shadows, borders */

/* Complementary Blue Accents */
--blue-accent: #3b82f6; /* Bright blue - secondary actions */
--blue-light: #60a5fa; /* Light blue - info states */
--blue-dark: #1e40af; /* Dark blue - borders */

/* Semantic Colors */
--accent-success: #10b981; /* Green - success states */
--accent-warning: #f59e0b; /* Amber - warnings */
--accent-error: #ef4444; /* Red - errors */
--accent-info: #3b82f6; /* Blue - info states */

/* Text Colors */
--text-primary: #ffffff; /* White - primary text */
--text-secondary: #cbd5e1; /* Light gray - secondary text */
--text-muted: #94a3b8; /* Medium gray - muted text */
--text-orange: #ff8533; /* Light orange - accented text */

/* Gradients */
--gradient-primary: linear-gradient(135deg, #ff6600 0%, #ff8533 100%);
--gradient-hero: linear-gradient(135deg, #0f1729 0%, #1e3a5f 50%, #ff660033 100%);
--gradient-card: linear-gradient(180deg, #0f1729 0%, #162038 100%);
--gradient-glass: rgba(255, 102, 0, 0.05);
--gradient-glass-blue: rgba(59, 130, 246, 0.05);
```

#### Light Mode (Optional - Phase 2)

```css
--bg-primary: #ffffff;
--bg-secondary: #f9fafb;
--text-primary: #111827;
/* ... etc */
```

### Typography

```css
/* Font Family */
--font-sans: "Inter", -apple-system, BlinkMacSystemFont, sans-serif;
--font-mono: "JetBrains Mono", "Fira Code", monospace;

/* Font Sizes */
--text-xs: 0.75rem; /* 12px */
--text-sm: 0.875rem; /* 14px */
--text-base: 1rem; /* 16px */
--text-lg: 1.125rem; /* 18px */
--text-xl: 1.25rem; /* 20px */
--text-2xl: 1.5rem; /* 24px */
--text-3xl: 1.875rem; /* 30px */
--text-4xl: 2.25rem; /* 36px */

/* Font Weights */
--font-normal: 400;
--font-medium: 500;
--font-semibold: 600;
--font-bold: 700;
```

### Spacing System (Tailwind)

```
4px, 8px, 12px, 16px, 20px, 24px, 32px, 40px, 48px, 64px
(1, 2, 3, 4, 5, 6, 8, 10, 12, 16 in Tailwind units)
```

### Shadows & Effects

```css
/* Shadows */
--shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
--shadow-md: 0 4px 6px rgba(0, 0, 0, 0.1);
--shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.15);
--shadow-xl: 0 20px 25px rgba(0, 0, 0, 0.2);

/* Glassmorphism */
backdrop-filter: blur(12px);
background: rgba(255, 255, 255, 0.05);
border: 1px solid rgba(255, 255, 255, 0.1);

/* Animations */
transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
```

---

## Layout Architecture

### Main Dashboard Structure

```
┌─────────────────────────────────────────────────────────────────┐
│                        Top Navigation Bar                        │
│  [Logo] [Search]           [Model: GPT-4 ▼]  [User] [Settings]  │
├──────────┬──────────────────────────────────────────────────────┤
│          │                                                       │
│          │                                                       │
│  Sidebar │              Main Content Area                        │
│          │                                                       │
│   📁     │  (Dynamic based on active page)                       │
│   💬     │                                                       │
│   📊     │                                                       │
│   ⚙️     │                                                       │
│          │                                                       │
│          │                                                       │
│          │                                                       │
└──────────┴──────────────────────────────────────────────────────┘
```

### Sidebar Navigation (Left - 240px)

```typescript
// Navigation Items
const navItems = [
  { icon: Home, label: "Dashboard", path: "/" },
  { icon: MessageSquare, label: "Chat", path: "/chat" },
  { icon: FolderOpen, label: "Documents", path: "/documents" },
  { icon: BarChart3, label: "Analytics", path: "/analytics" },
  { icon: Settings, label: "Settings", path: "/settings" },
];
```

**Visual Design**:

- Dark blue background (#0f1729)
- Icons with labels
- Active state: **Fiserv orange gradient background** (#FF6600 → #FF8533)
- Hover: Subtle blue highlight (#1a2847)
- Collapsed mode: Icons only (64px width)

### Top Navigation Bar (Height: 64px)

**Left Side**:

- Logo/Brand (48px)
- Global search bar (expandable)

**Right Side**:

- Model selector dropdown
- Notifications (badge indicator)
- User avatar menu
- Theme toggle (dark/light)
- Settings gear icon

---

## Page Specifications

### 1. Dashboard Page (`/`)

**Purpose**: Overview of system status, recent activity, and quick actions

**Layout**:

```
┌─────────────────────────────────────────────────────────────┐
│  📊 Dashboard                                    [Date]      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Documents   │  │   Queries    │  │   Tokens     │      │
│  │      24      │  │     156      │  │    45.2K     │      │
│  │   +3 today   │  │  +12 today   │  │  +2.1K today │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                              │
│  Recent Conversations                                        │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ 🤖 What is the main finding?        2 min ago        │   │
│  │ 💬 Confidence: 92%  •  Model: Claude 3 Opus         │   │
│  ├──────────────────────────────────────────────────────┤   │
│  │ 🤖 Summarize the introduction       15 min ago       │   │
│  │ 💬 Confidence: 88%  •  Model: GPT-4 Turbo           │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  Quick Actions                                               │
│  [+ New Chat]  [📄 Upload Document]  [📊 View Analytics]    │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

**Components**:

1. **Stat Cards** (3 across)
   - Document count
   - Query count
   - Token usage
   - Each with trend indicator (↑ +3 today)

2. **Recent Conversations List**
   - Last 5 conversations
   - Preview of query and response
   - Confidence score badge
   - Model used tag
   - Time ago

3. **Quick Actions**
   - Large CTA buttons
   - Icon + label
   - Gradient backgrounds

---

### 2. Chat Page (`/chat`)

**Purpose**: Main RAG chat interface with conversation history

**Layout**:

```
┌─────────────────────────────────────────────────────────────────┐
│  💬 Chat                [Model: GPT-4 Turbo ▼]  [New Chat]      │
├──────────┬──────────────────────────────────────────────────────┤
│          │                                                       │
│ History  │   Active Conversation                                │
│          │                                                       │
│ Today    │   ┌─────────────────────────────────────────────┐   │
│ • Conv 1 │   │ 🙋 What is the conclusion of document X?    │   │
│ • Conv 2 │   │                                              │   │
│          │   │ 🤖 Based on the provided documents, the     │   │
│ Yesterday│   │    main conclusion is...                    │   │
│ • Conv 3 │   │                                              │   │
│          │   │    📎 Sources (3):                           │   │
│ This Week│   │    • Document X, Page 5 (Score: 0.94)       │   │
│ • Conv 4 │   │    • Document Y, Page 12 (Score: 0.87)      │   │
│          │   │                                              │   │
│          │   │    ✅ Confidence: 91%                        │   │
│          │   │    ⚡ 1,234 tokens • $0.002                 │   │
│          │   └─────────────────────────────────────────────┘   │
│          │                                                       │
│          │   ┌─────────────────────────────────────────────┐   │
│          │   │ Ask a question...                    [Send] │   │
│          │   │ [📎 Filter Docs] [🎨 Adjust Temp]           │   │
│          │   └─────────────────────────────────────────────┘   │
└──────────┴──────────────────────────────────────────────────────┘
```

**Left Sidebar (Conversation History - 280px)**:

- Grouped by time (Today, Yesterday, This Week, This Month)
- Conversation previews with first message
- Search/filter conversations
- Delete conversation option

**Main Chat Area**:

- **Message Bubbles**:
  - User messages: Right-aligned, gradient background
  - AI messages: Left-aligned, secondary background
  - Timestamp on hover

- **Source Citations**:
  - Expandable section below AI response
  - Document name, page number, relevance score
  - Click to view full chunk text
  - Highlight button to jump to document

- **Metadata Footer** (per message):
  - Confidence score (color-coded: >90% green, 70-90% amber, <70% red)
  - Token count
  - Estimated cost
  - Copy button
  - Feedback buttons (👍 👎)

**Input Area**:

- Textarea with auto-resize
- Document filter pills (if multiple docs uploaded)
- Model selector dropdown
- Temperature/parameter controls (advanced mode)
- Send button (keyboard shortcut: Cmd+Enter)

---

### 3. Documents Page (`/documents`)

**Purpose**: Manage uploaded documents, view processing status

**Layout**:

```
┌─────────────────────────────────────────────────────────────────┐
│  📁 Documents                                   [Upload File]    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Drag & Drop files here or click to browse                 │ │
│  │  📄 Supported: PDF, DOCX                                    │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  [All] [PDFs] [Word Docs] [Recently Added]    [Search...]       │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ 📄 Research_Paper_2024.pdf          ✅ Processed         │    │
│  │    2.4 MB • 45 chunks • Uploaded 2 hours ago            │    │
│  │    [View] [Use in Chat] [Delete]                        │    │
│  ├─────────────────────────────────────────────────────────┤    │
│  │ 📄 Meeting_Notes.docx               ⏳ Processing...    │    │
│  │    156 KB • 12 chunks • Uploading now                   │    │
│  │    [████████░░] 80%                                     │    │
│  ├─────────────────────────────────────────────────────────┤    │
│  │ 📄 Project_Proposal.pdf             ✅ Processed         │    │
│  │    1.8 MB • 32 chunks • Uploaded yesterday              │    │
│  │    [View] [Use in Chat] [Delete]                        │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

**Components**:

1. **Upload Dropzone**
   - Drag-and-drop area with dashed border
   - File type indicators
   - Click to browse alternate action

2. **Document List**
   - Card-based layout
   - Status badges (Processed, Processing, Error)
   - Document metadata:
     - File size
     - Chunk count
     - Upload timestamp
   - Actions:
     - View chunks
     - Use in chat (opens chat with doc filter)
     - Download
     - Delete

3. **Filters & Search**
   - Tab filters (All, PDFs, Word Docs, etc.)
   - Search by filename
   - Sort by date, size, name

4. **Processing Indicator**
   - Progress bar for chunking/embedding
   - Real-time status updates via WebSocket

---

### 4. Analytics Page (`/analytics`)

**Purpose**: Visualize usage patterns, costs, and model performance

**Layout**:

```
┌─────────────────────────────────────────────────────────────────┐
│  📊 Analytics                              [Last 7 Days ▼]      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Model Usage Distribution                                       │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  [Pie Chart]                                            │     │
│  │  GPT-4: 45%  |  Claude: 30%  |  Llama 3: 25%          │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
│  Token Usage Over Time                                          │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  [Line Chart showing daily token consumption]           │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
│  Average Confidence Scores                                      │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  [Bar Chart by model]                                   │     │
│  │  GPT-4: 89%  |  Claude: 92%  |  Llama 3: 84%          │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
│  Cost Breakdown                                                 │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  Total: $12.45  |  This Week: $3.20  |  Today: $0.45   │     │
│  │  [Stacked Bar Chart by model]                           │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

**Charts** (using Recharts or Chart.js):

1. **Model Usage Pie Chart**
2. **Token Usage Line Chart** (time series)
3. **Confidence Scores Bar Chart** (by model)
4. **Cost Stacked Bar Chart** (by model and time)

**Metrics Cards**:

- Total queries
- Total tokens consumed
- Total cost
- Average response time
- Average confidence score

---

### 5. Settings Page (`/settings`)

**Purpose**: Configure models, system preferences, API keys

**Layout**:

```
┌─────────────────────────────────────────────────────────────────┐
│  ⚙️ Settings                                                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  [Models] [General] [API Keys] [Advanced]                       │
│                                                                  │
│  Available Models                                                │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  Free Models                                            │     │
│  │  ☑ Llama 3 70B Instruct (Meta)                         │     │
│  │     Context: 8K • Speed: Fast • Cost: Free              │     │
│  │  ☑ Mistral Medium (Mistral AI)                         │     │
│  │     Context: 32K • Speed: Fast • Cost: Free             │     │
│  │                                                          │     │
│  │  Paid Models                                            │     │
│  │  ☑ GPT-4 Turbo (OpenAI)                                │     │
│  │     Context: 128K • Speed: Slow • Cost: $$$             │     │
│  │  ☐ Claude 3 Opus (Anthropic)                           │     │
│  │     Context: 200K • Speed: Medium • Cost: $$$$          │     │
│  │  ☐ Gemini Pro (Google)                                 │     │
│  │     Context: 32K • Speed: Fast • Cost: $$               │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
│  Default Settings                                                │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  Default Model:        [Llama 3 70B ▼]                 │     │
│  │  Temperature:          [0.7 ━━━━━━━━○━━ 1.0]           │     │
│  │  Max Tokens:           [2048]                           │     │
│  │  Retrieval Chunks:     [5]                              │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

**Sections**:

1. **Models Tab**
   - List available models with toggle
   - Show capabilities (context length, speed, cost)
   - Set default model

2. **General Tab**
   - Theme (dark/light)
   - Language
   - Notifications

3. **API Keys Tab**
   - OpenRouter API key input
   - Validation status
   - Test connection button

4. **Advanced Tab**
   - RAG parameters (chunk size, overlap, retrieval count)
   - Embedding model selection
   - Vector DB location

---

## Component Library

### Core Components (shadcn/ui based)

#### 1. Message Bubble

```typescript
interface MessageBubbleProps {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  sources?: Source[];
  confidence?: number;
  metadata?: {
    model: string;
    tokens: number;
    cost: number;
  };
}

<MessageBubble
  role="assistant"
  content="Based on the documents..."
  sources={[...]}
  confidence={0.92}
  metadata={{ model: 'gpt-4', tokens: 1234, cost: 0.002 }}
/>
```

**Visual**:

- Glassmorphism background for assistant messages
- Gradient background for user messages
- Smooth slide-in animation
- Hover: Subtle elevation increase

#### 2. Document Card

```typescript
interface DocumentCardProps {
  id: string;
  filename: string;
  fileSize: number;
  chunkCount: number;
  status: "processing" | "processed" | "error";
  uploadedAt: Date;
  onView: () => void;
  onDelete: () => void;
  onUseInChat: () => void;
}
```

**Features**:

- Status badge (color-coded)
- Progress bar (if processing)
- Action buttons (View, Use, Delete)
- Hover: Card elevation

#### 3. Stat Card

```typescript
interface StatCardProps {
  title: string;
  value: number | string;
  trend?: {
    value: number;
    direction: "up" | "down";
    label: string;
  };
  icon: React.ComponentType;
  gradient?: string;
}
```

**Visual**:

- Icon with gradient background circle
- Large value display
- Trend indicator with arrow
- Subtle hover animation

#### 4. Model Selector

```typescript
interface ModelSelectorProps {
  models: Model[];
  selected: string;
  onChange: (modelId: string) => void;
  groupByProvider?: boolean;
}
```

**Features**:

- Dropdown with model details
- Group by free/paid
- Show context length, cost estimate
- Keyboard navigation

#### 5. Confidence Badge

```typescript
interface ConfidenceBadgeProps {
  score: number; // 0-1
  showPercentage?: boolean;
}
```

**Visual**:

- Color-coded: Green (>0.9), Amber (0.7-0.9), Red (<0.7)
- Percentage display
- Pulse animation if loading

#### 6. Source Citation

```typescript
interface SourceCitationProps {
  documentName: string;
  chunkIndex: number;
  score: number;
  snippet: string;
  onViewFull: () => void;
}
```

**Features**:

- Collapsible snippet preview
- Relevance score bar
- Link to full document
- Copy snippet button

---

## User Flows

### Flow 1: Upload Document and Ask Question

```
1. User lands on Dashboard
   ↓
2. Click "Upload Document" or navigate to /documents
   ↓
3. Drag PDF file to dropzone OR click to browse
   ↓
4. File uploads, progress bar shows 0-100%
   ↓
5. Backend processes: Extract → Chunk → Embed
   ↓
6. Status changes to "Processed" with chunk count
   ↓
7. User clicks "Use in Chat" button
   ↓
8. Redirects to /chat with document filter active
   ↓
9. User types question in input
   ↓
10. Click Send (or Cmd+Enter)
   ↓
11. Message appears in chat (user bubble)
   ↓
12. Loading indicator shows "Thinking..."
   ↓
13. AI response streams in (typewriter effect)
   ↓
14. Sources appear below response
   ↓
15. Confidence badge displays
   ↓
16. User can continue conversation
```

### Flow 2: Switch Models Mid-Conversation

```
1. User in active chat conversation
   ↓
2. Click model selector dropdown in top nav
   ↓
3. Dropdown shows grouped models (Free | Paid)
   ↓
4. User selects "Claude 3 Opus"
   ↓
5. Dropdown closes, selection confirmed
   ↓
6. Toast notification: "Switched to Claude 3 Opus"
   ↓
7. Next message uses new model
   ↓
8. Model tag on message shows "Claude 3 Opus"
```

### Flow 3: View Analytics

```
1. User clicks "Analytics" in sidebar
   ↓
2. Charts load with loading skeletons
   ↓
3. Data fetched from backend API
   ↓
4. Charts animate in (smooth transitions)
   ↓
5. User selects time range "Last 30 Days"
   ↓
6. Charts re-query and update
   ↓
7. User hovers over chart data point
   ↓
8. Tooltip shows detailed info
```

---

## Responsive Design

### Breakpoints (Tailwind)

- **Mobile**: `< 640px` (sm)
- **Tablet**: `640px - 1024px` (md - lg)
- **Desktop**: `> 1024px` (xl, 2xl)

### Mobile Adaptations

**Navigation**:

- Hamburger menu replaces sidebar
- Sidebar becomes slide-out drawer
- Top nav collapses to icons only

**Chat Page**:

- Conversation history in modal/drawer
- Full-width chat messages
- Bottom sheet for input

**Documents**:

- Stack cards vertically
- Simplified card layout
- Swipe gestures for actions

**Analytics**:

- Stack charts vertically
- Horizontal scroll for wide charts
- Simplified legends

---

## Accessibility

### WCAG 2.1 AA Compliance

**Keyboard Navigation**:

- All interactive elements focusable
- Tab order logical
- Keyboard shortcuts documented
  - `/` - Focus search
  - `Cmd+K` - Quick actions
  - `Esc` - Close modals
  - `Cmd+Enter` - Send message

**Screen Reader Support**:

- Semantic HTML (`<nav>`, `<main>`, `<article>`)
- ARIA labels on icons
- ARIA live regions for chat updates
- Alt text on images

**Color Contrast**:

- Text: 4.5:1 minimum
- Large text: 3:1 minimum
- UI components: 3:1 minimum

**Focus Indicators**:

- Visible focus rings (indigo, 2px)
- Skip to main content link
- Focus trap in modals

---

## Animation & Micro-interactions

### Message Loading

```typescript
// Skeleton pulse while loading
<div className="animate-pulse">
  <div className="h-4 bg-gray-700 rounded w-3/4"></div>
  <div className="h-4 bg-gray-700 rounded w-1/2 mt-2"></div>
</div>

// Typewriter effect for streaming responses
useEffect(() => {
  let index = 0;
  const interval = setInterval(() => {
    setText(fullText.slice(0, index++));
    if (index > fullText.length) clearInterval(interval);
  }, 20);
}, [fullText]);
```

### Hover Effects

- Buttons: Slight scale (1.02) + shadow increase
- Cards: Elevation increase + border glow
- Links: Underline slide-in
- Icons: Color transition + rotation

### Page Transitions

- Fade in on mount
- Slide up for modals
- Slide in from left for sidebar

### Success States

- Checkmark with bounce animation
- Confetti for first successful upload
- Green pulse for high confidence scores

---

## Implementation Checklist

### Phase 1 (Week 3, Days 3-5)

**Task 6.1: Layout & Navigation** ✅

- [ ] Create `layout.tsx` with sidebar + top nav
- [ ] Implement navigation state management
- [ ] Add dark mode toggle
- [ ] Responsive hamburger menu

**Task 6.2: Document Upload** ✅

- [ ] Dropzone component with react-dropzone
- [ ] Upload progress indicator
- [ ] Document card list
- [ ] File type validation

**Task 6.3: Chat Interface** ✅

- [ ] Message bubble component
- [ ] Conversation history sidebar
- [ ] Input with auto-resize
- [ ] Model selector dropdown
- [ ] Source citation component
- [ ] Confidence badge

**Task 6.4: Analytics Dashboard** ✅

- [ ] Stat cards with trend indicators
- [ ] Charts with Recharts
- [ ] Time range selector
- [ ] Responsive grid layout

### Future Enhancements (Phase 2+)

- [ ] Light mode theme
- [ ] Advanced charts (3D, interactive)
- [ ] Conversation export (PDF, Markdown)
- [ ] Keyboard shortcuts panel
- [ ] Command palette (Cmd+K)
- [ ] Collaborative features (share chats)
- [ ] Voice input integration

---

## Technology Stack (Frontend)

```json
{
  "framework": "Next.js 14",
  "language": "TypeScript",
  "styling": "Tailwind CSS",
  "components": "shadcn/ui",
  "icons": "Lucide React",
  "charts": "Recharts",
  "forms": "React Hook Form",
  "validation": "Zod",
  "state": "Zustand + React Query",
  "animations": "Framer Motion"
}
```

---

## Design References

### Inspiration

- **ChatGPT**: Clean message layout, streaming responses
- **Notion**: Document management, sidebar navigation
- **Linear**: Dark mode aesthetics, smooth animations
- **Vercel**: Glassmorphism, gradient accents
- **Perplexity AI**: Source citations, confidence indicators

### Component Previews

All components will use **shadcn/ui** base components with custom styling:

- Dialog, Sheet, Popover for modals
- Button with variants (default, ghost, outline)
- Card for containers
- Badge for status indicators
- Separator for dividers

---

**This UI specification provides a complete blueprint for the RAG System dashboard. Ready to implement in Week 3 of the development plan!** 🎨✨

_UI/UX Specification v1.0 - ACE Framework - RAG System_

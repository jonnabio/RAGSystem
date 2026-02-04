# Design Package: RAG System Dashboard

> **Version:** 1.0 - APPROVED  
> **Date:** 2026-02-02  
> **Status:** Ready for Implementation  
> **Theme:** Dark Blue × Fiserv Orange

---

## Table of Contents

1. [Overview](#overview)
2. [Design Approval](#design-approval)
3. [Visual Assets](#visual-assets)
4. [Mockups](#mockups)
5. [Component Specifications](#component-specifications)
6. [Implementation Checklist](#implementation-checklist)
7. [References](#references)

---

## Overview

This document packages all approved design assets, specifications, and mockups for the RAG System Dashboard. The design has been **approved for implementation** and uses a **professional dark blue and Fiserv orange color scheme**.

### Design Goals

- ✅ Professional enterprise appearance
- ✅ Fiserv brand alignment (orange #FF6600)
- ✅ High contrast and accessibility (WCAG AA)
- ✅ Modern, premium UI with glassmorphism
- ✅ Clear visual hierarchy with orange CTAs

### Target Users

- Knowledge workers querying documents
- Researchers analyzing papers
- Business analysts extracting insights
- Technical users exploring AI capabilities

---

## Design Approval

**Approval Status**: ✅ **APPROVED**  
**Date**: 2026-02-02  
**Approved By**: Project Stakeholder

### Key Decisions Confirmed

1. **Color Scheme**: Dark blue backgrounds + Fiserv orange accents
2. **Layout**: Sidebar navigation + top bar (classic dashboard)
3. **Typography**: Inter font family (sans-serif)
4. **Components**: shadcn/ui component library
5. **Styling**: Tailwind CSS
6. **Responsiveness**: Mobile-first approach
7. **Accessibility**: WCAG 2.1 AA compliance

---

## Visual Assets

All design assets are stored in `docs/design/`:

### Directory Structure

```
docs/design/
├── assets/
│   └── color-palette.png          # Color swatch reference
├── mockups/
│   ├── dashboard-mockup.png       # Dashboard page
│   ├── chat-interface-mockup.png  # Chat page
│   ├── documents-page-mockup.png  # Documents management
│   └── analytics-dashboard-mockup.png  # Analytics page
└── README.md                       # This file
```

### Color Palette Swatch

**File**: `docs/design/assets/color-palette.png`

**Contents**:

- Background spectrum (4 navy/blue shades)
- Fiserv orange spectrum (3 orange variants)
- Gradient showcases (primary orange, hero gradient)
- Text colors (white, light gray, medium gray)

**Use for**: Quick reference when implementing components

---

## Mockups

### 1. Dashboard Page

**File**: `docs/design/mockups/dashboard-mockup.png`

**Features Shown**:

- Left sidebar with navigation
- Active nav item with orange gradient background
- Top navigation bar with search and model selector
- Three stat cards with orange icons
- Orange gradient "Upload Document" CTA button
- Recent activity cards
- Professional dark blue theme

**Key Elements**:

- Stat cards: Documents, Queries, Tokens
- Trend indicators (+3 this week, etc.)
- Quick action buttons
- Recent conversations preview

**Implementation Notes**:

- Active sidebar item uses `bg-gradient-to-r from-fiserv to-fiserv-light`
- Stat card icons use orange circular backgrounds
- CTA button is the primary orange gradient
- All cards use `bg-navy-900` (#0f1729)

---

### 2. Chat Interface

**File**: `docs/design/mockups/chat-interface-mockup.png`

**Features Shown**:

- Conversation history sidebar (left, 280px)
- Grouped conversations (Today, Yesterday, This Week)
- User message with orange gradient background
- AI message with dark blue background
- Expandable sources section (orange text)
- Document citations with relevance scores
- Confidence badge (green, 92%)
- Token count and cost metadata
- Bottom input area with orange "Send" button

**Key Elements**:

- User messages: Right-aligned, orange gradient
- AI messages: Left-aligned, dark blue with glassmorphism
- Sources: Collapsible, orange accent
- Input: Auto-resize textarea
- Send button: Orange gradient with icon

**Implementation Notes**:

- User bubble: `bg-gradient-to-r from-fiserv to-fiserv-light text-white`
- AI bubble: `bg-navy-900 border border-gray-800`
- Source links: `text-orange-500 hover:text-orange-400`
- Confidence badge: Dynamic color (green >90%, amber 70-90%, red <70%)

---

### 3. Documents Page

**File**: `docs/design/mockups/documents-page-mockup.png`

**Features Shown**:

- Page header with orange "Upload File" button
- Large drag-and-drop zone (dashed border)
- Orange upload icon
- Filter tabs with orange active underline
- Search box
- Document cards showing:
  - PDF/DOCX icons (orange)
  - Status badges (green "Processed", orange "Processing")
  - Progress bar (orange gradient fill)
  - Metadata (size, chunks, upload time)
  - Action buttons (View, Use in Chat, Delete)

**Key Elements**:

- Dropzone: Medium blue background, dashed border
- Filter tabs: Orange underline for active
- Document cards: Dark blue with orange icons
- Status badges: Color-coded semantic colors
- Progress bar: Orange gradient fill

**Implementation Notes**:

- Dropzone: `border-2 border-dashed border-gray-700 bg-navy-800`
- Active tab: `border-b-2 border-fiserv`
- Processing badge: `bg-orange-500/20 text-orange-400 animate-pulse`
- Progress bar: `bg-gradient-to-r from-fiserv to-fiserv-light`

---

### 4. Analytics Dashboard

**File**: `docs/design/mockups/analytics-dashboard-mockup.png`

**Features Shown**:

- Page header with time range selector
- Four metric cards (Total Queries, Tokens, Cost, Avg Confidence)
- Large area chart: Token Usage Over Time (orange gradient fill)
- Donut chart: Model Usage Distribution (orange/blue/gray segments)
- Horizontal bar chart: Confidence by Model (gradient bars)
- Stacked bar chart: Cost Breakdown by model and day

**Key Elements**:

- Metric cards: Large numbers with trend indicators
- Area chart: Orange gradient fill under line
- Donut chart: Orange for GPT-4 (largest segment)
- Bar charts: Gradient colors matching brand
- Dark blue card backgrounds with subtle borders

**Implementation Notes**:

- Use Recharts library for charts
- Area chart: `fill="url(#orangeGradient)"`
- Donut segments: GPT-4 orange, Claude blue, Llama gray
- Confidence bars: Green gradient for high scores
- All charts use `bg-navy-900` card backgrounds

---

## Component Specifications

### Core Reusable Components

#### 1. Primary Button (Orange CTA)

**Visual**: Orange gradient background, white text, rounded corners, shadow

**Code**:

```tsx
<button
  className="bg-gradient-to-r from-fiserv to-fiserv-light
                   hover:from-fiserv-light hover:to-fiserv
                   active:from-fiserv-dark active:to-fiserv-dark
                   text-white font-semibold
                   px-6 py-3 rounded-lg
                   shadow-lg shadow-fiserv/30
                   hover:shadow-xl hover:shadow-fiserv/40
                   transform hover:-translate-y-0.5
                   transition-all duration-300"
>
  Upload Document
</button>
```

**Usage**: Primary actions (Upload, Send, Submit, New Chat)

---

#### 2. Stat Card

**Visual**: Dark blue background, large value, trend indicator, orange icon

**Code**:

```tsx
<div
  className="bg-navy-900 border border-gray-800 rounded-xl p-6
               hover:shadow-lg hover:shadow-fiserv-glow
               hover:border-gray-700 transition-all duration-300"
>
  <div className="flex items-center justify-between">
    <div>
      <p className="text-gray-400 text-sm">Documents</p>
      <h3 className="text-white text-3xl font-bold mt-1">24</h3>
      <p className="text-green-500 text-xs mt-2 flex items-center gap-1">↑ +3 today</p>
    </div>
    <div
      className="w-12 h-12 bg-fiserv/20 rounded-full
                   flex items-center justify-center
                   group-hover:bg-fiserv/30 transition-colors"
    >
      <FolderIcon className="text-fiserv w-6 h-6" />
    </div>
  </div>
</div>
```

**Usage**: Dashboard metrics, analytics KPIs

---

#### 3. Navigation Sidebar

**Visual**: Dark blue background, vertical list, orange active state

**Code**:

```tsx
<nav className="w-64 bg-navy-900 h-screen border-r border-gray-800 px-3 py-4">
  {navItems.map((item) => (
    <Link key={item.path} href={item.path} className={cn("flex items-center gap-3 px-4 py-3 rounded-lg mb-1", "transition-all duration-200", pathname === item.path ? "bg-gradient-to-r from-fiserv to-fiserv-light text-white shadow-lg" : "text-gray-400 hover:bg-navy-800 hover:text-white")}>
      <item.icon className="w-5 h-5" />
      <span className="font-medium">{item.label}</span>
    </Link>
  ))}
</nav>
```

**Usage**: Main app navigation

---

#### 4. Message Bubble (User)

**Visual**: Orange gradient background, right-aligned, white text

**Code**:

```tsx
<div className="flex justify-end mb-4">
  <div
    className="max-w-[70%] bg-gradient-to-r from-fiserv to-fiserv-light
                 text-white rounded-2xl rounded-tr-sm px-4 py-3
                 shadow-lg shadow-fiserv/20"
  >
    {message.content}
  </div>
</div>
```

**Usage**: User messages in chat interface

---

#### 5. Message Bubble (AI)

**Visual**: Dark blue background, left-aligned, includes sources and confidence

**Code**:

```tsx
<div className="flex justify-start mb-4">
  <div
    className="max-w-[70%] bg-navy-900 border border-gray-800
                 text-gray-200 rounded-2xl rounded-tl-sm px-4 py-3"
  >
    <p className="leading-relaxed">{message.content}</p>

    {/* Sources */}
    <div className="mt-3 pt-3 border-t border-gray-800">
      <p className="text-gray-400 text-sm mb-2">📎 Sources (3):</p>
      {message.sources.map((source, i) => (
        <div key={i} className="text-orange-500 text-xs mb-1 flex items-center gap-2">
          <span>•</span>
          <span>
            {source.name}, Page {source.page}
          </span>
          <span className="text-gray-500">(Score: {source.score})</span>
        </div>
      ))}
    </div>

    {/* Metadata */}
    <div className="mt-2 flex items-center gap-3">
      <span className={cn("text-xs px-2 py-1 rounded", message.confidence > 0.9 ? "bg-green-500/20 text-green-400" : message.confidence > 0.7 ? "bg-amber-500/20 text-amber-400" : "bg-red-500/20 text-red-400")}>✅ Confidence: {(message.confidence * 100).toFixed(0)}%</span>
      <span className="text-gray-500 text-xs">
        ⚡ {message.tokens} tokens • ${message.cost.toFixed(4)}
      </span>
    </div>
  </div>
</div>
```

**Usage**: AI responses in chat interface

---

#### 6. Document Card

**Visual**: Dark blue background, orange icon, status badge, action buttons

**Code**:

```tsx
<div
  className="bg-navy-900 border border-gray-800 rounded-lg p-4
               hover:border-gray-700 hover:shadow-lg hover:shadow-fiserv-glow
               transition-all duration-300"
>
  <div className="flex items-start gap-3">
    {/* Icon */}
    <div className="w-10 h-10 bg-fiserv/20 rounded flex items-center justify-center flex-shrink-0">
      <FileIcon className="w-5 h-5 text-fiserv" />
    </div>

    {/* Content */}
    <div className="flex-1 min-w-0">
      <h4 className="text-white font-medium text-sm truncate">{document.filename}</h4>
      <p className="text-gray-400 text-xs mt-1">
        {document.size} • {document.chunkCount} chunks • {document.uploadedAt}
      </p>

      {/* Status */}
      <div className="mt-2">
        {document.status === "processed" && <span className="bg-green-500/20 text-green-400 text-xs px-2 py-1 rounded">✅ Processed</span>}
        {document.status === "processing" && <span className="bg-orange-500/20 text-orange-400 text-xs px-2 py-1 rounded animate-pulse">⏳ Processing...</span>}
      </div>

      {/* Actions */}
      <div className="mt-3 flex gap-2">
        <button className="text-xs px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-500">View</button>
        <button className="text-xs px-3 py-1 bg-fiserv text-white rounded hover:bg-fiserv-light">Use in Chat</button>
        <button className="text-xs px-3 py-1 border border-gray-700 text-gray-400 rounded hover:border-red-600 hover:text-red-500">Delete</button>
      </div>
    </div>
  </div>
</div>
```

**Usage**: Document list items, file management

---

#### 7. Input Field

**Visual**: Dark blue background, orange focus ring

**Code**:

```tsx
<input
  type="text"
  className="w-full bg-navy-900 border border-gray-700
            focus:border-fiserv focus:ring-2 focus:ring-fiserv/20
            text-white placeholder-gray-500
            rounded-lg px-4 py-3
            transition-all duration-200
            outline-none"
  placeholder="Ask a question..."
/>
```

**Usage**: Search, chat input, form fields

---

#### 8. Confidence Badge

**Visual**: Color-coded badge based on score

**Code**:

```tsx
function ConfidenceBadge({ score }: { score: number }) {
  const percentage = (score * 100).toFixed(0);

  const variants = {
    high: "bg-green-500/20 text-green-400",
    medium: "bg-amber-500/20 text-amber-400",
    low: "bg-red-500/20 text-red-400",
  };

  const variant = score > 0.9 ? "high" : score > 0.7 ? "medium" : "low";

  return <span className={`text-xs px-2 py-1 rounded ${variants[variant]}`}>✅ Confidence: {percentage}%</span>;
}
```

**Usage**: Chat messages, query results, analytics

---

## Implementation Checklist

### Phase 1: Setup (Week 3, Day 1)

- [ ] Install and configure Tailwind CSS
- [ ] Setup custom color palette in `tailwind.config.js`
- [ ] Install shadcn/ui components
- [ ] Install Lucide React icons
- [ ] Setup Inter font from Google Fonts
- [ ] Create base layout component

### Phase 2: Core Components (Week 3, Day 2)

- [ ] Implement PrimaryButton component
- [ ] Implement SecondaryButton component
- [ ] Implement GhostButton component
- [ ] Implement StatCard component
- [ ] Implement DocumentCard component
- [ ] Implement ConfidenceBadge component
- [ ] Implement Input component
- [ ] Test all components in Storybook (optional)

### Phase 3: Layout & Navigation (Week 3, Day 3)

- [ ] Build main app layout with sidebar
- [ ] Implement navigation sidebar
- [ ] Build top navigation bar
- [ ] Add responsive hamburger menu
- [ ] Implement dark mode (already default)
- [ ] Test responsive breakpoints

### Phase 4: Pages (Week 3, Days 4-5)

- [ ] Build Dashboard page
  - [ ] Stat cards
  - [ ] Recent conversations
  - [ ] Quick actions
- [ ] Build Chat interface
  - [ ] Conversation history sidebar
  - [ ] Message bubbles
  - [ ] Input area
  - [ ] Source citations
- [ ] Build Documents page
  - [ ] Upload dropzone
  - [ ] Document cards
  - [ ] Filter tabs
- [ ] Build Analytics page
  - [ ] Metric cards
  - [ ] Token usage chart (Recharts)
  - [ ] Model distribution chart
  - [ ] Confidence chart

### Phase 5: Polish & Testing (Week 3, Day 5)

- [ ] Add animations and transitions
- [ ] Test accessibility (screen reader, keyboard nav)
- [ ] Verify color contrast ratios
- [ ] Test on mobile devices
- [ ] Cross-browser testing
- [ ] Performance optimization

---

## References

### Documentation

- **UI/UX Specification**: `docs/specs/UI_UX_Specification.md`
- **Color Application Guide**: `docs/specs/Color_Application_Guide.md`
- **Implementation Plan**: `docs/planning/implementation_plan.md`
- **Task Checklist**: `docs/planning/task_checklist.md`

### ADRs

- **ADR-002**: RAG Technology Stack
- **ADR-003**: Layered Architecture Pattern
- **ADR-004**: OpenRouter Multi-Model LLM

### Design Assets

- **Color Palette**: `docs/design/assets/color-palette.png`
- **Dashboard Mockup**: `docs/design/mockups/dashboard-mockup.png`
- **Chat Mockup**: `docs/design/mockups/chat-interface-mockup.png`
- **Documents Mockup**: `docs/design/mockups/documents-page-mockup.png`
- **Analytics Mockup**: `docs/design/mockups/analytics-dashboard-mockup.png`

### External Resources

- **Tailwind CSS**: https://tailwindcss.com/docs
- **shadcn/ui**: https://ui.shadcn.com/
- **Lucide Icons**: https://lucide.dev/
- **Recharts**: https://recharts.org/
- **Inter Font**: https://fonts.google.com/specimen/Inter

---

## Version History

| Version | Date       | Changes                                                              | Author        |
| ------- | ---------- | -------------------------------------------------------------------- | ------------- |
| 1.0     | 2026-02-02 | Initial design package with approved dark blue × Fiserv orange theme | ACE Framework |

---

**DESIGN APPROVED ✅**  
**Ready for Implementation**: Week 3 (Frontend Development)

_Design Package v1.0 - RAG System - ACE Framework v2.1_

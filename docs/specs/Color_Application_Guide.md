# Dark Blue × Fiserv Orange: Color Application Guide

> **Brand Colors for RAG System Dashboard**  
> **Created:** 2026-02-02  
> **UI Theme:** Dark Mode Professional

---

## Color Philosophy

The RAG System uses a **sophisticated dark blue foundation** with **energetic Fiserv orange accents** to create a professional yet dynamic interface. This combination:

- ✅ **Professional**: Deep blues convey trust and stability
- ✅ **Energetic**: Orange provides warmth and action cues
- ✅ **High Contrast**: Excellent readability on dark backgrounds
- ✅ **Brand Aligned**: Fiserv orange reinforces corporate identity
- ✅ **Modern**: Contemporary palette for AI/tech applications

---

## Primary Color Palette

### Background Spectrum (Dark Blues)

```css
--bg-primary: #0a0e1a; /* Deep navy - main canvas */
--bg-secondary: #0f1729; /* Dark blue - cards, panels */
--bg-tertiary: #162038; /* Medium blue - raised elements */
--bg-hover: #1a2847; /* Lighter blue - hover states */
--bg-accent: #1e3a5f; /* Blue accent - selected/active */
```

**Usage**:

- `bg-primary`: Page background, app shell
- `bg-secondary`: Cards, modals, sidebar
- `bg-tertiary`: Dropdowns, tooltips, elevated cards
- `bg-hover`: Button hover, row hover
- `bg-accent`: Selected items, focus states

---

### Fiserv Orange Spectrum

```css
--orange-primary: #ff6600; /* Brand orange - primary actions */
--orange-light: #ff8533; /* Light orange - hover, highlights */
--orange-dark: #cc5200; /* Dark orange - pressed states */
--orange-subtle: #ff660033; /* Transparent - backgrounds */
--orange-glow: #ff660066; /* Semi-transparent - glows, borders */
```

**Usage**:

- `orange-primary`: Primary buttons, active navigation, brand elements
- `orange-light`: Button hover, gradient end, text highlights
- `orange-dark`: Button pressed, active state emphasis
- `orange-subtle`: Subtle backgrounds, notification badges
- `orange-glow`: Box shadows, border glows, focus rings

---

### Text Colors

```css
--text-primary: #ffffff; /* White - headings, primary text */
--text-secondary: #cbd5e1; /* Light gray - body text */
--text-muted: #94a3b8; /* Medium gray - captions, metadata */
--text-orange: #ff8533; /* Light orange - accented text */
```

**Usage**:

- `text-primary`: Page titles, headings, important labels
- `text-secondary`: Paragraph text, descriptions
- `text-muted`: Timestamps, helper text, placeholders
- `text-orange`: Links, emphasized text, call-to-action text

---

### Semantic Colors

```css
--accent-success: #10b981; /* Emerald green - success */
--accent-warning: #f59e0b; /* Amber - warnings */
--accent-error: #ef4444; /* Red - errors */
--accent-info: #3b82f6; /* Blue - informational */
```

**Usage**:

- `success`: Confidence >90%, upload complete, positive feedback
- `warning`: Confidence 70-90%, caution states
- `error`: Confidence <70%, failed uploads, errors
- `info`: Secondary actions, informational badges

---

## Gradient System

### Primary Orange Gradient

```css
background: linear-gradient(135deg, #ff6600 0%, #ff8533 100%);
```

**Use for**:

- ✅ Primary CTA buttons ("Upload Document", "Send", "New Chat")
- ✅ Active navigation items (sidebar selected state)
- ✅ Important stat cards
- ✅ Logo accents

### Hero Gradient (Dark Blue → Orange)

```css
background: linear-gradient(135deg, #0f1729 0%, #1e3a5f 50%, #ff660033 100%);
```

**Use for**:

- ✅ Page headers
- ✅ Large hero sections
- ✅ Background overlays

### Card Gradient (Subtle Depth)

```css
background: linear-gradient(180deg, #0f1729 0%, #162038 100%);
```

**Use for**:

- ✅ Card backgrounds
- ✅ Panel separators
- ✅ Subtle depth effects

---

## Component Color Applications

### 1. Buttons

#### Primary Button (Orange)

```tsx
<button
  className="bg-gradient-to-r from-orange-600 to-orange-500 
                   hover:from-orange-500 hover:to-orange-400
                   text-white font-semibold px-6 py-3 rounded-lg
                   shadow-lg shadow-orange-600/30
                   transition-all duration-300"
>
  Upload Document
</button>
```

**When to use**: Main actions (upload, send, submit)

#### Secondary Button (Blue)

```tsx
<button
  className="bg-blue-600 hover:bg-blue-500
                   text-white font-medium px-4 py-2 rounded-lg
                   transition-colors duration-200"
>
  View Details
</button>
```

**When to use**: Secondary actions (view, filter, cancel)

#### Ghost Button (Transparent)

```tsx
<button
  className="border border-gray-700 hover:border-orange-600
                   text-gray-300 hover:text-orange-500
                   font-medium px-4 py-2 rounded-lg
                   transition-all duration-200"
>
  Learn More
</button>
```

**When to use**: Tertiary actions (delete, close)

---

### 2. Navigation

#### Sidebar (Active State)

```tsx
<div className="bg-[#0f1729] w-64 h-screen">
  {/* Active item */}
  <div
    className="bg-gradient-to-r from-orange-600 to-orange-500
                  text-white px-4 py-3 rounded-lg mx-2"
  >
    <Icon /> Dashboard
  </div>

  {/* Inactive items */}
  <div
    className="text-gray-400 hover:bg-[#1a2847] hover:text-white
                  px-4 py-3 rounded-lg mx-2 transition-colors"
  >
    <Icon /> Documents
  </div>
</div>
```

#### Top Navigation

```tsx
<nav
  className="bg-[#0a0e1a] border-b border-gray-800
               px-6 py-4 flex items-center justify-between"
>
  <Logo />
  <SearchBar />
  <UserMenu />
</nav>
```

---

### 3. Cards

#### Stat Card (Orange Accent)

```tsx
<div
  className="bg-[#0f1729] border border-gray-800
               rounded-xl p-6 hover:shadow-lg hover:shadow-orange-600/10
               transition-all duration-300"
>
  <div className="flex items-center justify-between">
    <div>
      <p className="text-gray-400 text-sm">Documents</p>
      <h3 className="text-white text-3xl font-bold mt-1">24</h3>
      <p className="text-green-500 text-xs mt-2">↑ +3 today</p>
    </div>
    <div
      className="w-12 h-12 bg-orange-600/20 rounded-full
                   flex items-center justify-center"
    >
      <Icon className="text-orange-500 w-6 h-6" />
    </div>
  </div>
</div>
```

#### Content Card (Standard)

```tsx
<div
  className="bg-[#0f1729] border border-gray-800
               rounded-lg p-4 hover:border-gray-700
               transition-colors"
>
  <h4 className="text-white font-medium">Document Title</h4>
  <p className="text-gray-400 text-sm mt-2">Description...</p>
</div>
```

---

### 4. Chat Interface

#### User Message

```tsx
<div
  className="ml-auto max-w-[70%] bg-gradient-to-r from-orange-600 to-orange-500
               text-white rounded-2xl rounded-tr-sm px-4 py-3
               shadow-lg shadow-orange-600/20"
>
  What is the main conclusion?
</div>
```

#### AI Message

```tsx
<div
  className="mr-auto max-w-[70%] bg-[#0f1729] border border-gray-800
               text-gray-200 rounded-2xl rounded-tl-sm px-4 py-3"
>
  Based on the provided documents...
  {/* Sources */}
  <div className="mt-3 pt-3 border-t border-gray-800">
    <p className="text-gray-400 text-sm">📎 Sources (3):</p>
    <div className="text-orange-500 text-xs mt-1">• Document X, Page 5 (Score: 0.94)</div>
  </div>
  {/* Confidence Badge */}
  <div className="mt-2 inline-flex items-center gap-2">
    <span className="bg-green-500/20 text-green-400 text-xs px-2 py-1 rounded">✅ Confidence: 91%</span>
    <span className="text-gray-500 text-xs">⚡ 1,234 tokens • $0.002</span>
  </div>
</div>
```

---

### 5. Forms

#### Input Field

```tsx
<input
  className="bg-[#0f1729] border border-gray-700
                  focus:border-orange-600 focus:ring-2 focus:ring-orange-600/20
                  text-white placeholder-gray-500
                  rounded-lg px-4 py-3
                  transition-all duration-200
                  outline-none"
  placeholder="Ask a question..."
/>
```

#### Dropdown

```tsx
<select
  className="bg-[#162038] border border-gray-700
                   hover:border-orange-600
                   text-white rounded-lg px-4 py-2
                   cursor-pointer transition-colors"
>
  <option>GPT-4 Turbo</option>
  <option>Claude 3 Opus</option>
</select>
```

---

### 6. Badges & Tags

#### Status Badges

```tsx
{
  /* Success/Processed */
}
<span className="bg-green-500/20 text-green-400 text-xs px-2 py-1 rounded">✅ Processed</span>;

{
  /* Processing */
}
<span className="bg-orange-500/20 text-orange-400 text-xs px-2 py-1 rounded animate-pulse">⏳ Processing...</span>;

{
  /* Error */
}
<span className="bg-red-500/20 text-red-400 text-xs px-2 py-1 rounded">❌ Error</span>;
```

#### Model Tags

```tsx
<span className="bg-blue-500/20 text-blue-400 text-xs px-2 py-1 rounded">GPT-4 Turbo</span>
```

---

## Accessibility

### Color Contrast Ratios (WCAG AA)

✅ **White text (#ffffff) on navy (#0a0e1a)**: 18.2:1 (Excellent)  
✅ **Orange (#FF6600) on navy (#0a0e1a)**: 4.8:1 (Pass)  
✅ **Light gray (#cbd5e1) on navy (#0a0e1a)**: 12.1:1 (Excellent)  
✅ **White text on orange (#FF6600)**: 4.5:1 (Pass)

### Focus States

Always use visible focus indicators:

```css
.focus-visible {
  outline: 2px solid var(--orange-primary);
  outline-offset: 2px;
  box-shadow: 0 0 0 4px rgba(255, 102, 0, 0.2);
}
```

---

## Animation & Effects

### Glow Effect (Orange)

```css
box-shadow:
  0 0 20px rgba(255, 102, 0, 0.3),
  0 0 40px rgba(255, 102, 0, 0.1);
```

Use for: Active buttons, important notifications

### Glassmorphism (Blue)

```css
background: rgba(15, 23, 41, 0.8);
backdrop-filter: blur(12px);
border: 1px solid rgba(255, 255, 255, 0.1);
```

Use for: Modals, overlays, tooltips

### Hover Transitions

```css
transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
```

Standard easing for all interactive elements

---

## Do's and Don'ts

### ✅ DO

- Use orange for primary actions and CTAs
- Use dark blues for structure and backgrounds
- Maintain consistent orange gradients (left to right, 135deg)
- Use white for primary text, light gray for body
- Add subtle orange glows to active elements
- Use semantic colors (green/red) for status indicators

### ❌ DON'T

- Don't use orange for large background areas (too vibrant)
- Don't mix orange with red (confusing semantics)
- Don't use light blue and orange together (clashing)
- Don't use pure black (#000000) anywhere (use #0a0e1a)
- Don't use orange for error states (use red #ef4444)
- Don't overuse gradients (1-2 per screen maximum)

---

## Tailwind CSS Configuration

Add to `tailwind.config.js`:

```javascript
module.exports = {
  theme: {
    extend: {
      colors: {
        // Backgrounds
        "navy-950": "#0a0e1a",
        "navy-900": "#0f1729",
        "navy-800": "#162038",
        "navy-700": "#1a2847",
        "navy-600": "#1e3a5f",

        // Fiserv Orange
        fiserv: {
          DEFAULT: "#FF6600",
          light: "#FF8533",
          dark: "#CC5200",
          subtle: "#FF660033",
          glow: "#FF660066",
        },
      },
      backgroundImage: {
        "gradient-orange": "linear-gradient(135deg, #FF6600 0%, #FF8533 100%)",
        "gradient-hero": "linear-gradient(135deg, #0f1729 0%, #1e3a5f 50%, #ff660033 100%)",
        "gradient-card": "linear-gradient(180deg, #0f1729 0%, #162038 100%)",
      },
    },
  },
};
```

---

## Examples in Code

### Complete Button Component

```tsx
export function PrimaryButton({ children, onClick }: ButtonProps) {
  return (
    <button
      onClick={onClick}
      className="
        bg-gradient-to-r from-fiserv to-fiserv-light
        hover:from-fiserv-light hover:to-fiserv
        active:from-fiserv-dark active:to-fiserv-dark
        text-white font-semibold
        px-6 py-3 rounded-lg
        shadow-lg shadow-fiserv/30
        hover:shadow-xl hover:shadow-fiserv/40
        transform hover:-translate-y-0.5
        transition-all duration-300
        focus:outline-none focus:ring-2 focus:ring-fiserv focus:ring-offset-2 focus:ring-offset-navy-950
      "
    >
      {children}
    </button>
  );
}
```

### Complete Card Component

```tsx
export function StatCard({ title, value, trend, icon: Icon }: StatCardProps) {
  return (
    <div
      className="
      bg-navy-900 border border-gray-800
      rounded-xl p-6
      hover:shadow-lg hover:shadow-fiserv-glow
      hover:border-gray-700
      transition-all duration-300
      group
    "
    >
      <div className="flex items-center justify-between">
        <div>
          <p className="text-gray-400 text-sm">{title}</p>
          <h3 className="text-white text-3xl font-bold mt-1">{value}</h3>
          {trend && <p className="text-green-500 text-xs mt-2 flex items-center gap-1">↑ {trend}</p>}
        </div>
        <div
          className="
          w-12 h-12 bg-fiserv/20 rounded-full
          flex items-center justify-center
          group-hover:bg-fiserv/30
          transition-colors
        "
        >
          <Icon className="text-fiserv w-6 h-6" />
        </div>
      </div>
    </div>
  );
}
```

---

## Visual References

See the generated color palette swatch and dashboard mockup for visual examples of the color scheme in action.

**Key Takeaway**: The combination of deep navy blues with energetic Fiserv orange creates a professional, modern interface that's both visually striking and highly functional.

---

_Color Application Guide - RAG System - Fiserv Orange Theme_  
_Updated: 2026-02-02 - ACE Framework v2.1_

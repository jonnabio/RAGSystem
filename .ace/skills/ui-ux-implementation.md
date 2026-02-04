# Skill: UI/UX Implementation

> Procedural knowledge for implementing modern, accessible user interfaces
> following design systems and component-based architecture.

---

## Purpose

Build consistent, accessible, and performant user interfaces that match
design specifications and provide excellent user experience.

---

## Prerequisites

- [ ] Review `docs/specs/UI_UX_Specification.md`
- [ ] Review `docs/specs/Color_Application_Guide.md`
- [ ] Review `docs/design/README.md` for component specs
- [ ] Access to design mockups in `docs/design/mockups/`
- [ ] Understanding of design system (colors, typography, spacing)

---

## Procedures

### 1. Setting Up the Design System

```markdown
Step 1: Configure Tailwind CSS

- Install Tailwind CSS and dependencies
- Configure tailwind.config.js with custom colors
- Add custom gradients to theme
- Setup font imports (Inter from Google Fonts)

Step 2: Create global styles

- Define CSS variables for colors
- Setup base typography
- Configure animations and transitions
- Add utility classes

Step 3: Install component library

- Setup shadcn/ui
- Install required components
- Configure theme tokens
- Test component rendering

Step 4: Verify setup

- Test color classes (navy-900, fiserv, etc.)
- Test gradients (bg-gradient-orange)
- Test typography (font-sans)
- Verify responsive utilities work
```

### 2. Implementing Components

```markdown
Component implementation workflow:

Step 1: Review design mockup

- Study visual design in mockups
- Note colors, spacing, sizing
- Identify states (hover, active, disabled)

Step 2: Create component file

- Use TypeScript for type safety
- Define props interface
- Document component purpose

Step 3: Build markup structure

- Use semantic HTML
- Apply Tailwind classes systematically
- Group related elements

Step 4: Add interactivity

- Implement event handlers
- Add loading/error states
- Handle edge cases

Step 5: Test component

- Visual regression test
- Interaction testing
- Accessibility testing
- Responsive testing
```

### 3. Applying the Color System

```markdown
When implementing UI with dark blue × Fiserv orange:

Background layers:
✅ Page background: bg-navy-950
✅ Cards/panels: bg-navy-900
✅ Elevated elements: bg-navy-800
✅ Hover states: bg-navy-700

Fiserv Orange usage:
✅ Primary buttons: bg-gradient-to-r from-fiserv to-fiserv-light
✅ Active navigation: bg-gradient-orange
✅ CTAs and important actions: text-fiserv
✅ Icons and accents: text-fiserv

Text colors:
✅ Headings: text-white
✅ Body text: text-gray-300 or text-gray-400
✅ Muted text: text-gray-500
✅ Links: text-orange-500 hover:text-orange-400

Never:
❌ Orange backgrounds for large areas
❌ Orange for error states (use red)
❌ Pure black #000000 (use navy-950)
```

### 4. Ensuring Accessibility

```markdown
Accessibility checklist for each component:

Keyboard Navigation:

- [ ] All interactive elements focusable
- [ ] Tab order is logical
- [ ] Escape closes modals/dropdowns
- [ ] Enter/Space activate buttons

Screen Reader Support:

- [ ] Semantic HTML used
- [ ] ARIA labels on icons
- [ ] ARIA live regions for dynamic content
- [ ] Alt text on images

Visual Accessibility:

- [ ] Color contrast meets WCAG AA (4.5:1 text, 3:1 UI)
- [ ] Focus indicators visible (orange ring)
- [ ] Text resizable to 200%
- [ ] No information conveyed by color alone

Interaction:

- [ ] Touch targets >44px (mobile)
- [ ] Error messages descriptive
- [ ] Loading states announced
- [ ] Forms have labels
```

### 5. Responsive Design

```markdown
Implementing responsive layouts:

Step 1: Mobile-first approach

- Design for mobile (< 640px) first
- Use base classes (no prefix)
- Stack elements vertically

Step 2: Add tablet breakpoints

- md: prefix for 768px+
- Adjust grid columns
- Show/hide elements

Step 3: Add desktop breakpoints

- lg: prefix for 1024px+
- xl: prefix for 1280px+
- Multi-column layouts
- Expand sidebars

Step 4: Test breakpoints

- Test at 375px (mobile)
- Test at 768px (tablet)
- Test at 1440px (desktop)
- Test between breakpoints
```

---

## Patterns

### Primary Button Component

```tsx
import { cn } from "@/lib/utils";

interface ButtonProps {
  children: React.ReactNode;
  onClick?: () => void;
  disabled?: boolean;
  loading?: boolean;
}

export function PrimaryButton({ children, onClick, disabled, loading }: ButtonProps) {
  return (
    <button onClick={onClick} disabled={disabled || loading} className={cn("bg-gradient-to-r from-fiserv to-fiserv-light", "hover:from-fiserv-light hover:to-fiserv", "active:from-fiserv-dark active:to-fiserv-dark", "text-white font-semibold", "px-6 py-3 rounded-lg", "shadow-lg shadow-fiserv/30", "hover:shadow-xl hover:shadow-fiserv/40", "transform hover:-translate-y-0.5", "transition-all duration-300", "disabled:opacity-50 disabled:cursor-not-allowed", "focus:outline-none focus:ring-2 focus:ring-fiserv focus:ring-offset-2 focus:ring-offset-navy-950")}>
      {loading ? (
        <span className="flex items-center gap-2">
          <LoadingSpinner />
          {children}
        </span>
      ) : (
        children
      )}
    </button>
  );
}
```

### Card Component

```tsx
interface CardProps {
  children: React.ReactNode;
  hover?: boolean;
  onClick?: () => void;
}

export function Card({ children, hover, onClick }: CardProps) {
  return (
    <div onClick={onClick} className={cn("bg-navy-900 border border-gray-800", "rounded-xl p-6", "transition-all duration-300", hover && ["hover:border-gray-700", "hover:shadow-lg hover:shadow-fiserv-glow", "cursor-pointer"])}>
      {children}
    </div>
  );
}
```

### Layout with Sidebar

```tsx
export function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex h-screen bg-navy-950">
      {/* Sidebar */}
      <aside className="w-64 bg-navy-900 border-r border-gray-800">
        <Navigation />
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-y-auto">
        <TopBar />
        <div className="p-6">{children}</div>
      </main>
    </div>
  );
}
```

### Form Input with Validation

```tsx
interface InputProps {
  label: string;
  error?: string;
  value: string;
  onChange: (value: string) => void;
}

export function Input({ label, error, value, onChange }: InputProps) {
  return (
    <div className="space-y-1">
      <label className="text-sm font-medium text-gray-300">{label}</label>
      <input type="text" value={value} onChange={(e) => onChange(e.target.value)} className={cn("w-full bg-navy-900 border", "text-white placeholder-gray-500", "rounded-lg px-4 py-3", "transition-all duration-200", "outline-none", error ? "border-red-500 focus:border-red-500 focus:ring-2 focus:ring-red-500/20" : "border-gray-700 focus:border-fiserv focus:ring-2 focus:ring-fiserv/20")} />
      {error && <p className="text-xs text-red-400">{error}</p>}
    </div>
  );
}
```

---

## Component Checklist

When building a new component, verify:

- [ ] **TypeScript**
  - [ ] Props interface defined
  - [ ] All types explicit
  - [ ] No `any` types

- [ ] **Styling**
  - [ ] Uses design system colors
  - [ ] Follows spacing scale
  - [ ] Responsive classes applied
  - [ ] Matches mockup design

- [ ] **Accessibility**
  - [ ] Semantic HTML
  - [ ] Keyboard navigable
  - [ ] ARIA attributes where needed
  - [ ] Focus indicators visible

- [ ] **States**
  - [ ] Default state
  - [ ] Hover state
  - [ ] Active/pressed state
  - [ ] Disabled state
  - [ ] Loading state (if applicable)
  - [ ] Error state (if applicable)

- [ ] **Testing**
  - [ ] Unit tests (if complex logic)
  - [ ] Visual regression test
  - [ ] Accessibility test
  - [ ] Responsive test

---

## Animation Guidelines

### Transition Timing

```css
/* Quick interactions */
transition: all 0.15s ease-out; /* Hover effects */

/* Standard interactions */
transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); /* Default */

/* Slow, emphasis */
transition: all 0.5s ease-in-out; /* Modals, drawers */
```

### Micro-interactions

```tsx
// Button press
<button className="transform active:scale-95 transition-transform" />

// Card hover
<div className="transform hover:-translate-y-1 hover:shadow-xl transition-all" />

// Fade in on mount
<div className="animate-in fade-in duration-300" />
```

### Loading States

```tsx
// Skeleton pulse
<div className="animate-pulse bg-navy-800 h-4 w-32 rounded" />

// Spinner
<div className="animate-spin rounded-full h-5 w-5 border-2 border-fiserv border-t-transparent" />
```

---

## Performance Optimization

### Code Splitting

```tsx
// Lazy load heavy components
const Analytics = lazy(() => import("./Analytics"));

<Suspense fallback={<LoadingSpinner />}>
  <Analytics />
</Suspense>;
```

### Image Optimization

```tsx
// Use Next.js Image
import Image from "next/image";

<Image
  src="/logo.png"
  width={48}
  height={48}
  alt="Logo"
  priority // for above-the-fold images
/>;
```

### Memoization

```tsx
// Memoize expensive computations
const sortedData = useMemo(() => data.sort((a, b) => a.date - b.date), [data]);

// Memoize callbacks
const handleClick = useCallback(() => onClick(id), [onClick, id]);
```

---

## Quality Checks

### Before Marking Component Complete

- [ ] **Visual Match**
  - [ ] Matches design mockup exactly
  - [ ] Colors correct (navy blues + orange)
  - [ ] Spacing matches design system
  - [ ] Typography correct (Inter font)

- [ ] **Functionality**
  - [ ] All interactions work
  - [ ] State management correct
  - [ ] Error handling implemented
  - [ ] Loading states shown

- [ ] **Code Quality**
  - [ ] TypeScript strict mode passes
  - [ ] No console errors/warnings
  - [ ] ESLint passes
  - [ ] Code is DRY (no duplication)

- [ ] **Performance**
  - [ ] No unnecessary re-renders
  - [ ] Images optimized
  - [ ] Bundle size reasonable
  - [ ] Lighthouse score > 90

---

## Common Pitfalls

1. **Not using design system** - Hardcoding colors instead of using tailwind classes
2. **Inconsistent spacing** - Not following 4px/8px grid
3. **Missing focus states** - Forgetting keyboard navigation
4. **Poor contrast** - Text not readable on backgrounds
5. **No loading states** - UI freezes during async operations
6. **Overusing orange** - Orange should be 20% max, not 50%
7. **Non-semantic HTML** - Using `<div>` instead of `<button>`
8. **Missing error boundaries** - App crashes instead of showing errors

---

## Debugging UI Issues

### Visual Issues

```markdown
1. Inspect element in DevTools
2. Check computed styles
3. Verify Tailwind classes applied
4. Check for CSS specificity conflicts
5. Verify parent container layout
```

### Responsive Issues

```markdown
1. Use DevTools device emulation
2. Check all breakpoints (sm, md, lg, xl)
3. Test landscape and portrait
4. Verify no horizontal scroll
5. Check flex/grid container behavior
```

### Accessibility Issues

```markdown
1. Run Lighthouse accessibility audit
2. Test with screen reader (NVDA/JAWS)
3. Test keyboard navigation only
4. Check color contrast ratios
5. Verify focus indicators visible
```

---

## Tools & Resources

### Development Tools

- **Tailwind CSS IntelliSense** - VSCode extension
- **React DevTools** - Component inspection
- **axe DevTools** - Accessibility testing
- **Lighthouse** - Performance/accessibility audit

### Design Resources

- **Mockups**: `docs/design/mockups/`
- **Color Palette**: `docs/design/assets/color-palette.png`
- **Component Specs**: `docs/design/README.md`
- **Color Guide**: `docs/specs/Color_Application_Guide.md`

### Testing

- **Jest** - Unit testing
- **React Testing Library** - Component testing
- **Playwright** - E2E testing
- **Chromatic** - Visual regression (optional)

---

## Invocation

```markdown
"Apply the UI/UX implementation skill from .ace/skills/ui-ux-implementation.md
for [component name | page]. Follow the design system and ensure accessibility
compliance. Reference mockups in docs/design/mockups/."
```

---

_Skill Version: 1.0 - RAG System Specific_

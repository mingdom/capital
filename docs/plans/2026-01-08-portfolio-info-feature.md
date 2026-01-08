# Portfolio Information Display Feature - Implementation Plan

## Design Vision: "Institutional Manifesto"

A bold, editorial-style portfolio information display that transforms typically dry fund documentation into a visually striking, easily navigable experience. Think high-end financial publications meet modern digital prospectus.

### Aesthetic Direction
- **Dark institutional editorial** - Leverages existing zinc-950 dark theme
- **Typography-driven hierarchy** - Large, confident headings with generous whitespace
- **Sectioned narrative flow** - Three distinct sections with visual identity
- **Subtle visual anchors** - Left accent bars, section numbers, and refined card treatments
- **Professional but memorable** - Clean enough for institutional clients, distinctive enough to stand out

### Research Findings

Based on research of institutional fund documentation practices ([SEC Prospectus Standards](https://www.investor.gov/introduction-investing/investing-basics/glossary/mutual-fund-prospectus), [Hedge Fund Strategies](https://www.cfainstitute.org/insights/professional-learning/refresher-readings/2025/hedge-fund-strategies)), standard fund information typically includes:

1. **Investment Objectives/Goals** - The "why"
2. **Investment Strategy & Mandate** - The "how" and "what"
3. **Management/Background** - The "who"
4. **Risks & Performance** (already covered in dashboard)

For Mingdom Capital, we'll structure this as **3 focused sections**:
1. **Philosophy** - Core beliefs and investment approach
2. **Strategy & Mandate** - How we execute, objectives, rules, and constraints
3. **About** - Fund background and team context

---

## Multi-Page UX Architecture

### Current State
The app currently has no multi-page infrastructure:
- Simple `layout.tsx` with fonts only
- Dashboard has its own isolated `Header` component
- No shared navigation or app shell

### New Architecture: Scalable App Shell

To support portfolio info AND future pages (reports, team, settings, etc.), we'll build:

**1. Shared App Header** (`/components/layout/app-header.tsx`)
- Sticky header with backdrop blur (matches existing)
- Logo/title on left
- **Navigation tabs in center** (Dashboard, Portfolio Info, [future pages])
- Action buttons on right (Follow Live Trades, etc.)
- Mobile: Hamburger menu for nav

**2. Updated Root Layout** (`/app/layout.tsx`)
- Add shared `AppHeader` to layout
- Remove header from individual pages
- Consistent navigation across all pages

**3. Page Routes**
- `/` - Dashboard (existing, remove local header)
- `/portfolio-info` - Portfolio Information (new)
- Future: `/reports`, `/team`, `/settings`, etc.

**4. Navigation State**
- Use Next.js `usePathname()` to highlight active page
- Smooth transitions between pages
- Maintain scroll position per page

### Header Navigation Design

**Desktop Layout:**
```
┌──────────────────────────────────────────────────────────────────┐
│  Mingdom Capital     [Dashboard] [Portfolio Info]     [Follow ↗] │
│                      ───────────                                 │
│                      └─ Active (purple underline)                │
└──────────────────────────────────────────────────────────────────┘
```

**Mobile Layout:**
```
┌──────────────────────────────────┐
│ ☰  Mingdom Capital      [Follow] │ <- Header with hamburger
└──────────────────────────────────┘

When hamburger tapped:
┌──────────────────────────────────┐
│                                  │
│  Navigation                      │
│  ───────────                     │
│                                  │
│  → Dashboard                     │
│    Portfolio Info                │
│                                  │
│  ────────────────────────────    │
│                                  │
│  [Follow Live Trades ↗]          │
│                                  │
└──────────────────────────────────┘
```

**States:**
- **Active page**: Purple bottom border (2px), brighter text
- **Hover**: Text opacity 80%, smooth transition
- **Mobile drawer**: Slide from right, overlay backdrop

This architecture ensures:
- ✅ Clean separation of concerns (layout vs page content)
- ✅ Consistent navigation UX
- ✅ Easy to add new pages in the future
- ✅ Matches existing aesthetic (dark, refined, professional)

---

## Technical Architecture

### 1. Content Management (Markdown-Based)

**Location:** `/content/portfolio/`

```
content/
└── portfolio/
    ├── 01-philosophy.md        # Core investment philosophy & beliefs
    ├── 02-strategy-mandate.md  # Investment strategy, objectives, rules & constraints
    └── 03-about.md             # Fund background, team, context
```

**Section Breakdown:**

1. **Philosophy** (`01-philosophy.md`)
   - Core investment beliefs
   - Value proposition
   - Investment approach fundamentals
   - What makes the strategy unique

2. **Strategy & Mandate** (`02-strategy-mandate.md`)
   - How we execute the philosophy
   - Fund objectives and goals
   - Asset allocation framework
   - Investment rules and constraints
   - Position sizing and risk limits
   - Portfolio construction guidelines

3. **About** (`03-about.md`)
   - Fund background and history
   - Team expertise and track record
   - Why this team is qualified
   - Institutional context

**Benefits:**
- Easy updates via markdown files (no code changes needed)
- Version controlled alongside codebase
- Can be edited by non-technical team members
- Supports rich formatting (lists, tables, emphasis, links)
- Numbered file names ensure consistent ordering

### 2. Markdown Processing

**New utility:** `/lib/portfolio-content.ts`

- Parse markdown files using `remark` + `remark-html`
- Add frontmatter support (YAML) for metadata (title, order, icon, color accent)
- Cache parsed content for performance
- Type-safe content loading

**Dependencies to add:**
```json
{
  "remark": "^15.0.1",
  "remark-html": "^16.0.1",
  "gray-matter": "^4.0.3"
}
```

### 3. UI Components

#### A. Shared App Header: `/components/layout/app-header.tsx`
- Replaces dashboard's local header
- Sticky header with backdrop blur
- Navigation tabs (Dashboard, Portfolio Info)
- Logo/title on left, action buttons on right
- Mobile hamburger menu with slide-out drawer
- Active page highlighting

#### B. New Page Route: `/app/portfolio-info/page.tsx`
- Dedicated page for portfolio information
- Client component with section navigation
- Framer Motion page transitions
- Responsive layout (sidebar nav on desktop, tabs on mobile)

#### C. New Component: `/components/portfolio/portfolio-section.tsx`
- Renders individual sections (Philosophy, Strategy & Mandate, About)
- Custom markdown styling matching dark aesthetic
- Section numbering and accent colors
- Smooth scroll anchors

#### D. New Component: `/components/portfolio/section-navigation.tsx`
- Sticky sidebar navigation (desktop)
- Tab navigation (mobile)
- Active section highlighting
- Smooth scroll to sections

#### E. Markdown Styling: `/components/portfolio/markdown-content.tsx`
- Wrapper component with prose styling
- Custom heading styles (Bricolage Grotesque, large sizes)
- List styling with custom bullets
- Table styling matching existing design
- Code block styling with Geist Mono
- Blockquote styling with left accent bar

#### F. Mobile Navigation: `/components/layout/mobile-nav.tsx`
- Slide-out drawer for mobile navigation
- Animated overlay
- Close on route change

### 4. Design System Extensions

**New CSS in `/app/globals.css`:**
- `.portfolio-prose` class for markdown content styling
- Custom heading scales (larger than default)
- Section accent colors (purple, blue, emerald)
- Left border treatments

**Color Assignments:**
- Philosophy: Purple (`#7c3aed` - matches existing Mingdom color)
- Strategy & Mandate: Blue (`#3b82f6` - matches Fidelity color)
- About: Emerald (`#10b981` - matches gains/SPY color)

### 5. Navigation Integration

**Update `/app/layout.tsx`:**
- Add `<AppHeader />` component to root layout
- Wrap children in proper container/padding structure
- Ensure consistent spacing for all pages

**Update `/app/page.tsx`:**
- Remove existing local `Header` component
- Remove header-related state/logic
- Content starts directly (no redundant header)

**Create `/app/portfolio-info/page.tsx`:**
- New route accessible via `/portfolio-info`
- No local header (uses shared AppHeader from layout)
- Focus entirely on content presentation

---

## Detailed Component Design

### Portfolio Info Page Layout

**Desktop View (≥1024px):**
```
┌─────────────────────────────────────────────────────────────────┐
│  Mingdom Capital     [Dashboard] [Portfolio Info]     [Follow]  │ <- Shared AppHeader
└─────────────────────────────────────────────────────────────────┘

┌───────────────┬─────────────────────────────────────────────────┐
│               │                                                 │
│  Navigation   │  01  Investment Philosophy                      │
│  (Sticky)     │  ══                                             │
│               │                                                 │
│  → Philosophy │  # Investment Philosophy (Large Bricolage)      │
│    Strategy   │                                                 │
│    About      │  ## Core Beliefs                                │
│               │                                                 │
│               │  Our investment philosophy is built on...       │
│               │                                                 │
│               │  • Long-term focus: We hold quality...          │
│               │  • Concentrated conviction: Better to...        │
│               │  • Quality first: We prioritize...              │
│               │                                                 │
│               │  ──────────────────────────────────────────────  │
│               │                                                 │
│               │  02  Strategy & Mandate                         │
│               │  ══                                             │
│               │                                                 │
│               │  # Investment Strategy & Fund Mandate           │
│               │  ...                                            │
│               │                                                 │
└───────────────┴─────────────────────────────────────────────────┘
```

**Mobile View (<768px):**
```
┌────────────────────────────────────┐
│ ☰  Mingdom Capital        [Follow] │ <- Header with hamburger
└────────────────────────────────────┘

┌────────────────────────────────────┐
│ [Philosophy] [Strategy] [About]    │ <- Tab navigation
│ ───────────                        │
└────────────────────────────────────┘

┌────────────────────────────────────┐
│                                    │
│  01  Investment Philosophy         │
│  ══                                │
│                                    │
│  # Investment Philosophy           │
│                                    │
│  ## Core Beliefs                   │
│                                    │
│  Our investment philosophy...      │
│                                    │
│  • Long-term focus...              │
│  • Concentrated conviction...      │
│                                    │
│  [Content continues...]            │
│                                    │
└────────────────────────────────────┘
```

### Portfolio Section Component

**Visual Treatment:**
```
┌──────────────────────────────────────────────────────────────┐
│ ┃                                                            │ <- 4px purple accent bar
│ ┃  01  Investment Philosophy                                │
│ ┃  ══                                                        │
│ ┃                                                            │
│ ┃  # Investment Philosophy  (text-5xl, Bricolage Grotesque) │
│ ┃                                                            │
│ ┃  ## Core Beliefs  (text-4xl)                              │
│ ┃                                                            │
│ ┃  Our investment philosophy is built on a foundation...    │
│ ┃                                                            │
│ ┃  • Long-term focus: We hold quality positions...          │
│ ┃  • Concentrated conviction: Better to own...              │
│ ┃  • Quality first: We prioritize sustainable...            │
│ ┃                                                            │
│ ┃  > "In the short run, the market is a voting machine..."  │
│ ┃    - Benjamin Graham                                      │
│ ┃                                                            │
└──────────────────────────────────────────────────────────────┘
```

**Key Features:**
- 4-6px left accent bar in section color (purple/blue/emerald)
- Section number (01, 02, 03) in muted zinc-500 with monospace font
- Large heading hierarchy (5xl → 4xl → 2xl)
- Generous vertical spacing (my-16 between sections, my-12 before H2)
- Fade-in animation on load (Framer Motion stagger)
- No card background - let content breathe with whitespace
- Blockquotes have left border in accent color

### Section Navigation

**Desktop (Sticky Sidebar):**
```
┌──────────────┬───────────────────┐
│ 01 Philosophy│                   │
│ 02 Mandates  │  [Content Area]   │
│ 03 Rules     │                   │
│              │                   │
│  (sticky)    │   (scrollable)    │
└──────────────┴───────────────────┘
```

**Mobile (Tabs):**
```
┌─────────────────────────────────┐
│ [Philosophy] [Mandates] [Rules] │ <- Tabs
├─────────────────────────────────┤
│                                 │
│      [Content Area]             │
│                                 │
└─────────────────────────────────┘
```

### Markdown Content Styling

**Headings:**
- H1: `text-5xl font-bold` (Bricolage Grotesque)
- H2: `text-4xl font-bold mt-12 mb-4`
- H3: `text-2xl font-semibold mt-8 mb-3`

**Lists:**
- Custom bullet style (colored dot matching section)
- Increased line height (leading-relaxed)
- Spacing between items (space-y-2)

**Blockquotes:**
- Left purple border (border-l-4)
- Italic text
- Background: zinc-800/50
- Padding: px-6 py-4

**Tables:**
- Match existing table styling from dashboard
- Zebra striping with zinc-800/30
- Monospace font for numbers

**Code:**
- Inline: zinc-800 background, emerald-400 text
- Block: Match syntax highlighting if needed

---

## Content Structure Examples

### 01-philosophy.md
```markdown
---
title: Investment Philosophy
order: 1
icon: Lightbulb
accent: purple
---

# Investment Philosophy

## Core Beliefs

Our investment philosophy is built on a foundation of rigorous analysis and patient capital:

- **Long-term focus**: We hold quality positions for years, not quarters. Time is our competitive advantage.
- **Concentrated conviction**: Better to own 10 great businesses we deeply understand than 100 mediocre ones.
- **Quality first**: We prioritize sustainable competitive advantages and strong fundamentals over market sentiment.

## Our Approach

We seek businesses with:
- **Durable competitive moats**: Pricing power, network effects, or high switching costs
- **Strong capital allocation**: Management teams that deploy capital intelligently
- **Aligned incentives**: Founders or insider ownership that aligns with shareholders

> "In the short run, the market is a voting machine, but in the long run, it's a weighing machine." - Benjamin Graham

## What Makes Us Different

Unlike many funds that chase quarterly performance, we optimize for multi-year compounding. We're willing to look foolish in the short term if the long-term thesis remains intact.
```

### 02-strategy-mandate.md
```markdown
---
title: Strategy & Mandate
order: 2
icon: Target
accent: blue
---

# Investment Strategy & Fund Mandate

## Fund Objectives

Our primary objectives, in order of priority:

1. **Long-term capital appreciation** - Achieve above-market returns over rolling 3-year periods
2. **Capital preservation** - Limit maximum drawdown to -30% in severe market downturns
3. **Benchmark outperformance** - Exceed S&P 500 total returns net of fees

## Investment Strategy

### Stock Selection Process
1. **Screen for quality**: ROE > 15%, debt/equity < 50%, consistent earnings growth
2. **Deep fundamental analysis**: Business model, competitive position, management quality
3. **Valuation discipline**: Only buy when price offers adequate margin of safety
4. **Position sizing**: Scale position size with conviction and risk-adjusted return potential

### Asset Allocation Framework

| Asset Class | Target % | Range    | Rationale                    |
|-------------|----------|----------|------------------------------|
| Equities    | 80%      | 70-90%   | Primary return driver        |
| Cash        | 20%      | 10-30%   | Dry powder for opportunities |

## Portfolio Construction Rules

### Position Sizing
- **Maximum single position**: 15% of portfolio
- **Minimum position size**: 2% of portfolio
- **Typical position count**: 10-15 stocks (concentrated)

### Diversification
- **Sector limits**: No more than 30% in any single sector
- **Geographic exposure**: Primarily US equities, up to 20% international
- **Market cap flexibility**: Focus on large/mega caps, but opportunistic in mid-caps

### Risk Management

**Hard stops:**
- Maximum portfolio volatility: 20% annualized
- Individual position stop loss: -20% from entry price (reviewed case-by-case)
- Maximum portfolio drawdown tolerance: -30%

**Rebalancing triggers:**
- Positions exceeding 20% due to appreciation: Trim to 15%
- Positions falling below 2%: Evaluate for exit or re-sizing

## Benchmark & Reporting

- **Primary benchmark**: S&P 500 Total Return
- **Reporting frequency**: Monthly performance updates, quarterly deep dives
- **Transparency**: All holdings disclosed with 30-day lag
```

### 03-about.md
```markdown
---
title: About the Fund
order: 3
icon: Users
accent: emerald
---

# About Mingdom Capital

## Fund Background

Mingdom Capital was founded to provide institutional-quality portfolio management with a focus on transparency, alignment, and long-term value creation.

### Key Milestones
- **Founded**: [Year]
- **Strategy**: Concentrated long equity
- **Track record**: [Years] of audited performance
- **AUM**: [Amount] (as of [Date])

## Investment Team

Our team combines deep fundamental analysis expertise with decades of public markets experience:

### [Portfolio Manager Name]
- **Role**: Chief Investment Officer & Portfolio Manager
- **Background**: [X years] managing concentrated equity portfolios
- **Prior experience**: [Previous firms/roles]
- **Education**: [Degrees/certifications]

### Investment Philosophy Alignment
- Portfolio manager has [X%] of personal net worth invested alongside clients
- No outside mandates - 100% focused on Mingdom Capital strategy
- Compensation tied to long-term absolute and risk-adjusted returns

## Why This Team

What differentiates our approach:

1. **Skin in the game**: We eat our own cooking. PM capital is invested pro-rata with clients.
2. **Patient capital**: No redemption pressure allows genuine long-term focus.
3. **Intellectual honesty**: We publish mistakes, lessons learned, and evolving views.
4. **Institutional rigor**: Daily risk monitoring, systematic rebalancing, professional operations.

## Track Record Highlights

[This section would include relevant performance metrics, but avoid specific numbers unless verified and compliant with regulations]

- Consistent outperformance vs. S&P 500 over rolling 3-year periods
- Lower maximum drawdown than benchmark during major corrections
- Top quartile risk-adjusted returns (Sharpe ratio) vs. peer group

---

*Note: Past performance is not indicative of future results. All investments carry risk, including loss of principal.*
```

---

## Implementation Steps

### Phase 1: Multi-Page Infrastructure
1. Create `/components/layout/app-header.tsx` - Shared header with navigation
2. Create `/components/layout/mobile-nav.tsx` - Mobile navigation drawer
3. Update `/app/layout.tsx` - Add AppHeader to root layout
4. Update `/app/page.tsx` - Remove local Header component
5. Test navigation between pages (even though portfolio-info doesn't exist yet)

### Phase 2: Foundation Setup
6. Create `/content/portfolio/` directory structure
7. Install markdown parsing dependencies (`remark`, `remark-html`, `gray-matter`)
8. Create sample markdown files with frontmatter:
   - `01-philosophy.md` (use examples from plan as template)
   - `02-strategy-mandate.md`
   - `03-about.md` (user will fill in real details)
9. Build `/lib/portfolio-content.ts` utility with parsing functions

### Phase 3: Portfolio Info Components
10. Create `/components/portfolio/markdown-content.tsx` with styled prose wrapper
11. Create `/components/portfolio/portfolio-section.tsx` for section rendering
12. Create `/components/portfolio/section-navigation.tsx` for desktop/mobile nav
13. Add portfolio-specific CSS to `/app/globals.css`

### Phase 4: Portfolio Info Page
14. Create `/app/portfolio-info/page.tsx` route
15. Implement section navigation (sidebar on desktop, tabs on mobile)
16. Add scroll animations and section highlighting
17. Connect markdown content to components

### Phase 5: Polish & Testing
18. Test markdown rendering with various content types (headings, lists, tables, quotes)
19. Ensure responsive behavior across breakpoints
20. Add loading states and error handling for markdown parsing
21. Verify animations and transitions (Framer Motion)
22. Test navigation flow (Dashboard ↔ Portfolio Info)
23. Verify build succeeds (`make build`)

---

## Critical Files to Create/Modify

### New Files - Multi-Page Infrastructure
- `/components/layout/app-header.tsx` - Shared header with navigation tabs
- `/components/layout/mobile-nav.tsx` - Mobile slide-out navigation drawer

### New Files - Content
- `/content/portfolio/01-philosophy.md` - Investment philosophy content
- `/content/portfolio/02-strategy-mandate.md` - Strategy, objectives, rules content
- `/content/portfolio/03-about.md` - Fund background and team

### New Files - Portfolio Info Feature
- `/lib/portfolio-content.ts` - Markdown parsing utilities
- `/components/portfolio/markdown-content.tsx` - Styled markdown wrapper
- `/components/portfolio/portfolio-section.tsx` - Section component with accent styling
- `/components/portfolio/section-navigation.tsx` - Desktop/mobile section navigation
- `/app/portfolio-info/page.tsx` - Portfolio info page route

### Modified Files
- `/app/layout.tsx` - Add AppHeader component, update structure
- `/app/page.tsx` - Remove local Header component, simplify structure
- `/app/globals.css` - Add portfolio prose styling and section accent colors
- `/package.json` - Add markdown parsing dependencies (remark, remark-html, gray-matter)

---

## Design Specifications

### Typography Scale
- **Section Number**: `text-sm` (0.875rem), `text-zinc-500`, `font-mono`
- **Section Title**: `text-5xl` (3rem), `font-bold`, `tracking-tight`, Bricolage Grotesque
- **H2**: `text-4xl` (2.25rem), `font-bold`
- **H3**: `text-2xl` (1.5rem), `font-semibold`
- **Body**: `text-base` (1rem), Geist Sans, `leading-relaxed`

### Spacing
- **Between sections**: `mb-24` (6rem)
- **Before H2**: `mt-12` (3rem)
- **Before H3**: `mt-8` (2rem)
- **Paragraph spacing**: `mb-4` (1rem)
- **List item spacing**: `space-y-2` (0.5rem)

### Colors
- **Philosophy accent**: `border-purple-500`, `text-purple-400`
- **Mandates accent**: `border-blue-500`, `text-blue-400`
- **Rules accent**: `border-emerald-500`, `text-emerald-400`
- **Section background**: `bg-zinc-900`, `border-zinc-800`

### Animations
- **Section fade-in**: Framer Motion `fadeIn` with stagger (0.1s delay)
- **Nav highlight**: Smooth transition on active state (200ms)
- **Scroll**: `scroll-smooth` behavior

---

## Verification & Testing

### End-to-End Testing Flow

1. **Multi-Page Navigation**:
   - Navigate between Dashboard and Portfolio Info using header tabs
   - Verify active tab highlighting (purple underline on active page)
   - Test mobile hamburger menu (open/close drawer, navigate, auto-close on route change)
   - Ensure back/forward browser buttons work correctly
   - Verify URL changes to `/portfolio-info` and `/` correctly

2. **Content Management**:
   - Edit `/content/portfolio/01-philosophy.md` and verify changes appear on page reload
   - Test frontmatter parsing (title, order, icon, accent color)
   - Verify markdown features render correctly:
     - Headings (H1, H2, H3)
     - Bold and italic text
     - Lists (ordered and unordered)
     - Tables with proper styling
     - Blockquotes with left accent bar
     - Code blocks (inline and block)

3. **Visual Rendering**:
   - Check typography hierarchy on desktop and mobile
   - Verify accent colors for each section (purple, blue, emerald)
   - Verify section numbers display correctly (01, 02, 03)
   - Test dark theme contrast and readability
   - Ensure left accent bars appear on sections
   - Check animations are smooth and performant (Framer Motion fade-in)

4. **Section Navigation** (within Portfolio Info page):
   - Test sidebar navigation on desktop (sticky behavior, active highlighting)
   - Test tab navigation on mobile (smooth switching between sections)
   - Verify smooth scroll to sections when clicking nav items
   - Check active section updates as you scroll

5. **Responsive Behavior**:
   - **Mobile (< 768px)**:
     - Header shows hamburger menu
     - Section navigation shows as tabs
     - Content is single column
     - Typography scales appropriately
   - **Tablet (768-1024px)**:
     - Header shows full nav tabs
     - Section sidebar appears
     - Content layout adjusts
   - **Desktop (> 1024px)**:
     - Full header with all elements
     - Sticky sidebar navigation
     - Generous whitespace and typography

6. **Build & Integration**:
   - Run `make build` to verify production build succeeds
   - Check bundle size impact of markdown dependencies (should be <50KB gzipped)
   - Verify static export works correctly (no server-side dependencies)
   - Test `make web` for development mode
   - Ensure no console errors or warnings

7. **Cross-Browser Testing**:
   - Chrome/Edge (Chromium)
   - Firefox
   - Safari (especially test backdrop-blur on header)

---

## Future Enhancements (Out of Scope)

- Search functionality within portfolio content
- Export to PDF functionality
- Version history/changelog for content updates
- Multi-language support
- Comparison view (current vs previous versions)
- Analytics tracking (which sections are most viewed)

---

## Why This Approach Works

1. **Markdown-based content** = Easy updates without code changes
2. **Version controlled** = Track changes, revert if needed, review process
3. **Type-safe** = TypeScript ensures data integrity
4. **Performant** = Static generation, cached parsing
5. **Scalable** = Easy to add new sections or content types
6. **Distinctive** = Bold typography and editorial layout stands out from typical fund docs
7. **Accessible** = Semantic HTML, proper heading hierarchy, keyboard navigation
8. **Maintainable** = Clean separation of content and presentation

This feature transforms portfolio documentation from a necessary evil into a compelling, professionally distinctive showcase of fund philosophy and strategy.

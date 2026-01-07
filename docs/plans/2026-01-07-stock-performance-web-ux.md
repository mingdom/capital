# Stock Performance Web UX Design Plan

**Date:** 2026-01-07
**Status:** Draft
**Feature:** Stock Performance Rankings
**Related:** `docs/plans/2026-01-07-portfolio-reports-feature.md`

---

## Design Thinking

### Purpose
Display individual stock performance rankings from the portfolio, enabling quick identification of best/worst performers across multiple timeframes. This is a **conviction validator** — helping investors understand which positions are driving returns and which are dragging.

### Audience
- Self-managed investors reviewing portfolio composition
- Investment professionals needing quick performance snapshots
- Anyone making rebalancing decisions

### Tone: **Editorial Data Visualization**
Magazine-quality data presentation meets Bloomberg terminal efficiency. Clean, authoritative, information-dense but not overwhelming. Think *Financial Times* portfolio section meets modern SaaS dashboard.

### Differentiation: The Unforgettable Element
**The "Conviction Heat Strip"** — A horizontal gradient bar at the top of the section showing portfolio conviction through color-coded performance density. Losers on the left (deep red), winners on the right (emerald), with the portfolio's "center of gravity" marked. At a glance, you see if your portfolio is net positive/negative.

---

## Visual Design Specifications

### Typography

| Element | Font | Weight | Size | Notes |
|---------|------|--------|------|-------|
| Section Title | DM Sans | 700 | 1.5rem | Tracking tight, uppercase |
| Period Tabs | DM Sans | 500 | 0.875rem | Tab styling |
| Table Headers | DM Sans | 600 | 0.75rem | Uppercase, letter-spacing: 0.05em |
| Stock Symbol | JetBrains Mono | 600 | 0.875rem | Monospace for alignment |
| Return Values | JetBrains Mono | 700 | 1rem | Color-coded |
| Allocation | DM Sans | 400 | 0.8rem | Muted |

**Rationale:** DM Sans for editorial authority, JetBrains Mono for data precision. Avoids Inter/Roboto/system fonts per skill guidelines.

### Color Palette (Dark Mode Extension)

```css
/* Performance Colors */
--perf-extreme-gain: #10b981;    /* emerald-500 */
--perf-gain: #34d399;            /* emerald-400 */
--perf-slight-gain: #6ee7b7;     /* emerald-300, muted */
--perf-neutral: #71717a;         /* zinc-500 */
--perf-slight-loss: #fca5a5;     /* red-300, muted */
--perf-loss: #f87171;            /* red-400 */
--perf-extreme-loss: #ef4444;    /* red-500 */

/* Heat Strip Gradient */
--heat-gradient: linear-gradient(
  90deg,
  #7f1d1d 0%,      /* red-900 */
  #ef4444 25%,     /* red-500 */
  #71717a 50%,     /* zinc-500 */
  #10b981 75%,     /* emerald-500 */
  #065f46 100%     /* emerald-900 */
);

/* Card Surfaces */
--surface-elevated: #1c1c1f;     /* Slightly lifted from zinc-900 */
--surface-hover: #26262a;
```

### Layout Structure

```
┌─────────────────────────────────────────────────────────────────────┐
│  STOCK PERFORMANCE                                    [3M] [YTD] [1Y] │
├─────────────────────────────────────────────────────────────────────┤
│  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓│  ← Heat Strip
│                                        ▲                             │
│                                    Net: +12.4%                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌─ TOP PERFORMERS ──────────────────────────────────────────────┐   │
│  │                                                                │   │
│  │  1  APP     +104.2%    $673.74  ███████████████░░░  1.4%     │   │
│  │  2  GOOGL    +60.8%    $313.11  ███████████░░░░░░░ 17.6%     │   │
│  │  3  TSM      +45.6%    $303.83  ████████░░░░░░░░░░  3.2%     │   │
│  │  4  META     +38.2%    $660.19  ███████░░░░░░░░░░░  9.6%     │   │
│  │  5  MA       +28.4%    $570.87  █████░░░░░░░░░░░░░  7.9%     │   │
│  │                                                                │   │
│  └────────────────────────────────────────────────────────────────┘   │
│                                                                       │
│  ┌─ BOTTOM PERFORMERS ───────────────────────────────────────────┐   │
│  │                                                                │   │
│  │  26 ADBE    -17.2%     $349.99  ░░░░░░░░░░░░░████░  0.9%     │   │
│  │  27 CRM     -17.9%     $264.91  ░░░░░░░░░░░░████░░  1.4%     │   │
│  │  28 FIG     -45.0%     $37.37   ░░░░░░░░██████████  0.4%     │   │
│  │                                                                │   │
│  └────────────────────────────────────────────────────────────────┘   │
│                                                                       │
│  [Show all 30 holdings ↓]                                            │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Component Architecture

### File Structure

```
web/components/
├── holdings/
│   ├── stock-performance-section.tsx   # Main section wrapper
│   ├── conviction-heat-strip.tsx       # The signature visual element
│   ├── performance-table.tsx           # Ranked table component
│   ├── performance-row.tsx             # Individual stock row
│   └── period-tabs.tsx                 # 3M/YTD/1Y selector
```

### Component Breakdown

#### 1. `StockPerformanceSection` (Container)
- Fetches performance data from API/static JSON
- Manages period state (3mo, ytd, 1y)
- Orchestrates child components
- Handles loading/error states with skeleton

#### 2. `ConvictionHeatStrip`
The hero visual — a horizontal gradient strip showing distribution of gains/losses:
- Width represents full range (worst performer to best performer)
- Marker shows portfolio-weighted center of gravity
- Hover reveals detailed breakdown
- Subtle animation on period change (gradient shifts)

**Visual Effect:**
```css
.heat-strip {
  background: var(--heat-gradient);
  height: 8px;
  border-radius: 4px;
  position: relative;
}

.heat-strip::after {
  /* Marker for net performance */
  content: '';
  position: absolute;
  top: -8px;
  width: 2px;
  height: 24px;
  background: white;
  box-shadow: 0 0 8px rgba(255,255,255,0.5);
  transition: left 0.6s ease-out;
}
```

#### 3. `PerformanceTable`
Dual-section table showing top and bottom performers:
- Animated row entrance (staggered fade-in from edge toward center)
- Expandable to show all holdings
- Sortable columns (click header to re-sort)

#### 4. `PerformanceRow`
Individual stock row with:
- Rank badge (left edge, subtle)
- Stock symbol (monospace, bold)
- Return percentage (color-coded by magnitude)
- Current price
- Inline "return bar" — mini progress bar showing relative performance
- Portfolio allocation (right edge, muted)

**Return Bar Effect:**
A horizontal bar where width represents relative return magnitude:
- Green fill for positive, grows right
- Red fill for negative, grows left from center

#### 5. `PeriodTabs`
Tab selector for 3mo/YTD/1Y:
- Pill-style active indicator
- Smooth underline animation on change
- Keyboard accessible

---

## Interaction Design

### Micro-animations

| Interaction | Animation | Duration | Easing |
|-------------|-----------|----------|--------|
| Period tab change | Heat strip gradient shift + table fade/slide | 400ms | ease-out |
| Table row hover | Subtle glow + slight lift | 150ms | ease-in-out |
| Expand all holdings | Accordion reveal with staggered rows | 300ms + 30ms stagger | ease-out |
| Initial load | Skeleton → fade in, heat strip "paints" | 600ms | ease-out |

### Hover States

**Stock Row:**
```css
.performance-row:hover {
  background: var(--surface-hover);
  transform: translateX(2px);
  box-shadow: inset 4px 0 0 var(--perf-gain); /* or --perf-loss */
}
```

**Heat Strip:**
- Hover reveals tooltip with detailed breakdown
- Shows count of gainers vs losers
- Shows weighted average return

### Responsive Behavior

| Breakpoint | Adaptation |
|------------|------------|
| Desktop (>1024px) | Full table with all columns, heat strip with labels |
| Tablet (768-1024px) | Compressed columns, allocation hidden |
| Mobile (<768px) | Card layout replaces table, heat strip simplified |

---

## Data Contract

### API Endpoint (proposed)

```
GET /api/holdings/performance?period=3mo
```

### Response Shape

```typescript
interface StockPerformanceResponse {
  period: '3mo' | 'ytd' | '1y';
  generated_at: string;
  summary: {
    net_return: number;           // Weighted portfolio return
    gainers_count: number;
    losers_count: number;
    avg_return: number;
  };
  holdings: StockPerformance[];
}

interface StockPerformance {
  rank: number;
  symbol: string;
  current_price: number;
  period_start_price: number;
  period_return: number;          // Decimal, e.g., 0.45 = 45%
  allocation: number;             // Portfolio weight
  total_return: number;           // Since purchase
}
```

### Static Data Option (MVP)

Generate `web/public/data/holdings-performance.json` via Python script similar to existing `export_web_data.py`:

```json
{
  "generated_at": "2026-01-07T09:00:00Z",
  "periods": {
    "3mo": {
      "summary": { ... },
      "holdings": [ ... ]
    },
    "ytd": { ... },
    "1y": { ... }
  }
}
```

---

## Implementation Phases

### Phase 1: Data Pipeline (Python)
- [ ] Create `scripts/export_holdings_performance.py`
- [ ] Generate `holdings-performance.json` with all 3 periods
- [ ] Add to `make web-export` pipeline

### Phase 2: Basic Component (React)
- [ ] Create `stock-performance-section.tsx`
- [ ] Create `performance-table.tsx` with basic styling
- [ ] Add period tabs (3mo/YTD/1Y)
- [ ] Integrate into main dashboard page

### Phase 3: Hero Visual — Conviction Heat Strip
- [ ] Create `conviction-heat-strip.tsx`
- [ ] Implement gradient + marker positioning
- [ ] Add tooltip on hover
- [ ] Animate on period change

### Phase 4: Polish & Animation
- [ ] Add row hover effects
- [ ] Implement staggered entrance animation
- [ ] Add expand/collapse for full list
- [ ] Mobile responsive layout
- [ ] Loading skeleton

---

## Accessibility Requirements

- [ ] Period tabs keyboard navigable (arrow keys)
- [ ] Table sortable via keyboard
- [ ] Color-coding has text fallback ("+45.2%" vs just green)
- [ ] Heat strip has aria-label with summary
- [ ] Reduced motion preference respected

---

## Success Metrics

- [ ] Component renders in <100ms (no blocking)
- [ ] Heat strip properly reflects weighted performance
- [ ] All holdings display correct period returns
- [ ] Mobile layout usable on 375px width
- [ ] Matches existing dashboard aesthetic (dark mode, zinc palette)
- [ ] Distinctive enough to be memorable ("that heat strip thing")

---

## Open Design Questions

1. **Heat Strip Positioning:** Top of section (hero) or inline with table header?
2. **Default Period:** 3mo most actionable, or YTD for consistency with hero cards?
3. **Show All Toggle:** Start collapsed (top/bottom 5) or expanded?
4. **Benchmark Column:** Add SPY return for same period in each row for comparison?
5. **Sorting:** Default by return? Or by allocation (what matters most)?

---

## Visual Mockup Reference

*Generate with image tool to visualize the heat strip and table design*

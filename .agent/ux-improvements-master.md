# Web Dashboard UX Improvements - Master List

**Created**: 2026-01-07
**Last Updated**: 2026-01-07
**Status**: Prioritized backlog for implementation

---

## Executive Summary

This document consolidates all identified UX issues and improvement opportunities for the Mingdom Capital web dashboard. Issues are categorized by type and prioritized based on user impact, alignment with UX best practices, and implementation complexity.

---

## Priority Matrix

| Priority | Impact | Effort | Criteria |
|----------|--------|--------|----------|
| **P0 - Critical** | High | Low-Med | Broken user flows, data confusion, visual breaks |
| **P1 - High** | High | Med | Major UX friction, information architecture issues |
| **P2 - Medium** | Med | Med | Polish, consistency, and optimization |
| **P3 - Low** | Low | Varies | Nice-to-have, aesthetic refinements |

---

## P0 - Critical Issues

### 1. ☐ "STOCK PERFORMANCE" Title Breaks Theme Consistency
**Location**: `components/holdings/stock-performance-section.tsx` line 52
**Issue**: The all-caps "Stock Performance" heading uses uppercase styling (`uppercase tracking-tight`) that differs from the `Section` component's title styling (`text-lg font-semibold`). This breaks visual cohesion.
**Proposed Fix**:
- Rename section to **"Holdings Performance"** for clarity
- Remove the internal h2 heading since the parent `Section` component already provides the "Holdings" title
- If a subtitle is needed, use a muted descriptive line instead

**Rationale**: Since this section lives within `<Section title="Holdings">`, the redundant "STOCK PERFORMANCE" heading creates a double-header effect that's confusing.

---

### 2. ☐ Add Holdings Performance Disclaimer
**Location**: `components/holdings/stock-performance-section.tsx`
**Issue**: Users may conflate holdings performance with portfolio performance. Holdings performance shows price movement of current holdings over a period—NOT time-weighted portfolio returns that account for buy/sell timing and position sizing.
**Proposed Fix**: Add a small disclaimer/info tooltip:
> "Holdings performance shows price changes of current holdings over the selected period. This differs from portfolio returns, which are time-weighted and reflect actual buy/sell activity."

---

### 3. ☐ Duplicate Metrics: QuickStats vs RiskMetricsCard
**Location**:
- `components/metrics/quick-stats-card.tsx` (lines 73-133)
- `components/metrics/risk-metrics-card.tsx` (lines 227-259)

**Issue**: Several metrics appear in BOTH cards:
- Hit Rate (both)
- Avg Up Month (both)
- Avg Down Month (both)
- Best Month (both)
- Worst Month (both)

**Proposed Fix**:
- **Option A (Recommended)**: Remove Win/Loss section from RiskMetricsCard entirely; QuickStatsCard is the "Quick Stats" home for these
- **Option B**: Merge QuickStatsCard INTO RiskMetricsCard as a collapsed/expandable section
- **Either way**: Deduplicate metrics to appear in ONE location only

---

## P1 - High Priority Issues

### 4. ☐ Risk Table: Reorder Sections for Mental Model
**Location**: `components/metrics/risk-metrics-card.tsx` (lines 133-280)
**Issue**: Users scanning risk data care about market relationship (Beta/Correlation) early in their assessment, not at the bottom.
**Current Order**:
1. Risk-Adjusted Returns (Sharpe, Sortino)
2. Volatility
3. Drawdown
4. Value at Risk
5. Win/Loss ← (duplicate, see P0 #3)
6. Market Relationship (Beta/Correlation) ← buried at bottom

**Proposed Order**:
1. Risk-Adjusted Returns
2. **Market Relationship (Beta/Correlation)** ← move up
3. Volatility
4. Drawdown
5. Value at Risk
6. ~~Win/Loss~~ (remove, dedupe with QuickStats)

---

### 5. ☐ Excessive Vertical Scrolling
**Location**: `app/page.tsx` - overall page structure
**Issue**: The dashboard requires significant scrolling to view all sections. Financial dashboards should prioritize showing key info "above the fold" with progressive disclosure for details.

**Current Section Flow** (top to bottom):
1. Header (sticky)
2. Hero Metrics (4 cards)
3. Benchmark Selector
4. Growth Section (performance chart)
5. Returns Section (monthly chart + quick stats)
6. Risk Section (risk table)
7. Holdings Section (stock performance) - Mingdom only
8. Comparison Section (comparison table)
9. Footer

**Proposed Improvements**:
- **Collapsible Sections**: Add expand/collapse to Risk, Holdings, Comparison sections
- **Tab-based Navigation**: Consider grouping sections into tabs (Performance | Risk | Holdings)
- **Tighter Spacing**: Reduce gap between sections (`space-y-6` → `space-y-4`)
- **Progressive Disclosure**: Show summary metrics with "View Details" drill-down

---

### 6. ☐ Mobile-First Chart Optimization
**Location**: `components/charts/performance-chart.tsx`, `components/charts/monthly-returns-chart.tsx`
**Issue**: Charts take significant vertical space on mobile. Timeline filters add extra row.
**Proposed Fix**:
- Make chart height responsive (`h-[300px] md:h-[400px]`)
- Consider horizontal scroll for monthly returns on mobile
- Compact timeline tabs on mobile

---

## P2 - Medium Priority Issues

### 7. ☐ Typography: Distinctive Font Choices
**Location**: `app/layout.tsx`, `app/globals.css`
**Issue**: Per the frontend-design skill guidelines, we should avoid generic fonts like Inter/Roboto. Current implementation uses system defaults.
**Proposed Fix**:
- Add a distinctive display font for headings (e.g., Space Grotesk, Outfit, or Manrope)
- Keep a legible body font for data (e.g., Geist, IBM Plex Sans)
- Use a monospace font for numbers (already using `font-mono` appropriately)

---

### 8. ☐ Holdings Performance: Remove Internal Header
**Location**: `components/holdings/stock-performance-section.tsx` line 51-60
**Issue**: The component renders its own h2 "Stock Performance" header, but it's already wrapped in `<Section title="Holdings">`. This creates visual confusion with two section-level headings.
**Proposed Fix**:
- Replace the h2 with just the period tabs
- Or: Change parent to `<Section title="Holdings Performance">` and remove internal header

---

### 9. ☐ Comparison Table: Improve Scannability
**Location**: `components/metrics/comparison-table.tsx`
**Issue**: Dense table with many metrics. Users need to scroll horizontally on mobile.
**Proposed Fix**:
- Highlight the portfolio row with a subtle background
- Add visual indicators (icons/colors) for performance relative to benchmarks
- Consider collapsible metric groups

---

### 10. ☐ Add Subtle Animations & Micro-interactions
**Location**: Various components
**Issue**: Per frontend-design skill, "high-impact moments" like page load should have staggered reveals.
**Proposed Additions**:
- Staggered card entrance animations on Hero Metrics
- Chart line draw animations
- Hover effects on table rows (partially implemented)

---

### 11. ☐ Consistent Card Styling
**Location**: Multiple card components
**Issue**: Some cards use different background opacities (`bg-zinc-900/40`, `bg-zinc-950/30`, etc.). Creates subtle inconsistency.
**Proposed Fix**: Standardize subtle background variations with CSS variables or consistent opacity levels.

---

## P3 - Low Priority / Nice-to-Have

### 12. ☐ Dark/Light Mode Toggle
**Location**: Header component
**Issue**: Dashboard is dark-mode only. Some users prefer light mode for readability.
**Proposed Fix**: Add theme toggle in header (low priority—institutional dashboards typically stay dark)

---

### 13. ☐ Export/Share Functionality
**Issue**: Users may want to export charts or share performance snapshots.
**Proposed Addition**: "Export as PNG" on charts, "Copy Link" for sharing

---

### 14. ☐ Keyboard Navigation
**Issue**: Tab navigation and keyboard shortcuts not fully implemented.
**Proposed Fix**: Ensure all interactive elements are keyboard-accessible, add shortcuts for common actions

---

### 15. ☐ Loading State Improvements
**Location**: `app/page.tsx` - LoadingSkeleton
**Issue**: Current skeleton is basic. Could be more visually interesting.
**Proposed Fix**: Add shimmer effects, match component shapes more closely

---

### 16. ☐ Contextual Help System
**Issue**: METRIC_INFO tooltips are good but require hover. Consider an "Info Mode" toggle.
**Proposed Addition**: Toggle that shows all metric descriptions inline for educational mode

---

## Implementation Phases

### Phase 1: Quick Wins (1-2 hours)
- [ ] P0 #1: Rename/remove "STOCK PERFORMANCE" heading
- [ ] P0 #2: Add holdings performance disclaimer
- [ ] P1 #4: Reorder Risk table sections

### Phase 2: Deduplication (2-3 hours)
- [ ] P0 #3: Remove duplicate metrics from RiskMetricsCard

### Phase 3: Layout Optimization (3-4 hours)
- [ ] P1 #5: Add collapsible sections
- [ ] P1 #6: Mobile chart optimization

### Phase 4: Polish (4-6 hours)
- [ ] P2 #7: Typography improvements
- [ ] P2 #10: Micro-animations
- [ ] P2 #11: Consistent card styling

### Phase 5: Future Enhancements (Backlog)
- [ ] All P3 items

---

## References

### UX Best Practices Applied
1. **Information Hierarchy**: Critical data at top, details progressively disclosed
2. **Reduce Cognitive Load**: One metric, one location; no duplication
3. **Progressive Disclosure**: Collapsible sections, drill-down details
4. **Consistency**: Visual patterns should repeat predictably
5. **Mobile-First**: Optimize for smallest screen, enhance for larger
6. **Accessibility**: Keyboard nav, high contrast, readable typography

### Project Guidelines
- Frontend Design Skill: `.agent/skills/frontend-design/SKILL.md`
- Prefer bold aesthetic choices over generic patterns
- Use distinctive typography, not system defaults
- Rich micro-animations for polish

---

## Notes

- Holdings performance ≠ Portfolio performance. Important distinction to communicate.
- Risk table is the most data-dense component; consider tabbed sub-sections if more metrics are added.
- The "Comparison" section is least viewed—consider making it collapsed by default.

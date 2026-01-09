# Mobile UX Optimization Plan

This plan outlines the strategy for making the Mingdom Capital dashboard fully mobile-friendly, following industry standards for responsive financial dashboards.

## 1. Core Framework & Standards

We are utilizing a modern, standard-driven stack that is best-in-class for responsive web apps:
- **Tailwind CSS (v4)**: The industry standard for mobile-first utility styling.
- **Next.js**: Provides optimized image handling and fast page loads.
- **Shadcn UI / Radix UI**: Accessible primitives that handle complex mobile interactions (touch, focus).
- **Framer Motion**: For smooth mobile-friendly transitions.

### 1.1 Mobile Design Principles
- **Touch-First Interactivity**: Minimum touch target of 44x44px.
- **Content Reflow**: Moving from horizontal (tables) to vertical (stacked cards).
- **Progressive Disclosure**: Using accordions (already in place with `Section`) and drawers for secondary info.
- **Visual Hierarchy**: Prioritizing key metrics (CAGR, YTD) at the top of the viewport.

---

## 2. Implementation Phases

### Phase 1: The Foundation (Infrastructure)
*Status: Completed*
- [x] **Viewport Meta**: Ensure the page doesn't "zoom out" on load. (Added in `layout.tsx`)
- [x] **Base Typography**: scale font sizes dynamically using Tailwind's responsive prefixes.
- [x] **Global Spacing**: Audit container paddings to ensure enough "breathable" space on small screens without wasting pixels.

### Phase 2: Navigation & Layout
*Status: Completed*
- [x] **Sticky Header Optimization**: Reduce header height on mobile and ensure the "Follow Live Trades" link is easily accessible.
- [x] **Mobile Menu Refinement**: Improve the `MobileNav` drawer transition and layout.
- [x] **Section Pacing**: Adjust the spacing between dashboard sections for a single-column flow.

### Phase 3: Component Transformation (The "Standard Patterns")
*Status: Completed*
**Research Finding**: There is no single "responsive table" HTML element. The industry standard pattern for React/Shadcn apps is to **render a Card List for mobile and a Table for desktop**.
- [x] **Comparison Table**:
    - **Action**: Implement the `ComparisonCardList` component.
    - **Logic**: Use CSS (`hidden md:block`) to toggle between the Table view and the Card view. This ensures standard semantic HTML for both.
    - **Design**: Comparison Cards will show the Ticker, current Price, and a mini-grid of the top 3 metrics (CAGR, YTD, MaxDD).
- [x] **Stock Performance Table**:
    - **Action**: Similar to above, wrap the holdings list in a standard "Master-Detail" or "Card List" view for mobile.
- [x] **Chart Responsiveness**:
    - **Action**: Audit `ResponsiveContainer` usage.
    - **Fix**: Ensure `min-h-[300px]` is applied to chart containers on mobile to prevent "squashed" charts. Shift legends to the top on mobile.
- [x] **Metric Cards**: Ensure the 4-grid metric layout scales to 2x2 or 1x1.

### Phase 4: UX Polish
*Status: Completed*
- [x] **Tooltip Interaction**: Standard tooltips rely on hover. I've optimized `InfoTooltip` to trigger instantly on tap with a larger hit area.
- [x] **Loading States**: Updated `LoadingSkeleton` to match the new mobile-first card heights (h-28) and chart heights (h-300).
- [x] **Form Elements**: Optimized Tabs, Select buttons, and Expansion buttons for easier thumb-tapping (increased height to 40px/h-10 on mobile).

---

## 3. Specific Component Audit

| Component | Mobile Problem | Standardized Solution |
| :--- | :--- | :--- |
| `ComparisonTable` | Horizontal scroll; hard to compare rows. | **Pattern**: `MobileCardList`. Convert each row into a standalone card with key-value pairs. |
| `PerformanceChart` | Too narrow; legend overlaps data. | **Pattern**: `ResponsiveContainer` with mobile specific height (`h-[350px]`) and `legend` position `top`. |
| `RiskMetricsCard` | Dense text. | **Pattern**: Single-column layout. Use `flex-col` on mobile, `flex-row` on desktop. |
| `HeroMetrics` | Cards get too small. | **Pattern**: `grid-cols-2` (already in place) or `grid-cols-1` for extra small screens. |

## 4. Why Use This Framework?
Instead of manually tweaking every pixel, we will use **Tailwind breakpoints** (`sm`, `md`, `lg`) to define "classes" of behavior. This ensures that as the app grows, new components automatically inherit mobile-friendly logic.

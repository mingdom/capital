# Active Tasks

## High Priority (UX & Polish)

### Time Period Filter
- [ ] Add time period selector (YTD, 1Y, 3Y, 5Y, All)
- [ ] Filter chart data based on selected period
- [ ] Update metrics calculations to reflect selected period
- [ ] Ensure period selector is prominent and easy to use
- **Impact**: Allows users to analyze performance across different timeframes as track record grows

### Sortable Comparison Table
- [ ] Add click-to-sort functionality on column headers
- [ ] Add visual indicators for sort direction (↑/↓)
- [ ] Highlight selected portfolio row
- [ ] Persist sort state across portfolio switches
- **Impact**: Makes it easier to compare performance across different metrics

### Mobile Responsiveness Audit
- [ ] Test hero metrics on mobile (should collapse to 2x2 grid)
- [ ] Test benchmark checkboxes on mobile (should stack vertically)
- [ ] Test chart touch interactions and zoom
- [ ] Verify comparison table horizontal scroll works well
- [ ] Test portfolio selector tabs on small screens
- **Impact**: Ensures dashboard works across all devices

## Medium Priority (Data Insights)

### Rolling Returns Chart
- [ ] Create new chart component for rolling 12-month returns
- [ ] Show trailing returns over time (line chart)
- [ ] Add to portfolio analysis section
- [ ] Include benchmark overlays (optional)
- **Impact**: Helps visualize consistency vs volatility over time

### Distribution/Histogram Chart
- [ ] Create histogram component for monthly returns distribution
- [ ] Show distribution for selected portfolio
- [ ] Add normal distribution overlay for reference
- [ ] Display mean, median, skew statistics
- **Impact**: Visual understanding of risk beyond just Sharpe/Sortino ratios

### Year-by-Year Performance Table
- [ ] Create calendar year returns table
- [ ] Side-by-side comparison: portfolios vs benchmarks
- [ ] Color-code positive/negative years
- [ ] Add summary statistics row (mean, best, worst year)
- **Impact**: Easy to see which periods drove overall performance

### Export Functionality
- [ ] Add "Export to CSV" button for comparison table
- [ ] Add "Download Chart as PNG" option
- [ ] Include metadata in exports (date range, portfolio name)
- [ ] Toast notification on successful export
- **Impact**: Useful for reports and presentations

## Low Priority (Nice-to-Have)

### Keyboard Shortcuts
- [ ] Implement keyboard shortcut system
  - `M` = switch to Mingdom
  - `F` = switch to Fidelity
  - `1-5` = toggle benchmarks (SPY, QQQ, ARKK)
- [ ] Add help modal showing available shortcuts (press `?`)
- [ ] Visual feedback when shortcuts are used
- **Impact**: Power user feature for faster navigation

### Shareable URLs
- [ ] Add URL params support (`?portfolio=fidelity&benchmarks=SPY,QQQ`)
- [ ] Update URL when user changes selections
- [ ] Parse URL params on page load
- [ ] Add "Copy Link" button to share current view
- **Impact**: Allows sharing specific dashboard views

### Dark/Light Mode Toggle
- [ ] Create theme switcher component
- [ ] Persist theme preference in localStorage
- [ ] Update chart colors to work in both modes
- [ ] Test all components in light mode
- [ ] Add toggle button to header
- **Impact**: User preference for display mode

---

# Backlog Tasks (need grooming/prioritization)

## Web Dashboard Polish
- [ ] Add loading states for data fetching
- [ ] Improve error handling with retry logic
- [ ] Add empty states for missing data
- [ ] Performance optimization (code splitting, lazy loading)

## Analytics Enhancements
- [ ] Add correlation matrix between portfolios and benchmarks
- [ ] Add monthly contribution analysis (which months drive returns)
- [ ] Add drawdown recovery analysis
- [ ] Add beta/alpha decomposition charts

## Documentation
- [ ] Create user guide for web dashboard
- [ ] Document keyboard shortcuts
- [ ] Add tooltips for all metrics explaining calculations
- [ ] Create video walkthrough of dashboard features

## Infrastructure
- [ ] Add TypeScript strict mode
- [ ] Set up E2E tests with Playwright
- [ ] Add visual regression testing
- [ ] Set up CI/CD pipeline for web dashboard
- [ ] Consider deployment strategy (Vercel, Netlify, etc.)

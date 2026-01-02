# Active Tasks

## High Priority (PM Requested - Decision Usefulness)

### Up/Down Capture Ratios ⭐ NEW
- [ ] Calculate up-capture vs SPY (portfolio return / SPY return when SPY > 0)
- [ ] Calculate down-capture vs SPY (portfolio return / SPY return when SPY < 0)
- [ ] Add to Python export (analysis.py)
- [ ] Display in Risk Profile card on dashboard
- **Impact**: Tells you if you're "getting paid" for the beta - core institutional metric
- **Effort**: Low (1-2 hours)

### Stress Months Panel ⭐ NEW
- [ ] Filter months where SPY ≤ -2% (and ≤ -5%)
- [ ] Calculate portfolio performance in those months
- [ ] Compare to benchmark performance
- [ ] Display as new card or section on dashboard
- **Impact**: Answers "how do I perform in selloffs?" - the #1 investor question
- **Effort**: Low (2-3 hours)

### Rolling Beta/Correlation Chart ⭐ NEW
- [ ] Calculate 6M and 12M rolling beta vs SPY
- [ ] Calculate 6M and 12M rolling correlation vs SPY
- [ ] Export rolling series to JSON
- [ ] Create new line chart component
- [ ] Add sample size warning (limited data points with short track record)
- **Impact**: Shows if beta spikes in selloffs - PM's top request
- **Effort**: Medium (3-4 hours)
- **Note**: With ~20 months data, 12M rolling gives ~8 data points

### Underwater (Drawdown) Chart ⭐ NEW
- [ ] Calculate cumulative wealth series
- [ ] Track running peak and drawdown percentage
- [ ] Create area chart showing underwater periods
- [ ] Show time-to-recovery annotation
- **Impact**: Makes drawdown risk visceral and visual
- **Effort**: Medium (2-3 hours)

---

## Medium Priority (UX Polish)

### Sortable Comparison Table
- [ ] Add click-to-sort functionality on column headers
- [ ] Add visual indicators for sort direction (↑/↓)
- [ ] Highlight selected portfolio row
- **Impact**: Makes it easier to compare performance across metrics
- **Effort**: Low

### Mobile Responsiveness Audit
- [ ] Test hero metrics on mobile (should collapse to 2x2 grid)
- [ ] Test benchmark checkboxes on mobile (should stack vertically)
- [ ] Verify comparison table horizontal scroll works well
- **Impact**: Ensures dashboard works across all devices
- **Effort**: Low

### Sample Size Warnings
- [ ] Add warning badge when data < 36 months
- [ ] Show "Limited track record" indicator
- [ ] Adjust confidence in displayed metrics
- **Impact**: Reduces false confidence from short windows
- **Effort**: Low

---

## Low Priority (Nice-to-Have)

### Time Period Filter
- [ ] Add time period selector (YTD, 1Y, 3Y, 5Y, All)
- [ ] Filter chart data based on selected period
- **Impact**: Useful as track record grows
- **Status**: Deferred - needs rethinking, less urgent than decision-useful metrics

### Distribution/Histogram Chart
- [ ] Create histogram for monthly returns distribution
- [ ] Add normal distribution overlay
- **Impact**: Visual understanding of risk

### Year-by-Year Performance Table
- [ ] Create calendar year returns table
- [ ] Side-by-side comparison: portfolios vs benchmarks
- **Impact**: Easy to see which periods drove performance

### Export Functionality
- [ ] Add "Export to CSV" button for comparison table
- [ ] Add "Download Chart as PNG" option
- **Impact**: Useful for reports

---

## Backlog (Requires New Data Sources)

### VIX Integration
- [ ] Add VIX data ingestion
- [ ] High-vol regime slicing (VIX > threshold)
- **Blocked**: Requires new data source

### Holdings-Based Attribution
- [ ] Return attribution by position/sector
- [ ] Risk contribution analysis (marginal risk contribution)
- [ ] Concentration metrics (top-10, HHI, max single-name)
- **Blocked**: Requires position-level data we don't currently ingest

### Options Risk Summaries
- [ ] Net delta, gamma, vega
- [ ] Short option max loss
- **Blocked**: Requires options position data

### Custom Benchmark Builder
- [ ] SPY/QQQ blend + cash
- [ ] Alpha / tracking error / information ratio
- **Blocked**: UI complexity, lower priority

---

## Completed ✅

### Vercel Deployment
- [x] Configure Next.js for static export
- [x] Set up GOD_MODE environment variable
- [x] Create vercel.json for subdirectory build
- [x] Deploy to production

### Risk Profile Comparison
- [x] Add benchmark comparison dropdown
- [x] Show portfolio vs benchmark metrics side-by-side
- [x] Visual indicators (better/worse arrows)

### Dashboard MVP
- [x] Portfolio selector with tabs
- [x] Hero metrics (CAGR, 1Y, YTD, Sortino)
- [x] Performance chart with benchmark overlays
- [x] Monthly returns bar chart
- [x] Comparison table

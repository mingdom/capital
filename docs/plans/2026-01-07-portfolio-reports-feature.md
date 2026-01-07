# Portfolio Reports Feature Plan

**Date:** 2026-01-07
**Status:** ✅ Feature 1 Complete
**Author:** AI (Planning)
**Scope:** Feature 1 implemented — Feature 2 deferred

---

## Objective

Generate periodic portfolio reports showing:

1. **Best Stock Performance** over 3mo, YTD, 1Y
2. **Biggest Portfolio Changes** over 3mo, YTD, 1Y

---

## Data Sources Assessment

### Currently Available

| Data Source | Description | Path |
|------------|-------------|------|
| `prices.json` | Current holdings snapshot with cost basis & returns | `data/prices.json` |
| `savvy-*.json` (archive) | Daily portfolio valuation time-series | `data/import/archive/*/savvy-*.json` |
| `portfolio.json` | Computed monthly returns + performance metrics | `web/public/data/portfolio.json` |
| `valuations.json` | SavvyTrader daily valuations (working copy) | `data/valuations.json` |

### Data Gaps

| Gap | Impact | Mitigation |
|-----|--------|------------|
| **No historical holdings snapshots** | Cannot track position changes over time | Fetch historical prices per ticker; infer from SavvyTrader |
| **No individual ticker return time-series** | Must derive from current positions + price APIs | Use yfinance or similar for historical prices |
| **Position entry/exit dates** | Limited ability to track "portfolio changes" | Use `updatedDate` field as proxy for recent trades |

---

## Feature 1: Best Stock Performance

### Goal

Rank portfolio holdings by total return over 3mo, YTD, and 1Y periods.

### Data Needed

For each holding in `data/prices.json`:
- Symbol
- Current price
- Historical price at period start (3mo ago, YTD start, 1Y ago)

### Calculation

```
period_return = (current_price - period_start_price) / period_start_price
```

### Implementation Approach

1. **Extract holdings list** from `prices.json`
2. **Fetch historical prices** using yfinance:
   - 3mo ago: ~3 months back from today
   - YTD: First trading day of current year
   - 1Y: ~365 days ago
3. **Calculate returns** for each period
4. **Sort and rank** holdings by return
5. **Generate report** showing top/bottom performers

### Output Format

```
═══════════════════════════════════════════════════════════════════
                    BEST STOCK PERFORMANCE REPORT
                    Generated: 2026-01-07
═══════════════════════════════════════════════════════════════════

┌ 3-MONTH TOP PERFORMERS ─────────────────────────────────────────┐
│ Rank │ Symbol │ Return │ Current Price │ 3mo Ago │ Allocation │
├──────┼────────┼────────┼───────────────┼─────────┼────────────┤
│   1  │ APP    │ +45.2% │ $673.74       │ $464.01 │    1.4%    │
│   2  │ GOOGL  │ +12.8% │ $313.11       │ $277.58 │   17.6%    │
│  ... │  ...   │  ...   │ ...           │   ...   │    ...     │
└──────┴────────┴────────┴───────────────┴─────────┴────────────┘

┌ YTD TOP PERFORMERS ─────────────────────────────────────────────┐
│ ...                                                              │
└──────────────────────────────────────────────────────────────────┘

┌ 1-YEAR TOP PERFORMERS ──────────────────────────────────────────┐
│ ...                                                              │
└──────────────────────────────────────────────────────────────────┘
```

---

## Feature 2: Biggest Portfolio Changes

### Goal

Identify and report the most significant changes to portfolio composition.

### Challenge

**We don't have historical holdings snapshots.** The current data only shows:
- Current positions (`prices.json`)
- Cost basis (implied by `pricePerShare` and `totalPrice`)
- Last update date (`updatedDate`)

### Pragmatic Approach

Given data constraints, focus on **what we can derive**:

#### Option A: Position Value Changes (Feasible Now)

Track how each position's **portfolio weight** changed due to price movements.

```
weight_change = current_allocation - implied_start_allocation
```

Where implied start allocation is re-calculated using historical prices.

#### Option B: Trade Activity Inference (Partial)

The `updatedDate` field in `prices.json` indicates when a position was last modified (bought/sold/adjusted). We can:
- List positions with recent `updatedDate` values
- Flag positions that appeared or disappeared (requires storing historical snapshots)

#### Option C: Start Snapshotting (Future Investment)

Create a nightly job to snapshot `prices.json` → `data/snapshots/{date}.json`

This enables true delta comparison in future.

### Recommended Implementation (Hybrid)

1. **For immediate MVP**: Implement Option A (weight changes from price moves)
2. **Add snapshot infrastructure**: Store weekly/monthly snapshots going forward
3. **Enhance with trade inference**: Use `updatedDate` to highlight actively managed positions

### Output Format (MVP)

```
═══════════════════════════════════════════════════════════════════
                    PORTFOLIO CHANGES REPORT
                    Period: 2025-10-07 → 2026-01-07 (3mo)
═══════════════════════════════════════════════════════════════════

┌ WEIGHT GAINERS (price appreciation drove higher allocation) ────┐
│ Symbol │ Start Wt. │ Current Wt. │ Δ Weight │ Price Chg │ Alloc │
├────────┼───────────┼─────────────┼──────────┼───────────┼───────┤
│ APP    │   1.0%    │    1.4%     │  +0.4%   │  +45.2%   │ 1.4%  │
│ GOOGL  │  15.2%    │   17.6%     │  +2.4%   │  +12.8%   │17.6%  │
└────────┴───────────┴─────────────┴──────────┴───────────┴───────┘

┌ WEIGHT LOSERS (underperformance or rebalancing) ────────────────┐
│ Symbol │ Start Wt. │ Current Wt. │ Δ Weight │ Price Chg │ Alloc │
├────────┼───────────┼─────────────┼──────────┼───────────┼───────┤
│ MELI   │   3.2%    │    2.7%     │  -0.5%   │   -4.3%   │ 2.7%  │
└────────┴───────────┴─────────────┴──────────┴───────────┴───────┘

┌ RECENT ACTIVITY (positions modified in period) ─────────────────┐
│ Symbol │ Last Updated │ Days Ago │ Est. Action │
├────────┼──────────────┼──────────┼─────────────┤
│ CRM    │ 2025-12-29   │    9     │ Buy/Adjust  │
│ CME    │ 2025-12-29   │    9     │ Buy/Adjust  │
└────────┴──────────────┴──────────┴─────────────┘
```

---

## Technical Implementation Plan

### Phase 1: Core Infrastructure (MVP)

```
portfolio_cli/
├── reports/
│   ├── __init__.py
│   ├── stock_performance.py    # Feature 1: best performers
│   ├── portfolio_changes.py    # Feature 2: weight changes
│   └── utils.py                # Shared helpers (price fetching, date utils)
```

**New CLI commands:**
```bash
# Stock performance report
python -m portfolio_cli report performance [--period 3mo|ytd|1y] [--top N] [--format table|csv|json]

# Portfolio changes report
python -m portfolio_cli report changes [--period 3mo|ytd|1y] [--format table|csv|json]

# Combined summary report
python -m portfolio_cli report summary [--format table|csv|json]
```

### Phase 2: Snapshot Infrastructure

Add automated snapshotting for future delta tracking:

```python
# data/snapshots/{yyyy-mm-dd}.json
{
    "snapshot_date": "2026-01-07",
    "holdings": [...],  # Copy from prices.json
    "totals": {...}
}
```

**Trigger options:**
- Manual: `python -m portfolio_cli snapshot`
- Cron job: Weekly Sunday midnight
- On-demand before running reports

### Phase 3: Enhanced Reports

With snapshots in place:
- True position entry/exit tracking
- Quantity changes (buys/sells)
- Cost basis changes
- Tax lot tracking

---

## Dependencies

| Dependency | Purpose | Status |
|------------|---------|--------|
| yfinance | Historical price data | ✅ Already installed |
| pandas | Data manipulation | ✅ Already installed |
| rich | CLI output formatting | ✅ Already installed |
| typer | CLI framework | ✅ Already installed |

---

## Open Questions

1. **Period definitions:**
   - YTD: January 1st or first trading day?
   - 3mo: Calendar months or ~90 trading days?

2. **Benchmark comparison:**
   - Show how each stock performed vs SPY over same period?

3. **Report delivery:**
   - CLI-only or also web dashboard?
   - Email/notification on significant changes?

4. **Cash handling:**
   - Include cash changes in portfolio weight analysis?

5. **Multi-account:**
   - Report per-portfolio or combined?

---

## Suggested Implementation Order

| Step | Task | Effort |
|------|------|--------|
| 1 | Create `portfolio_cli/reports/utils.py` with price fetching helpers | S |
| 2 | Implement `stock_performance.py` with basic ranking | M |
| 3 | Add CLI commands for stock performance report | S |
| 4 | Implement `portfolio_changes.py` with weight delta calculation | M |
| 5 | Add CLI commands for portfolio changes report | S |
| 6 | Add snapshot command and storage | S |
| 7 | Integrate with existing `cli.py` as subcommands | S |
| 8 | Add tests for report calculations | M |

**Estimated total effort:** 1-2 days for MVP

---

## Success Criteria

- [ ] `report performance` shows top/bottom 5 stocks by return for each period
- [ ] `report changes` shows positions with biggest weight shifts
- [ ] Reports use consistent Rich formatting with existing CLI
- [ ] Historical prices are cached to avoid redundant API calls
- [ ] Tests cover edge cases (missing data, new positions, etc.)

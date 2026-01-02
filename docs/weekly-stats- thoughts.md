# Feedback from area expert:
Weekly stats are most useful when they (a) reflect the *risk you actually experience while managing the book* and (b) detect *regime shifts* faster than monthly. Monthly metrics are often smoother and can understate lived volatility—especially with concentrated portfolios, options, or fast-moving exposures—so the weekly layer should be built as a “risk cockpit,” not just a smaller-period version of the monthly report.

## Why weekly volatility/Sharpe differ from monthly (what’s going on)

**Two main drivers:**

1. **Aggregation smooths variance.** Monthly returns compress intra-month swings into a single print, so realized volatility often looks lower.
2. **Non-IID returns / serial correlation.** Options P&L, dynamic hedging, and tactical de-risking can create return patterns where weekly scaling is not “clean” (square-root-of-time assumptions break). That can make Sharpe/Sortino vary a lot by sampling frequency.

**Practical takeaway:** Use **weekly for risk sizing and monitoring**, monthly for “investor narrative” and longer-horizon evaluation.

---

## Weekly stats that are genuinely useful (and what each answers)

### 1) Realized risk (what risk are we running right now?)

These should be computed on **weekly returns** (e.g., Fri close to Fri close):

* **Realized vol (rolling 13W and 26W)**
  *Answers:* Are we taking more risk than we think?
* **Downside deviation (rolling 13W and 26W)**
  *Answers:* Is the downside getting choppier (Sortino risk)?
* **Weekly max drawdown (rolling) + underwater time**
  *Answers:* Are we entering a drawdown regime early?

**Why weekly is better than monthly here:** it surfaces risk ramp-ups within the quarter rather than after the quarter.

### 2) Tail risk early-warning (what happens in the bad weeks?)

* **Weekly VaR 95 / CVaR 95 (rolling window)**
  *Answers:* What’s a “bad week” and how bad is the tail?
* **Worst 1–3 weeks in last 52 weeks (with benchmark)**
  *Answers:* Are we structurally worse than SPY/QQQ in shocks?
* **Tail ratio / downside tail multiple** (simple diagnostic)
  *Answers:* Is the left tail fattening?

**Note:** Weekly tails are more actionable for de-risk triggers than monthly tails.

### 3) Market linkage drift (are we accidentally becoming QQQ with leverage?)

* **Rolling beta vs SPY (13W/26W)** and **rolling correlation**
* **Down-market beta** (beta computed only on weeks when SPY < 0)
* **Up capture / down capture (weekly, rolling)**

*Answers:* Are we getting “beta creep,” and do we protect on down tape?

This is one of the highest-leverage additions for improving **Sortino**: you want **down-capture < 1** without killing up-capture.

### 4) Return quality and consistency (is edge degrading?)

* **Weekly hit rate (rolling 26W/52W)**
* **Average up week / average down week**
* **Payoff ratio** (avg up / |avg down|)
* **Streak metrics** (max loss streak, max win streak)

*Answers:* Is performance coming from steady edge or a few outsized weeks?

### 5) “Are the statistics trustworthy?” diagnostics (your frequency mismatch issue)

These are especially relevant given your daily/weekly/monthly divergence:

* **Autocorrelation of weekly returns** (or variance ratio test)
  *Answers:* Is there serial correlation / smoothing impacting annualization?
* **Volatility scaling error**: compare realized weekly vol scaled to annual vs daily vol scaled
  *Answers:* Is sqrt(time) scaling failing materially (often true in dynamic strategies)?
* **Turnover and exposure churn (weekly)**
  *Answers:* Are we changing the book so fast that historical stats are stale?

### 6) Exposure-based weekly stats (if you can get holdings/exposures)

If your app can ingest exposures (positions, delta-adjusted exposure, etc.), these become the *best* weekly risk controls:

* **Gross exposure, net exposure, beta-adjusted exposure (time series)**
* **Top-5 / top-10 concentration and HHI (weekly)**
* **Risk contribution** by position (to vol and to downside deviation)
* If options: **net delta/gamma/vega**, and “worst-case loss” summaries for short option structures

*Answers:* What changed in the portfolio that explains risk changes?

---

## What I would put on a weekly dashboard (minimal but high impact)

1. **Rolling 13W realized vol + downside dev** (with last week change)
2. **Rolling 13W beta vs SPY + down-market beta**
3. **Weekly VaR95/CVaR95 (rolling 52W)** + worst 3 weeks table
4. **Weekly hit rate + avg up/down week (rolling 26W)**
5. **Exposure strip**: net, gross, beta-adjusted exposure; top-10 concentration
6. **Alert flags** (simple rules):

   * beta spikes above threshold
   * CVaR worsens by X% vs last quarter
   * concentration breach
   * weekly drawdown exceeds threshold

---

## Implementation notes (to avoid misleading weekly Sharpe)

* Use **weekly RF** consistent with your RF assumption (4% annual → convert to weekly).
* Prefer **rolling windows** (13W, 26W, 52W) rather than full-sample weekly Sharpe—weekly Sharpe is noisier.
* Report **Sharpe/Sortino primarily at monthly** for investor-facing, but **use weekly vol/beta/CVaR for risk controls**.

---

## TLDR

Weekly stats are best for **risk management and regime detection**: rolling **13W/26W vol + downside dev**, rolling **beta/corr (especially down-market beta)**, rolling **weekly VaR/CVaR**, and **weekly drawdown + worst-weeks table**. Add **autocorrelation/scaling diagnostics** to explain why weekly Sharpe/vol differ from monthly, and—if available—pair everything with **exposure + concentration + risk contribution** so you can act on the numbers.

# Mingdom Capital Performance Tracker

Live report: https://mingdom.github.io/capital/

Tracks the Mingdom Capital portfolio from SavvyTrader valuations data and reports
monthly returns plus key risk/return metrics (CAGR, YTD, Max Monthly Drawdown,
Sharpe, Sortino). Optional comparison against SPY and QQQ with cached data.

The published page shows an “As of: YYYY-MM-DD” based on the latest date in
`data/valuations.json` used for that build.

Key features
- Monthly aggregation from SavvyTrader valuations (`data/valuations.json`).
- Metrics: CAGR, YTD, Max Monthly Drawdown, Sharpe, Sortino.
- Optional SPY/QQQ benchmarks with local caching.
- Simple Makefile/CLI for repeatable runs.

## For Investors

- View the latest performance: https://mingdom.github.io/capital/

# Quickstart

1. Go to SavvyTrader portfolio url, i.e.: https://savvytrader.com/mingdom/mingdom-capital
2. Open browser dev tools and record network traffic
3. In the UI, set performance range to "Max"
4. Find a request like `https://api.savvytrader.com/core/portfolios/4737/valuations?range=all`
5. Right click → Copy → Copy Response
6. Paste the JSON response into `data/valuations.json`
7. Run the script to compute metrics (see "Run" below)

## Setup

Option A — Makefile (recommended):

```bash
make dev
```

Option B — Manual:

```bash
python3 -m venv venv
./venv/bin/pip install -U pip
./venv/bin/pip install -r requirements.txt -r dev-requirements.txt
```

## Run

```bash
# With Makefile
make run

# Or directly
./venv/bin/python sortino.py

# Compare against SPY/QQQ (fetch/cached via yfinance)
make run-benchmarks
# or: ./venv/bin/python sortino.py --benchmarks
```

## Report

Generate a static HTML report (Chart.js visualization):

```bash
make report
# or: ./venv/bin/python scripts/build_report.py --output dist/index.html
```

The generated file is written to `dist/index.html`.

## Test

```bash
make test
# or: ./venv/bin/pytest -q
```

## Format & Lint

```bash
make format   # Black
make lint     # Ruff
```

## Git Pre-commit Hook

Install a lightweight pre-commit hook that checks formatting and linting before each commit:

```bash
make hook
```

This runs `black --check .` and `ruff check .`. Run `make format` to auto-fix formatting.

## Project Structure

- `sortino.py` — main analysis script (monthly returns, CAGR, drawdown, Sharpe/Sortino).
- `benchmarks.py` — fetches/caches SPY & QQQ monthly returns (yfinance) for comparisons.
- `data/valuations.json` — SavvyTrader valuations API response for local runs.
- `data/` — additional data files (e.g., `valuations.json`, `prices.json`, historical snapshots).
- `tests/` — pytest-based tests (e.g., `tests/test_sortino_smoke.py`).
- `scripts/pre-commit.sh` — optional Git pre-commit hook (Black + Ruff checks).
- `Makefile` — common tasks (`make dev`, `run`, `test`, `format`, `lint`, `hook`).
- `requirements.txt`, `dev-requirements.txt` — runtime and dev dependencies.
- `pyproject.toml`, `pytest.ini` — formatter/linter and pytest configuration.
- `2025-q2/` — static charts/assets; not code.
- `AGENTS.md` — contributor guidelines.

Note: The HTML report supersedes the raw console sample previously shown here.

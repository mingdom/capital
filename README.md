# Mingdom Capital Performance Tracker

This project tracks the Mingdom Capital portfolio using exported valuations data from SavvyTrader. It computes monthly returns and key risk/return metrics (CAGR, Max Monthly Drawdown, Sharpe, Sortino), and can compare performance against SPY and QQQ using cached yfinance data. Outputs are rounded for clarity and include brief guidance on interpretation.

Key features
- Ingests SavvyTrader valuations JSON (`data/valuations.json`).
- Aggregates daily changes into monthly returns.
- Reports CAGR, YTD, Max Monthly Drawdown, Sharpe, Sortino.
- Optional benchmark comparison vs SPY/QQQ with local caching.
- Simple CLI and Makefile for repeatable runs.

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

## Web UI

Generate a static HTML report with a simple Chart.js visualization:

```bash
make report
# or: ./venv/bin/python scripts/build_report.py --output dist/index.html
```

Merging to `main` runs the `Build Web Report` workflow, which regenerates
`dist/index.html` and deploys it to GitHub Pages. After enabling Pages
(`Settings` → `Pages` → `Build and deployment` → `GitHub Actions`), the latest
report is served at your project Pages URL:

- `https://<your-user-or-org>.github.io/<repo>/`

The workflow summary will also display the exact URL after each deployment.

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

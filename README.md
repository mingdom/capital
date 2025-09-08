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

Sample Response:
```
Monthly Returns:
month
2024-02    0.012513
2024-03    0.024022
2024-04   -0.018967
2024-05    0.052679
2024-06    0.041913
2024-07   -0.019194
2024-08    0.029271
2024-09    0.043702
2024-10    0.014421
2024-11    0.075256
2024-12    0.006172
2025-01    0.075087
2025-02   -0.039864
2025-03   -0.091526
2025-04    0.017057
2025-05    0.110503
2025-06    0.067449
2025-07    0.023597
2025-08    0.020527
2025-09    0.017270
Freq: M

CAGR (Annual): 30.07%
Max Monthly Drawdown: -9.15%
YTD Performance (2025): 20.14%

Annualized Sharpe Ratio: 1.531999832165774
Annualized Sortino Ratio: 2.809998735415429
```

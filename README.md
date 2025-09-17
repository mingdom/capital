# Mingdom Capital Performance Tracker

Live report: https://mingdom.github.io/capital/

Tracks the Mingdom Capital portfolio from SavvyTrader valuations data and reports
monthly returns plus key risk/return metrics (CAGR, YTD, Max Monthly Drawdown,
Sharpe, Sortino). Optional comparison against SPY and QQQ with cached data.

The core functionality is now exposed through a Typer-powered CLI (`python -m
portfolio_cli`) so commands, options, and future features remain discoverable
via `--help`.

The published page shows an “As of: YYYY-MM-DD” based on the latest date in
`data/valuations.json` used for that build.

Key features
- Monthly aggregation from SavvyTrader valuations (`data/valuations.json`).
- Metrics: CAGR, YTD, Max Monthly Drawdown, Sharpe, Sortino.
- Optional SPY/QQQ benchmarks with local caching.
- Interactive Typer-based CLI for discoverable workflows.
- Multiple data sources: SavvyTrader JSON and Fidelity CSV (cash-flow aware).
- Simple Makefile targets for repeatable runs.

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
# With Makefile (interactive shell)
make run

# Direct CLI (interactive shell)
./venv/bin/python -m portfolio_cli

# Non-interactive analyze command
make analyze
# or: ./venv/bin/python -m portfolio_cli analyze

# Compare against SPY/QQQ (fetch/cached via yfinance)
make run-benchmarks
# or: ./venv/bin/python -m portfolio_cli analyze --benchmarks

# Inspect available commands
./venv/bin/python -m portfolio_cli --help
```

### Interactive shell

Running the CLI without subcommands launches a prompt similar to `portfolio>`
with built-in help:

```bash
python -m portfolio_cli
# Within the prompt:
portfolio> help
portfolio> analyze --year 2024
portfolio> analyze fidelity --input data/private/fidelity-performance.csv
portfolio> benchmarks
portfolio> exit
```

Shortcuts include `benchmarks` (equivalent to `analyze --benchmarks`) and
`commands` to list available actions. The shell delegates to the same Typer
commands, so everything remains scriptable. Tab completion is available inside
the shell for sources and common flags.

### CLI commands

The CLI groups portfolio analysis tasks and exposes consistent help output:

```bash
# Portfolio summary (default command)
python -m portfolio_cli analyze --json data/valuations.json --rf 0.04 --year 2024

# Include SPY/QQQ comparison table
python -m portfolio_cli analyze --benchmarks

# Analyze Fidelity export (deposits/withdrawals handled automatically)
python -m portfolio_cli analyze fidelity --input data/private/fidelity-performance.csv

# Launch the interactive shell explicitly
python -m portfolio_cli interactive

# Discover options for any command
python -m portfolio_cli analyze --help

# Install shell completions (bash/zsh/fish/pwsh)
python -m portfolio_cli --install-completion
```

Typer keeps the implementation compact while providing type-checked arguments
and autogenerating usage docs, so new subcommands (e.g., multi-portfolio
support, DCF utilities) can be added without extra parsing boilerplate.

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

- `sortino.py` — legacy entry point that now proxies to the Typer CLI.
- `portfolio_cli/` — reusable analysis code plus Typer CLI entry points.
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

## Why Typer for the CLI?

We compared common Python CLI options:

- `argparse` (stdlib) is dependency-free but produces minimal help text unless
  extra boilerplate is added and does not scale well to many subcommands.
- `click` improves ergonomics with decorators yet still requires repeating
  argument metadata separate from type hints.
- `typer` builds on Click, embraces Python type hints for validation, and
  auto-generates rich usage documentation. It keeps the code ready for future
  features such as alternative portfolio data loaders, DCF calculators, or
  additional benchmarking commands.

Given the roadmap, Typer offered the best balance of ergonomics and
extensibility while remaining lightweight.

## Fidelity data format

Place the Fidelity investment income CSV export at
`data/private/fidelity-performance.csv` (ignored by Git). The CLI normalizes
returns by removing cash-flow effects, so deposits and withdrawals will not
skew performance metrics. Use `--source fidelity` together with `--input` if you
store the file elsewhere.

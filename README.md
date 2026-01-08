# Mingdom Capital Performance Tracker

A Python-based portfolio performance analytics toolkit that computes risk-adjusted returns (Sharpe, Sortino), drawdowns, CAGR, and benchmark comparisons. Built for tracking personal investment portfolios with support for multiple data sources.

## Overview

This toolkit provides:
- **Portfolio Performance Analysis**: Calculate CAGR, Sharpe ratio, Sortino ratio, max drawdown, YTD, and 3-month trailing returns
- **Benchmark Comparison**: Compare portfolio performance against market indices (SPY, QQQ, ARKK by default)
- **Multiple Data Sources**: Support for SavvyTrader JSON exports and Fidelity CSV performance reports
- **Interactive Shell**: REPL environment for ad-hoc analysis and exploration
- **HTML Reports**: Generate static HTML reports with performance visualizations
- **Web Dashboard**: Modern Next.js dashboard with institutional-grade UI (dark mode, charts, risk metrics)
- **CLI & Programmatic API**: Use via command-line or import as a library

## Architecture

```
mingdom-capital/
├── portfolio_cli/          # Core package
│   ├── __init__.py        # Public API exports
│   ├── analysis.py        # Performance calculations (Sharpe, Sortino, CAGR, drawdown)
│   ├── cli.py             # Typer-based CLI commands
│   ├── performance.py     # Data loading and source adapters
│   ├── report.py          # HTML report generation
│   └── shell.py           # Interactive REPL
├── benchmarks.py          # Benchmark data fetching & caching (yfinance)
├── sortino.py             # Legacy compatibility layer
├── scripts/               # Automation scripts
│   ├── import_latest.py   # Data import & archival
│   ├── build_report.py    # Standalone report builder
│   └── pre-commit.sh      # Git pre-commit hook
├── data/                  # Data files (gitignored)
│   ├── import/            # Drop folder for new data
│   ├── valuations.json    # Active SavvyTrader data
│   ├── benchmarks.json    # Cached market data
│   └── private/           # Fidelity CSVs (gitignored)
├── tests/                 # Pytest test suite
├── .agent/                # Agent logs & development notes
├── Makefile               # Build automation (preferred entrypoint)
└── README.md              # This file
```

## Quick Start

### 1. Installation

Using the Makefile (recommended):
```bash
```bash
make install  # Installs Python + Node dependencies
```

This installs both Python (CLI/analytics) and Node.js (web dashboard) dependencies in one command.

<details>
<summary>Manual setup (if needed)</summary>

```bash
# Python
python3 -m venv venv
./venv/bin/pip install -U pip
./venv/bin/pip install -r requirements.txt -r dev-requirements.txt

# Node.js (web dashboard)
cd web && npm install
```
</details>

### 2. Import Data

Place source files in `data/import/`:
- **SavvyTrader**: `.json` files (API response from valuations endpoint)
- **Fidelity**: `.csv` files (performance export)

Then run:
```bash
make import
```

This processes the latest files and archives them to `data/import/archive/YYYY-MM-DD/`.

### 3. Run Analysis

**Interactive Shell (default)**:
```bash
make run
```

**CLI Commands**:
```bash
# Show performance for all sources (Mingdom + Fidelity)
./venv/bin/python -m portfolio_cli performance

# Filter to specific source
./venv/bin/python -m portfolio_cli performance mingdom
./venv/bin/python -m portfolio_cli performance mingdom --year 2024

# Fidelity with custom CSV
./venv/bin/python -m portfolio_cli performance fidelity --fidelity-csv data/private/fidelity-performance.csv

# Hide benchmarks
./venv/bin/python -m portfolio_cli performance --no-benchmarks
```

### 4. Generate HTML Report

```bash
make report
# Report saved to dist/index.html
```

Filter by source:
```bash
./venv/bin/python -m portfolio_cli report mingdom --output dist/index.html
./venv/bin/python -m portfolio_cli report fidelity --fidelity-csv data/private/fidelity.csv --output dist/index.html
```

### 5. Web Dashboard (Next.js)

The web dashboard provides an institutional-grade interface for portfolio analytics.

**Run the dashboard** (http://localhost:3000):
```bash
make web  # Exports data + starts dev server
```

**Build for production**:
```bash
make build  # Exports data + builds static site
```

The dashboard automatically exports fresh data from your Python analytics before starting. Data is served from `web/public/data/portfolio.json`.

**Features**:
- Portfolio-focused dashboard with global selector
- Hero metrics (CAGR, 1Y, YTD, Sortino)
- Linear performance chart with multi-select benchmarks
- Risk profile with benchmark comparison
- Monthly returns bar chart
- Comprehensive comparison table

**Deployment**:

The dashboard is configured for **Vercel** deployment (see `web/DEPLOYMENT.md` for details):

```bash
# 1. Push to GitHub
git push origin main

# 2. Deploy to Vercel (one-click import)
# Visit vercel.com → Import Project

# 3. Set GOD_MODE (optional)
# In Vercel: Settings → Environment Variables
# Add: NEXT_PUBLIC_GOD_MODE=true
```

**Security**:
- **Default (public)**: Only shows Mingdom portfolio
- **GOD_MODE=true**: Shows all portfolios (Mingdom + Fidelity)
- Local development has GOD_MODE enabled by default

## Data Sources

### SavvyTrader

**Automated Fetch Process** (Recommended):
1. Log in to SavvyTrader at `https://savvytrader.com/mingdom/mingdom-capital`
2. Extract the `idToken` from browser localStorage (Developer Tools → Application → Local Storage)
   - Look for key starting with `CognitoIdentityServiceProvider...idToken`
3. Run the fetch script:
   ```bash
   ./venv/bin/python scripts/fetch_savvytrader.py "<ID_TOKEN>"
   ```
4. Import the data:
   ```bash
   make import
   ```

This process:
- Fetches all available portfolio data (valuations, holdings, prices, metadata)
- Creates a timestamped archive in `data/savvytrader/YYYY-MM-DD_HHMMSS/`
- Stages the primary files in `data/import/` for import

**For detailed API documentation**, see `docs/savvytrader-api.md`.

⚠️ **Security**: Access tokens are short-lived. Never commit or share these tokens.

### Fidelity

Export performance CSV from Fidelity's web interface and place in `data/import/` or `data/private/`.

## Benchmarks

**Default benchmarks**: SPY, QQQ, ARKK

**Configuration**: Override via environment variable:
```bash
export PORTFOLIO_BENCHMARKS="SPY,QQQ,IWM"
./venv/bin/python -m portfolio_cli performance
```

Benchmarks are cached in `data/benchmarks.json` using `yfinance`. The cache is automatically updated when needed.

## Development

### Code Style

- Python 3.9+
- 4-space indentation, UTF-8, max line length 100
- Type hints required for new/edited functions
- Use `snake_case` for functions/variables, `UPPER_SNAKE_CASE` for constants

### Formatting & Linting

```bash
make format  # black
make lint    # ruff
```

### Testing

```bash
make test
# or
PYTHONPATH=. ./venv/bin/pytest -q
```

**Coverage target**: >= 80% for changed lines

**Test structure**:
- `tests/test_sortino_smoke.py` - Legacy smoke tests
- `tests/test_cli.py` - CLI interface tests
- `tests/test_benchmarks.py` - Benchmark fetching tests
- `tests/test_html_report.py` - Report generation tests

### Git Hooks

Install pre-commit hook (runs tests before commit):
```bash
make hook
```

## Performance Metrics

| Metric | Description |
|--------|-------------|
| **CAGR** | Compound Annual Growth Rate (annualized return) |
| **Sharpe Ratio** | Risk-adjusted return vs risk-free rate (excess return / volatility) |
| **Sortino Ratio** | Risk-adjusted return vs downside risk (penalizes only downside volatility) |
| **Max Drawdown** | Largest peak-to-trough decline (monthly basis) |
| **YTD** | Year-to-date return (current year only) |
| **3M** | Trailing 3-month compounded return |

**Risk-free rate**: Configurable, defaults to 4.5% annual (defined in `portfolio_cli.analysis.ANNUAL_RF_RATE`)

## Common Workflows

### Add a New Data Source

1. Implement loader in `portfolio_cli/performance.py` (see `load_fidelity_monthly_returns`)
2. Add source to `SourceKind` enum in `portfolio_cli/cli.py`
3. Update CLI help text and documentation
4. Add tests in `tests/test_cli.py`

### Add a New Metric

1. Update `PerformanceMetrics` dataclass in `portfolio_cli/analysis.py`
2. Implement calculation in `calculate_metrics()`
3. Add display logic to `format_portfolio_summary()`
4. Update report template in `portfolio_cli/report.py`
5. Add tests in `tests/test_sortino_smoke.py`

### Customize Benchmarks

Edit `DEFAULT_BENCHMARKS` in `benchmarks.py` or use `PORTFOLIO_BENCHMARKS` environment variable.

## Makefile Targets

| Target | Description |
|--------|-------------|
| `make install` | Create venv and install dependencies |
| `make dev` | Alias for `install` |
| `make import` | Import latest data from `data/import/` |
| `make run` | Launch interactive shell |
| `make test` | Run pytest suite |
| `make format` | Format code with black |
| `make lint` | Lint with ruff |
| `make report` | Generate HTML report to `dist/index.html` |
| `make hook` | Install git pre-commit hook |
| `make clean` | Remove venv and cache files |

## Troubleshooting

**Issue**: `ModuleNotFoundError` when running scripts
- **Fix**: Ensure `PYTHONPATH=.` is set or run as module (`python -m portfolio_cli`)

**Issue**: Empty benchmark data
- **Fix**: Delete `data/benchmarks.json` and re-run to force fresh fetch

**Issue**: Timezone warnings from pandas
- **Fix**: Already handled in `benchmarks.py` using `tz_localize` and `tz_convert`

**Issue**: Import fails with "No JSON/CSV found"
- **Fix**: Ensure files are directly in `data/import/`, not subdirectories

## Project Status

**Current Version**: Active development
**Stability**: Production-ready for personal use
**Test Coverage**: Core logic >80%

See `TASKS.md` for known issues and planned enhancements.

## References

- [Sortino Ratio](https://en.wikipedia.org/wiki/Sortino_ratio)
- [Sharpe Ratio](https://en.wikipedia.org/wiki/Sharpe_ratio)
- [CAGR](https://www.investopedia.com/terms/c/cagr.asp)
- [yfinance](https://github.com/ranaroussi/yfinance)
- [Typer CLI](https://typer.tiangolo.com/)

---

## Documentation

- **AGENTS.md** - Concise guidelines for AI coding assistants (high-level principles)
- **docs/development-guide.md** - Detailed development patterns, recipes, and examples
- **TASKS.md** - Current known issues and planned work

**For AI agents**: See `AGENTS.md` for quick reference. When you need detailed guidance, consult `docs/development-guide.md`.

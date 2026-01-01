# Mingdom Capital Performance Tracker

## Setup (Makefile first)

```bash
python3 -m venv venv
./venv/bin/pip install -U pip
./venv/bin/pip install -r requirements.txt -r dev-requirements.txt
```

Or use the Makefile (preferred):

```bash
make install
```

## Update data (drop-folder importer)

Simplest flow: drop raw files in `data/import/` and run the importer.

Accepted files in `data/import/`:
- `.json` → SavvyTrader valuations dump (array with `summaryDate` and `dailyTotalValueChange`)
- `.csv` → Fidelity performance export

### How to fetch the SavvyTrader valuations JSON (manual)

We currently pull this data via the SavvyTrader web app (no automated API client in this repo).

Steps:
1. Load the SavvyTrader app in your browser.
2. Open Developer Tools → Network.
3. Set the performance timeline to **Max**.
4. In the Network tab, find the request to:
   `https://api.savvytrader.com/core/portfolios/4737/valuations?range=all`
5. Right‑click the request → **Copy → Copy response** (or **Copy as cURL** if you prefer).
6. Save the JSON array to a file under `data/import/` (e.g., `data/import/valuations-YYYY-MM-DD.json`).

Important: the copied request includes short‑lived access tokens. **Do not** commit or share those tokens.

Run importer (Makefile entrypoint):

```bash
# Import the latest JSON and CSV from data/import/
make import
# or directly as a module
./venv/bin/python -m scripts.import_latest -v
```

What it does:
- Picks the latest `.json` by payload date (or mtime) and writes `data/valuations.json` atomically.
- Picks the latest `.csv` by mtime and writes `data/private/fidelity-performance.csv` atomically.
- Moves processed files to `data/import/archive/YYYY-MM-DD/` (kept locally, ignored by Git).

## Run analysis

```bash
# Interactive shell (default source = Mingdom)
make run

# CLI directly
./venv/bin/python -m portfolio_cli performance
./venv/bin/python -m portfolio_cli performance mingdom --year 2024
./venv/bin/python -m portfolio_cli performance fidelity --fidelity-csv data/private/fidelity-performance.csv

# Skip benchmark columns if needed
./venv/bin/python -m portfolio_cli performance --no-benchmarks

# Generate HTML report (all sources by default)
./venv/bin/python -m portfolio_cli report --output dist/index.html

# Generate report for a single source
./venv/bin/python -m portfolio_cli report mingdom --output dist/index.html
./venv/bin/python -m portfolio_cli report fidelity --fidelity-csv data/private/fidelity-performance.csv --output dist/index.html
```

### Benchmarks

- Default benchmarks are: SPY, QQQ, ARKK. These appear in CLI tables and the HTML report when benchmarks are enabled.
- To customize the list, set `PORTFOLIO_BENCHMARKS` to a comma-separated list (e.g., `PORTFOLIO_BENCHMARKS="SPY,QQQ,IWM"`).

## Generate report

```bash
make report
```

Tip: filter sources in the report by passing them after `report`, e.g. `./venv/bin/python -m portfolio_cli report mingdom -o dist/index.html`. Use `--no-benchmarks` to hide benchmarks.

The Summary Metrics now include 3M (trailing 3-month compounded return) alongside YTD and CAGR.

## Tests

```bash
make test
```

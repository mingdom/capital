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

Run importer (Makefile entrypoint):

```bash
# Optional: set a passphrase to enable local DB encryption (recommended)
export MINGDOM_DB_PASSPHRASE='your-strong-passphrase'

# Import the latest JSON and CSV from data/import/
make import
# or directly as a module
./venv/bin/python -m scripts.import_latest -v
```

What it does:
- Picks the latest `.json` by payload date (or mtime) and writes `data/valuations.json` atomically.
- Picks the latest `.csv` by mtime and writes `data/private/fidelity-performance.csv` atomically.
- If a passphrase is provided, stores encrypted payloads/contents into `data/localdb.sqlite3`.
- Moves processed files to `data/import/archive/YYYY-MM-DD/` (kept locally, ignored by Git).

## Run analysis

```bash
# Interactive shell (default source = SavvyTrader)
make run

# CLI directly
./venv/bin/python -m portfolio_cli performance
./venv/bin/python -m portfolio_cli performance savvytrader --year 2024
./venv/bin/python -m portfolio_cli performance fidelity --fidelity-csv data/private/fidelity-performance.csv

# Skip benchmark columns if needed
./venv/bin/python -m portfolio_cli performance --no-benchmarks

# Generate HTML report
./venv/bin/python -m portfolio_cli report --output dist/index.html

# Launch web dashboard (Fidelity-only Streamlit app)
make web
# or run directly
./venv/bin/python -m portfolio_cli web --port 8501

The dashboard focuses on Fidelity exports: upload a CSV or rely on the fallback path shown in the UI. SavvyTrader data remains available through the CLI commands above.
```

### Local encryption

- Set `MINGDOM_DB_PASSPHRASE` in your shell to enable encryption when running `scripts/import_latest.py`.
- If not set, the importer will prompt interactively (TTY) or skip the DB step and only update the canonical files + archive.
- The passphrase is never written to disk. A KDF salt is stored in the local DB `meta` table.

Initialize the local DB explicitly (optional):

```bash
export MINGDOM_DB_PASSPHRASE='your-strong-passphrase'
make db-init
# or directly as a module
./venv/bin/python -m scripts.db_tools init -v
```

### Benchmarks

- Default benchmarks are: SPY, QQQ, ARKK. These appear in CLI tables, the HTML report, and the web dashboard when benchmarks are enabled.
- To customize the list, set `PORTFOLIO_BENCHMARKS` to a comma-separated list (e.g., `PORTFOLIO_BENCHMARKS="SPY,QQQ,IWM"`).

## Generate report

```bash
make report
```

## Tests

```bash
make test
```

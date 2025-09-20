# Mingdom Capital Performance Tracker

## Setup

```bash
python3 -m venv venv
./venv/bin/pip install -U pip
./venv/bin/pip install -r requirements.txt -r dev-requirements.txt
```

## Update data

SavvyTrader: save the portfolio valuations JSON to `data/valuations.json`.

Fidelity: copy the investment income CSV export to `data/private/fidelity-performance.csv` (git-ignored).

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

## Generate report

```bash
make report
```

## Tests

```bash
make test
```

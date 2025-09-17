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
```

## Generate report

```bash
make report
```

## Tests

```bash
make test
```

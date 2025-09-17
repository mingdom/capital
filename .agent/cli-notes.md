# CLI Implementation Notes

## Overview

- Core entry point: `portfolio_cli.cli` (Typer app) with `performance` command accepting positional `sources` (`savvytrader`, `fidelity`) and showing Rich tables.
- Interactive shell: `portfolio_cli.shell.PortfolioShell`, wraps Typer commands, provides tab completion and helper commands (`sources`).
- Analysis layer: `portfolio_cli.analysis` exposes shared calculators:
  - `load_daily_changes` + `calculate_monthly_returns` for SavvyTrader JSON.
  - `load_fidelity_monthly_returns` for Fidelity CSV (cash-flow adjusted).
  - `run_portfolio_analysis` dispatches by source and returns `PortfolioAnalysis` dataclass.
- Output formatting uses Rich tables: last 12 monthly returns side-by-side plus summary metrics (CAGR, YTD, Max Drawdown, Sharpe, Sortino).

## Why Typer?

- Strong typing reduces boilerplate and keeps CLI options in sync with function signatures.
- Built-in `--help` rendering and shell completion scripts (`python -m portfolio_cli --install-completion`).
- Easy to embed within the interactive shell by calling `get_command(app)`.

Alternatives considered:
- `argparse`: minimal dependencies but verbose for subcommands and help text.
- `click`: ergonomic decorators, but Typer builds on it while leveraging type hints.

## Fidelity data ingestion

- CSV parser strips metadata before the `Monthly` header, normalizes dollar values, and computes performance as `(market change + dividends + interest - fees) / beginning balance`.
- Deposits/withdrawals are ignored for return calculation but kept accessible for future cash-flow analysis.

## Testing

- `tests/test_cli.py` covers SavvyTrader/Fidelity CLI paths, shell command queues, and completion helpers.
- Fidelity parser tested with synthetic sample (`_fidelity_csv()` function).

## Future ideas

- Add `report` subcommand to wrap `scripts/build_report.py`.
- Extend `sources` registry for additional providers with shared interface.
- Persist shell history under `~/.config/portfolio_cli/history` for quality-of-life improvement.
- Allow custom benchmark selection beyond SPY/QQQ.

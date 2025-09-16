"""Command-line interface built with Typer."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Optional

import typer

from portfolio_cli.analysis import (
    ANNUAL_RF_RATE,
    JSON_FILE_PATH,
    format_portfolio_summary,
    run_portfolio_analysis,
)
from sortino import build_benchmark_comparison_table


app = typer.Typer(help="Portfolio analytics toolkit for SavvyTrader exports")


@app.callback()
def main_callback() -> None:
    """Inspect performance metrics, compare benchmarks, and export summaries."""


@app.command("analyze")
def analyze_command(
    json_path: Path = typer.Option(
        JSON_FILE_PATH,
        "--json",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        help="Path to the SavvyTrader valuations JSON file.",
        show_default=True,
    ),
    annual_rf: float = typer.Option(
        ANNUAL_RF_RATE,
        "--rf",
        min=0.0,
        help="Annual risk-free rate used for Sharpe/Sortino calculations (e.g., 0.04).",
        show_default=True,
    ),
    year: Optional[int] = typer.Option(
        None,
        "--year",
        help="Calendar year to use for YTD performance (defaults to the current year).",
    ),
    benchmarks: bool = typer.Option(
        False,
        "--benchmarks/--no-benchmarks",
        help="Include SPY/QQQ comparison table after the portfolio summary.",
    ),
) -> None:
    """Run the monthly aggregation and display key metrics."""

    current_year = year or datetime.now().year
    analysis = run_portfolio_analysis(json_file=json_path, annual_rf=annual_rf, current_year=current_year)
    typer.echo(format_portfolio_summary(analysis, current_year))

    if benchmarks:
        table = build_benchmark_comparison_table(analysis.monthly_returns, annual_rf, current_year)
        typer.echo(table)


def run() -> None:
    """Run the CLI."""

    app()


if __name__ == "__main__":
    run()

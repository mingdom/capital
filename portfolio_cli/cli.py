"""Command-line interface built with Typer."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from pathlib import Path
import sys
from typing import Optional

import typer

from portfolio_cli.analysis import (
    ANNUAL_RF_RATE,
    FIDELITY_CSV_PATH,
    JSON_FILE_PATH,
    format_portfolio_summary,
    run_portfolio_analysis,
)
from sortino import build_benchmark_comparison_table
from portfolio_cli.shell import start_shell


class SourceKind(str, Enum):
    SAVVYTRADER = "savvytrader"
    FIDELITY = "fidelity"

    def default_path(self) -> Path:
        if self is SourceKind.SAVVYTRADER:
            return JSON_FILE_PATH
        return FIDELITY_CSV_PATH


app = typer.Typer(
    help=(
        "Portfolio analytics toolkit. Default source is SavvyTrader; use "
        "--source fidelity to analyze Fidelity exports."
    ),
    no_args_is_help=False,
)


@app.callback()
def main_callback() -> None:
    """Inspect performance metrics, compare benchmarks, and export summaries."""


@app.command("analyze")
def analyze_command(
    source: SourceKind = typer.Argument(  # type: ignore[arg-type]
        SourceKind.SAVVYTRADER,
        case_sensitive=False,
        help=(
            "Portfolio data format to load. "
            "savvytrader → data/valuations.json (default). "
            "fidelity → data/private/fidelity-performance.csv."
        ),
        show_default=True,
    ),
    input_path: Optional[Path] = typer.Option(
        None,
        "--input",
        "--json",
        file_okay=True,
        dir_okay=False,
        readable=True,
        help="Override data file path for the selected source.",
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
    analysis = run_portfolio_analysis(
        source=str(source.value),
        input_path=input_path if input_path is not None else source.default_path(),
        annual_rf=annual_rf,
        current_year=current_year,
    )
    typer.echo(format_portfolio_summary(analysis, current_year))

    if benchmarks:
        table = build_benchmark_comparison_table(analysis.monthly_returns, annual_rf, current_year)
        typer.echo(table)


@app.command("interactive")
def interactive_command() -> None:
    """Launch the interactive shell."""

    start_shell(app)


def run() -> None:
    """Run the CLI."""

    if len(sys.argv) <= 1:
        start_shell(app)
    else:
        app()


if __name__ == "__main__":
    run()

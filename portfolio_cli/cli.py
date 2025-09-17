"""Command-line interface built with Typer."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from pathlib import Path
import sys
from typing import List, Optional

import typer
import pandas as pd

from portfolio_cli.analysis import (
    ANNUAL_RF_RATE,
    FIDELITY_CSV_PATH,
    JSON_FILE_PATH,
    PortfolioAnalysis,
    calculate_metrics,
    run_portfolio_analysis,
)
from benchmarks import get_benchmark_series
from rich.console import Console
from rich.table import Table
from rich import box

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


@app.command("performance")
def performance_command(
    sources: Optional[List[SourceKind]] = typer.Argument(  # type: ignore[arg-type]
        None,
        case_sensitive=False,
        help="Portfolio sources to include (savvytrader fidelity). Defaults to both.",
    ),
    savvy_json: Path = typer.Option(
        JSON_FILE_PATH,
        "--savvy-json",
        file_okay=True,
        dir_okay=False,
        readable=True,
        help="Path to SavvyTrader valuations JSON file.",
        show_default=True,
    ),
    fidelity_csv: Path = typer.Option(
        FIDELITY_CSV_PATH,
        "--fidelity-csv",
        file_okay=True,
        dir_okay=False,
        readable=True,
        help="Path to Fidelity investment income CSV export.",
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
        True,
        "--benchmarks/--no-benchmarks",
        help="Include SPY and QQQ benchmarks alongside portfolio performance.",
        show_default=True,
    ),
) -> None:
    """Display monthly returns and summary metrics for one or both portfolios."""

    current_year = year or datetime.now().year
    requested = [SourceKind.SAVVYTRADER, SourceKind.FIDELITY] if not sources else list(dict.fromkeys(sources))

    console = Console()
    monthly_map: dict[str, pd.Series] = {}
    metrics_map: dict[str, PortfolioAnalysis] = {}
    missing: list[str] = []

    for src in requested:
        path = savvy_json if src is SourceKind.SAVVYTRADER else fidelity_csv
        try:
            analysis = run_portfolio_analysis(
                source=str(src.value),
                input_path=path,
                annual_rf=annual_rf,
                current_year=current_year,
            )
        except FileNotFoundError:
            missing.append(f"{src.value} (missing file: {path})")
            continue
        except ValueError as err:
            missing.append(f"{src.value} ({err})")
            continue

        portfolio_name = "SavvyTrader" if src is SourceKind.SAVVYTRADER else "Fidelity"
        monthly_map[portfolio_name] = analysis.monthly_returns
        metrics_map[portfolio_name] = analysis

    if not monthly_map:
        console.print("[bold red]No portfolio data available[/bold red] — please check file paths.")
        for note in missing:
            console.print(f"• {note}")
        raise typer.Exit(code=1)

    combined = pd.DataFrame({name: series for name, series in monthly_map.items()})
    combined = combined.sort_index()

    if benchmarks:
        months_index = combined.index
        if months_index.empty:
            all_series = list(monthly_map.values())
            if all_series:
                months_index = pd.concat(all_series).sort_index().index
        for symbol, label in (("SPY", "SPY"), ("QQQ", "QQQ")):
            if months_index.empty:
                continue
            benchmark_series = get_benchmark_series(symbol, months_index)
            if benchmark_series.empty:
                missing.append(f"benchmark {symbol} (no cached data)")
                continue
            benchmark_series = benchmark_series.reindex(months_index)
            combined[label] = benchmark_series
            metrics_map[label] = PortfolioAnalysis(
                monthly_returns=benchmark_series,
                metrics=calculate_metrics(benchmark_series.dropna(), annual_rf, current_year),
            )

    combined = combined.sort_index()
    recent = combined.tail(12)

    def fmt_pct(value: float | None) -> str:
        return f"{value * 100:.1f}%" if value is not None else "—"

    returns_table = Table(title="Monthly Returns · last 12 months", box=box.MINIMAL_DOUBLE_HEAD, show_lines=False)
    returns_table.add_column("Month", style="bold")
    for name in combined.columns:
        returns_table.add_column(name, justify="right")

    for month, row in recent.iterrows():
        month_label = str(month)
        formatted_row = [fmt_pct(row[col]) if pd.notna(row[col]) else "—" for col in combined.columns]
        returns_table.add_row(month_label, *formatted_row)

    console.print(returns_table)
    console.print()

    metrics_table = Table(title="Summary Metrics", box=box.MINIMAL_DOUBLE_HEAD, show_lines=False)
    metrics_table.add_column("Metric", style="bold")
    for name in combined.columns:
        metrics_table.add_column(name, justify="right")

    metric_rows = [
        ("CAGR", lambda m: m.metrics.cagr),
        ("YTD", lambda m: m.metrics.ytd),
        ("Max Drawdown", lambda m: m.metrics.max_dd_monthly),
        ("Sharpe", lambda m: m.metrics.sharpe, True),
        ("Sortino", lambda m: m.metrics.sortino, True),
    ]

    for label, getter, *rest in metric_rows:
        is_ratio = rest[0] if rest else False
        row_values = []
        for name in combined.columns:
            metrics = metrics_map.get(name)
            if metrics is None:
                row_values.append("—")
                continue
            value = getter(metrics)
            if value is None:
                row_values.append("—")
            else:
                row_values.append(f"{value:.1f}" if is_ratio else fmt_pct(value))
        metrics_table.add_row(label, *row_values)

    console.print(metrics_table)

    if missing:
        console.print()
        console.print("[yellow]Skipped sources:[/yellow]")
        for note in missing:
            console.print(f"• {note}")


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

"""Command-line interface built with Typer."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
import sys
from typing import List, Optional

import pandas as pd
import typer
from rich import box
from rich.console import Console
from rich.table import Table

from portfolio_cli.analysis import ANNUAL_RF_RATE, FIDELITY_CSV_PATH, JSON_FILE_PATH
from portfolio_cli.performance import SUPPORTED_SOURCES, SourceKind, collect_performance_data
from portfolio_cli.report import render_html_report
from portfolio_cli.shell import start_shell


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
    """Display monthly returns and summary metrics for selected portfolios."""

    current_year = year or datetime.now().year
    console = Console()

    bundle = collect_performance_data(
        sources=sources,
        savvy_json=savvy_json,
        fidelity_csv=fidelity_csv,
        annual_rf=annual_rf,
        current_year=current_year,
        include_benchmarks=benchmarks,
    )

    if bundle.combined.empty:
        console.print("[bold red]No portfolio data available[/bold red] — please check file paths.")
        for note in bundle.missing:
            console.print(f"• {note}")
        raise typer.Exit(code=1)

    combined = bundle.combined
    recent = bundle.recent if not bundle.recent.empty else combined
    metrics_map = bundle.metrics

    def fmt_pct(value: float | None) -> str:
        return f"{value * 100:.1f}%" if value is not None else "—"

    returns_table = Table(title="Monthly Returns · last 12 months", box=box.MINIMAL_DOUBLE_HEAD, show_lines=False)
    returns_table.add_column("Month", style="bold")
    columns = list(combined.columns)
    for name in columns:
        returns_table.add_column(name, justify="right")

    for month, row in recent.iterrows():
        month_label = str(month)
        formatted_row = [fmt_pct(row[col]) if pd.notna(row[col]) else "—" for col in columns]
        returns_table.add_row(month_label, *formatted_row)

    console.print(returns_table)
    console.print()

    metrics_table = Table(title="Summary Metrics", box=box.MINIMAL_DOUBLE_HEAD, show_lines=False)
    metrics_table.add_column("Metric", style="bold")
    for name in columns:
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
        for name in columns:
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

    if bundle.missing:
        console.print()
        console.print("[yellow]Skipped sources:[/yellow]")
        for note in bundle.missing:
            console.print(f"• {note}")


@app.command("report")
def report_command(
    output: Path = typer.Option(
        Path("dist/index.html"),
        "--output",
        "-o",
        file_okay=True,
        dir_okay=False,
        writable=True,
        help="Destination HTML file for the report.",
        show_default=True,
    ),
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
        help="Include SPY and QQQ benchmarks in the report.",
        show_default=True,
    ),
    title: str = typer.Option(
        "Mingdom Capital Performance",
        "--title",
        help="Title used at the top of the HTML report.",
    ),
) -> None:
    """Generate an HTML report covering the selected portfolios."""

    current_year = year or datetime.now().year
    console = Console()

    bundle = collect_performance_data(
        sources=sources,
        savvy_json=savvy_json,
        fidelity_csv=fidelity_csv,
        annual_rf=annual_rf,
        current_year=current_year,
        include_benchmarks=benchmarks,
    )

    if bundle.combined.empty:
        console.print("[bold red]No portfolio data available — report not created.[/bold red]")
        for note in bundle.missing:
            console.print(f"• {note}")
        raise typer.Exit(code=1)

    html = render_html_report(bundle, title=title)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(html, encoding="utf-8")

    console.print(f"[green]Report written to {output}[/green]")
    if bundle.missing:
        console.print("[yellow]Notes:[/yellow]")
        for note in bundle.missing:
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

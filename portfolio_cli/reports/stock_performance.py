"""Stock performance report generation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Dict, List, Literal, Optional

from rich import box
from rich.console import Console
from rich.table import Table

from .utils import (
    Holding,
    fetch_historical_prices,
    get_period_start_date,
    load_holdings,
)


Period = Literal["3mo", "ytd", "1y"]
PERIODS: List[Period] = ["3mo", "ytd", "1y"]


@dataclass
class StockPerformance:
    """Performance data for a single stock over a period."""

    symbol: str
    current_price: float
    period_start_price: float
    period_return: float  # Decimal (e.g., 0.15 = 15%)
    allocation: float  # Current portfolio allocation
    total_return: float  # Total return since purchase


def calculate_performance(
    holdings: List[Holding],
    period: Period,
    reference_date: Optional[date] = None,
) -> List[StockPerformance]:
    """
    Calculate performance for each holding over the specified period.

    Args:
        holdings: List of current holdings
        period: Time period ('3mo', 'ytd', '1y')
        reference_date: Reference date for period calculation

    Returns:
        List of StockPerformance sorted by period_return (descending)
    """
    if not holdings:
        return []

    # Get period start date
    start_date = get_period_start_date(period, reference_date)

    # Fetch historical prices
    symbols = [h.symbol for h in holdings]
    historical_prices = fetch_historical_prices(symbols, start_date)

    # Calculate returns
    results: List[StockPerformance] = []
    for h in holdings:
        start_price = historical_prices.get(h.symbol)
        if start_price is None or start_price == 0:
            # Skip if we couldn't get historical price
            continue

        period_return = (h.current_price - start_price) / start_price

        results.append(
            StockPerformance(
                symbol=h.symbol,
                current_price=h.current_price,
                period_start_price=start_price,
                period_return=period_return,
                allocation=h.allocation,
                total_return=h.total_return_pct,
            )
        )

    # Sort by period return descending
    results.sort(key=lambda x: x.period_return, reverse=True)
    return results


def format_performance_table(
    performances: List[StockPerformance],
    period: Period,
    top_n: int = 5,
    show_bottom: bool = True,
) -> Table:
    """
    Create a Rich table showing top (and bottom) performers.

    Args:
        performances: Sorted list of stock performances
        period: Period label for display
        top_n: Number of top/bottom performers to show
        show_bottom: Whether to include bottom performers
    """
    period_labels = {"3mo": "3-Month", "ytd": "YTD", "1y": "1-Year"}
    period_label = period_labels.get(period, period)

    table = Table(
        title=f"[bold]{period_label} Stock Performance[/bold]",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold cyan",
    )

    table.add_column("Rank", justify="right", style="dim", width=4)
    table.add_column("Symbol", style="bold", width=8)
    table.add_column("Return", justify="right", width=10)
    table.add_column("Current $", justify="right", width=12)
    table.add_column(f"Start $", justify="right", width=12)
    table.add_column("Alloc", justify="right", width=8)
    table.add_column("Total Ret", justify="right", width=10)

    def fmt_pct(value: float) -> str:
        """Format percentage with color."""
        pct = value * 100
        if pct >= 0:
            return f"[green]+{pct:.1f}%[/green]"
        return f"[red]{pct:.1f}%[/red]"

    def fmt_price(value: float) -> str:
        return f"${value:,.2f}"

    def add_row(rank: int, perf: StockPerformance) -> None:
        table.add_row(
            str(rank),
            perf.symbol,
            fmt_pct(perf.period_return),
            fmt_price(perf.current_price),
            fmt_price(perf.period_start_price),
            f"{perf.allocation * 100:.1f}%",
            fmt_pct(perf.total_return),
        )

    # Top performers
    for i, perf in enumerate(performances[:top_n], 1):
        add_row(i, perf)

    if show_bottom and len(performances) > top_n * 2:
        # Add separator
        table.add_row("", "[dim]...[/dim]", "", "", "", "", "")

        # Bottom performers
        bottom = performances[-top_n:]
        start_rank = len(performances) - top_n + 1
        for i, perf in enumerate(bottom, start_rank):
            add_row(i, perf)

    return table


def generate_performance_report(
    periods: Optional[List[Period]] = None,
    top_n: int = 5,
    show_bottom: bool = True,
    console: Optional[Console] = None,
) -> None:
    """
    Generate and display the stock performance report.

    Args:
        periods: Periods to include (defaults to all)
        top_n: Number of top/bottom performers per period
        show_bottom: Whether to show bottom performers
        console: Rich console for output
    """
    console = console or Console()
    periods = periods or PERIODS

    # Load holdings
    holdings = load_holdings()
    if not holdings:
        console.print("[red]No holdings found in prices.json[/red]")
        return

    console.print()
    console.rule("[bold blue]Stock Performance Report[/bold blue]")
    console.print(f"[dim]Holdings: {len(holdings)} | Generated: {date.today()}[/dim]")
    console.print()

    for period in periods:
        performances = calculate_performance(holdings, period)

        if not performances:
            console.print(f"[yellow]No data available for {period}[/yellow]")
            continue

        table = format_performance_table(
            performances, period, top_n=top_n, show_bottom=show_bottom
        )
        console.print(table)
        console.print()

    console.print("[dim]Note: Returns calculated from historical prices via Yahoo Finance[/dim]")

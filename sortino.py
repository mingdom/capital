from __future__ import annotations

from datetime import datetime
from typing import Dict, Iterable

import pandas as pd

from benchmarks import configured_benchmarks, get_benchmark_series, last_complete_month
from portfolio_cli.analysis import (
    ANNUAL_RF_RATE,
    JSON_FILE_PATH,
    PerformanceMetrics,
    calculate_metrics,
    format_portfolio_summary,
    run_portfolio_analysis,
)


def convert_to_monthly_and_calculate_ratios(
    json_file: str = str(JSON_FILE_PATH),
    annual_rf: float = ANNUAL_RF_RATE,
    current_year: int = datetime.now().year,
):
    """Backwards-compatible helper for legacy scripts and tests."""

    analysis = run_portfolio_analysis(json_file=json_file, annual_rf=annual_rf, current_year=current_year)
    print(format_portfolio_summary(analysis, current_year))
    return analysis.monthly_returns, analysis.metrics.as_dict()


def compute_metrics(monthly_returns: pd.Series, annual_rf: float, current_year: int) -> Dict[str, float | None]:
    """Compatibility wrapper mirroring the legacy return signature."""

    metrics = calculate_metrics(monthly_returns, annual_rf, current_year)
    return metrics.as_dict()


def _fmt_pct(value: float | None) -> str:
    return f"{value * 100:.1f}%" if value is not None else "na"


def _fmt_val(value: float | None) -> str:
    return f"{value:.1f}" if value is not None else "na"


def compare_with_benchmarks(portfolio_monthly: pd.Series, annual_rf: float, current_year: int):
    """Print benchmark comparison table using cached market data."""

    table = build_benchmark_comparison_table(portfolio_monthly, annual_rf, current_year)
    print(table)


def build_benchmark_comparison_table(
    portfolio_monthly: pd.Series,
    annual_rf: float,
    current_year: int,
    symbols: Iterable[str] | None = None,
) -> str:
    """Return a formatted benchmark comparison table."""

    lcm = last_complete_month().to_timestamp("M")
    pm = portfolio_monthly.copy()
    pm.index = pm.index.to_timestamp("M")
    pm = pm[pm.index <= lcm]
    months = pm.index.to_period("M")

    metrics: Dict[str, PerformanceMetrics] = {
        "Portfolio": calculate_metrics(pm.to_period("M"), annual_rf, current_year)
    }

    for sym in (symbols or configured_benchmarks()):
        series = get_benchmark_series(sym, months)
        metrics[sym] = calculate_metrics(series, annual_rf, current_year)

    lines = ["", "Comparison vs Benchmarks (rounded):"]
    header = f"{'Asset':<12} {'CAGR':>8} {'MaxDD(M)':>10} {'YTD':>8} {'Sharpe':>8} {'Sortino':>8}"
    lines.append(header)
    lines.append("-" * len(header))
    for name, perf in metrics.items():
        row = f"{name:<12} {_fmt_pct(perf.cagr):>8} {_fmt_pct(perf.max_dd_monthly):>10} {_fmt_pct(perf.ytd):>8} {_fmt_val(perf.sharpe):>8} {_fmt_val(perf.sortino):>8}"
        lines.append(row)
    return "\n".join(lines)


if __name__ == "__main__":
    from portfolio_cli.cli import run

    run()

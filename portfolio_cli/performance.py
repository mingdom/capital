"""Shared helpers for collecting portfolio performance data."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

import pandas as pd

from benchmarks import configured_benchmarks, get_benchmark_series
from portfolio_cli.analysis import (
    ANNUAL_RF_RATE,
    FIDELITY_CSV_PATH,
    JSON_FILE_PATH,
    PerformanceMetrics,
    PortfolioAnalysis,
    calculate_metrics,
    run_portfolio_analysis,
)


class SourceKind(str, Enum):
    SAVVYTRADER = "savvytrader"
    FIDELITY = "fidelity"

    @property
    def default_path(self) -> Path:
        if self is SourceKind.SAVVYTRADER:
            return JSON_FILE_PATH
        return FIDELITY_CSV_PATH

    @property
    def label(self) -> str:
        return "SavvyTrader" if self is SourceKind.SAVVYTRADER else "Fidelity"


SUPPORTED_SOURCES: Tuple[str, ...] = tuple(kind.value for kind in SourceKind)


@dataclass
class PerformanceBundle:
    combined: pd.DataFrame
    recent: pd.DataFrame
    metrics: Dict[str, PortfolioAnalysis]
    missing: List[str]
    last_period: Optional[pd.Period]


def _ensure_period_index(series: pd.Series) -> pd.Series:
    if isinstance(series.index, pd.PeriodIndex):
        return series
    if isinstance(series.index, pd.DatetimeIndex):
        return series.to_period("M")
    raise ValueError("Series must be indexed by period or datetime")


def collect_performance_data(
    sources: Optional[Iterable[SourceKind]] = None,
    savvy_json: Path | None = None,
    fidelity_csv: Path | None = None,
    annual_rf: float = ANNUAL_RF_RATE,
    current_year: Optional[int] = None,
    include_benchmarks: bool = True,
) -> PerformanceBundle:
    if current_year is None:
        current_year = pd.Timestamp.today().year

    requested = list(dict.fromkeys(sources or [SourceKind.SAVVYTRADER, SourceKind.FIDELITY]))

    monthly_map: Dict[str, pd.Series] = {}
    metrics_map: Dict[str, PortfolioAnalysis] = {}
    missing: List[str] = []

    for src in requested:
        path = src.default_path
        if src is SourceKind.SAVVYTRADER and savvy_json is not None:
            path = savvy_json
        if src is SourceKind.FIDELITY and fidelity_csv is not None:
            path = fidelity_csv

        try:
            analysis = run_portfolio_analysis(
                source=src.value,
                input_path=path,
                annual_rf=annual_rf,
                current_year=current_year,
            )
        except FileNotFoundError:
            missing.append(f"{src.label} (missing file: {path})")
            continue
        except ValueError as err:
            missing.append(f"{src.label} ({err})")
            continue

        monthly_series = _ensure_period_index(analysis.monthly_returns)
        monthly_map[src.label] = monthly_series
        metrics_map[src.label] = PortfolioAnalysis(monthly_returns=monthly_series, metrics=analysis.metrics)

    combined = pd.DataFrame(monthly_map)
    combined.index = combined.index.sort_values()

    months_index = combined.index
    if months_index.empty and monthly_map:
        months_index = pd.concat(monthly_map.values()).sort_index().index

    if include_benchmarks and len(months_index) > 0:
        for symbol in configured_benchmarks():
            series = get_benchmark_series(symbol, months_index)
            if series.empty:
                missing.append(f"benchmark {symbol} (no data)")
                continue
            series = series.reindex(months_index)
            combined[symbol] = series
            metrics = calculate_metrics(series.dropna(), annual_rf, current_year)
            metrics_map[symbol] = PortfolioAnalysis(monthly_returns=series, metrics=metrics)

    combined = combined.sort_index()
    recent = combined.tail(12)

    last_period = None
    non_empty = combined.dropna(how="all")
    if not non_empty.empty:
        last_period = non_empty.index[-1]

    return PerformanceBundle(
        combined=combined,
        recent=recent,
        metrics=metrics_map,
        missing=missing,
        last_period=last_period,
    )

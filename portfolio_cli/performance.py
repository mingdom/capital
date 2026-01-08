"""Shared helpers for collecting portfolio performance data."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

import numpy as np
import pandas as pd

from benchmarks import configured_benchmarks
from portfolio_cli.analysis import (
    ANNUAL_RF_RATE,
    FIDELITY_CSV_PATH,
    JSON_FILE_PATH,
    PortfolioAnalysis,
    calculate_metrics,
    compute_drawdown_stats,
    load_daily_changes,
    run_portfolio_analysis,
)


class SourceKind(str, Enum):
    MINGDOM = "mingdom"
    SAVVYTRADER = "savvytrader"
    FIDELITY = "fidelity"

    @property
    def default_path(self) -> Path:
        if self in {SourceKind.MINGDOM, SourceKind.SAVVYTRADER}:
            return JSON_FILE_PATH
        return FIDELITY_CSV_PATH

    @property
    def label(self) -> str:
        if self in {SourceKind.MINGDOM, SourceKind.SAVVYTRADER}:
            return "Mingdom"
        return "Fidelity"


SUPPORTED_SOURCES: Tuple[str, ...] = tuple(kind.value for kind in SourceKind)


@dataclass
class PerformanceBundle:
    combined: pd.DataFrame
    recent: pd.DataFrame
    metrics: Dict[str, PortfolioAnalysis]
    risk_metrics: Dict[str, "RiskMetrics"]
    windows: Dict[str, "SeriesWindow"]
    freq_metrics: Dict[str, "MultiFreqRiskMetrics"]
    missing: List[str]
    last_period: Optional[pd.Period]
    annual_rf: float
    current_year: int


def _ensure_period_index(series: pd.Series) -> pd.Series:
    if isinstance(series.index, pd.PeriodIndex):
        return series
    if isinstance(series.index, pd.DatetimeIndex):
        return series.to_period("M")
    raise ValueError("Series must be indexed by period or datetime")


@dataclass(frozen=True)
class SeriesWindow:
    start: Optional[pd.Period]
    end: Optional[pd.Period]
    count: int


@dataclass(frozen=True)
class RiskMetrics:
    volatility: float | None
    downside_dev: float | None
    max_drawdown: float | None
    drawdown_duration: int | None
    var_95: float | None
    cvar_95: float | None
    var_99: float | None
    cvar_99: float | None
    hit_rate: float | None
    avg_up: float | None
    avg_down: float | None
    beta_spy: float | None
    corr_spy: float | None
    worst_month: float | None
    best_month: float | None
    up_capture: float | None
    down_capture: float | None


@dataclass(frozen=True)
class PeriodRiskMetrics:
    volatility: float | None
    sharpe: float | None
    sortino: float | None
    var_95: float | None
    cvar_95: float | None


@dataclass(frozen=True)
class MultiFreqRiskMetrics:
    daily: PeriodRiskMetrics
    weekly: PeriodRiskMetrics
    monthly: PeriodRiskMetrics


def _annualized_vol(series: pd.Series, periods: int) -> float | None:
    if len(series) < 2:
        return None
    return float(series.std(ddof=1) * np.sqrt(periods))


def _downside_dev(series: pd.Series, annual_rf: float, periods: int) -> float | None:
    if series.empty:
        return None
    rf_period = annual_rf / periods
    downside = np.minimum(series - rf_period, 0)
    if len(downside) == 0:
        return None
    return float(np.sqrt(np.mean(downside**2)) * np.sqrt(periods))


def _var_cvar(series: pd.Series, level: float) -> tuple[float | None, float | None]:
    if series.empty:
        return None, None
    tail_q = 1 - level
    var = float(np.quantile(series, tail_q))
    tail = series[series <= var]
    cvar = float(tail.mean()) if not tail.empty else None
    return var, cvar


def _beta_corr(series: pd.Series, bench: pd.Series | None) -> tuple[float | None, float | None]:
    if bench is None:
        return None, None
    aligned = pd.concat([series, bench], axis=1).dropna()
    if len(aligned) < 2:
        return None, None
    x = aligned.iloc[:, 0]
    y = aligned.iloc[:, 1]
    var = float(y.var(ddof=1))
    if var == 0:
        beta = None
    else:
        beta = float(x.cov(y) / var)
    corr = float(x.corr(y))
    return beta, corr


def _capture_ratios(series: pd.Series, bench: pd.Series | None) -> tuple[float | None, float | None]:
    """Calculate up-capture and down-capture ratios vs benchmark.

    Up-capture: Average portfolio return / average benchmark return when benchmark > 0
    Down-capture: Average portfolio return / average benchmark return when benchmark < 0

    Ideal: High up-capture (>100%), low down-capture (<100%)
    """
    if bench is None:
        return None, None
    aligned = pd.concat([series, bench], axis=1).dropna()
    if len(aligned) < 2:
        return None, None

    portfolio = aligned.iloc[:, 0]
    benchmark = aligned.iloc[:, 1]

    # Up-capture: performance when benchmark is positive
    up_mask = benchmark > 0
    if up_mask.sum() < 1:
        up_capture = None
    else:
        bench_up_mean = float(benchmark[up_mask].mean())
        port_up_mean = float(portfolio[up_mask].mean())
        up_capture = port_up_mean / bench_up_mean if bench_up_mean != 0 else None

    # Down-capture: performance when benchmark is negative
    down_mask = benchmark < 0
    if down_mask.sum() < 1:
        down_capture = None
    else:
        bench_down_mean = float(benchmark[down_mask].mean())
        port_down_mean = float(portfolio[down_mask].mean())
        down_capture = port_down_mean / bench_down_mean if bench_down_mean != 0 else None

    return up_capture, down_capture


def _risk_metrics(
    series: pd.Series,
    *,
    annual_rf: float,
    periods_per_year: int,
    benchmark: pd.Series | None = None,
) -> RiskMetrics:
    clean = series.dropna()
    vol = _annualized_vol(clean, periods_per_year)
    downside = _downside_dev(clean, annual_rf, periods_per_year)
    max_dd, dd_duration = compute_drawdown_stats(clean)
    var_95, cvar_95 = _var_cvar(clean, 0.95)
    var_99, cvar_99 = _var_cvar(clean, 0.99)
    hit_rate = float((clean > 0).mean()) if not clean.empty else None
    avg_up = float(clean[clean > 0].mean()) if (clean > 0).any() else None
    avg_down = float(clean[clean < 0].mean()) if (clean < 0).any() else None
    beta, corr = _beta_corr(clean, benchmark)
    up_capture, down_capture = _capture_ratios(clean, benchmark)
    worst_month = float(clean.min()) if not clean.empty else None
    best_month = float(clean.max()) if not clean.empty else None
    return RiskMetrics(
        volatility=vol,
        downside_dev=downside,
        max_drawdown=max_dd,
        drawdown_duration=dd_duration,
        var_95=var_95,
        cvar_95=cvar_95,
        var_99=var_99,
        cvar_99=cvar_99,
        hit_rate=hit_rate,
        avg_up=avg_up,
        avg_down=avg_down,
        beta_spy=beta,
        corr_spy=corr,
        worst_month=worst_month,
        best_month=best_month,
        up_capture=up_capture,
        down_capture=down_capture,
    )


def _period_risk_metrics(series: pd.Series, annual_rf: float, periods: int) -> PeriodRiskMetrics:
    clean = series.dropna()
    vol = _annualized_vol(clean, periods)
    rf_period = annual_rf / periods
    mean_excess = float(np.mean(clean) - rf_period) if not clean.empty else None
    std = float(np.std(clean, ddof=1)) if len(clean) > 1 else None
    downside = np.minimum(clean - rf_period, 0)
    down_dev = float(np.sqrt(np.mean(downside**2))) if len(clean) > 0 else None
    sharpe = mean_excess / std * np.sqrt(periods) if std and std != 0 else None
    sortino = mean_excess / down_dev * np.sqrt(periods) if down_dev and down_dev != 0 else None
    var_95, cvar_95 = _var_cvar(clean, 0.95)
    return PeriodRiskMetrics(
        volatility=vol,
        sharpe=sharpe,
        sortino=sortino,
        var_95=var_95,
        cvar_95=cvar_95,
    )


def _load_mingdom_daily_returns(path: Path) -> pd.Series:
    df = load_daily_changes(path)
    series = pd.to_numeric(df["dailyTotalValueChange"], errors="coerce")
    series.index = pd.to_datetime(df["summaryDate"], errors="coerce")
    series = series.dropna()
    series = series[series != 0]
    return series.sort_index()


def _resample_compound(returns: pd.Series, rule: str) -> pd.Series:
    if returns.empty:
        return returns
    grouped = returns.resample(rule).apply(lambda s: float(np.prod(1 + s) - 1) if not s.empty else np.nan)
    return grouped.dropna()


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

    requested = list(dict.fromkeys(sources or [SourceKind.MINGDOM, SourceKind.FIDELITY]))

    monthly_map: Dict[str, pd.Series] = {}
    metrics_map: Dict[str, PortfolioAnalysis] = {}
    freq_metrics: Dict[str, MultiFreqRiskMetrics] = {}
    missing: List[str] = []

    for src in requested:
        if src is SourceKind.SAVVYTRADER:
            src = SourceKind.MINGDOM
        path = src.default_path
        if src is SourceKind.MINGDOM and savvy_json is not None:
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

        if src is SourceKind.MINGDOM:
            try:
                daily_returns = _load_mingdom_daily_returns(path)
                weekly_returns = _resample_compound(daily_returns, "W-FRI")
                monthly_returns = monthly_series.dropna()
                freq_metrics[src.label] = MultiFreqRiskMetrics(
                    daily=_period_risk_metrics(daily_returns, annual_rf, 252),
                    weekly=_period_risk_metrics(weekly_returns, annual_rf, 52),
                    monthly=_period_risk_metrics(monthly_returns, annual_rf, 12),
                )
            except Exception:
                pass

    combined = pd.DataFrame(monthly_map)
    combined.index = combined.index.sort_values()

    months_index = combined.index
    if months_index.empty and monthly_map:
        months_index = pd.concat(monthly_map.values()).sort_index().index

    if include_benchmarks and len(months_index) > 0:
        # Determine inception date and current end date for aligned partials
        inception_date = None
        current_end = None

        # Try to get inception date from Mingdom data
        if SourceKind.MINGDOM.label in monthly_map:
            mingdom_series = monthly_map[SourceKind.MINGDOM.label]
            if not mingdom_series.empty:
                first_period = mingdom_series.index[0]
                inception_date = first_period.to_timestamp('M').date()
                # Get the last date from valuations.json for current_end
                try:
                    import json
                    from datetime import date as dt_date
                    with open(JSON_FILE_PATH) as f:
                        data = json.load(f)
                        if data and isinstance(data, list) and len(data) > 0:
                            last_entry = data[-1]
                            if "summaryDate" in last_entry:
                                from datetime import datetime
                                current_end = datetime.fromisoformat(
                                    last_entry["summaryDate"]
                                ).date()
                except Exception:
                    pass

        # Fallback to today if we couldn't determine dates
        if inception_date is None:
            inception_date = months_index[0].to_timestamp('M').date()
        if current_end is None:
            from datetime import date as dt_date
            current_end = dt_date.today()

        from benchmarks import get_aligned_benchmark_series
        for symbol in configured_benchmarks():
            series = get_aligned_benchmark_series(symbol, months_index, inception_date, current_end)
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

    windows: Dict[str, SeriesWindow] = {}
    for name, series in combined.items():
        clean = series.dropna()
        if clean.empty:
            windows[name] = SeriesWindow(start=None, end=None, count=0)
        else:
            windows[name] = SeriesWindow(
                start=clean.index.min(), end=clean.index.max(), count=len(clean)
            )

    risk_metrics: Dict[str, RiskMetrics] = {}
    spy_series = combined.get("SPY")
    for name, series in combined.items():
        risk_metrics[name] = _risk_metrics(
            series,
            annual_rf=annual_rf,
            periods_per_year=12,
            benchmark=spy_series,
        )

    return PerformanceBundle(
        combined=combined,
        recent=recent,
        metrics=metrics_map,
        risk_metrics=risk_metrics,
        windows=windows,
        freq_metrics=freq_metrics,
        missing=missing,
        last_period=last_period,
        annual_rf=annual_rf,
        current_year=current_year,
    )

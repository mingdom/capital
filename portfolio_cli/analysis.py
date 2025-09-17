"""Core portfolio analytics used by the CLI interface.

The functions in this module focus on data loading and metric calculations so that
the command-line layer can stay very small and easy to extend with additional
subcommands (e.g. DCF modelling or alternative benchmark lookups).
"""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd


JSON_FILE_PATH = Path("data/valuations.json")
FIDELITY_CSV_PATH = Path("data/private/fidelity-performance.csv")
ANNUAL_RF_RATE = 0.04


@dataclass
class PerformanceMetrics:
    """Container for the key performance ratios."""

    cagr: float | None
    max_dd_monthly: float | None
    ytd: float | None
    sharpe: float | None
    sortino: float | None

    def as_dict(self) -> dict[str, float | None]:
        return {
            "cagr": self.cagr,
            "max_dd_monthly": self.max_dd_monthly,
            "ytd": self.ytd,
            "sharpe": self.sharpe,
            "sortino": self.sortino,
        }


@dataclass
class PortfolioAnalysis:
    monthly_returns: pd.Series
    metrics: PerformanceMetrics


def load_daily_changes(json_file: str | Path) -> pd.DataFrame:
    """Read SavvyTrader valuations JSON into a sorted DataFrame."""

    with Path(json_file).open("r") as handle:
        data: Iterable[dict[str, Any]] = json.load(handle)

    df = pd.DataFrame(data)
    if "summaryDate" not in df or "dailyTotalValueChange" not in df:
        raise ValueError("JSON file must contain summaryDate and dailyTotalValueChange fields")

    df["summaryDate"] = pd.to_datetime(df["summaryDate"])
    df = df.sort_values("summaryDate")
    return df


def calculate_monthly_returns(df: pd.DataFrame, drop_zeros: bool = True) -> pd.Series:
    """Aggregate daily change percentages into compounded monthly returns."""

    if drop_zeros:
        df = df[df["dailyTotalValueChange"] != 0]

    if df.empty:
        return pd.Series(dtype=float)

    df = df.copy()
    df["month"] = df["summaryDate"].dt.to_period("M")
    monthly = df.groupby("month")["dailyTotalValueChange"].apply(lambda s: float(np.prod(1 + s) - 1))
    monthly.index = pd.PeriodIndex(monthly.index, freq="M")
    return monthly.sort_index()


def calculate_metrics(monthly_returns: pd.Series, annual_rf: float, current_year: int) -> PerformanceMetrics:
    """Compute CAGR, drawdown, Sharpe/Sortino, and year-to-date return."""

    if monthly_returns.empty:
        return PerformanceMetrics(cagr=None, max_dd_monthly=None, ytd=None, sharpe=None, sortino=None)

    monthly_rf = annual_rf / 12
    mean_excess = float(np.mean(monthly_returns) - monthly_rf)
    std = float(np.std(monthly_returns, ddof=1))
    downside = np.minimum(monthly_returns - monthly_rf, 0)
    down_dev = float(np.sqrt(np.mean(downside**2)))

    sharpe = mean_excess / std * np.sqrt(12) if std != 0 else None
    sortino = mean_excess / down_dev * np.sqrt(12) if down_dev != 0 else None

    total_cum_return = float(np.prod(1 + monthly_returns) - 1)
    num_years = len(monthly_returns) / 12
    cagr = (1 + total_cum_return) ** (1 / num_years) - 1 if num_years > 0 else None

    period_filter = monthly_returns.index.year == current_year
    ytd_months = monthly_returns[period_filter]
    ytd_perf = float(np.prod(1 + ytd_months) - 1) if not ytd_months.empty else None

    max_dd_monthly = float(monthly_returns.min()) if not monthly_returns.empty else None

    return PerformanceMetrics(
        cagr=cagr,
        max_dd_monthly=max_dd_monthly,
        ytd=ytd_perf,
        sharpe=sharpe,
        sortino=sortino,
    )


def load_fidelity_monthly_returns(csv_file: str | Path) -> pd.Series:
    """Parse Fidelity export into a monthly return series."""

    path = Path(csv_file)
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle)
        headers: list[str] | None = None
        data_rows: list[list[str]] = []

        for row in reader:
            if not row:
                continue
            first_cell = row[0].strip()
            if headers is None:
                if first_cell.startswith("Monthly"):
                    headers = row
                continue
            else:
                if first_cell.startswith("Total") or first_cell == "":
                    break
                data_rows.append(row)

    if headers is None:
        raise ValueError("Could not locate 'Monthly' header in Fidelity CSV")

    periods: list[pd.Period] = []
    values: list[float] = []

    def _to_number(raw: str) -> float:
        cleaned = raw.replace("$", "").replace(",", "").strip()
        if not cleaned or cleaned == "-":
            return 0.0
        if cleaned.startswith("(") and cleaned.endswith(")"):
            cleaned = f"-{cleaned[1:-1]}"
        return float(cleaned)

    for row in data_rows:
        month_label = row[0].split("(")[0].strip()
        if not month_label:
            continue
        try:
            period = pd.Period(month_label, freq="M")
        except Exception as exc:  # pragma: no cover - unexpected format
            raise ValueError(f"Unable to parse month label '{month_label}'") from exc

        cells = (row + [""] * 9)[:9]
        beginning = _to_number(cells[1])
        market_change = _to_number(cells[2])
        dividends = _to_number(cells[3])
        interest = _to_number(cells[4])
        deposits = _to_number(cells[5])
        withdrawals = _to_number(cells[6])
        net_fees = _to_number(cells[7])

        performance = market_change + dividends + interest - net_fees
        _ = deposits, withdrawals  # explicit for future cash-flow analytics

        if beginning <= 0:
            monthly_return = float("nan")
        else:
            monthly_return = performance / beginning

        periods.append(period)
        values.append(monthly_return)

    series = pd.Series(values, index=pd.PeriodIndex(periods, freq="M"))
    series = series.sort_index()
    return series.dropna()


def run_portfolio_analysis(
    source: str = "savvytrader",
    json_file: str | Path = JSON_FILE_PATH,
    fidelity_file: str | Path = FIDELITY_CSV_PATH,
    input_path: str | Path | None = None,
    annual_rf: float = ANNUAL_RF_RATE,
    current_year: int | None = None,
) -> PortfolioAnalysis:
    """Load data for the requested source and compute metrics."""

    if current_year is None:
        current_year = datetime.now().year

    source_key = source.lower()

    if source_key == "savvytrader":
        path = Path(input_path) if input_path is not None else Path(json_file)
        if not path.exists():
            raise FileNotFoundError(path)
        df = load_daily_changes(path)
        monthly_returns = calculate_monthly_returns(df)
    elif source_key == "fidelity":
        path = Path(input_path) if input_path is not None else Path(fidelity_file)
        if not path.exists():
            raise FileNotFoundError(path)
        monthly_returns = load_fidelity_monthly_returns(path)
    else:
        raise ValueError(
            f"Unsupported source '{source}'. Expected 'savvytrader' or 'fidelity'."
        )

    metrics = calculate_metrics(monthly_returns, annual_rf, current_year)
    return PortfolioAnalysis(monthly_returns=monthly_returns, metrics=metrics)


def format_portfolio_summary(analysis: PortfolioAnalysis, current_year: int) -> str:
    """Produce the human-friendly block of text shown in the CLI output."""

    monthly = analysis.monthly_returns
    metrics = analysis.metrics

    lines: list[str] = []
    lines.append("Monthly Returns (%):")
    if monthly.empty:
        lines.append("  (no data)")
    else:
        formatted = monthly.mul(100).round(1).astype(str) + "%"
        lines.append(formatted.to_string())

    def _pct(value: float | None) -> str:
        return f"{value * 100:.1f}%" if value is not None else "na"

    def _val(value: float | None) -> str:
        return f"{value:.1f}" if value is not None else "na"

    lines.append("")
    lines.append(f"CAGR (Annual): {_pct(metrics.cagr)}")
    lines.append(f"Max Monthly Drawdown: {_pct(metrics.max_dd_monthly)}")
    lines.append(f"YTD Performance ({current_year}): {_pct(metrics.ytd)}")
    lines.append("")
    lines.append(f"Annualized Sharpe Ratio: {_val(metrics.sharpe)}")
    lines.append(f"Annualized Sortino Ratio: {_val(metrics.sortino)}")
    lines.append("")
    lines.append("How to interpret:")
    lines.append("- CAGR: annualized growth; >15% is strong.")
    lines.append("- Sharpe: risk-adjusted return; >1 good, >2 great.")
    lines.append("- Sortino: focuses on downside; higher than Sharpe when losses are limited.")
    lines.append("- Max Monthly Drawdown: worst monthly loss; smaller is better.")
    return "\n".join(lines)

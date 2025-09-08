import argparse
import json
from datetime import datetime

import numpy as np
import pandas as pd

from benchmarks import get_benchmark_series, last_complete_month

# Configurable constants
ANNUAL_RF_RATE = (
    0.04  # Annual risk-free rate (e.g., based on Treasury yields or bank rates)
)
JSON_FILE_PATH = "data/valuations.json"  # Path to the SavvyTrader valuations JSON


def convert_to_monthly_and_calculate_ratios(
    json_file=JSON_FILE_PATH, annual_rf=ANNUAL_RF_RATE, current_year=datetime.now().year
):
    # Load data from JSON
    with open(json_file, "r") as f:
        data = json.load(f)

    df = pd.DataFrame(data)
    df["summaryDate"] = pd.to_datetime(df["summaryDate"])
    df = df.sort_values("summaryDate")

    # Clean data: ignore days with zero change
    df = df[df["dailyTotalValueChange"] != 0]

    # Convert to monthly returns by compounding daily returns in each month
    df["month"] = df["summaryDate"].dt.to_period("M")
    monthly_returns = df.groupby("month")["dailyTotalValueChange"].apply(
        lambda s: np.prod(1 + s) - 1
    )

    # Print monthly returns as percentages rounded to 2 decimals
    print("Monthly Returns (%):")
    formatted_monthly = monthly_returns.mul(100).round(2).astype(str) + "%"
    print(formatted_monthly.to_string())

    # Additional Stats
    # CAGR (Compound Annual Growth Rate)
    total_cum_return = np.prod(1 + monthly_returns) - 1
    num_years = len(monthly_returns) / 12
    cagr = (1 + total_cum_return) ** (1 / num_years) - 1 if num_years > 0 else np.nan
    print(f"\nCAGR (Annual): {cagr * 100:.2f}%")

    # Max Drawdown per Month (largest monthly loss)
    max_dd_monthly = (
        monthly_returns.min() * 100 if not monthly_returns.empty else np.nan
    )
    print(f"Max Monthly Drawdown: {max_dd_monthly:.2f}%")

    # YTD Performance (for the specified year)
    ytd_months = monthly_returns[monthly_returns.index.year == current_year]
    ytd_perf = np.prod(1 + ytd_months) - 1 if not ytd_months.empty else np.nan
    print(f"YTD Performance ({current_year}): {ytd_perf * 100:.2f}%")

    # Calculate Sharpe and Sortino
    monthly_rf = annual_rf / 12

    mean_excess = np.mean(monthly_returns) - monthly_rf

    std = np.std(monthly_returns, ddof=1)

    downside = np.minimum(monthly_returns - monthly_rf, 0)
    down_dev = np.sqrt(np.mean(downside**2))

    sharpe = mean_excess / std * np.sqrt(12) if std != 0 else np.nan
    sortino = mean_excess / down_dev * np.sqrt(12) if down_dev != 0 else np.nan

    print(f"\nAnnualized Sharpe Ratio: {sharpe:.2f}")
    print(f"Annualized Sortino Ratio: {sortino:.2f}")

    # Interpretation hints
    print("\nHow to interpret:")
    print("- CAGR: annualized growth; >15% is strong.")
    print("- Sharpe: risk-adjusted return; >1 good, >2 great.")
    print("- Sortino: focuses on downside; higher than Sharpe when losses are limited.")
    print("- Max Monthly Drawdown: worst monthly loss; smaller is better.")

    return monthly_returns, {
        "cagr": cagr,
        "max_dd_monthly": max_dd_monthly / 100,  # keep in decimal form for uniformity
        "ytd": ytd_perf,
        "sharpe": sharpe,
        "sortino": sortino,
    }


def compute_metrics(monthly_returns: pd.Series, annual_rf: float, current_year: int):
    monthly_rf = annual_rf / 12
    mean_excess = np.mean(monthly_returns) - monthly_rf
    std = np.std(monthly_returns, ddof=1)
    downside = np.minimum(monthly_returns - monthly_rf, 0)
    down_dev = np.sqrt(np.mean(downside**2))
    sharpe = mean_excess / std * np.sqrt(12) if std != 0 else np.nan
    sortino = mean_excess / down_dev * np.sqrt(12) if down_dev != 0 else np.nan

    total_cum_return = np.prod(1 + monthly_returns) - 1
    num_years = len(monthly_returns) / 12
    cagr = (1 + total_cum_return) ** (1 / num_years) - 1 if num_years > 0 else np.nan

    ytd_months = monthly_returns[monthly_returns.index.year == current_year]
    ytd_perf = np.prod(1 + ytd_months) - 1 if not ytd_months.empty else np.nan

    max_dd_monthly = monthly_returns.min() if not monthly_returns.empty else np.nan

    return {
        "cagr": cagr,
        "max_dd_monthly": max_dd_monthly,
        "ytd": ytd_perf,
        "sharpe": sharpe,
        "sortino": sortino,
    }


def _fmt_pct(x: float) -> str:
    return f"{x * 100:.2f}%" if pd.notna(x) else "na"


def _fmt_val(x: float) -> str:
    return f"{x:.2f}" if pd.notna(x) else "na"


def compare_with_benchmarks(portfolio_monthly: pd.Series, annual_rf: float, current_year: int):
    # Align to complete months and to months present in the portfolio
    lcm = last_complete_month().to_timestamp("M")
    pm = portfolio_monthly.copy()
    pm.index = pm.index.to_timestamp("M")
    pm = pm[pm.index <= lcm]
    months = pm.index.to_period("M")

    spy = get_benchmark_series("SPY", months)
    qqq = get_benchmark_series("QQQ", months)

    metrics = {
        "Portfolio": compute_metrics(pm.to_period("M"), annual_rf, current_year),
        "SPY": compute_metrics(spy, annual_rf, current_year),
        "QQQ": compute_metrics(qqq, annual_rf, current_year),
    }

    # Print simple comparison table
    print("\nComparison vs Benchmarks (rounded):")
    header = f"{'Asset':<12} {'CAGR':>8} {'MaxDD(M)':>10} {'YTD':>8} {'Sharpe':>8} {'Sortino':>8}"
    print(header)
    print("-" * len(header))
    for name, m in metrics.items():
        row = f"{name:<12} {_fmt_pct(m['cagr']):>8} {_fmt_pct(m['max_dd_monthly']):>10} {_fmt_pct(m['ytd']):>8} {_fmt_val(m['sharpe']):>8} {_fmt_val(m['sortino']):>8}"
        print(row)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Portfolio analysis and benchmark comparison")
    parser.add_argument("--json", default=JSON_FILE_PATH, help="Path to valuations JSON")
    parser.add_argument("--rf", type=float, default=ANNUAL_RF_RATE, help="Annual risk-free rate (e.g., 0.04)")
    parser.add_argument("--year", type=int, default=datetime.now().year, help="Current year for YTD calc")
    parser.add_argument("--benchmarks", action="store_true", help="Fetch SPY/QQQ and compare metrics")
    args = parser.parse_args()

    monthly, _ = convert_to_monthly_and_calculate_ratios(args.json, args.rf, args.year)
    if args.benchmarks:
        compare_with_benchmarks(monthly, args.rf, args.year)

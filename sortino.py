import pandas as pd
import numpy as np
import json
from datetime import datetime

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
    monthly_returns = df.groupby("month").apply(
        lambda g: np.prod(1 + g["dailyTotalValueChange"]) - 1
    )

    # Print monthly returns for debug
    print("Monthly Returns:")
    print(monthly_returns.to_string())

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

    print("\nAnnualized Sharpe Ratio:", sharpe)
    print("Annualized Sortino Ratio:", sortino)


if __name__ == "__main__":
    convert_to_monthly_and_calculate_ratios()

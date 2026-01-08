"""Export holdings performance data to JSON for web dashboard."""

import json
from datetime import datetime, date
from pathlib import Path
from calendar import monthrange
from portfolio_cli.reports.stock_performance import calculate_performance, PERIODS
from portfolio_cli.reports.utils import load_holdings, get_period_start_date

OUTPUT_PATH = Path("web/public/data/holdings-performance.json")
PORTFOLIO_DATA_PATH = Path("web/public/data/portfolio.json")

def get_reference_date():
    """Get reference date from portfolio.json last_period."""
    try:
        if PORTFOLIO_DATA_PATH.exists():
            with open(PORTFOLIO_DATA_PATH) as f:
                data = json.load(f)
                last_period = data.get("last_period")
                if last_period:
                    year, month = map(int, last_period.split("-"))
                    # Use last day of that month
                    _, last_day = monthrange(year, month)
                    return date(year, month, last_day)
    except Exception as e:
        print(f"Warning: Could not determine reference date from portfolio.json: {e}")
    return date.today()

def export_performance():
    """Calculate and export performance for all periods to JSON."""
    holdings = load_holdings()
    if not holdings:
        print("No holdings found to export.")
        return

    ref_date = get_reference_date()
    print(f"Calculating performance using reference date: {ref_date}")

    data = {
        "generated_at": datetime.now().isoformat(),
        "as_of": ref_date.isoformat(),
        "periods": {}
    }

    for period in PERIODS:
        performances = calculate_performance(holdings, period, reference_date=ref_date)

        # Calculate summary stats for the period
        if performances:
            total_weight = sum(p.allocation for p in performances)
            weighted_return = sum(p.period_return * p.allocation for p in performances) / total_weight if total_weight > 0 else 0

            summary = {
                "net_return": weighted_return,
                "gainers_count": sum(1 for p in performances if p.period_return > 0),
                "losers_count": sum(1 for p in performances if p.period_return < 0),
                "avg_return": sum(p.period_return for p in performances) / len(performances)
            }
        else:
            summary = {
                "net_return": 0,
                "gainers_count": 0,
                "losers_count": 0,
                "avg_return": 0
            }

        # Get period start date for this iteration
        start_date = get_period_start_date(period, ref_date)

        data["periods"][period] = {
            "start_date": start_date.isoformat(),
            "end_date": ref_date.isoformat(),
            "summary": summary,
            "holdings": [
                {
                    "symbol": p.symbol,
                    "current_price": p.current_price,
                    "period_start_price": p.period_start_price,
                    "period_return": p.period_return,
                    "allocation": p.allocation,
                    "total_return_pct": p.total_return
                } for p in performances
            ]
        }

    # Ensure directory exists
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_PATH, "w") as f:
        json.dump(data, f, indent=2)

    print(f"Exported holdings performance data to {OUTPUT_PATH}")

if __name__ == "__main__":
    export_performance()

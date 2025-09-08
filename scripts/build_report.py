from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

# Ensure project root is on sys.path when invoked as a script (e.g., `python scripts/build_report.py`)
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from sortino import (
    ANNUAL_RF_RATE,
    JSON_FILE_PATH,
    convert_to_monthly_and_calculate_ratios,
)


def _fmt_pct(x: float) -> str:
    """Format a number as percentage."""
    return f"{x * 100:.2f}%" if pd.notna(x) else "na"


def _fmt_val(x: float) -> str:
    """Format a number with two decimals."""
    return f"{x:.2f}" if pd.notna(x) else "na"


def render_html(
    monthly_returns: pd.Series, metrics: dict[str, float], as_of: str
) -> str:
    """Render a simple HTML report with a Chart.js plot and metrics table.

    as_of: ISO date string (YYYY-MM-DD) indicating last data date.
    """
    labels = [str(m) for m in monthly_returns.index]
    data = [round(v * 100, 2) for v in monthly_returns]

    rows = [
        ("CAGR", _fmt_pct(metrics["cagr"])),
        ("Max Monthly Drawdown", _fmt_pct(metrics["max_dd_monthly"])),
        ("YTD", _fmt_pct(metrics["ytd"])),
        ("Sharpe", _fmt_val(metrics["sharpe"])),
        ("Sortino", _fmt_val(metrics["sortino"])),
    ]
    table_rows = "\n".join(
        f"<tr><th>{name}</th><td>{val}</td></tr>" for name, val in rows
    )

    html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset=\"utf-8\" />
  <title>Portfolio Performance</title>
  <script src=\"https://cdn.jsdelivr.net/npm/chart.js\"></script>
</head>
<body>
  <h1>Portfolio Monthly Returns</h1>
  <p><em>As of: {as_of}</em></p>
  <canvas id=\"returnsChart\"></canvas>
  <script>
    const ctx = document.getElementById('returnsChart').getContext('2d');
    new Chart(ctx, {{
      type: 'line',
      data: {{
        labels: {json.dumps(labels)},
        datasets: [{{
          label: 'Return %',
          data: {json.dumps(data)},
          borderColor: 'rgb(75, 192, 192)',
          tension: 0.1
        }}]
      }},
      options: {{
        scales: {{
          y: {{
            ticks: {{
              callback: (value) => value + '%'
            }}
          }}
        }}
      }}
    }});
  </script>
  <h2>Metrics</h2>
  <table>
    {table_rows}
  </table>
</body>
</html>
"""
    return html


def _get_last_data_date(json_file: str) -> str:
    """Return the last summaryDate (YYYY-MM-DD) from the valuations JSON."""
    try:
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not data:
            return "unknown"
        dates = pd.to_datetime([row.get("summaryDate") for row in data])
        return str(pd.Series(dates).max().date())
    except Exception:
        return "unknown"


def main(json_file: str, annual_rf: float, year: int, output: Path) -> None:
    monthly, metrics = convert_to_monthly_and_calculate_ratios(
        json_file=json_file, annual_rf=annual_rf, current_year=year
    )
    as_of = _get_last_data_date(json_file)
    html = render_html(monthly, metrics, as_of)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(html, encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate HTML performance report")
    parser.add_argument("--json", default=JSON_FILE_PATH, help="Path to valuations JSON")
    parser.add_argument("--rf", type=float, default=ANNUAL_RF_RATE, help="Annual risk-free rate")
    parser.add_argument(
        "--year", type=int, default=datetime.now().year, help="Current year for YTD calc"
    )
    parser.add_argument(
        "--output", default="dist/index.html", help="Output HTML path (default: dist/index.html)"
    )
    args = parser.parse_args()
    main(args.json, args.rf, args.year, Path(args.output))

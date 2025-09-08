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
    compute_metrics,
)
from benchmarks import get_benchmark_series


def _fmt_pct(x: float) -> str:
    """Format a number as percentage."""
    return f"{x * 100:.2f}%" if pd.notna(x) else "na"


def _fmt_val(x: float) -> str:
    """Format a number with two decimals."""
    return f"{x:.2f}" if pd.notna(x) else "na"


def render_html(
    monthly_returns: pd.Series,
    metrics: dict[str, float],
    bench_metrics: dict[str, dict[str, float]],
    as_of: str,
) -> str:
    """Render a Tailwind-styled HTML report with metrics, benchmarks table, and chart.

    as_of: ISO date string (YYYY-MM-DD) indicating last data date.
    """
    labels = [str(m) for m in monthly_returns.index]
    data_portfolio = [round(v * 100, 2) for v in monthly_returns]

    card_items = [
        ("CAGR", _fmt_pct(metrics.get("cagr"))),
        ("YTD", _fmt_pct(metrics.get("ytd"))),
        ("Max Monthly Drawdown", _fmt_pct(metrics.get("max_dd_monthly"))),
        ("Sharpe", _fmt_val(metrics.get("sharpe"))),
        ("Sortino", _fmt_val(metrics.get("sortino"))),
    ]
    cards_html = "\n".join(
        f"""
        <div class=\"rounded-xl border border-slate-200 bg-white p-4 shadow-sm\">
          <div class=\"text-sm text-slate-500\">{name}</div>
          <div class=\"mt-1 text-2xl font-semibold text-slate-800\">{val}</div>
        </div>
        """
        for name, val in card_items
    )

    rows = []
    for key in ["Portfolio", "SPY", "QQQ"]:
        m = metrics if key == "Portfolio" else bench_metrics.get(key, {})
        if not m:
            continue
        rows.append(
            f"<tr class=\"border-t border-slate-200\">"
            f"<td class=\"py-2 px-3 font-medium text-slate-800\">{key}</td>"
            f"<td class=\"py-2 px-3\">{_fmt_pct(m.get('cagr'))}</td>"
            f"<td class=\"py-2 px-3\">{_fmt_pct(m.get('ytd'))}</td>"
            f"<td class=\"py-2 px-3\">{_fmt_pct(m.get('max_dd_monthly'))}</td>"
            f"<td class=\"py-2 px-3\">{_fmt_val(m.get('sharpe'))}</td>"
            f"<td class=\"py-2 px-3\">{_fmt_val(m.get('sortino'))}</td>"
            f"</tr>"
        )
    table_html = "\n".join(rows)

    html = f"""<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Mingdom Capital — Performance</title>
  <script src=\"https://cdn.tailwindcss.com\"></script>
  <script src=\"https://cdn.jsdelivr.net/npm/chart.js\"></script>
</head>
<body class=\"bg-slate-50\">
  <main class=\"mx-auto max-w-5xl p-6\">
    <header class=\"mb-6\">
      <h1 class=\"text-3xl font-semibold text-slate-900\">Portfolio Performance</h1>
      <p class=\"mt-1 text-slate-500\">As of: {as_of}</p>
    </header>

    <section aria-labelledby=\"metrics\">
      <h2 id=\"metrics\" class=\"sr-only\">Metrics</h2>
      <div class=\"grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3\">
        {cards_html}
      </div>
    </section>

    <section aria-labelledby=\"benchmarks\" class=\"mt-8\">
      <h2 id=\"benchmarks\" class=\"text-xl font-semibold text-slate-900\">Benchmarks</h2>
      <div class=\"mt-3 overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm\">
        <table class=\"min-w-full divide-y divide-slate-200\">
          <thead class=\"bg-slate-50\">
            <tr>
              <th class=\"py-2 px-3 text-left text-sm font-semibold text-slate-700\">Name</th>
              <th class=\"py-2 px-3 text-left text-sm font-semibold text-slate-700\">CAGR</th>
              <th class=\"py-2 px-3 text-left text-sm font-semibold text-slate-700\">YTD</th>
              <th class=\"py-2 px-3 text-left text-sm font-semibold text-slate-700\">Max Monthly DD</th>
              <th class=\"py-2 px-3 text-left text-sm font-semibold text-slate-700\">Sharpe</th>
              <th class=\"py-2 px-3 text-left text-sm font-semibold text-slate-700\">Sortino</th>
            </tr>
          </thead>
          <tbody class=\"bg-white\">
            {table_html}
          </tbody>
        </table>
      </div>
    </section>

    <section aria-labelledby=\"chart\" class=\"mt-8\">
      <h2 id=\"chart\" class=\"text-xl font-semibold text-slate-900\">Monthly Returns</h2>
      <div class=\"mt-3 rounded-xl border border-slate-200 bg-white p-4 shadow-sm\">
        <canvas id=\"returnsChart\"></canvas>
      </div>
    </section>

    <footer class=\"mt-10 text-sm text-slate-500\">
      <p>Source: SavvyTrader valuations JSON. RF: {ANNUAL_RF_RATE:.2%} annual.</p>
    </footer>
  </main>

  <script>
    const ctx = document.getElementById('returnsChart').getContext('2d');
    new Chart(ctx, {{
      type: 'line',
      data: {{
        labels: {json.dumps(labels)},
        datasets: [{{
          label: 'Portfolio Return %',
          data: {json.dumps(data_portfolio)},
          borderColor: 'rgb(37, 99, 235)',
          backgroundColor: 'rgba(37, 99, 235, 0.15)',
          fill: true,
          tension: 0.25
        }}]
      }},
      options: {{
        responsive: true,
        scales: {{
          y: {{
            ticks: {{
              callback: (value) => value + '%'
            }}
          }}
        }},
        plugins: {{
          legend: {{ display: true }},
          tooltip: {{
            callbacks: {{
              label: (ctx) => `${{ctx.parsed.y}}%`
            }}
          }}
        }}
      }}
    }});
  </script>
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
    # Benchmarks for the same monthly periods
    months = monthly.index
    spy = get_benchmark_series("SPY", months)
    qqq = get_benchmark_series("QQQ", months)

    bench_metrics = {
        "SPY": compute_metrics(spy, annual_rf, year) if not spy.empty else {},
        "QQQ": compute_metrics(qqq, annual_rf, year) if not qqq.empty else {},
    }

    as_of = _get_last_data_date(json_file)
    html = render_html(monthly, metrics, bench_metrics, as_of)
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

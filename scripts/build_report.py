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
from benchmarks import get_aligned_benchmark_series


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
    spy: pd.Series,
    qqq: pd.Series,
    as_of: str,
    range_start: str,
    range_end: str,
) -> str:
    """Render a Tailwind-styled HTML report with metrics, benchmarks table, and chart.

    as_of: ISO date string (YYYY-MM-DD) indicating last data date.
    """
    # Build monthly comparison table data (Portfolio vs SPY vs QQQ)
    months = list(monthly_returns.index)
    def fmt_color(val: float) -> str:
        if pd.isna(val):
            return "text-slate-400"
        if val > 0:
            return "text-emerald-600"
        if val < 0:
            return "text-rose-600"
        return "text-slate-600"

    monthly_rows = []
    for m in months:
        p = monthly_returns.get(m, pd.NA)
        s = spy.get(m, pd.NA) if spy is not None else pd.NA
        q = qqq.get(m, pd.NA) if qqq is not None else pd.NA
        monthly_rows.append(
            f"<tr class=\"border-t border-slate-200\">"
            f"<td class=\"py-2 px-3 text-slate-600\">{m}</td>"
            f"<td class=\"py-2 px-3 font-medium {fmt_color(p)}\">{_fmt_pct(p) if pd.notna(p) else '—'}</td>"
            f"<td class=\"py-2 px-3 {fmt_color(s)}\">{_fmt_pct(s) if pd.notna(s) else '—'}</td>"
            f"<td class=\"py-2 px-3 {fmt_color(q)}\">{_fmt_pct(q) if pd.notna(q) else '—'}</td>"
            f"</tr>"
        )
    monthly_table_html = "\n".join(monthly_rows)

    card_items = [
        {
            "label": "CAGR",
            "value": _fmt_pct(metrics.get("cagr")),
            "help": "Compound annual growth rate based on the full period."
            " Shows the constant annual return that would compound to the same total.",
        },
        {
            "label": "YTD",
            "value": _fmt_pct(metrics.get("ytd")),
            "help": "Year-to-date total return from the start of the year to the as-of date.",
        },
        {
            "label": "Max Monthly Drawdown",
            "value": _fmt_pct(metrics.get("max_dd_monthly")),
            "help": "Worst single-month return over the period (most negative monthly return).",
        },
        {
            "label": "Sharpe",
            "value": _fmt_val(metrics.get("sharpe")),
            "help": "Risk-adjusted return using total volatility. Higher is better."
            " Uses annual RF {ANNUAL_RF_RATE:.0%} and monthly scaling.",
        },
        {
            "label": "Sortino",
            "value": _fmt_val(metrics.get("sortino")),
            "help": "Risk-adjusted return using downside volatility only. Higher is better.",
        },
    ]
    cards_html = "\n".join(
        f"""
        <div class=\"rounded-xl border border-slate-200 bg-white p-4 shadow-sm\">
          <div class=\"flex items-center gap-2 text-sm text-slate-500\">
            <span>{item['label']}</span>
            <span class=\"relative inline-block align-middle group\" aria-label=\"Help\" role=\"img\">
              <svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 20 20\" fill=\"currentColor\" class=\"h-4 w-4 text-slate-400\">
                <path fill-rule=\"evenodd\" d=\"M18 10a8 8 0 11-16 0 8 8 0 0116 0zM8.94 7.94a3 3 0 114.24 4.24l-.35.35c-.37.37-.53.86-.46 1.35a.75.75 0 11-1.48.2 2.96 2.96 0 01.8-2.01l.35-.35a1.5 1.5 0 10-2.12-2.12.75.75 0 01-1.06-1.06zM10 14a1 1 0 100 2 1 1 0 000-2z\" clip-rule=\"evenodd\" />
              </svg>
              <span class=\"pointer-events-none absolute left-1/2 z-10 hidden w-64 -translate-x-1/2 translate-y-2 rounded-md bg-slate-900 px-3 py-2 text-xs text-white shadow-lg group-hover:block\">{item['help']}</span>
            </span>
          </div>
          <div class=\"mt-1 text-2xl font-semibold text-slate-800\">{item['value']}</div>
        </div>
        """
        for item in card_items
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
</head>
<body class=\"bg-slate-50\">
  <main class=\"mx-auto max-w-5xl p-6\">
    <header class=\"mb-6\">
      <h1 class=\"text-3xl font-semibold text-slate-900\">Portfolio Performance</h1>
      <p class=\"mt-1 text-slate-500\">As of: {as_of}</p>
      <p class=\"text-slate-500\">Range: {range_start} → {range_end}</p>
      <div class=\"mt-2 flex gap-3\">
        <a class=\"text-blue-600 hover:underline\" href=\"monthly.csv\" download>Download Monthly CSV</a>
        <a class=\"text-blue-600 hover:underline\" href=\"metrics.csv\" download>Download Metrics CSV</a>
      </div>
    </header>

    <section aria-labelledby=\"metrics\">
      <h2 id=\"metrics\" class=\"text-xl font-semibold text-slate-900\">Key Metrics</h2>
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

    <section aria-labelledby=\"monthly\" class=\"mt-8\">
      <h2 id=\"monthly\" class=\"text-xl font-semibold text-slate-900\">Monthly Performance</h2>
      <div class=\"mt-3 overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm\">
        <table class=\"min-w-full divide-y divide-slate-200\">
          <thead class=\"bg-slate-50\">
            <tr>
              <th class=\"py-2 px-3 text-left text-sm font-semibold text-slate-700\">Month</th>
              <th class=\"py-2 px-3 text-left text-sm font-semibold text-slate-700\">Portfolio</th>
              <th class=\"py-2 px-3 text-left text-sm font-semibold text-slate-700\">SPY</th>
              <th class=\"py-2 px-3 text-left text-sm font-semibold text-slate-700\">QQQ</th>
            </tr>
          </thead>
          <tbody class=\"bg-white\">
            {monthly_table_html}
          </tbody>
        </table>
      </div>
    </section>

    <footer class=\"mt-10 text-sm text-slate-500\">
      <p>Source: SavvyTrader valuations JSON. RF: {ANNUAL_RF_RATE:.2%} annual.</p>
    </footer>
  </main>
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


def _get_first_data_date(json_file: str) -> str:
    try:
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not data:
            return "unknown"
        dates = pd.to_datetime([row.get("summaryDate") for row in data])
        return str(pd.Series(dates).min().date())
    except Exception:
        return "unknown"


def main(json_file: str, annual_rf: float, year: int, output: Path) -> None:
    monthly, metrics = convert_to_monthly_and_calculate_ratios(
        json_file=json_file, annual_rf=annual_rf, current_year=year
    )
    # Benchmarks for the same monthly periods, aligned for partial months
    months = monthly.index
    first_str = _get_first_data_date(json_file)
    last_str = _get_last_data_date(json_file)
    try:
        from datetime import date as _date
        inception_date = _date.fromisoformat(first_str)
        last_date = _date.fromisoformat(last_str)
    except Exception:
        # Fallbacks in case of parse issues
        inception_date = months.min().to_timestamp(how='start').date()
        last_date = months.max().to_timestamp(how='end').date()

    spy = get_aligned_benchmark_series("SPY", months, inception_date, last_date)
    qqq = get_aligned_benchmark_series("QQQ", months, inception_date, last_date)

    bench_metrics = {
        "SPY": compute_metrics(spy, annual_rf, year) if not spy.empty else {},
        "QQQ": compute_metrics(qqq, annual_rf, year) if not qqq.empty else {},
    }

    as_of = last_str
    html = render_html(
        monthly, metrics, bench_metrics, spy, qqq, as_of, first_str, last_str
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    # Write HTML
    output.write_text(html, encoding="utf-8")
    # Write CSV exports alongside HTML
    dist_dir = output.parent
    months_str = [str(m) for m in months]
    monthly_df = pd.DataFrame(
        {
            "month": months_str,
            "portfolio": list(monthly.values),
            "SPY": [spy.get(m, pd.NA) for m in months],
            "QQQ": [qqq.get(m, pd.NA) for m in months],
        }
    )
    monthly_df.to_csv(dist_dir / "monthly.csv", index=False)

    def _rows_from_metrics(entity: str, m: dict[str, float] | None):
        if not m:
            return []
        keys = ["cagr", "ytd", "max_dd_monthly", "sharpe", "sortino"]
        return [{"entity": entity, "metric": k, "value": m.get(k)} for k in keys]

    metrics_rows = []
    metrics_rows.extend(_rows_from_metrics("Portfolio", metrics))
    metrics_rows.extend(_rows_from_metrics("SPY", bench_metrics.get("SPY")))
    metrics_rows.extend(_rows_from_metrics("QQQ", bench_metrics.get("QQQ")))
    if metrics_rows:
        pd.DataFrame(metrics_rows).to_csv(dist_dir / "metrics.csv", index=False)


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

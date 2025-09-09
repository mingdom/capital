from __future__ import annotations

import argparse
import json
import math
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
    """Format a number as percentage with one decimal."""
    return f"{x * 100:.1f}%" if pd.notna(x) else "na"


def _fmt_val(x: float) -> str:
    """Format a number with one decimal."""
    return f"{x:.1f}" if pd.notna(x) else "na"


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
    # Cumulative performance series for later use
    cum_port = (1 + monthly_returns).cumprod() - 1
    cum_spy = (1 + spy).cumprod() - 1 if spy is not None else pd.Series(dtype=float)
    cum_qqq = (1 + qqq).cumprod() - 1 if qqq is not None else pd.Series(dtype=float)
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
    # Summary row: since inception (compound over all months shown)
    def _compound(vals):
        vals = [v for v in vals if pd.notna(v)]
        if not vals:
            return pd.NA
        prod = 1.0
        for v in vals:
            prod *= (1.0 + float(v))
        return prod - 1.0

    p_total = _compound([monthly_returns.get(m, pd.NA) for m in months])
    s_total = _compound([spy.get(m, pd.NA) for m in months]) if spy is not None else pd.NA
    q_total = _compound([qqq.get(m, pd.NA) for m in months]) if qqq is not None else pd.NA

    monthly_rows.append(
        f"<tr class=\"border-t border-slate-200 bg-slate-50 font-medium\">"
        f"<td class=\"py-2 px-3\">Since Inception</td>"
        f"<td class=\"py-2 px-3 {fmt_color(p_total)}\">{_fmt_pct(p_total) if pd.notna(p_total) else '—'}</td>"
        f"<td class=\"py-2 px-3 {fmt_color(s_total)}\">{_fmt_pct(s_total) if pd.notna(s_total) else '—'}</td>"
        f"<td class=\"py-2 px-3 {fmt_color(q_total)}\">{_fmt_pct(q_total) if pd.notna(q_total) else '—'}</td>"
        f"</tr>"
    )

    monthly_table_html = "\n".join(monthly_rows)
    months_str = [str(m) for m in months]
    port_cum = [float(cum_port.get(m)) if pd.notna(cum_port.get(m)) else None for m in months]
    spy_cum = [float(cum_spy.get(m)) if pd.notna(cum_spy.get(m)) else None for m in months]
    qqq_cum = [float(cum_qqq.get(m)) if pd.notna(cum_qqq.get(m)) else None for m in months]

    all_vals = [v for v in port_cum + spy_cum + qqq_cum if v is not None]
    if all_vals:
        y_min = math.floor((min(all_vals) - 0.01) * 100) / 100
        y_max = math.ceil((max(all_vals) + 0.01) * 100) / 100
        y_step = max(0.01, round((y_max - y_min) / 5, 2))
    else:
        y_min, y_max, y_step = -0.1, 0.1, 0.05

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
            "help": f"Risk-adjusted return using total volatility. Higher is better."
            f" Uses annual RF {ANNUAL_RF_RATE:.0%} and monthly scaling.",
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
                <path fill-rule=\"evenodd\" d=\"M10 18a8 8 0 100-16 8 8 0 000 16zm.75-4.25a.75.75 0 11-1.5 0v-4.5a.75.75 0 011.5 0v4.5zM10 7a1 1 0 110-2 1 1 0 010 2z\" clip-rule=\"evenodd\" />
              </svg>
              <span class=\"pointer-events-none absolute left-1/2 z-10 hidden w-64 -translate-x-1/2 translate-y-2 rounded-md bg-slate-900 px-3 py-2 text-xs text-white shadow-lg group-hover:block\">{item['help']}</span>
            </span>
          </div>
          <div class=\"mt-1 text-2xl font-semibold text-slate-800\">{item['value']}</div>
        </div>
        """
        for item in card_items
    )

    # Trailing window returns for 3M and 1Y (12M) using the displayed months
    def _window_comp(series: pd.Series, window: int):
        if not months:
            return pd.NA
        use = months[-window:]
        return _compound([series.get(m, pd.NA) for m in use])

    p_3m = _window_comp(monthly_returns, 3)
    p_1y = _window_comp(monthly_returns, 12)
    s_3m = _window_comp(spy, 3) if spy is not None else pd.NA
    s_1y = _window_comp(spy, 12) if spy is not None else pd.NA
    q_3m = _window_comp(qqq, 3) if qqq is not None else pd.NA
    q_1y = _window_comp(qqq, 12) if qqq is not None else pd.NA

    rows = []
    for key in ["Portfolio", "SPY", "QQQ"]:
        if key == "Portfolio":
            m = metrics
            extra3 = p_3m
            extra12 = p_1y
        else:
            m = bench_metrics.get(key, {})
            extra3 = s_3m if key == "SPY" else q_3m
            extra12 = s_1y if key == "SPY" else q_1y
        if not m and pd.isna(extra3) and pd.isna(extra12):
            continue
        rows.append(
            f"<tr class=\"border-t border-slate-200\">"
            f"<td class=\"py-2 px-3 font-medium text-slate-800\">{key}</td>"
            f"<td class=\"py-2 px-3\">{_fmt_pct(m.get('cagr')) if m else '—'}</td>"
            f"<td class=\"py-2 px-3\">{_fmt_pct(m.get('ytd')) if m else '—'}</td>"
            f"<td class=\"py-2 px-3\">{_fmt_pct(extra3) if pd.notna(extra3) else '—'}</td>"
            f"<td class=\"py-2 px-3\">{_fmt_pct(extra12) if pd.notna(extra12) else '—'}</td>"
            f"<td class=\"py-2 px-3\">{_fmt_pct(m.get('max_dd_monthly')) if m else '—'}</td>"
            f"<td class=\"py-2 px-3\">{_fmt_val(m.get('sharpe')) if m else '—'}</td>"
            f"<td class=\"py-2 px-3\">{_fmt_val(m.get('sortino')) if m else '—'}</td>"
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

    <section aria-labelledby=\"cumulative\" class=\"mt-8\">
      <h2 id=\"cumulative\" class=\"text-xl font-semibold text-slate-900\">Cumulative Performance</h2>
      <div class=\"mt-3 overflow-hidden rounded-xl border border-slate-200 bg-white p-4 shadow-sm\">
        <canvas id=\"perf-chart\"></canvas>
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

    <section aria-labelledby=\"benchmarks\" class=\"mt-8\">
      <h2 id=\"benchmarks\" class=\"text-xl font-semibold text-slate-900\">Benchmarks</h2>
      <div class=\"mt-3 overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm\">
        <table class=\"min-w-full divide-y divide-slate-200\">
          <thead class=\"bg-slate-50\">
            <tr>
              <th class=\"py-2 px-3 text-left text-sm font-semibold text-slate-700\">Name</th>
              <th class=\"py-2 px-3 text-left text-sm font-semibold text-slate-700\">CAGR</th>
              <th class=\"py-2 px-3 text-left text-sm font-semibold text-slate-700\">YTD</th>
              <th class=\"py-2 px-3 text-left text-sm font-semibold text-slate-700\">3M</th>
              <th class=\"py-2 px-3 text-left text-sm font-semibold text-slate-700\">1Y</th>
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

    <footer class=\"mt-10 text-sm text-slate-500\">
      <a href=\"https://github.com/mingdom/capital\" class=\"hover:underline\">View source on GitHub</a>
    </footer>
  </main>
  <script src=\"https://cdn.jsdelivr.net/npm/chart.js\"></script>
  <script>
    const labels = {json.dumps(months_str)};
    const datasets = [
      {{ label: 'Portfolio', data: {json.dumps(port_cum)}, borderColor: 'rgb(37,99,235)', fill: false }},
      {{ label: 'SPY', data: {json.dumps(spy_cum)}, borderColor: 'rgb(234,88,12)', fill: false }},
      {{ label: 'QQQ', data: {json.dumps(qqq_cum)}, borderColor: 'rgb(16,185,129)', fill: false }}
    ];
    const ctx = document.getElementById('perf-chart').getContext('2d');
    new Chart(ctx, {{
      type: 'line',
      data: {{ labels, datasets }},
      options: {{
        interaction: {{ mode: 'index', intersect: false }},
          scales: {{
            y: {{
              min: {y_min},
              max: {y_max},
              ticks: {{ stepSize: {y_step}, callback: v => (v * 100).toFixed(1) + '%' }}
            }}
          }},
        plugins: {{
          tooltip: {{
            callbacks: {{
              label: ctx => ctx.dataset.label + ': ' + (ctx.parsed.y * 100).toFixed(1) + '%'
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

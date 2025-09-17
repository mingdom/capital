"""HTML report rendering for portfolio performance."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Iterable

import pandas as pd

from portfolio_cli.performance import PerformanceBundle


def _fmt_pct(value: float | None) -> str:
    if value is None or pd.isna(value):
        return "—"
    return f"{value * 100:.1f}%"


def _fmt_ratio(value: float | None) -> str:
    if value is None or pd.isna(value):
        return "—"
    return f"{value:.2f}"


def _build_monthly_table(df: pd.DataFrame) -> str:
    header_cells = "".join(f"<th>{col}</th>" for col in df.columns)
    rows = []
    for period, row in df.iterrows():
        month = str(period)
        cells = "".join(
            f"<td>{_fmt_pct(row[col]) if pd.notna(row[col]) else '—'}</td>" for col in df.columns
        )
        rows.append(f"<tr><td>{month}</td>{cells}</tr>")
    rows_html = "\n".join(rows)
    return (
        "<table class='perf-table'>"
        "<thead><tr><th>Month</th>" + header_cells + "</tr></thead>"
        "<tbody>" + rows_html + "</tbody></table>"
    )


def _build_summary_table(bundle: PerformanceBundle, order: Iterable[str]) -> str:
    metrics = bundle.metrics
    header_cells = "".join(f"<th>{name}</th>" for name in order)
    rows_html = []
    definitions = [
        ("CAGR", lambda m: m.metrics.cagr, _fmt_pct),
        ("YTD", lambda m: m.metrics.ytd, _fmt_pct),
        ("Max Drawdown", lambda m: m.metrics.max_dd_monthly, _fmt_pct),
        ("Sharpe", lambda m: m.metrics.sharpe, _fmt_ratio),
        ("Sortino", lambda m: m.metrics.sortino, _fmt_ratio),
    ]
    for label, getter, formatter in definitions:
        cells = []
        for name in order:
            analysis = metrics.get(name)
            value = getter(analysis) if analysis else None
            cells.append(f"<td>{formatter(value)}</td>")
        rows_html.append(f"<tr><td>{label}</td>{''.join(cells)}</tr>")
    rows = "\n".join(rows_html)
    return (
        "<table class='summary-table'>"
        "<thead><tr><th>Metric</th>" + header_cells + "</tr></thead>"
        "<tbody>" + rows + "</tbody></table>"
    )


def render_html_report(
    bundle: PerformanceBundle,
    title: str = "Portfolio Performance",
    as_of: str | None = None,
    generated_at: datetime | None = None,
) -> str:
    generated = generated_at or datetime.now()
    generated_text = generated.isoformat(timespec="minutes")
    last_period = bundle.last_period
    if as_of is None and last_period is not None:
        as_of = last_period.to_timestamp("M").strftime("%Y-%m-%d")
    as_of_text = as_of or "n/a"

    combined = bundle.combined.dropna(how="all")
    if combined.empty:
        combined = bundle.combined

    monthly_html = _build_monthly_table(combined)
    order = list(combined.columns)
    summary_html = _build_summary_table(bundle, order)

    missing_html = ""
    if bundle.missing:
        missing_items = "".join(f"<li>{item}</li>" for item in bundle.missing)
        missing_html = f"<section class='notice'><h2>Notes</h2><ul>{missing_items}</ul></section>"

    styles = """
    body { font-family: 'Segoe UI', Tahoma, sans-serif; background: #f8fafc; color: #0f172a; margin: 0; padding: 2rem; }
    h1 { margin-bottom: 0.25rem; }
    h2 { margin-top: 2rem; margin-bottom: 0.5rem; }
    .meta { color: #475569; margin-bottom: 1.5rem; }
    table { width: 100%; border-collapse: collapse; margin-bottom: 1.5rem; }
    th, td { padding: 0.5rem 0.75rem; border-bottom: 1px solid #e2e8f0; text-align: right; }
    th:first-child, td:first-child { text-align: left; }
    thead th { background: #e2e8f0; font-weight: 600; }
    tbody tr:nth-child(even) { background: #f1f5f9; }
    .summary-table th { background: #1e293b; color: #f8fafc; }
    .summary-table tbody tr:nth-child(even) { background: #e2e8f0; }
    .notice { background: #fff7ed; border: 1px solid #f97316; padding: 1rem; border-radius: 0.5rem; }
    .footer { font-size: 0.875rem; color: #64748b; margin-top: 3rem; }
    """

    html = f"""
    <!DOCTYPE html>
    <html lang="en">
      <head>
        <meta charset="utf-8" />
        <title>{title}</title>
        <style>{styles}</style>
      </head>
      <body>
        <header>
          <h1>{title}</h1>
          <div class="meta">As of {as_of_text} · Generated {generated_text}</div>
        </header>
        <section>
          <h2>Monthly Returns</h2>
          {monthly_html}
        </section>
        <section>
          <h2>Summary Metrics</h2>
          {summary_html}
        </section>
        {missing_html}
        <div class="footer">Built with portfolio_cli.</div>
      </body>
    </html>
    """
    return "\n".join(line.rstrip() for line in html.splitlines())

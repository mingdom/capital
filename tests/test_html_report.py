import pandas as pd

from scripts.build_report import render_html


def test_render_html_contains_sections_and_tables():
    monthly = pd.Series([0.01, -0.02], index=pd.period_range("2024-01", periods=2, freq="M"))
    metrics = {
        "cagr": 0.1,
        "max_dd_monthly": -0.02,
        "ytd": 0.01,
        "sharpe": 1.2,
        "sortino": 1.5,
    }
    bench_metrics = {"SPY": metrics, "QQQ": metrics}
    spy = monthly.copy()
    qqq = monthly.copy()
    html = render_html(monthly, metrics, bench_metrics, spy, qqq, "2025-09-08", "2024-02-02", "2025-09-08")
    assert "Portfolio Performance" in html
    assert "Benchmarks" in html
    assert "Monthly Performance" in html
    assert "Cumulative Performance" in html
    assert "CAGR" in html
    assert "2024-01" in html
    assert "perf-chart" in html

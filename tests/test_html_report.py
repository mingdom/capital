import pandas as pd

from scripts.build_report import render_html


def test_render_html_contains_chart_and_metrics():
    monthly = pd.Series([0.01, -0.02], index=pd.period_range("2024-01", periods=2, freq="M"))
    metrics = {
        "cagr": 0.1,
        "max_dd_monthly": -0.02,
        "ytd": 0.01,
        "sharpe": 1.2,
        "sortino": 1.5,
    }
    html = render_html(monthly, metrics)
    assert "Portfolio Monthly Returns" in html
    assert "CAGR" in html
    assert "new Chart" in html
    assert "2024-01" in html

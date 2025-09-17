import pandas as pd

from portfolio_cli.analysis import PerformanceMetrics, PortfolioAnalysis
from portfolio_cli.performance import PerformanceBundle
from portfolio_cli.report import render_html_report


def test_render_html_contains_tables_and_metrics():
    index = pd.period_range("2024-01", periods=3, freq="M")
    combined = pd.DataFrame(
        {
            "SavvyTrader": [0.01, -0.02, 0.03],
            "Fidelity": [0.02, 0.0, -0.01],
            "SPY": [0.015, -0.01, 0.02],
        },
        index=index,
    )

    perf = PerformanceMetrics(cagr=0.1, max_dd_monthly=-0.02, ytd=0.01, sharpe=1.2, sortino=1.5)
    metrics = {
        "SavvyTrader": PortfolioAnalysis(monthly_returns=combined["SavvyTrader"], metrics=perf),
        "Fidelity": PortfolioAnalysis(monthly_returns=combined["Fidelity"], metrics=perf),
        "SPY": PortfolioAnalysis(monthly_returns=combined["SPY"], metrics=perf),
    }

    bundle = PerformanceBundle(
        combined=combined,
        recent=combined,
        metrics=metrics,
        missing=[],
        last_period=index[-1],
    )

    html = render_html_report(bundle, title="Test Report", as_of="2024-03-31")
    assert "Test Report" in html
    assert "Monthly Returns" in html
    assert "Summary Metrics" in html
    assert "SavvyTrader" in html
    assert "Fidelity" in html
    assert "SPY" in html
    assert "CAGR" in html
    assert "2024-01" in html

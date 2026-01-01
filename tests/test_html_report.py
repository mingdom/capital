import pandas as pd

from portfolio_cli.analysis import PerformanceMetrics, PortfolioAnalysis
from portfolio_cli.performance import MultiFreqRiskMetrics, PerformanceBundle, PeriodRiskMetrics, RiskMetrics, SeriesWindow
from portfolio_cli.report import render_html_report


def test_render_html_contains_tables_and_metrics():
    index = pd.period_range("2024-01", periods=3, freq="M")
    combined = pd.DataFrame(
        {
            "Mingdom": [0.01, -0.02, 0.03],
            "Fidelity": [0.02, 0.0, -0.01],
            "SPY": [0.015, -0.01, 0.02],
        },
        index=index,
    )

    perf = PerformanceMetrics(cagr=0.1, three_month=0.02, max_dd_monthly=-0.02, ytd=0.01, sharpe=1.2, sortino=1.5)
    metrics = {
        "Mingdom": PortfolioAnalysis(monthly_returns=combined["Mingdom"], metrics=perf),
        "Fidelity": PortfolioAnalysis(monthly_returns=combined["Fidelity"], metrics=perf),
        "SPY": PortfolioAnalysis(monthly_returns=combined["SPY"], metrics=perf),
    }

    risk = RiskMetrics(
        volatility=0.1,
        downside_dev=0.05,
        max_drawdown=-0.2,
        drawdown_duration=2,
        var_95=-0.1,
        cvar_95=-0.15,
        var_99=-0.2,
        cvar_99=-0.25,
        hit_rate=0.6,
        avg_up=0.03,
        avg_down=-0.02,
        beta_spy=1.1,
        corr_spy=0.8,
        worst_month=-0.2,
        best_month=0.3,
    )
    windows = {
        "Mingdom": SeriesWindow(start=index[0], end=index[-1], count=3),
        "Fidelity": SeriesWindow(start=index[0], end=index[-1], count=3),
        "SPY": SeriesWindow(start=index[0], end=index[-1], count=3),
    }
    period = PeriodRiskMetrics(
        volatility=0.2,
        sharpe=1.0,
        sortino=1.2,
        var_95=-0.02,
        cvar_95=-0.03,
    )
    freq = MultiFreqRiskMetrics(daily=period, weekly=period, monthly=period)
    bundle = PerformanceBundle(
        combined=combined,
        recent=combined,
        metrics=metrics,
        risk_metrics={"Mingdom": risk, "Fidelity": risk, "SPY": risk},
        windows=windows,
        freq_metrics={"Mingdom": freq},
        missing=[],
        last_period=index[-1],
        annual_rf=0.04,
        current_year=2024,
    )

    html = render_html_report(bundle, title="Test Report", as_of="2024-03-31")
    assert "Test Report" in html
    assert "Monthly Returns" in html
    assert "Summary Metrics" in html
    assert "Mingdom" in html
    assert "Fidelity" in html
    assert "SPY" in html
    assert "CAGR" in html
    assert "2024-01" in html

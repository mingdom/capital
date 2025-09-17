"""User-facing entry-point helpers for the portfolio CLI."""

from .analysis import (  # noqa: F401
    ANNUAL_RF_RATE,
    FIDELITY_CSV_PATH,
    JSON_FILE_PATH,
    PerformanceMetrics,
    PortfolioAnalysis,
    calculate_metrics,
    calculate_monthly_returns,
    format_portfolio_summary,
    load_daily_changes,
    load_fidelity_monthly_returns,
    run_portfolio_analysis,
)
from .cli import app, run  # noqa: F401
from .shell import start_shell  # noqa: F401

__all__ = [
    "ANNUAL_RF_RATE",
    "FIDELITY_CSV_PATH",
    "JSON_FILE_PATH",
    "PerformanceMetrics",
    "PortfolioAnalysis",
    "calculate_metrics",
    "calculate_monthly_returns",
    "format_portfolio_summary",
    "load_daily_changes",
    "load_fidelity_monthly_returns",
    "run_portfolio_analysis",
    "app",
    "run",
    "start_shell",
]

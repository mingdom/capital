#!/usr/bin/env python3
"""Export portfolio data to JSON for the web dashboard.

This script collects all portfolio and benchmark data, computes metrics,
and exports everything as a single JSON file that the Next.js app can consume.

Usage:
    python -m scripts.export_web_data [--output web/public/data/portfolio.json]
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from datetime import date, datetime
from pathlib import Path
from typing import Any

import pandas as pd

from portfolio_cli.performance import (
    PerformanceBundle,
    SourceKind,
    collect_performance_data,
)


def serialize_value(obj: Any) -> Any:
    """Convert non-JSON-serializable objects to serializable form."""
    if obj is None:
        return None
    if isinstance(obj, (pd.Period, pd.Timestamp)):
        return str(obj)
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()
    if isinstance(obj, float):
        if pd.isna(obj):
            return None
        # Round floats to 6 decimal places for cleaner JSON
        return round(obj, 6)
    if isinstance(obj, pd.Series):
        return {str(k): serialize_value(v) for k, v in obj.items()}
    if isinstance(obj, pd.DataFrame):
        return {str(k): serialize_value(v) for k, v in obj.to_dict(orient="series").items()}
    if isinstance(obj, dict):
        return {str(k): serialize_value(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [serialize_value(v) for v in obj]
    if hasattr(obj, "__dataclass_fields__"):
        return {k: serialize_value(v) for k, v in asdict(obj).items()}
    return obj


def bundle_to_dict(bundle: PerformanceBundle) -> dict:
    """Convert PerformanceBundle to a JSON-serializable dict."""

    # Monthly returns time series for charts
    monthly_returns = {}
    for col in bundle.combined.columns:
        series = bundle.combined[col].dropna()
        monthly_returns[col] = {
            str(period): round(val, 6) for period, val in series.items()
        }

    # Performance metrics per source/benchmark
    performance = {}
    for name, analysis in bundle.metrics.items():
        metrics = analysis.metrics
        performance[name] = {
            "cagr": serialize_value(metrics.cagr),
            "one_year": serialize_value(metrics.one_year),
            "three_month": serialize_value(metrics.three_month),
            "ytd": serialize_value(metrics.ytd),
            "sharpe": serialize_value(metrics.sharpe),
            "sortino": serialize_value(metrics.sortino),
            "max_drawdown": serialize_value(metrics.max_dd_monthly),
        }

    # Risk metrics per source/benchmark
    risk = {}
    for name, rm in bundle.risk_metrics.items():
        risk[name] = {
            "volatility": serialize_value(rm.volatility),
            "downside_dev": serialize_value(rm.downside_dev),
            "max_drawdown": serialize_value(rm.max_drawdown),
            "drawdown_duration": rm.drawdown_duration,
            "var_95": serialize_value(rm.var_95),
            "cvar_95": serialize_value(rm.cvar_95),
            "var_99": serialize_value(rm.var_99),
            "cvar_99": serialize_value(rm.cvar_99),
            "hit_rate": serialize_value(rm.hit_rate),
            "avg_up": serialize_value(rm.avg_up),
            "avg_down": serialize_value(rm.avg_down),
            "beta_spy": serialize_value(rm.beta_spy),
            "corr_spy": serialize_value(rm.corr_spy),
            "worst_month": serialize_value(rm.worst_month),
            "best_month": serialize_value(rm.best_month),
            "up_capture": serialize_value(rm.up_capture),
            "down_capture": serialize_value(rm.down_capture),
        }

    # Data windows (date ranges)
    windows = {}
    for name, win in bundle.windows.items():
        windows[name] = {
            "start": str(win.start) if win.start else None,
            "end": str(win.end) if win.end else None,
            "count": win.count,
        }

    # Multi-frequency risk metrics (if available)
    freq_risk = {}
    for name, mf in bundle.freq_metrics.items():
        freq_risk[name] = {
            "daily": serialize_value(mf.daily),
            "weekly": serialize_value(mf.weekly),
            "monthly": serialize_value(mf.monthly),
        }

    # Identify portfolios vs benchmarks
    portfolios = [s.label for s in [SourceKind.MINGDOM, SourceKind.FIDELITY]
                  if s.label in performance]
    benchmarks = [k for k in performance.keys() if k not in portfolios]

    return {
        "generated_at": datetime.now().isoformat(),
        "current_year": bundle.current_year,
        "annual_rf": bundle.annual_rf,
        "last_period": str(bundle.last_period) if bundle.last_period else None,
        "portfolios": portfolios,
        "benchmarks": benchmarks,
        "monthly_returns": monthly_returns,
        "performance": performance,
        "risk": risk,
        "windows": windows,
        "freq_risk": freq_risk,
        "warnings": bundle.missing,
    }


def main():
    parser = argparse.ArgumentParser(description="Export portfolio data for web dashboard")
    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=Path("web/public/data/portfolio.json"),
        help="Output JSON file path",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Print detailed output",
    )
    args = parser.parse_args()

    if args.verbose:
        print("Collecting portfolio and benchmark data...")

    bundle = collect_performance_data(
        sources=[SourceKind.MINGDOM, SourceKind.FIDELITY],
        include_benchmarks=True,
    )

    if args.verbose:
        print(f"  Found {len(bundle.metrics)} data sources")
        for name in bundle.metrics:
            print(f"    - {name}")
        if bundle.missing:
            print(f"  Warnings: {bundle.missing}")

    data = bundle_to_dict(bundle)

    # Ensure output directory exists
    args.output.parent.mkdir(parents=True, exist_ok=True)

    with open(args.output, "w") as f:
        json.dump(data, f, indent=2)

    if args.verbose:
        print(f"Exported to {args.output}")
        print(f"  File size: {args.output.stat().st_size / 1024:.1f} KB")
    else:
        print(f"✓ Exported portfolio data to {args.output}")


if __name__ == "__main__":
    main()

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from portfolio_cli.analysis import ANNUAL_RF_RATE, FIDELITY_CSV_PATH, JSON_FILE_PATH
from portfolio_cli.performance import SourceKind, collect_performance_data
from portfolio_cli.report import render_html_report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate HTML performance report")
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=Path("dist/index.html"),
        help="Destination HTML file",
    )
    parser.add_argument(
        "--sources",
        nargs="*",
        choices=[kind.value for kind in SourceKind],
        help="Portfolio sources to include",
    )
    parser.add_argument(
        "--savvy-json",
        type=Path,
        default=JSON_FILE_PATH,
        help="Path to SavvyTrader valuations JSON",
    )
    parser.add_argument(
        "--fidelity-csv",
        type=Path,
        default=FIDELITY_CSV_PATH,
        help="Path to Fidelity investment income CSV",
    )
    parser.add_argument(
        "--rf",
        type=float,
        default=ANNUAL_RF_RATE,
        help="Annual risk-free rate (e.g., 0.04)",
    )
    parser.add_argument(
        "--year",
        type=int,
        help="Calendar year for YTD calculation (defaults to current year)",
    )
    parser.add_argument(
        "--no-benchmarks",
        action="store_true",
        help="Skip benchmarks",
    )
    parser.add_argument(
        "--title",
        default="Mingdom Capital Performance",
        help="Report title",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    selected_sources = [SourceKind(value) for value in args.sources] if args.sources else None
    current_year = args.year or datetime.now().year

    bundle = collect_performance_data(
        sources=selected_sources,
        savvy_json=args.savvy_json,
        fidelity_csv=args.fidelity_csv,
        annual_rf=args.rf,
        current_year=current_year,
        include_benchmarks=not args.no_benchmarks,
    )

    if bundle.combined.empty:
        print("No portfolio data available — report not created.", file=sys.stderr)
        for note in bundle.missing:
            print(f"Note: {note}", file=sys.stderr)
        return 1

    html = render_html_report(bundle, title=args.title)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(html, encoding="utf-8")
    print(f"Report written to {args.output}")
    for note in bundle.missing:
        print(f"Note: {note}")
    return 0


if __name__ == "__main__":  # pragma: no cover - manual invocation
    raise SystemExit(main())

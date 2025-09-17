from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable

import pandas as pd
import streamlit as st

from portfolio_cli.analysis import ANNUAL_RF_RATE, FIDELITY_CSV_PATH, JSON_FILE_PATH
from portfolio_cli.performance import SourceKind, collect_performance_data


def _format_percentages(df: pd.DataFrame) -> pd.DataFrame:
    def fmt(value: float | None) -> str:
        if value is None or pd.isna(value):
            return "—"
        return f"{value * 100:.1f}%"

    return df.applymap(fmt)


def _format_summary(bundle, ordered_columns: Iterable[str]) -> pd.DataFrame:
    records = []
    for name in ordered_columns:
        metrics = bundle.metrics.get(name)
        if not metrics:
            continue
        m = metrics.metrics
        records.append(
            {
                "Source": name,
                "CAGR": m.cagr,
                "YTD": m.ytd,
                "Max Drawdown": m.max_dd_monthly,
                "Sharpe": m.sharpe,
                "Sortino": m.sortino,
            }
        )
    df = pd.DataFrame(records)
    if df.empty:
        return df
    percent_cols = ["CAGR", "YTD", "Max Drawdown"]
    for col in percent_cols:
        df[col] = df[col].apply(lambda x: f"{x * 100:.1f}%" if pd.notna(x) else "—")
    for col in ["Sharpe", "Sortino"]:
        df[col] = df[col].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "—")
    return df.set_index("Source")


def main() -> None:
    st.set_page_config(page_title="Portfolio Performance", layout="wide")
    st.title("Portfolio Performance Dashboard")

    col1, col2 = st.columns(2)
    default_sources_env = os.getenv("PORTFOLIO_SOURCES")
    default_sources = (
        [s for s in (default_sources_env or "").split(",") if s in {kind.value for kind in SourceKind}]
        if default_sources_env
        else [kind.value for kind in SourceKind]
    )
    include_benchmarks_default = os.getenv("PORTFOLIO_INCLUDE_BENCHMARKS", "1") != "0"
    default_rf_env = os.getenv("PORTFOLIO_RISK_FREE")
    rf_default = float(default_rf_env) if default_rf_env is not None else ANNUAL_RF_RATE
    default_savvy = os.getenv("PORTFOLIO_SAVVY_JSON", str(JSON_FILE_PATH))
    default_fidelity = os.getenv("PORTFOLIO_FIDELITY_CSV", str(FIDELITY_CSV_PATH))

    with col1:
        selected_sources = st.multiselect(
            "Sources",
            options=[kind.value for kind in SourceKind],
            default=default_sources,
        )
        include_benchmarks = st.checkbox("Include SPY/QQQ benchmarks", value=include_benchmarks_default)
    with col2:
        savvy_path = st.text_input("SavvyTrader JSON", value=default_savvy)
        fidelity_path = st.text_input("Fidelity CSV", value=default_fidelity)
        annual_rf = st.number_input("Annual risk-free rate", value=rf_default, step=0.01)

    sources = [SourceKind(value) for value in selected_sources] if selected_sources else None

    bundle = collect_performance_data(
        sources=sources,
        savvy_json=Path(savvy_path),
        fidelity_csv=Path(fidelity_path),
        annual_rf=annual_rf,
        include_benchmarks=include_benchmarks,
    )

    if bundle.combined.empty:
        st.warning("No portfolio data available. Check file paths and try again.")
        if bundle.missing:
            st.write("Notes:")
            for item in bundle.missing:
                st.write(f"- {item}")
        return

    st.subheader("Monthly Returns")
    recent = bundle.combined.tail(12) if not bundle.combined.empty else bundle.combined
    st.dataframe(_format_percentages(recent), use_container_width=True)

    st.subheader("Summary Metrics")
    summary_df = _format_summary(bundle, recent.columns if not recent.empty else bundle.combined.columns)
    if not summary_df.empty:
        st.dataframe(summary_df, use_container_width=True)

    st.subheader("Cumulative Performance")
    cumulative = (1 + bundle.combined.fillna(0)).cumprod() - 1
    st.line_chart(cumulative)

    if bundle.missing:
        with st.expander("Notes"):
            for item in bundle.missing:
                st.write(f"- {item}")


if __name__ == "__main__":  # pragma: no cover
    main()

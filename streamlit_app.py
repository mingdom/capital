from __future__ import annotations

import os
import io
from pathlib import Path
from typing import Dict, Iterable

import pandas as pd
import streamlit as st
import altair as alt

from benchmarks import configured_benchmarks, get_benchmark_series
from portfolio_cli.analysis import (
    ANNUAL_RF_RATE,
    FIDELITY_CSV_PATH,
    PerformanceMetrics,
    calculate_metrics,
    load_fidelity_monthly_returns,
)


def _format_percentages(df: pd.DataFrame) -> pd.DataFrame:
    def fmt(value: float | None) -> str:
        if value is None or pd.isna(value):
            return "—"
        return f"{value * 100:.1f}%"

    return df.applymap(fmt)


def _format_summary(metrics_map: Dict[str, PerformanceMetrics], ordered_columns: Iterable[str]) -> pd.DataFrame:
    records = []
    for name in ordered_columns:
        metrics = metrics_map.get(name)
        if metrics is None:
            continue
        records.append(
            {
                "Source": name,
                "CAGR": metrics.cagr,
                "YTD": metrics.ytd,
                "Max Drawdown": metrics.max_dd_monthly,
                "Sharpe": metrics.sharpe,
                "Sortino": metrics.sortino,
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


def _ensure_period_index(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    if isinstance(df.index, pd.PeriodIndex):
        return df
    converted = df.copy()
    converted.index = pd.PeriodIndex(df.index, freq="M")
    return converted


def _filter_range(df: pd.DataFrame, range_key: str, current_year: int) -> pd.DataFrame:
    df = _ensure_period_index(df)
    if df.empty:
        return df
    if range_key == "All":
        return df
    if range_key == "YTD":
        filtered = df[df.index.year == current_year]
        return filtered if not filtered.empty else df
    periods = 3 if range_key == "3M" else 12
    return df.tail(periods)


def main() -> None:
    st.set_page_config(page_title="Fidelity Performance", layout="wide")
    st.title("Fidelity Performance Dashboard")

    include_benchmarks_default = os.getenv("PORTFOLIO_INCLUDE_BENCHMARKS", "1") != "0"
    default_rf_env = os.getenv("PORTFOLIO_RISK_FREE")
    rf_default = float(default_rf_env) if default_rf_env is not None else ANNUAL_RF_RATE
    default_fidelity = os.getenv("PORTFOLIO_FIDELITY_CSV", str(FIDELITY_CSV_PATH))

    col_left, col_right = st.columns([2, 1])
    with col_left:
        uploaded_file = st.file_uploader(
            "Upload Fidelity CSV export",
            type="csv",
            help="Drop the Fidelity monthly performance CSV here to analyze it immediately.",
        )
        fidelity_path_input = st.text_input(
            "Fallback Fidelity CSV path",
            value=default_fidelity,
            help="Used when no file is uploaded.",
        )
    with col_right:
        include_benchmarks = st.checkbox(
            "Include benchmarks",
            value=include_benchmarks_default,
        )
        annual_rf = st.number_input("Annual risk-free rate", value=rf_default, step=0.01)

    range_options = ("3M", "YTD", "1Y", "All")
    range_choice = st.radio(
        "Time range",
        options=range_options,
        index=range_options.index("All"),
        horizontal=True,
    )

    monthly_returns = pd.Series(dtype=float)
    missing: list[str] = []
    source_note: str | None = None

    if uploaded_file is not None:
        try:
            csv_buffer = io.StringIO(uploaded_file.getvalue().decode("utf-8-sig"))
            monthly_returns = load_fidelity_monthly_returns(csv_buffer)
            source_note = f"Using uploaded file: {uploaded_file.name}"
        except Exception as exc:  # pragma: no cover - surfaced in UI
            st.error(f"Unable to parse uploaded CSV: {exc}")
            return
    else:
        fidelity_path = Path(fidelity_path_input).expanduser()
        if fidelity_path_input:
            try:
                monthly_returns = load_fidelity_monthly_returns(fidelity_path)
                source_note = f"Using file: {fidelity_path}"
            except FileNotFoundError:
                missing.append(f"Fidelity (missing file: {fidelity_path})")
            except ValueError as exc:
                missing.append(f"Fidelity ({exc})")
        else:
            missing.append("Fidelity (no file uploaded)")

    if monthly_returns.empty:
        st.warning("No Fidelity data available. Upload a CSV or check the fallback path.")
        if missing:
            with st.expander("Notes"):
                for item in missing:
                    st.write(f"- {item}")
        return

    if source_note:
        st.caption(source_note)

    current_year = pd.Timestamp.today().year
    combined = pd.DataFrame({"Fidelity": monthly_returns})

    months_index = combined.index

    if include_benchmarks and not months_index.empty:
        for symbol in configured_benchmarks():
            series = get_benchmark_series(symbol, months_index)
            if series.empty:
                missing.append(f"benchmark {symbol} (no data)")
                continue
            aligned = series.reindex(months_index)
            combined[symbol] = aligned
    combined = _ensure_period_index(combined)

    filtered_returns = _filter_range(combined, range_choice, current_year)

    metrics_map: Dict[str, PerformanceMetrics] = {}
    for name in combined.columns:
        series = filtered_returns[name].dropna() if name in filtered_returns else pd.Series(dtype=float)
        metrics_map[name] = calculate_metrics(series, annual_rf, current_year)

    st.subheader("Monthly Returns")
    st.dataframe(_format_percentages(filtered_returns), width="stretch")

    st.subheader("Summary Metrics")
    summary_df = _format_summary(metrics_map, combined.columns)
    if not summary_df.empty:
        st.dataframe(summary_df, width="stretch")

    st.subheader("Cumulative Performance")
    cumulative = (1 + combined.fillna(0)).cumprod() - 1
    cumulative_filtered = _filter_range(cumulative, range_choice, current_year)
    chart_df = cumulative_filtered.dropna(how="all")
    if chart_df.empty:
        st.info("Not enough data to render cumulative chart for the selected range.")
    else:
        chart_df = chart_df.reset_index().rename(columns={"index": "Period"})
        chart_df["Date"] = chart_df["Period"].dt.to_timestamp()
        value_columns = [col for col in chart_df.columns if col not in {"Period", "Date"}]
        long_df = chart_df.melt(id_vars="Date", value_vars=value_columns, var_name="Series", value_name="Return")
        long_df = long_df.dropna(subset=["Return"])
        if long_df.empty:
            st.info("Not enough data to render cumulative chart for the selected range.")
        else:
            chart = (
                alt.Chart(long_df)
                .mark_line()
                .encode(
                    x=alt.X("Date:T", axis=alt.Axis(title="Date")),
                    y=alt.Y("Return:Q", axis=alt.Axis(title="Cumulative Return", format=".0%")),
                    color=alt.Color("Series:N", title="Series"),
                    tooltip=[
                        alt.Tooltip("Date:T", title="Month"),
                        alt.Tooltip("Series:N", title="Series"),
                        alt.Tooltip("Return:Q", title="Cumulative", format=".2%"),
                    ],
                )
                .properties(height=320)
            )
            st.altair_chart(chart, use_container_width=True)

    if missing:
        with st.expander("Notes"):
            for item in missing:
                st.write(f"- {item}")


if __name__ == "__main__":  # pragma: no cover
    main()

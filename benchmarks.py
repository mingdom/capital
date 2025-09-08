from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import pandas as pd
import yfinance as yf


CACHE_PATH = Path("data/benchmarks.json")


def last_complete_month(today: date | None = None) -> pd.Period:
    if today is None:
        today = date.today()
    first_of_month = today.replace(day=1)
    last_day_prev_month = first_of_month - timedelta(days=1)
    return pd.Period(last_day_prev_month, freq="M")


def _load_cache() -> Dict[str, Dict[str, float]]:
    if CACHE_PATH.exists():
        with open(CACHE_PATH, "r") as f:
            return json.load(f)
    return {}


def _save_cache(cache: Dict[str, Dict[str, float]]) -> None:
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CACHE_PATH, "w") as f:
        json.dump(cache, f, indent=2)


def _periods_to_str(periods: Iterable[pd.Period]) -> List[str]:
    return [str(p) for p in periods]


def fetch_monthly_returns(symbol: str, start_period: pd.Period, end_period: pd.Period) -> pd.Series:
    start = (start_period.to_timestamp("M") - pd.offsets.MonthBegin(1)).normalize()
    end = end_period.to_timestamp("M")
    hist = yf.Ticker(symbol).history(start=start, end=end + pd.offsets.MonthEnd(1), interval="1mo", auto_adjust=True)
    if hist.empty:
        return pd.Series(dtype=float)
    closes = hist["Close"].copy()
    rets = closes.pct_change().dropna()
    periods = rets.index.to_period("M")
    rets.index = periods
    # Limit to requested period window
    rets = rets[(rets.index >= start_period) & (rets.index <= end_period)]
    return rets


def ensure_benchmark_cache(symbols: Iterable[str], needed_months: Iterable[pd.Period]) -> Dict[str, Dict[str, float]]:
    cache = _load_cache()
    lcm = last_complete_month()
    needed = [p for p in needed_months if p <= lcm]
    if not needed:
        return cache

    for sym in symbols:
        sym_cache = cache.get(sym, {})
        missing = [p for p in needed if str(p) not in sym_cache]
        if not missing:
            cache[sym] = sym_cache
            continue
        start_p, end_p = min(missing), max(missing)
        series = fetch_monthly_returns(sym, start_p, end_p)
        for p, v in series.items():
            if p <= lcm:
                sym_cache[str(p)] = float(v)
        cache[sym] = sym_cache

    _save_cache(cache)
    return cache


def get_benchmark_series(symbol: str, months: Iterable[pd.Period]) -> pd.Series:
    cache = ensure_benchmark_cache([symbol], months)
    mapping = cache.get(symbol, {})
    values = {pd.Period(k): v for k, v in mapping.items()}
    out = []
    for m in months:
        if m in values:
            out.append((m, values[m]))
    if not out:
        return pd.Series(dtype=float)
    idx = pd.PeriodIndex([m for m, _ in out], freq="M")
    data = [v for _, v in out]
    return pd.Series(data, index=idx, name=symbol).sort_index()


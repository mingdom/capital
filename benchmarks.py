from __future__ import annotations

import json
from datetime import date, datetime, timedelta
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
    try:
        hist = yf.Ticker(symbol).history(
            start=start,
            end=end + pd.offsets.MonthEnd(1),
            interval="1mo",
            auto_adjust=True,
        )
    except Exception:
        return pd.Series(dtype=float)
    if hist.empty:
        return pd.Series(dtype=float)
    closes = hist["Close"].copy()
    rets = closes.pct_change().dropna()
    periods = rets.index.to_period("M")
    rets.index = periods
    # Limit to requested period window
    rets = rets[(rets.index >= start_period) & (rets.index <= end_period)]
    return rets


def _first_trading_close(series: pd.Series, start: pd.Timestamp) -> float | None:
    # Normalize timezone to tz-naive to avoid tz-aware vs naive comparisons
    if isinstance(series.index, pd.DatetimeIndex) and series.index.tz is not None:
        series = series.copy()
        series.index = series.index.tz_localize(None)
    s = series[series.index >= start]
    if not s.empty:
        return float(s.iloc[0])
    return None


def _last_trading_close(series: pd.Series, end: pd.Timestamp) -> float | None:
    # Normalize timezone to tz-naive to avoid tz-aware vs naive comparisons
    if isinstance(series.index, pd.DatetimeIndex) and series.index.tz is not None:
        series = series.copy()
        series.index = series.index.tz_localize(None)
    s = series[series.index <= end]
    if not s.empty:
        return float(s.iloc[-1])
    return None


def fetch_partial_return(symbol: str, start_date: date, end_date: date) -> float | None:
    """Fetch adjusted-close based return between two dates inclusive.

    Uses daily data and computes return = last_adj_close / first_adj_close - 1.
    Chooses the first trading day on/after start_date and the last trading day on/before end_date.
    """
    if end_date < start_date:
        return None
    start_ts = pd.Timestamp(start_date)
    end_ts = pd.Timestamp(end_date)
    try:
        hist = yf.Ticker(symbol).history(
            start=start_ts,
            end=end_ts + pd.offsets.Day(1),
            interval="1d",
            auto_adjust=True,
        )
    except Exception:
        return None
    if hist.empty:
        return None
    closes = hist["Close"].copy()
    first = _first_trading_close(closes, start_ts)
    last = _last_trading_close(closes, end_ts)
    if first is None or last is None or first == 0:
        return None
    return float(last / first - 1.0)


def ensure_benchmark_cache(
    symbols: Iterable[str], needed_months: Iterable[pd.Period]
) -> Dict[str, Dict[str, float]]:
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


def ensure_aligned_partials(
    symbols: Iterable[str], inception_date: date, current_end: date
) -> Dict:
    """Ensure cache contains aligned partial returns for inception and current months.

    Stores under top-level key "_aligned":
      { symbol: { "YYYY-MM": { start: str, end: str, return: float, as_of: str } } }
    """
    cache = _load_cache()
    aligned = cache.get("_aligned", {})

    inception_month = pd.Period(inception_date, freq="M")
    current_month = pd.Period(current_end, freq="M")

    for sym in symbols:
        sym_aligned = aligned.get(sym, {})
        # Inception partial (from inception_date to month end)
        inc_end = inception_month.to_timestamp("M")  # end of month timestamp
        inc_end_date = (inc_end + pd.offsets.MonthEnd(0)).date()
        key_inc = str(inception_month)
        if key_inc not in sym_aligned:
            r = fetch_partial_return(sym, inception_date, inc_end_date)
            if r is not None:
                sym_aligned[key_inc] = {
                    "start": str(inception_date),
                    "end": str(inc_end_date),
                    "return": r,
                    "as_of": str(inc_end_date),
                }

        # Current partial (from month start to current_end)
        cm_start_date = date(current_month.start_time.year, current_month.start_time.month, 1)
        key_cur = str(current_month)
        existing = sym_aligned.get(key_cur)
        needs_update = existing is None or existing.get("end") != str(current_end)
        if needs_update:
            r = fetch_partial_return(sym, cm_start_date, current_end)
            if r is not None:
                sym_aligned[key_cur] = {
                    "start": str(cm_start_date),
                    "end": str(current_end),
                    "return": r,
                    "as_of": str(current_end),
                }

        aligned[sym] = sym_aligned

    cache["_aligned"] = aligned
    cache.setdefault("_meta", {})["last_updated"] = datetime.utcnow().isoformat() + "Z"
    _save_cache(cache)
    return cache


def get_aligned_benchmark_series(
    symbol: str,
    months: Iterable[pd.Period],
    inception_date: date,
    current_end: date,
) -> pd.Series:
    """Return benchmark monthly series aligned to portfolio partial months.

    - Inception month uses partial from inception_date to month end.
    - Current ongoing month uses partial from month start to current_end.
    - All other months use cached full-month returns (up to last complete month).
    """
    # Ensure we have monthly for full months
    ensure_benchmark_cache([symbol], months)
    # Ensure aligned for inception and current
    cache = ensure_aligned_partials([symbol], inception_date, current_end)
    monthly_map = _load_cache().get(symbol, {})
    aligned = cache.get("_aligned", {}).get(symbol, {})

    out = []
    for m in months:
        key = str(m)
        if key in aligned:
            out.append((m, float(aligned[key]["return"])))
        elif key in monthly_map:
            out.append((m, float(monthly_map[key])))
        # else skip missing
    if not out:
        return pd.Series(dtype=float)
    idx = pd.PeriodIndex([m for m, _ in out], freq="M")
    data = [v for _, v in out]
    return pd.Series(data, index=idx, name=symbol).sort_index()

import pandas as pd

from benchmarks import _first_trading_close, _last_trading_close


def test_first_last_trading_close_naive_index():
    idx = pd.to_datetime(["2024-02-01", "2024-02-02", "2024-02-05"])  # B D B
    s = pd.Series([100.0, 102.0, 101.0], index=idx)
    first = _first_trading_close(s, pd.Timestamp("2024-02-02"))
    last = _last_trading_close(s, pd.Timestamp("2024-02-04"))
    assert first == 102.0
    assert last == 102.0


def test_first_last_trading_close_tz_aware_index():
    idx = pd.to_datetime(["2024-02-01", "2024-02-02", "2024-02-05"]).tz_localize(
        "America/New_York"
    )
    s = pd.Series([100.0, 102.0, 101.0], index=idx)
    # Start/end are tz-naive; helpers should handle internally
    first = _first_trading_close(s, pd.Timestamp("2024-02-02"))
    last = _last_trading_close(s, pd.Timestamp("2024-02-04"))
    assert first == 102.0
    assert last == 102.0


from datetime import datetime

from benchmarks import last_complete_month


def test_last_complete_month_after_market_close() -> None:
    # Last business day of Dec 2025 is 12/31; after 1pm PT counts as complete.
    dt = datetime(2025, 12, 31, 13, 1)
    assert str(last_complete_month(dt)) == "2025-12"


def test_last_complete_month_before_market_close() -> None:
    # Before 1pm PT on the last trading day, treat the current month as incomplete.
    dt = datetime(2025, 12, 31, 12, 0)
    assert str(last_complete_month(dt)) == "2025-11"

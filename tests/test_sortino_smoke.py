import json
from datetime import datetime, timedelta
from tempfile import NamedTemporaryFile

from sortino import convert_to_monthly_and_calculate_ratios


def _sample_data():
    # Two months of synthetic daily changes (no zeros)
    start = datetime(2024, 2, 1)
    rows = []
    for i in range(5):
        rows.append({
            "summaryDate": (start + timedelta(days=i)).strftime("%Y-%m-%d"),
            "dailyTotalValueChange": 0.01,  # +1%
        })
    start = datetime(2024, 3, 1)
    for i in range(5):
        rows.append({
            "summaryDate": (start + timedelta(days=i)).strftime("%Y-%m-%d"),
            "dailyTotalValueChange": -0.005,  # -0.5%
        })
    return rows


def test_smoke_runs_and_prints(capsys):
    data = _sample_data()
    with NamedTemporaryFile("w+", suffix=".json") as tmp:
        json.dump(data, tmp)
        tmp.flush()
        convert_to_monthly_and_calculate_ratios(json_file=tmp.name, annual_rf=0.04, current_year=2024)

    out = capsys.readouterr().out
    # Basic smoke checks
    assert "Monthly Returns:" in out
    assert "Annualized Sharpe Ratio:" in out
    assert "Annualized Sortino Ratio:" in out

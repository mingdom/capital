import json
from datetime import datetime, timedelta

from typer.testing import CliRunner

from portfolio_cli.cli import app


def _sample_data():
    start = datetime(2024, 2, 1)
    rows = []
    for i in range(5):
        rows.append({
            "summaryDate": (start + timedelta(days=i)).strftime("%Y-%m-%d"),
            "dailyTotalValueChange": 0.01,
        })
    start = datetime(2024, 3, 1)
    for i in range(5):
        rows.append({
            "summaryDate": (start + timedelta(days=i)).strftime("%Y-%m-%d"),
            "dailyTotalValueChange": -0.005,
        })
    return rows


def test_cli_analyze_prints_summary(tmp_path):
    data_path = tmp_path / "valuations.json"
    with data_path.open("w") as handle:
        json.dump(_sample_data(), handle)

    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "analyze",
            "--json",
            str(data_path),
            "--rf",
            "0.04",
            "--year",
            "2024",
        ],
    )

    assert result.exit_code == 0
    assert "Monthly Returns" in result.stdout
    assert "Annualized Sharpe Ratio" in result.stdout

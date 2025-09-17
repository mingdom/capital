import json
from datetime import datetime, timedelta

import pytest
from typer.testing import CliRunner

from portfolio_cli.analysis import load_fidelity_monthly_returns
from portfolio_cli.cli import app
from portfolio_cli.shell import PortfolioShell, start_shell


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


def test_cli_performance_savvytrader(tmp_path):
    data_path = tmp_path / "valuations.json"
    with data_path.open("w") as handle:
        json.dump(_sample_data(), handle)

    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "performance",
            "savvytrader",
            "--savvy-json",
            str(data_path),
            "--rf",
            "0.04",
            "--year",
            "2024",
            "--no-benchmarks",
        ],
    )

    assert result.exit_code == 0
    assert "Monthly Returns" in result.stdout
    assert "Summary Metrics" in result.stdout


def _fidelity_csv() -> str:
    return """Investment income Export
"Income For:"
Investment income - (Jan-01-2024 - Mar-31-2024)
"Monthly","Beginning balance","Market change","Dividends","Interest","Deposits","Withdrawals","Net advisory fees","Ending balance"
"Mar 2024","$110.00","$11.00","$0.00","$0.00","$0.00","$0.00","$0.00","$121.00"
"Feb 2024","$100.00","$5.00","$2.00","$0.00","$10.00","$0.00","$1.00","$116.00"
"Jan 2024","$90.00","$-4.50","$1.50","$0.00","$0.00","$0.00","$0.00","$87.00"
"Total"," "," ","$3.50","$0.00","$10.00","$0.00","$1.00"
"""


def test_load_fidelity_monthly_returns(tmp_path):
    csv_file = tmp_path / "fidelity.csv"
    csv_file.write_text(_fidelity_csv())

    series = load_fidelity_monthly_returns(csv_file)

    assert list(series.index.astype(str)) == ["2024-01", "2024-02", "2024-03"]
    assert pytest.approx(series.iloc[0], rel=1e-6) == (-4.5 + 1.5) / 90
    assert pytest.approx(series.iloc[1], rel=1e-6) == (5 + 2 - 1) / 100
    assert pytest.approx(series.iloc[2], rel=1e-6) == 11 / 110


def test_shell_runs_performance_command(tmp_path, capsys):
    data_path = tmp_path / "valuations.json"
    with data_path.open("w") as handle:
        json.dump(_sample_data(), handle)

    start_shell(
        app,
        commands=[
            f"performance savvytrader --savvy-json {data_path} --rf 0.04 --year 2024 --no-benchmarks",
            "exit",
        ],
    )

    out = capsys.readouterr().out
    assert "Monthly Returns" in out
    assert "Goodbye" in out


def test_cli_performance_fidelity(tmp_path):
    csv_file = tmp_path / "fidelity.csv"
    csv_file.write_text(_fidelity_csv())

    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "performance",
            "fidelity",
            "--fidelity-csv",
            str(csv_file),
            "--rf",
            "0.02",
            "--year",
            "2024",
            "--no-benchmarks",
        ],
    )

    assert result.exit_code == 0
    assert "Monthly Returns" in result.stdout


def test_shell_sources_command(capsys):
    start_shell(
        app,
        commands=[
            "sources",
            "exit",
        ],
    )

    out = capsys.readouterr().out
    assert "Supported sources" in out
    assert "savvytrader" in out
    assert "fidelity" in out


def test_shell_complete_performance_suggests_sources():
    shell = PortfolioShell(app)

    suggestions = shell.complete_performance("", "performance ", len("performance "), len("performance "))
    assert set(suggestions) >= {"savvytrader", "fidelity"}

    partial = shell.complete_performance("fi", "performance fi", len("performance "), len("performance fi"))
    assert partial == ["fidelity"]

    flags = shell.complete_performance("--", "performance fidelity --", len("performance fidelity "), len("performance fidelity --"))
    assert "--no-benchmarks" in flags

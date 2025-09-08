# Repository Guidelines

## Project Structure & Module Organization
- `sortino.py` — main analysis script; exposes `convert_to_monthly_and_calculate_ratios`.
- `data/valuations.json` — paste SavvyTrader valuations API response for local runs.
- `data/` — extra data files (e.g., `prices.json`, historical snapshots).
- `tests/` — pytest tests (e.g., `tests/test_sortino_smoke.py`).
- `scripts/pre-commit.sh` — optional Git pre-commit hook.
- `Makefile`, `requirements*.txt`, `pyproject.toml`, `pytest.ini` — tooling and config.
- `2025-q2/` — static charts/assets used for reporting; not code.
- `README.md` — Quickstart and usage notes.
- `venv/` — local virtual environment (do not rely on it being present on other machines).

## Build, Test, and Development Commands
- Setup environment:
  - `python3 -m venv venv && source venv/bin/activate`
  - `pip install --upgrade pip pandas numpy`
- Run locally:
  - `python3 sortino.py` — computes monthly returns, CAGR, drawdown, Sharpe/Sortino.
- Optional tooling (recommended):
  - `pip install black ruff pytest`
  - `black .` — format; `ruff check .` — lint.

## Coding Style & Naming Conventions
- Python, 4‑space indentation; UTF‑8; max line length 100.
- Use snake_case for functions/variables; UPPER_SNAKE_CASE for constants.
- Add type hints for new/edited functions; keep functions pure when practical.
- Keep I/O (file/print) at the top‑level script; isolate logic into importable functions.

## Testing Guidelines
- Framework: `pytest`.
- Location: `tests/` mirroring targets (e.g., `tests/test_sortino.py`).
- Write unit tests for monthly aggregation and ratio math; use small synthetic fixtures.
- Run: `pytest -q`; target coverage >= 80% for changed lines (use `pytest --maxfail=1`).

## Commit & Pull Request Guidelines
- Commit messages: Conventional style (`feat:`, `fix:`, `docs:`, `chore:`). Keep scope small.
- PRs must include: purpose, summary of changes, sample output (before/after) for numeric changes, and any data/source notes. Link related issues.
- Avoid bundling refactors with logic changes; prefer separate PRs.

## Security & Data Tips
- Do not commit API keys or personal data. Sanitize `data/valuations.json` when sharing.
- Large or transient datasets should be git‑ignored; prefer minimal repro samples.

## Agent‑Specific Instructions
- Make minimal, focused changes; do not rename `sortino.py` without justification.
- If you change commands or flags, update `README.md` accordingly.
- Avoid adding heavy dependencies; prefer stdlib + `pandas`/`numpy` already in use.

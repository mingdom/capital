# AI Agent Guidelines for Mingdom Capital

This document provides comprehensive guidelines for AI coding assistants (Claude, Gemini, GPT-4, etc.) working on this repository. Read this carefully before making any changes.

## Role Definition

You are acting as a **pragmatic senior software engineer** contributing to a personal portfolio analytics toolkit. Your priorities are:

1. **Correctness**: Never fabricate behavior, test results, or performance metrics
2. **Simplicity**: Prefer minimal, focused changes over large refactors
3. **Maintainability**: Follow existing patterns and conventions
4. **Clarity**: Make assumptions explicit; ask questions when uncertain

## Core Principles

### Communication First
- **When asked a question, answer it first** - do NOT immediately jump into writing code
- At the end of every task, **summarize what you did** (changes made, testing performed, next steps)
- If requirements are ambiguous, **ask clarifying questions** before implementing
- Document non-obvious decisions in `.agent/devlog-YYYY-MM-DD.md` when prompted

### Minimal, Focused Changes
- Make the **smallest change** that solves the root cause
- Keep pull requests focused: don't bundle refactors with bug fixes
- Avoid renaming files, moving code, or "drive-by" clean-ups unless explicitly requested
- Respect existing architecture - **understand before changing**

### Evidence-Based Development
- If you didn't verify it (via test, manual run, or inspection), don't state it as fact
- Run tests locally before claiming something works: `make test`
- Validate report generation if you touch display/formatting: `make report`
- Surface errors, edge cases, and trade-offs transparently

## Project Architecture

### High-Level Structure

```
Core Data Pipeline:
  SavvyTrader JSON / Fidelity CSV
         ↓
  [portfolio_cli/performance.py] ← Load & normalize data
         ↓
  [portfolio_cli/analysis.py]    ← Calculate metrics (CAGR, Sharpe, Sortino, drawdown)
         ↓
  [portfolio_cli/cli.py]         ← CLI commands (performance, report, shell)
  [portfolio_cli/report.py]      ← HTML report generation
  [portfolio_cli/shell.py]       ← Interactive REPL

Benchmark Pipeline:
  [benchmarks.py]                ← Fetch & cache market data via yfinance
         ↓
  data/benchmarks.json           ← Persistent cache
```

### Module Responsibilities

| Module | Purpose | Key Functions |
|--------|---------|---------------|
| `portfolio_cli/analysis.py` | Core math & metrics | `calculate_metrics()`, `calculate_monthly_returns()` |
| `portfolio_cli/performance.py` | Data loading | `load_daily_changes()`, `load_fidelity_monthly_returns()` |
| `portfolio_cli/cli.py` | CLI interface | `performance_command()`, `report_command()` |
| `portfolio_cli/report.py` | HTML generation | `build_report()`, `_render_source_section()` |
| `portfolio_cli/shell.py` | Interactive shell | `start_shell()` |
| `benchmarks.py` | Market data fetching | `fetch_monthly_returns()`, `get_benchmark_series()` |
| `sortino.py` | Legacy compatibility | Backwards-compatible wrappers for old scripts |

### Data Flow

1. **Import**: `scripts/import_latest.py` processes files from `data/import/` → archives to `data/import/archive/`
2. **Load**: `performance.py` reads `data/valuations.json` or Fidelity CSVs
3. **Calculate**: `analysis.py` computes monthly returns → performance metrics
4. **Display**: `cli.py` formats tables or `report.py` generates HTML
5. **Benchmarks**: `benchmarks.py` fetches market data on-demand, caches to `data/benchmarks.json`

## Code Style & Standards

### Python Conventions
- **Python Version**: 3.9+ (targeting 3.11 for type hints)
- **Indentation**: 4 spaces (no tabs)
- **Line Length**: 100 characters max
- **Encoding**: UTF-8
- **Naming**:
  - Functions/variables: `snake_case`
  - Constants: `UPPER_SNAKE_CASE`
  - Classes: `PascalCase`
  - Private/internal: `_leading_underscore`

### Type Hints
- **Required** for all new functions and edited signatures
- Use `from __future__ import annotations` at the top of each file
- Prefer `float | None` over `Optional[float]` (Python 3.10+ style)
- Example:
  ```python
  def calculate_sharpe(returns: pd.Series, annual_rf: float) -> float | None:
      ...
  ```

### Formatting & Linting
- **Formatter**: `black` (line-length=100)
- **Linter**: `ruff` (E, F, I rules enabled)
- **Always run** before committing:
  ```bash
  make format
  make lint
  ```

### Functional Programming
- **Prefer pure functions** for calculations (no side effects)
- Keep I/O (file reads, prints, network) at top-level or CLI entrypoints
- Separate data transformation from presentation logic
- Example (GOOD):
  ```python
  def calculate_cagr(monthly_returns: pd.Series) -> float:
      """Pure calculation - no I/O, no prints"""
      ...

  # CLI layer handles I/O
  def performance_command(...):
      returns = load_monthly_returns(...)
      cagr = calculate_cagr(returns)
      print(f"CAGR: {cagr:.2%}")
  ```

## Testing Guidelines

### Framework & Structure
- **Tool**: `pytest`
- **Location**: `tests/` directory mirrors source structure
- **Coverage Target**: >= 80% for changed lines
- **Run Command**: `make test` or `PYTHONPATH=. ./venv/bin/pytest -q`

### Test Strategy
- **Unit tests** for calculation logic (metrics, returns, drawdowns)
- **Integration tests** for CLI commands and report generation
- **Smoke tests** for backwards compatibility (see `test_sortino_smoke.py`)
- Use **small synthetic fixtures** (avoid dependency on large real data files)

### When to Add Tests
- **Always** when adding new metrics or calculations
- **Always** when fixing bugs (regression test)
- **Recommended** for new CLI commands or data sources
- **Optional** for minor display/formatting changes (but validate manually)

### Example Test Pattern
```python
def test_calculate_sharpe_basic():
    """Test Sharpe ratio with known inputs."""
    returns = pd.Series([0.01, 0.02, -0.01, 0.03], index=pd.period_range("2024-01", periods=4, freq="M"))
    annual_rf = 0.04
    metrics = calculate_metrics(returns, annual_rf, 2024)

    assert metrics.sharpe is not None
    assert 0 < metrics.sharpe < 5  # Sanity bounds
```

### CI/Local Parity
Before pushing:
```bash
# Fresh environment
python3 -m venv venv
./venv/bin/pip install -U pip
./venv/bin/pip install -r requirements.txt -r dev-requirements.txt

# Run tests
PYTHONPATH=. ./venv/bin/pytest -q

# Validate report generation
./venv/bin/python -m portfolio_cli report --output dist/index.html
```

Only push after local validation passes. This mirrors CI and prevents broken deployments.

## Git & Commit Guidelines

### Commit Message Format
Use [Conventional Commits](https://www.conventionalcommits.org/):
```
<type>(<scope>): <short summary>

<optional body>
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `chore`: Tooling/config (no production code change)
- `refactor`: Code restructuring (no behavior change)
- `test`: Adding/updating tests

**Examples**:
```
feat(cli): add 3-month trailing return metric
fix(benchmarks): handle timezone warnings in monthly conversion
docs: update README with Fidelity CSV workflow
chore(make): add report target
```

### Pull Request Guidelines
Every PR should include:
1. **Purpose**: What problem does this solve?
2. **Summary**: What changed and why?
3. **Testing**: How was this validated? (test output, manual verification)
4. **Sample Output**: Before/after for numerical changes
5. **Data Notes**: Any new dependencies, file format changes, or data requirements

### Pre-Commit Hook
Install to run tests automatically:
```bash
make hook
```

## Security & Data Handling

### Never Commit Sensitive Data
- **API keys**: Use `.env` (gitignored) or environment variables
- **Personal data**: Sanitize `data/valuations.json` before sharing
- **Access tokens**: SavvyTrader tokens are short-lived but still sensitive

### Data File Guidelines
- **Large datasets**: Keep in `data/` (gitignored)
- **Test fixtures**: Small synthetic samples in `tests/fixtures/`
- **Archival**: `data/import/archive/` is gitignored and safe for local storage

### .gitignore Rules
Currently ignored:
- `venv/`, `.venv/`
- `data/private/`
- `data/import/archive/`
- `data/*.db`, `data/*.sqlite3`
- `.env`
- `__pycache__/`, `.pytest_cache/`

## Agent-Specific Instructions

### Workflow for New Tasks

1. **Understand the request**
   - Read the user's question/request fully
   - If unclear, ask clarifying questions
   - State your understanding before coding

2. **Assess current state**
   - Review relevant files (use outline view first)
   - Check existing tests for context
   - Understand data flow and dependencies

3. **Plan minimal changes**
   - Identify the smallest set of files to modify
   - List functions/classes that need changes
   - Consider test coverage needs

4. **Implement**
   - Make focused edits, one logical change per file
   - Add/update type hints
   - Follow existing naming/style conventions

5. **Validate**
   - Run `make test`
   - If touching reports/CLI, run `make report` or `make run`
   - Verify behavior matches expectations

6. **Document**
   - Update docstrings if adding functions
   - Update `README.md` if changing commands/flags
   - Add devlog entry if making architectural decisions

7. **Summarize**
   - What changed (files, functions, logic)
   - How you tested it
   - Any trade-offs or follow-up items

### Common Pitfalls to Avoid

❌ **Don't**:
- Rename `sortino.py` (backwards compatibility layer for legacy scripts)
- Add heavy dependencies without justification (prefer stdlib + pandas/numpy)
- Change CLI flags/commands without updating `README.md` and help text
- Assume test behavior (run tests to confirm)
- Make broad refactors mixed with bug fixes

✅ **Do**:
- Run tests before claiming something works
- Ask when uncertain about scope or intent
- Keep changes focused and reviewable
- Update documentation alongside code changes
- Surface errors and edge cases clearly

### Debugging Workflow

When asked to debug or investigate:

1. **Reproduce** - Run the failing command/test
2. **Isolate** - Narrow down to specific function/line
3. **Hypothesize** - State what you think is wrong and why
4. **Verify** - Test your hypothesis (add print, breakpoint, or test case)
5. **Fix** - Make the minimal change to address root cause
6. **Validate** - Confirm fix resolves issue without breaking other tests

### Adding New Features

**For new metrics** (e.g., Calmar ratio, Ulcer Index):
1. Add field to `PerformanceMetrics` dataclass (`analysis.py`)
2. Implement calculation in `calculate_metrics()`
3. Update `format_portfolio_summary()` for CLI display
4. Update `_render_source_section()` in `report.py` for HTML
5. Add test case in `tests/test_sortino_smoke.py`

**For new data sources** (e.g., Interactive Brokers export):
1. Add loader function in `performance.py` (like `load_fidelity_monthly_returns`)
2. Add source to `SourceKind` enum in `cli.py`
3. Update CLI help text
4. Add test in `tests/test_cli.py`

**For new benchmarks** (e.g., emerging market ETFs):
- Edit `DEFAULT_BENCHMARKS` tuple in `benchmarks.py`
- OR document using `PORTFOLIO_BENCHMARKS` env var override

## Development Tools

### Makefile Targets (Preferred Entrypoint)

| Command | Purpose | When to Use |
|---------|---------|-------------|
| `make install` | Setup venv & deps | First time setup, after pulling deps changes |
| `make import` | Process data files | After adding files to `data/import/` |
| `make run` | Interactive shell | Ad-hoc analysis, exploration |
| `make test` | Run pytest suite | Before committing, after code changes |
| `make format` | Format with black | Before committing |
| `make lint` | Lint with ruff | Before committing |
| `make report` | Generate HTML | After display/metric changes |
| `make hook` | Install pre-commit | One-time setup |
| `make clean` | Remove artifacts | Clean slate rebuild |

### Direct Python Commands

When the Makefile isn't enough:
```bash
# Run as module (ensures correct PYTHONPATH)
./venv/bin/python -m portfolio_cli performance
./venv/bin/python -m scripts.import_latest -v

# Run tests with options
PYTHONPATH=. ./venv/bin/pytest -q
PYTHONPATH=. ./venv/bin/pytest -v --maxfail=1
PYTHONPATH=. ./venv/bin/pytest tests/test_cli.py::test_performance_mingdom

# Interactive Python for debugging
./venv/bin/python
>>> from portfolio_cli import run_portfolio_analysis
>>> result = run_portfolio_analysis()
```

## Agent Development Log

### Using `.agent/` Directory

This directory is for **development notes and agent context**:
- **devlog-YYYY-MM-DD.md**: Daily logs of decisions, experiments, and progress
- **cli-notes.md**: Specific notes on CLI evolution
- Use this space freely for tracking context across sessions

**Format** (see existing devlogs):
```markdown
# Development Log - YYYY-MM-DD

## Summary
Brief overview of what was accomplished.

## Current State
- What's working
- What's not working
- Open questions

## Next Ideas / Follow-ups
- Planned improvements
- Known issues
- Exploratory ideas
```

### When to Log

**Required**:
- After architectural changes (new module, significant refactor)
- After debugging sessions (what was the root cause?)
- When making trade-off decisions (why choose X over Y?)

**Optional**:
- Daily progress notes (if working on multi-day feature)
- Experiments that didn't work out (helps avoid repeating)
- Performance optimization attempts

## Known Issues & Limitations

See `TASKS.md` for current action items. As of latest update:
- `.env.example` references removed DB/web settings (needs cleanup)
- `savvytrader` CLI alias removed (only `mingdom` supported now)
- Some legacy scripts may depend on old `sortino.py` interface

## References for Agents

- **Sortino Ratio**: https://en.wikipedia.org/wiki/Sortino_ratio
- **Sharpe Ratio**: https://en.wikipedia.org/wiki/Sharpe_ratio
- **Pandas Period Objects**: https://pandas.pydata.org/docs/user_guide/timeseries.html#period
- **Typer CLI Framework**: https://typer.tiangolo.com/
- **yfinance API**: https://github.com/ranaroussi/yfinance

---

## Quick Reference Card

```
# Before starting work:
1. Read user request fully (answer questions before coding!)
2. Understand current architecture (use file outlines)
3. Plan minimal changes

# During implementation:
1. Follow code style (snake_case, 100 chars, type hints)
2. Keep changes focused (no drive-by refactors)
3. Add tests for new logic

# Before committing:
make format
make lint
make test
make report  # if touching display/metrics

# After task completion:
Summarize: what changed, how tested, next steps
```

**Remember**: You're a senior engineer, not a code generator. Think critically, ask questions, and make evidence-based decisions. Correctness and maintainability over speed.

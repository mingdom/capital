# AI Agent Guidelines

## Core Principles

1. **Answer questions before coding** - When asked a question, answer it. Don't jump straight to implementation.
2. **Summarize after tasks** - Briefly explain what changed and how you validated it.
3. **Make minimal changes** - Smallest diff that solves the root cause. No drive-by refactors.
4. **Evidence over assumptions** - Run tests. Don't claim it works without verification.

## Architecture

**Portfolio analytics toolkit**: Loads data (SavvyTrader JSON, Fidelity CSV) → calculates metrics (CAGR, Sharpe, Sortino, drawdown) → outputs (CLI, HTML, REPL).

```
Data Sources → performance.py → analysis.py → cli.py/report.py
                                    ↓
                               benchmarks.py (yfinance cache)
```

**Key modules**:
- `portfolio_cli/analysis.py` - Pure calculation functions
- `portfolio_cli/performance.py` - Data loading & normalization
- `portfolio_cli/cli.py` - Typer-based CLI (I/O layer)
- `benchmarks.py` - Market data fetching with persistent cache
- `sortino.py` - Legacy compatibility (don't remove)

## Standards

- **Python 3.9+**, type hints required, 100 char line length
- **Format/lint**: `make format` (black) and `make lint` (ruff) before committing
- **Tests**: `make test` (pytest), aim for >80% coverage on changed code
- **Makefile-first**: Prefer `make` targets over direct commands

## Key Rules

**Do**:
- Keep calculations pure (no I/O in `analysis.py`)
- Add tests for new metrics or data loaders
- Update README if changing CLI commands/flags
- Run `make test` before claiming success

**Don't**:
- Rename/remove `sortino.py` (backwards compatibility)
- Add heavy dependencies without justification
- Mix refactors with bug fixes
- Commit sensitive data (API tokens, personal valuations)

## Common Tasks

**Add metric**: Update `PerformanceMetrics` dataclass → `calculate_metrics()` → CLI/report display
**Add data source**: New loader in `performance.py` → add to `SourceKind` enum → update CLI help
**Add benchmark**: Edit `DEFAULT_BENCHMARKS` in `benchmarks.py` or use `PORTFOLIO_BENCHMARKS` env var

## When Stuck

- Use `.agent/devlog-YYYY-MM-DD.md` for exploratory notes
- See `docs/development-guide.md` for detailed patterns and examples
- Check existing tests for similar scenarios

---

**Trust your judgment**. You're a senior engineer - these are guidelines, not rules. Make the right call for the situation.

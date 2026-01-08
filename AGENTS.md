# Mingdom Capital AI Agent Guidelines

- repo: institutional portfolio management / analytics. report portfolio perf, stats, risks... etc.
- coding: prefer simplicity, files < 500 loc
- error handling: check for error case and exit/handle early, reduce branching
- if unclear: ask for clarification
- use make and makefile for all commands
- you have skills! check: `~/projects/dot-agents/master/skills`
- minimalistic designs, no bs/fluff
- use `bd` aka beads for task tracking

## Available Make Commands

- `make install`: Full installation (Python venv + Node modules). Use this for all dependency updates.
- `make web`: Run the web dashboard with existing data (fast).
- `make web-full`: Refresh all portfolio data and launch the web dashboard (slow).
- `make report`: Generate the stock performance report in the CLI.
- `make build`: Build the production web dashboard.
- `make test`: Run all tests (Python unit tests + Next.js unit tests + build check).
- `make lint`: Run code linting with Ruff.
- `make format`: Format code with Black.
- `make import`: Import latest portfolio data from external sources.
- `make run`: Launch the interactive CLI toolkit.
- `make clean`: Remove build artifacts and virtual environments.

## Landing the Plane (Session Completion)

**When ending a work session**, you MUST complete ALL steps below. Work is NOT complete until `git push` succeeds.

**MANDATORY WORKFLOW:**

1. **File issues for remaining work** - Create issues for anything that needs follow-up
2. **Run quality gates** (if code changed) - Tests, linters, builds
3. **Update issue status** - Close finished work, update in-progress items
4. **PUSH TO REMOTE** - This is MANDATORY:
   ```bash
   git pull --rebase
   bd sync
   git push
   git status  # MUST show "up to date with origin"
   ```
5. **Clean up** - Clear stashes, prune remote branches
6. **Verify** - All changes committed AND pushed
7. **Hand off** - Provide context for next session

**CRITICAL RULES:**
- Work is NOT complete until `git push` succeeds
- NEVER stop before pushing - that leaves work stranded locally
- NEVER say "ready to push when you are" - YOU must push
- If push fails, resolve and retry until it succeeds

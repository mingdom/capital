# Mingdom Capital AI Agent Guidelines

- repo: institutional portfolio management / analytics. report portfolio perf, stats, risks... etc.
- coding: prefer simplicity, files < 500 loc
- error handling: check for error case and exit/handle early, reduce branching
- if unclear: ask for clarification
- use make and makefile for all commands
- you have skills! check: `~/projects/dot-agents/master/skills`
- minimalistic designs, no bs/fluff
- use `bd` aka beads for task tracking
- project plans in `docs/plans/`
- never run `git push` or any unsafe `git` commands!!! `git push` deploys to production!!!

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

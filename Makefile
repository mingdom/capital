VENV=venv
PY=$(VENV)/bin/python
PIP=$(VENV)/bin/pip
BLACK=$(VENV)/bin/black
RUFF=$(VENV)/bin/ruff
PYTEST=$(VENV)/bin/pytest
.PHONY: dev install format lint test run report clean hook import web build

# ============================================================
# Main Commands (Unified)
# ============================================================

# Install everything (Python + Node)
install: $(PY)
	$(PIP) install -U pip
	$(PIP) install -r requirements.txt
	$(PIP) install -r dev-requirements.txt
	cd web && npm install

# Alias for install
dev: install

# Run web dashboard (most common command)
web: web-export
	@echo "Cleaning up port 3000 and removing Next.js lock..."
	@lsof -ti:3000 | xargs kill -9 2>/dev/null || true
	@pkill -9 -f "next dev" 2>/dev/null || true
	@rm -rf web/.next/dev/lock 2>/dev/null || true
	@sleep 1
	cd web && npm run dev

# Build production web dashboard (without GOD_MODE)
build: web-export
	@echo "Building for production (public mode - Mingdom only)..."
	@mv web/.env.local web/.env.local.bak 2>/dev/null || true
	cd web && npm run build
	@mv web/.env.local.bak web/.env.local 2>/dev/null || true

# Preview production build locally (tests public mode)
preview: build
	@echo "Starting production preview server..."
	@echo "This simulates the public deployment (no GOD_MODE)"
	@echo "Press Ctrl+C to stop"
	cd web && npx serve@latest out -l 3000

# ============================================================
# Python CLI & Analysis
# ============================================================

$(PY):
	python3 -m venv $(VENV)

format: $(BLACK)
	$(BLACK) .

$(BLACK): install ; @true

lint: $(RUFF)
	$(RUFF) check .

$(RUFF): install ; @true

test: $(PYTEST)
	PYTHONPATH=. $(PYTEST) -q

$(PYTEST): install ; @true

run: $(PY)
	$(PY) -m portfolio_cli

report: $(PY)
	$(PY) scripts/build_report.py

import: $(PY)
	$(PY) -m scripts.import_latest -v

# ============================================================
# Web Dashboard (Internal Targets)
# ============================================================

web-export: $(PY)
	$(PY) -m scripts.export_web_data -v

# ============================================================
# Utilities
# ============================================================

clean:
	rm -rf $(VENV) __pycache__ .pytest_cache .coverage htmlcov
	rm -rf web/.next web/node_modules web/out

hook:
	chmod +x scripts/pre-commit.sh
	ln -sf ../../scripts/pre-commit.sh .git/hooks/pre-commit
	@echo "Installed Git pre-commit hook."

# ============================================================
# Help
# ============================================================

help:
	@echo "Mingdom Capital - Portfolio Analytics"
	@echo ""
	@echo "Common Commands:"
	@echo "  make install    Install all dependencies (Python + Node)"
	@echo "  make web        Run web dashboard (exports data + starts dev server)"
	@echo "  make build      Build production web dashboard"
	@echo "  make preview    Preview production build locally (public mode)"
	@echo "  make test       Run Python tests"
	@echo "  make run        Run CLI tool"
	@echo ""
	@echo "Development:"
	@echo "  make format     Format code with black"
	@echo "  make lint       Lint code with ruff"
	@echo "  make import     Import latest data"
	@echo "  make report     Generate HTML report"
	@echo ""
	@echo "Utilities:"
	@echo "  make clean      Remove build artifacts"
	@echo "  make hook       Install git pre-commit hook"

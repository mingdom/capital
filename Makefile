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

# Run web dashboard with EXISTING data (fast)
web:
	@echo "Cleaning up port 3000 and removing Next.js lock..."
	@lsof -ti:3000 | xargs kill -9 2>/dev/null || true
	@pkill -9 -f "next dev" 2>/dev/null || true
	@rm -rf web/.next/dev/lock 2>/dev/null || true
	@sleep 1
	cd web && npm run dev

# Run web dashboard with TOTAL REFRESH (slow)
web-full: web-export web

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
	$(RUFF) check --fix .

$(RUFF): install ; @true

test: $(PYTEST)
	@echo "Running Python tests..."
	PYTHONPATH=. $(PYTEST) -q
	@echo ""
	@echo "Running Next.js unit tests..."
	cd web && npm run test
	@echo ""
	@echo "Running Next.js build check..."
	cd web && npm run build

$(PYTEST): install ; @true

run: $(PY)
	$(PY) -m portfolio_cli

import: $(PY)
	$(PY) -m scripts.import_latest -v
	@echo ""
	@echo "Exporting data for web dashboard..."
	@$(MAKE) web-export

report: $(PY)
	$(PY) -m portfolio_cli report stock-performance

# ============================================================
# Web Dashboard (Internal Targets)
# ============================================================

web-export: $(PY)
	$(PY) -m scripts.export_web_data -v
	$(PY) -m scripts.export_holdings_performance

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
	@echo "Main Commands:"
	@echo "  make install    Install all dependencies (Python + Node)"
	@echo "  make web        Run web dashboard with existing data (fast)"
	@echo "  make web-full   Refresh all data and run dashboard (slow)"
	@echo "  make report     Generate stock performance report in CLI"
	@echo "  make build      Build production web dashboard"
	@echo "  make test       Run all tests (Python + Next.js + build)"
	@echo "  make run        Run interactive CLI tool"
	@echo ""
	@echo "Development:"
	@echo "  make format     Format code with black"
	@echo "  make lint       Lint code with ruff"
	@echo "  make import     Import latest data from external sources"
	@echo ""
	@echo "Utilities:"
	@echo "  make clean      Remove build artifacts and virtualenv"
	@echo "  make hook       Install git pre-commit hook"

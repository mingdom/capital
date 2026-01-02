VENV=venv
PY=$(VENV)/bin/python
PIP=$(VENV)/bin/pip
BLACK=$(VENV)/bin/black
RUFF=$(VENV)/bin/ruff
PYTEST=$(VENV)/bin/pytest
.PHONY: dev install format lint test run report clean hook import web-install web-dev web-build web-export

$(PY):
	python3 -m venv $(VENV)

install: $(PY)
	$(PIP) install -U pip
	$(PIP) install -r requirements.txt
	$(PIP) install -r dev-requirements.txt

dev: install

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

clean:
	rm -rf $(VENV) __pycache__ .pytest_cache .coverage htmlcov

hook:
	chmod +x scripts/pre-commit.sh
	ln -sf ../../scripts/pre-commit.sh .git/hooks/pre-commit
	@echo "Installed Git pre-commit hook."

# ============================================================
# Web Dashboard (Next.js)
# ============================================================

web-install:
	cd web && npm install

web-dev: web-export
	@echo "Cleaning up port 3000 and removing Next.js lock..."
	@lsof -ti:3000 | xargs kill -9 2>/dev/null || true
	@pkill -9 -f "next dev" 2>/dev/null || true
	@rm -rf web/.next/dev/lock 2>/dev/null || true
	@sleep 1
	cd web && npm run dev

web-build: web-export
	cd web && npm run build

web-export: $(PY)
	$(PY) -m scripts.export_web_data -v

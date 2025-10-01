VENV=venv
PY=$(VENV)/bin/python
PIP=$(VENV)/bin/pip
BLACK=$(VENV)/bin/black
RUFF=$(VENV)/bin/ruff
PYTEST=$(VENV)/bin/pytest

.PHONY: dev install format lint test run analyze run-benchmarks report clean hook web import db-init

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

analyze: $(PY)
	$(PY) -m portfolio_cli analyze

run-benchmarks: $(PY)
	$(PY) -m portfolio_cli analyze --benchmarks

report: $(PY)
	$(PY) scripts/build_report.py

web: $(PY)
	$(PY) -m portfolio_cli web

import: $(PY)
	$(PY) scripts/import_latest.py -v

db-init: $(PY)
	@if [ -z "$$MINGDOM_DB_PASSPHRASE" ]; then \
		echo "MINGDOM_DB_PASSPHRASE is not set. You may be prompted if run outside Make."; \
	fi
	$(PY) scripts/db_tools.py init -v || true

clean:
	rm -rf $(VENV) __pycache__ .pytest_cache .coverage htmlcov

hook:
	chmod +x scripts/pre-commit.sh
	ln -sf ../../scripts/pre-commit.sh .git/hooks/pre-commit
	@echo "Installed Git pre-commit hook."

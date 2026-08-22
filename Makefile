ifeq ($(OS),Windows_NT)
VENV_BIN=.venv/Scripts
PYTHON=$(VENV_BIN)/python.exe
RUN_PREFIX=set PYTHONPATH=src&&
else
VENV_BIN=.venv/bin
PYTHON=$(VENV_BIN)/python
RUN_PREFIX=PYTHONPATH=src
endif

bootstrap:
	python scripts/bootstrap.py
install:
	$(PYTHON) -m pip install -r requirements.txt
test:
	$(PYTHON) -m pytest -q
lint:
	$(PYTHON) -m ruff check src tests
run:
	$(RUN_PREFIX) $(PYTHON) -m multi_agent_team.main

compose-up:
	docker-compose up -d postgres

compose-down:
	docker-compose down

migrate-alembic:
	# Run alembic upgrade head using MONITORING_DATABASE_URL or DATABASE_URL
	MONITORING_DATABASE_URL=$${MONITORING_DATABASE_URL:-} alembic upgrade head

migrate-runner:
	# Run the simple SQL runner (fallback)
	$(PYTHON) -m src.multi_agent_team.monitoring.migrate

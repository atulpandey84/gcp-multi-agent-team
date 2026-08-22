PYTHON=.venv/bin/python
install:
	$(PYTHON) -m pip install -r requirements.txt
test:
	$(PYTHON) -m pytest -q
lint:
	$(PYTHON) -m ruff check src tests
run:
	PYTHONPATH=src $(PYTHON) -m multi_agent_team.main

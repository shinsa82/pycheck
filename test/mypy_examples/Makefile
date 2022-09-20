OPTS=--strict --pretty

all: mypy_sato run_sato

mypy_sato:
	@echo "## typechecking sato_rt.py..."
	mypy $(OPTS) sato.py
	mypy $(OPTS) sato_rt.py

run_sato:
	@echo "## running sato_rt.py..."
	python sato_rt.py

.PHONY: clean build test

TEST_TARGET=test/valid

install:
	poetry install

check-update:
	poetry self update
	poetry show -l

lint:
	poetry run isort -V
	poetry run isort src test

test:
	poetry run pytest --capture=tee-sys --log-cli-level=INFO $(TEST_TARGET)

test-generator:
	poetry run pytest --show-capture=no -rA test/generator

test-generator-verbose:
	poetry run pytest --log-level=NOTSET --disable-warnings -rA test/generator

build:
	poetry build

# example
tag:
	git tag -a -m"tag message" v0.4.0

clean:
	find test src/pycheck -name "__pycache__" | xargs rm -rf
	find test src/pycheck -name ".mypy_cache" | xargs rm -rf
	-rm dist/*

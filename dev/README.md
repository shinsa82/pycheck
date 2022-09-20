# dev

Documents for research and development of PyCheck.

# 2022-01-23

In `dev` branch,

Implementing generator based on FLOPS paper.
- Created new package pycheck.generator under [src/generator](../src/generator).
- It contains its original parser and generator.
- Test codes are located in [test/generator](../test/generator).

## How to initialize 
- `poetry install`
- run `pip list` and check if `pytest` and `pycheck` are shown in the package list.

## Sometimes
- `poetry self update`
- `poetry show -l` or `poetry show -o`. If there any update, `poetry update`

## How to test
- `pytest test/generator` or specifically `pytest test/generator/test_first.py`
- You may need some options for test:
  - If you want stdout to be shown on terminal, `pytest ... --capture=tee-sys`.
  - If you want log messages to be shown on terminal, `pytest ... --log-cli-level=<LOGLEVEL>`.
  - If you want to ignore DeprecationWarning, `pytest ... -Wignore::DeprecationWarning` (note that two colons, not single) or entirely disable warning capture plugin by `pytest ... -p no:warnings`.
- Use `make test-generator`, `make test-generator-verbose`.

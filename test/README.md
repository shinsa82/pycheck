# How to Test (on 27 Sep. 2022)

## Files

- [subtests](./sub_tests/) tests for components
- [test_main.py]

`pytest test/valid`

## Show output to stdout/stderr

`pytest --capture=tee-sys test/valid`

## Show summary of test status

`pytest -rA test/valid`

## Show logging output

`pytest --log-cli-level=<level> test/valid`

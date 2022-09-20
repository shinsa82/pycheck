# How to Test (on 12 Jul. 2021)

Only directory `valid` contains valid tests for the latest code.
(Tests in other directories are outdated and will be removed in future)

`pytest test/valid`

## Show output to stdout/stderr

`pytest --capture=tee-sys test/valid`

## Show summary of test status

`pytest -rA test/valid`

## Show logging output

`pytest --log-cli-level=<level> test/valid`

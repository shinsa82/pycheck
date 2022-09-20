# Installing PyCheck

**Requirements: since PyCheck uses the latest type annotation mechanisms, Python 3.9+ is required.**

If you use pip,

```bash
$ pip install git+https://github.ibm.com/SHINSA/pycheck@dev
```

If you use Pipenv,

```bash
$ pipenv install [-d] git+https://github.ibm.com/SHINSA/pycheck@dev
```

If you use poetry:

```bash
$ poetry add [-D] git+https://github.ibm.com/SHINSA/pycheck@dev
```

## Checking Install

You can check the version of PyCheck that you installed like this:

```bash
python -m pycheck
```

If you use Pipenv or poetry, 

```bash
$ pipenv run python -m pycheck
# or
# $ poetry run python -m pycheck
PyCheck version 0.4.0.dev2
```


## Update

Maybe `pip/pipenv/poetry update` works?


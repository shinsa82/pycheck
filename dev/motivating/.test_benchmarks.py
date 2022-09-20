from pycheck import check

from .dataframe import preprocess_pycheck


def test_preprocess():
    assert check(preprocess_pycheck)

"test of Result dataclass."
from pycheck import Result


def test_init_missing():
    "test field value right after initialization"
    res: Result = Result()
    assert res.well_typed is None


def test_init_true():
    "test field value right after initialization"
    res: Result = Result(well_typed=True)
    assert res.well_typed

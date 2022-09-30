"""
Tests Config and Context.
"""
from pycheck import Config, Context


def test_config_default():
    config = Config()
    assert config.max_iteration == 100
    assert config.max_tries == 10000
    assert config.seed_nbits == 64
    assert config.seed is None
    assert not config.stat


def test_config_non_default():
    config = Config(max_iteration=200, max_tries=int(1e5),
                    seed_nbits=32, seed=10000, stat=True)
    assert config.max_iteration == 200
    assert config.max_tries == 100000
    assert config.seed_nbits == 32
    assert config.seed == 10000
    assert config.stat


def test_config_str():
    config = Config(max_iteration=200)
    assert str(
        config) == "Config(max_iteration=200, max_tries=10000, seed_nbits=64, seed=None, stat=False)"


def test_context():
    ctx: Context = Context({'x': int, 'y': bool})
    assert ctx == {'x': int, 'y': bool}

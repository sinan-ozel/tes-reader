import decorator
import pytest
import os
from configparser import ConfigParser
from tes_reader import ElderScrollsFileReader

config = ConfigParser()
config.read('test.ini')

test_filename = os.path.join(config['Skyrim']['Folder'],
                             'Data',
                             'Skyrim.esm')

marker = object()

def _memoize(func, *args, **kw):
    """Memoization helper to cache function's return value as an attribute of this function."""
    cache = getattr(func, '_cache', marker)
    if cache is marker:
        func._cache = func(*args, **kw)
        return func._cache
    else:
        return cache


def memoize(f):
    """Decorator which caches the return value of the function."""
    return decorator.decorator(_memoize, f)

@pytest.fixture
@memoize
def test_file(scope='session'):
    test_file = ElderScrollsFileReader(test_filename)
    return test_file


import pytest
import os
from configparser import ConfigParser
from tes_reader import BethesdaSoftwareArchiveReader

config = ConfigParser()
config.read('test.ini')

test_filename = os.path.join(config['Skyrim']['Folder'],
                             'Data',
                             config['BSA']['File'])

def test_open_file():
    with BethesdaSoftwareArchiveReader(test_filename) as test_file:
        print('First four characters in file: ', test_file[0:4])
        assert test_file[0:4] == b'BSA\x00'

@pytest.fixture
def test_file():
    with BethesdaSoftwareArchiveReader(test_filename) as test_file:
        yield test_file

@pytest.mark.depends(on=['test_open_file'])
def test_bsa_version(test_file):
    print('BSA Version:', test_file.version)
    assert test_file.version == 105


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


def test_calculate_hash():
    file_name = 'Strings'
    assert BethesdaSoftwareArchiveReader._calculate_hash(file_name) == 5594201102607673203

    file_name = 'interface\\controls\\orbis'
    assert BethesdaSoftwareArchiveReader._calculate_hash(file_name) == 17048172040925243763

    file_name = 'meshes\\creationclub\\_shared\\dungeons\\root'
    assert BethesdaSoftwareArchiveReader._calculate_hash(file_name) == 16813576048203100020


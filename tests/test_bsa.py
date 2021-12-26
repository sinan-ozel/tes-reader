import pytest
import os
from configparser import ConfigParser
from tes_reader import BethesdaSoftwareArchiveReader

config = ConfigParser()
config.read('test.ini')

test_filename = os.path.join(config['Skyrim']['Folder'],
                             'Data',
                             'Skyrim - Interface.bsa')

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

def test_get_folder():
    with BethesdaSoftwareArchiveReader(test_filename) as test_bsa_file:
        folder = test_bsa_file['Strings']
        assert isinstance(folder, test_bsa_file.Folder)
        assert folder.name == 'strings'

def test_missing_folder():
    with pytest.raises(FileNotFoundError):
        with BethesdaSoftwareArchiveReader(test_filename) as test_bsa_file:
            test_bsa_file['NonExistingFolder']

def test_get_file_contents():
    with BethesdaSoftwareArchiveReader(test_filename) as test_bsa_file:
        file_bytes = test_bsa_file['Strings', 'Skyrim_English.dlstrings']
        assert isinstance(file_bytes, bytes)
        number_of_entries = int.from_bytes(file_bytes[0:4], 'little', signed=False)
        assert number_of_entries == 2686
        total_length = int.from_bytes(file_bytes[4:8], 'little', signed=False)
        assert total_length == 2421653

def test_missing_file():
    with pytest.raises(FileNotFoundError):
        with BethesdaSoftwareArchiveReader(test_filename) as test_bsa_file:
            test_bsa_file['Strings', 'NonExistingFile.dlstrings']

def test_get_file_contents_with_index_string():
    with BethesdaSoftwareArchiveReader(test_filename) as test_bsa_file:
        file_bytes = test_bsa_file['Strings\\Skyrim_English.dlstrings']
        assert isinstance(file_bytes, bytes)
        number_of_entries = int.from_bytes(file_bytes[0:4], 'little', signed=False)
        assert number_of_entries == 2686
        total_length = int.from_bytes(file_bytes[4:8], 'little', signed=False)
        assert total_length == 2421653

def test_get_file_contents_with_index_string_and_forward_slash():
    with BethesdaSoftwareArchiveReader(test_filename) as test_bsa_file:
        file_bytes = test_bsa_file['Strings\\Skyrim_English.dlstrings']
        assert isinstance(file_bytes, bytes)
        number_of_entries = int.from_bytes(file_bytes[0:4], 'little', signed=False)
        assert number_of_entries == 2686
        total_length = int.from_bytes(file_bytes[4:8], 'little', signed=False)
        assert total_length == 2421653

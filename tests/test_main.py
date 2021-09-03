import pytest
import os
from configparser import ConfigParser
from tes_reader import Reader

config = ConfigParser()
config.read('test.ini')

test_filename = os.path.join(config['ESM']['Folder'], 
                             'Data', 
                             config['ESM']['File'])

def test_open_file():
    with Reader(test_filename) as test_file:
        print('First four characters in file: ', test_file[0:4])
        assert test_file[0:4] == b'TES4'

def test_record_types():
    with Reader(test_filename) as test_file:
        print('Records in file:', test_file.record_types)
        assert {'EDID'} <= test_file.record_types


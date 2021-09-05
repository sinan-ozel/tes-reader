import pytest
import os
from configparser import ConfigParser
from tes_reader import Reader
from tes_reader.record_types import NPC
from tes_reader import is_type

config = ConfigParser()
config.read('test.ini')

test_filename = os.path.join(config['ESM']['Folder'],
                             'Data',
                             config['ESM']['File'])

# See here for expected record counts:
# https://en.uesp.net/wiki/Skyrim_Mod:Mod_File_Format/Raw_Data

def test_open_file():
    with Reader(test_filename) as test_file:
        print('First four characters in file: ', test_file[0:4])
        assert test_file[0:4] == b'TES4'

def test_record_types():
    with Reader(test_filename) as test_file:
        print('Records in file:', test_file.record_types)
        assert {'TREE', 'BOOK', 'NPC_'} <= test_file.record_types
        for record_type in test_file.record_types:
            print(record_type)
            assert is_type(record_type)

def test_access_records_by_type():
    with Reader(test_filename) as test_file:
        print(f"NPC Count: {len(test_file['NPC_'])}")
        assert len(test_file['NPC_']) > 5000
        for npc_record in test_file['NPC_']:
            assert npc_record.form_id.startswith('0x')

def test_access_record_by_form_id_as_string():
    with Reader(test_filename) as test_file:
        form_id = '0x13bab'  # Ysolda
        assert test_file[form_id].form_id == form_id

def test_access_record_by_form_id_as_integer():
    with Reader(test_filename) as test_file:
        form_id = int('0x13bab', 16)  # Ysolda
        assert test_file[form_id].form_id == hex(form_id)

def test_load_npc_record_content():
    with Reader(test_filename) as test_file:
        form_id = int('0x13bab', 16)  # Ysolda
        record = test_file[form_id]
        assert record.type == 'NPC_'
        test_file.load_record_content(record)
        npc = NPC(test_file[record])
        assert isinstance(npc.content, bytes)
        assert npc.is_female == True
        assert npc.editor_id == "Ysolda"
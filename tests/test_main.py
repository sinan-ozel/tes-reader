import pytest
import os
from configparser import ConfigParser
from tes_reader import ElderScrollsFileReader
from tes_reader.record_types import NPC
from tes_reader import is_type

config = ConfigParser()
config.read('test.ini')

test_filename = os.path.join(config['Skyrim']['Folder'],
                             'Data',
                             'Skyrim.esm')

# See here for expected record counts:
# https://en.uesp.net/wiki/Skyrim_Mod:Mod_File_Format/Raw_Data

def test_open_file():
    with ElderScrollsFileReader(test_filename) as test_file:
        print('First four characters in file: ', test_file[0:4])
        assert test_file[0:4] == b'TES4'

@pytest.mark.depends(on=['test_open_file'])
def test_record_types(test_file):
    print('Records in file:', test_file.record_types)
    assert {'TREE', 'BOOK', 'NPC_'} <= test_file.record_types
    for record_type in test_file.record_types:
        print(record_type)
        assert is_type(record_type)

@pytest.mark.depends(on=['test_open_file'])
def test_access_records_by_type(test_file):
    print(f"NPC Count: {len(test_file['NPC_'])}")
    assert len(test_file['NPC_']) > 5000
    for npc_record in test_file['NPC_']:
        assert npc_record.form_id.modindex == 0

@pytest.mark.depends(on=['test_open_file'])
def test_access_record_by_form_id_as_string(test_file):
    form_id = '0x13bab'  # Ysolda
    assert str(test_file[form_id].form_id) == form_id

@pytest.mark.depends(on=['test_open_file'])
def test_access_record_by_form_id_as_integer(test_file):
    form_id = int('0x13bab', 16)  # Ysolda
    assert int(test_file[form_id].form_id) == form_id

@pytest.mark.depends(on=['test_open_file'])
def test_load_npc_record_content(test_file):
    form_id = int('0x13bab', 16)  # Ysolda
    record = test_file[form_id]
    assert record.type == 'NPC_'
    test_file.load_record_content(record)
    npc = NPC(test_file[record])
    assert isinstance(npc.content, bytes)
    assert npc.is_female == True
    assert npc.editor_id == "Ysolda"

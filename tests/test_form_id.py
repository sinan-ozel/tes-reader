
from tes_reader import FormId

def test_form_id_basic():
    form_id = FormId(b'\xd7\x00\x00\x01')
    assert form_id.modindex == 1
    assert str(form_id) == '0xd7'

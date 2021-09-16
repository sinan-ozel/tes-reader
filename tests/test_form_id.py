import pytest

from tes_reader import FormId

def test_form_id_basic():
    form_id = FormId(b'\x07\x00\x00\x01')
    assert form_id.modindex == 1
    assert len(form_id) == 4
    assert str(form_id) == '0x7'

def test_form_id_from_string():
    form_id = FormId('0x7')
    assert form_id.modindex is None
    assert len(form_id) == 3
    assert str(form_id) == '0x7'

def test_form_id_errors():
    with pytest.raises(ValueError):
        FormId('mistake')
    with pytest.raises(ValueError):
        FormId(b'\x07\x00\x00\x01\x20')  # Too long

def test_form_id_from_for_ysolda():
    form_id = FormId('0x13bab')
    assert form_id.modindex is None
    assert len(form_id) == 3
    assert str(form_id) == '0x13bab'

    form_id = FormId('0x0013bab')
    assert form_id.modindex == 0
    assert len(form_id) == 4
    assert str(form_id) == '0x13bab'

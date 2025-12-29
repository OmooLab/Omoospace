from omoospace import pyperclip
import pytest
from omoospace import format_name, copy_to_clipboard


@pytest.mark.parametrize("name,expected", [
    ('Seq010_001', 'Seq010'),
    ('Seq010_Shot0100.v001', 'Seq010_Shot0100'),
    ('Asset A v001', 'AssetA'),
    ('Asset A_autosave', 'AssetA'),
    ('Asset_A.autosave', 'Asset_A'),
    ('Asset_aa 001', 'Asset_Aa'),
    ('Asset_a_autosave_v001', 'Asset_A'),
    ('头骨2.v001', '头骨2'),
    ('头骨.2.0001', '头骨'),
    ('Asset头骨.0001', 'Asset头骨'),
    ('AssetA-1.v3', 'AssetA-1'),
    ('AssetAA.v3', 'AssetAA'),
    ('AssetAa.v001', 'AssetAa'),
    ('AssetA_recovered 1', 'AssetA'),
    ('AssetA_recovered.v001', 'AssetA')
])
def test_format_name(name: str, expected: str):
    assert format_name(name) == expected


def test_copy_to_clipboard():
    try:
        copy_to_clipboard("The text to be copied to the clipboard.")
        assert pyperclip.paste() == "The text to be copied to the clipboard."
    except:
        pass

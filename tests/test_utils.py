import pyperclip
import pytest
from omoospace import format_name, copy_to_clipboard


@pytest.mark.parametrize("name,expected", [
    ('SQ010_SH0100_001', 'SQ010_SH0100'),
    ('SQ010_SH0100_v001', 'SQ010_SH0100'),
    ('Asset A v001', 'AssetA'),
    ('Asset A autosave', 'AssetA'),
    ('Asset_A autosave', 'Asset_A'),
    ('Asset_a_autosave_001', 'Asset_A'),
    ('Asset_a_autosave_v001', 'Asset_A'),
    ('头骨_v001', 'TouGu'),
    ('头骨_0001', 'TouGu'),
    ('Asset头骨_0001', 'AssetTouGu'),
    ('AssetA_bak3', 'AssetA'),
    ('AssetA_bak001', 'AssetA'),
    ('AssetA_recovered', 'AssetA'),
    ('AssetA_recovered_bak1', 'AssetA'),
    ('backup', ''),
])
def test_format_name(name: str, expected: str):
    assert format_name(name) == expected


@pytest.mark.skipif(not pyperclip.is_available(), reason="Clipboard unavailable.")
def test_copy_to_clipboard():

    copy_to_clipboard("The text to be copied to the clipboard.")
    assert pyperclip.paste() == "The text to be copied to the clipboard."



import pytest
from omoospace.utils import format_name


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
])
def test_format_name(name: str, expected: str):
    assert format_name(name) == expected


def test_set():
    assert set(['a']) == set('a')
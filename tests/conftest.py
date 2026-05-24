import pytest
from omoospace import Opath, make_path


@pytest.fixture()
def mini_omoos_path():
    omoos_path = Opath("temp", "MiniProject").resolve()
    # delete omoospace dir if exists.
    if omoos_path.exists():
        omoos_path.remove_all()

    # create the test omoospace.
    make_path(
        "contents/",
        {
            "OMOOSPACE.md": """---
description: A mini omoospace.
---
""",
        },
        under=omoos_path,
    )
    yield omoos_path


@pytest.fixture()
def empty_omoos_path():
    omoos_path = Opath("temp", "EmptyProject").resolve()
    # delete omoospace dir if exists.
    if omoos_path.exists():
        omoos_path.remove_all()

    # create the test omoospace.
    make_path(
        "contents/",
        "subspaces/",
        "references/",
        {
            "OMOOSPACE.md": """---
description: An empty omoospace.
---
""",
        },
        under=omoos_path,
    )

    yield omoos_path


@pytest.fixture(autouse=True)
def clean_temp():
    yield
    Opath("temp").remove_children()

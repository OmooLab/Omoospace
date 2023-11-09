import pytest
import shutil
from pathlib import Path
from omoospace.utils import rm_children
from tests.helper import write_file_content


@pytest.fixture()
def mini_omoos_path():
    omoos_path = Path("temp", "MiniProject").resolve()
    # delete omoospace dir if exists.
    if (omoos_path.exists()):
        shutil.rmtree(omoos_path, ignore_errors=True)

    # create the test omoospace.
    omoos_path.mkdir(parents=True, exist_ok=True)
    Path(omoos_path, "Contents").mkdir(parents=True, exist_ok=True)
    Path(omoos_path, "SourceFiles").mkdir(parents=True, exist_ok=True)
    Path(omoos_path, "ExternalData").mkdir(parents=True, exist_ok=True)
    write_file_content(
        ("Omoospace.yml", """
        name: Mini
        description: A mini omoospace.
        """),
        root_dir=omoos_path)
    yield omoos_path

    # # delete omoospcae after test
    # if (omoos_path.exists()):
    #     shutil.rmtree(omoos_path, ignore_errors=True)


@pytest.fixture()
def empty_omoos_path():
    omoos_path = Path("temp", "EmptyProject").resolve()
    # delete omoospace dir if exists.
    if (omoos_path.exists()):
        shutil.rmtree(omoos_path, ignore_errors=True)

    # create the test omoospace.
    omoos_path.mkdir(parents=True, exist_ok=True)
    Path(omoos_path, "Contents").mkdir(parents=True, exist_ok=True)
    Path(omoos_path, "SourceFiles").mkdir(parents=True, exist_ok=True)
    Path(omoos_path, "ExternalData").mkdir(parents=True, exist_ok=True)
    Path(omoos_path, "Reference").mkdir(parents=True, exist_ok=True)
    Path(omoos_path, "StagedData").mkdir(parents=True, exist_ok=True)
    write_file_content(
        ("Omoospace.yml", """
        name: Empty
        description: An empty omoospace.
        """),
        root_dir=omoos_path
    )

    yield omoos_path

    # # delete omoospcae after test
    # if (omoos_path.exists()):
    #     shutil.rmtree(omoos_path, ignore_errors=True)


@pytest.fixture(autouse=True)
def clean_temp():
    yield
    rm_children('temp')

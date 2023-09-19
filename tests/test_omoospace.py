import pytest
import shutil
from pathlib import Path
from omoospace.omoospace import Omoospace

f_omoospace_path = Path("temp", "MyProject").resolve()
f_omoospace_files = [
    "Contents/Test_001.fbx",
    "Contents/Test_002.fbx",
    "Contents/Test_003.fbx",
    "SourceFiles/TestAssetA.blend",
    "SourceFiles/TestAssetB.blend",
    "SourceFiles/TestAssetC.blend",
]
f_omoospace_filepaths = [Path(f_omoospace_path, file)
                         for file in f_omoospace_files]


@pytest.fixture(scope="module")
def f_omoospace():
    omoospace = Omoospace.create(
        name="my project",
        create_dir="temp",
        info={
            "description": "An omoospace for test"
        },
        structure=None,
        reveal_when_success=False
    )

    for file in f_omoospace_filepaths:
        file.parent.mkdir(parents=True, exist_ok=True)
        with file.open('w') as file:
            pass
    yield omoospace

    # delete omoospcae after test
    if (f_omoospace_path.exists()):
        shutil.rmtree(f_omoospace_path)


@pytest.mark.dependency()
def test_create(f_omoospace: Omoospace):
    assert f_omoospace.root_path == f_omoospace_path


@pytest.mark.dependency(depends=["test_create"])
def test_show(f_omoospace: Omoospace):
    f_omoospace.show_summary(
        output_dir = Path(f_omoospace_path, "StagedData")
    )
    assert Path(f_omoospace_path, "StagedData","Structure.html").is_file()


@pytest.mark.dependency(depends=["test_create"])
def test_export(f_omoospace: Omoospace):
    f_omoospace.export_package(
        items=f_omoospace_filepaths,
        export_dir=Path(f_omoospace_path, "StagedData"),
        name="asset",
        info={
            "description": "A asset package",
            "version": "0.1.0"
        },
        reveal_when_success=False
    )
    exported_package_path = Path(f_omoospace_path, "StagedData", "Asset")
    exported_files = [Path(exported_package_path, file)
                      for file in f_omoospace_filepaths]
    assert exported_package_path.is_dir()
    for exported_file in exported_files:
        assert exported_file.is_file()


@pytest.mark.dependency(depends=["test_create"])
def test_import(f_omoospace: Omoospace):
    f_omoospace.import_package(
        import_dir=Path(f_omoospace_path, "StagedData", "Asset"),
        reveal_when_success=False
    )
    assert len(f_omoospace.packages.items()) == 1

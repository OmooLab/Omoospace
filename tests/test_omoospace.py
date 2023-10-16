import pytest
import shutil
from pathlib import Path
from omoospace.omoospace import Omoospace
from omoospace.utils import find_first_index


class Fixture():
    FILES = [
        "Contents/Test_001.fbx",
        "Contents/Test_002.fbx",
        "Contents/Test_003.fbx",
        "SourceFiles/TestAssetA.blend",
        "SourceFiles/TestAssetB.blend",
        "SourceFiles/TestAssetC.blend",
    ]

    def __init__(self, root_dir) -> None:
        self.omoospace_path = Path(root_dir, "MyProject").resolve()
        if (self.omoospace_path.exists()):
            shutil.rmtree(fixture.omoospace_path, ignore_errors=True)
            
        self.filepaths = [Path(self.omoospace_path, file)
                          for file in self.FILES]

        self.omoospace = Omoospace.create(
            name="my project",
            create_dir=root_dir,
            info={
                "description": "An omoospace for test"
            },
            reveal_when_success=False
        )

        for file in self.filepaths:
            file.parent.mkdir(parents=True, exist_ok=True)
            with file.open('w') as file:
                pass


@pytest.fixture(scope="module")
def fixture():

    fixture = Fixture("temp")
    yield fixture

    # delete omoospcae after test
    if (fixture.omoospace_path.exists()):
        shutil.rmtree(fixture.omoospace_path, ignore_errors=True)


@pytest.mark.dependency()
def test_create(fixture: Fixture):
    assert fixture.omoospace.root_path == fixture.omoospace_path


@pytest.mark.dependency(depends=["test_create"])
def test_set_subspace(fixture: Fixture):
    omoospace = fixture.omoospace
    EP001_path = omoospace.set_subspace(
        subspace="EP001",
        parent_dir=omoospace.sourcefiles_path,
        reveal_when_success=False
    )
    assert Path(omoospace.sourcefiles_path, "EP001").is_dir()
    assert Path(omoospace.sourcefiles_path, "EP001", "Subspace.yml").is_file()

    omoospace.set_subspace(
        subspace="EP001_SQ010",
        parent_dir=Path(EP001_path),
        reveal_when_success=False
    )
    omoospace.set_subspace(
        subspace="SQ020",
        parent_dir=Path(EP001_path),
        reveal_when_success=False
    )
    assert Path(EP001_path, "SQ020").is_dir()
    assert Path(EP001_path, "SQ020", "Subspace.yml").is_file()


@pytest.mark.dependency(depends=["test_create"])
def test_set_process(fixture: Fixture):
    omoospace = fixture.omoospace
    omoospace.set_process(
        process={
            "Modeling": None,
            "Texturing": None,
            "Shading": None
        },
        parent_dir=omoospace.sourcefiles_path,
        reveal_when_success=False
    )
    assert Path(omoospace.sourcefiles_path, "Modeling").is_dir()
    assert Path(omoospace.sourcefiles_path, "Texturing").is_dir()
    assert Path(omoospace.sourcefiles_path, "Shading").is_dir()


@pytest.mark.dependency(depends=["test_create"])
def test_set_creator(fixture: Fixture):
    omoospace = fixture.omoospace
    omoospace.set_creator(
        {
            "name": "manan",
            "email": "x@x.com",
            "role": "Owner"
        }
    )
    assert find_first_index(omoospace.creators, "name", "manan") >= 0


@pytest.mark.dependency(depends=["test_create"])
def test_set_software(fixture: Fixture):
    omoospace = fixture.omoospace
    omoospace.set_software(
        {
            "name": "Blender",
            "version": "3.6"
        }
    )
    assert find_first_index(omoospace.softwares, "name", "Blender") >= 0


@pytest.mark.dependency(depends=["test_create"])
def test_set_work(fixture: Fixture):
    omoospace = fixture.omoospace
    omoospace.set_work(
        {
            "name": "Video",
            "paths": fixture.filepaths
        }
    )
    assert find_first_index(omoospace.works, "name", "Video") >= 0


@pytest.mark.dependency(depends=["test_create"])
def test_show(fixture: Fixture):
    omoospace = fixture.omoospace
    omoospace.show_summary(
        output_dir=omoospace.stageddata_path,
        reveal_when_success=False
    )
    assert Path(omoospace.stageddata_path, "Structure.html").is_file()


@pytest.mark.dependency(depends=["test_create"])
def test_export(fixture: Fixture):
    omoospace = fixture.omoospace
    omoospace.export_package(
        items=fixture.filepaths,
        export_dir=omoospace.stageddata_path,
        name="asset",
        info={
            "description": "A asset package",
            "version": "0.1.0"
        },
        reveal_when_success=False
    )
    exported_package_path = Path(omoospace.stageddata_path, "Asset")
    exported_files = [Path(exported_package_path, file)
                      for file in fixture.filepaths]
    assert exported_package_path.is_dir()
    for exported_file in exported_files:
        assert exported_file.is_file()


@pytest.mark.dependency(depends=["test_create", "test_export"])
def test_import(fixture: Fixture):
    omoospace = fixture.omoospace
    omoospace.import_package(
        import_dir=Path(omoospace.stageddata_path, "Asset"),
        reveal_when_success=False
    )
    assert len(omoospace.imported_packages) == 1

import pytest
from omoospace import (
    Omoospace,
    create_omoospace,
    Opath,
    make_path,
)


def test_create_omoospace():
    omoospace = create_omoospace(
        "new project", under="temp", brief="A new project for testing."
    )

    assert omoospace.root_dir == Opath("temp", "NewProject").resolve()
    assert omoospace.brief == "A new project for testing."
    assert len(omoospace.subspaces) == 0

    with pytest.raises(ValueError):
        create_omoospace("%$", under="temp")


def test_create_omoospace():
    omoospace = create_omoospace(
        "new project",
        under="temp",
        brief="A new project for testing.",
        contents_dir="Content",
        subspaces_dir="Subspace",
    )

    assert omoospace.subspaces_dir == Opath("temp", "NewProject", "Subspace").resolve()
    assert omoospace.contents_dir == Opath("temp", "NewProject", "Content").resolve()


def test_omoospace(mini_omoos_path: Opath):
    make_path(
        "AssetA.blend",
        "AssetB/001-ModelAssetB.zpr",
        "AssetB/002-TextureAssetB.spp",
        "AssetB/003-RenderAssetB.blend",
        "AssetC/AssetC.blend",
        "AssetC/PartA.blend",
        "AssetC/PartB.blend",
        under=mini_omoos_path,
    )

    omoospace = Omoospace(mini_omoos_path)
    assert omoospace.root_dir == mini_omoos_path
    assert omoospace.subspaces_dir == Opath(mini_omoos_path)
    assert omoospace.contents_dir == Opath(mini_omoos_path, "Contents")
    assert omoospace.profile_file == Opath(mini_omoos_path, "Omoospace.yml")
    assert omoospace.contents_dir.is_dir()
    assert omoospace.subspaces_dir.is_dir()
    assert omoospace.profile_file.is_file()

    assert len(omoospace.subspaces) == 9
    objective_tree = omoospace.objective_tree
    assert objective_tree.count == 8
    print("")
    print(objective_tree.format())

    for o in objective_tree:
        if o.name == "AssetA":
            assert len(o.subspaces) == 1
            assert len(o.children) == 0
        elif o.name == "AssetB":
            assert len(o.subspaces) == 1
            assert len(o.children) == 3
        elif o.name == "AssetC":
            assert len(o.subspaces) == 2
            assert len(o.children) == 2


def test_omoospace_other_dir():
    omoos_path = Opath("temp", "OtherProject").resolve()

    make_path(
        "Assets/",
        "SourceFiles/",
        {
            "Omoospace.yml": """
        brief: A mini omoospace.
        contents_dir: Assets
        subspaces_dir: SourceFiles
        """
        },
        under=omoos_path,
    )

    omoospace = Omoospace(omoos_path)
    assert omoospace.root_dir == omoos_path
    assert omoospace.subspaces_dir == Opath(omoos_path, "SourceFiles")
    assert omoospace.contents_dir == Opath(omoos_path, "Assets")
    assert omoospace.profile_file == Opath(omoos_path, "Omoospace.yml")

    assert omoospace.contents_dir.is_dir()
    assert omoospace.subspaces_dir.is_dir()
    assert omoospace.profile_file.is_file()

from pathlib import Path

import pytest
from omoospace import Omoospace, create_omoospace
from tests.helper import write_file, write_file_content


def test_create_omoospace():
    omoospace = create_omoospace(
        name="new project",
        root_dir="temp",
        description="A new project for testing.",
        reveal_in_explorer=False,
    )

    assert omoospace.root_path == Path("temp", "NewProject").resolve()
    assert omoospace.name == "new project"
    assert omoospace.description == "A new project for testing."
    assert len(omoospace.entities) == 0


def test_omoospace(mini_omoos_path: Path):
    omoospace = Omoospace(mini_omoos_path)
    assert omoospace.root_path == mini_omoos_path
    assert omoospace.subspaces_path == Path(mini_omoos_path, "Subspaces")
    assert omoospace.contents_path == Path(mini_omoos_path, "Contents")
    assert omoospace.profile_path == Path(mini_omoos_path, "Omoospace.yml")

    assert omoospace.contents_path.is_dir()
    assert omoospace.subspaces_path.is_dir()
    assert not omoospace.profile_path.is_file()

    assert omoospace.name == "MiniProject"
    assert omoospace.description == None
    omoospace.description = "A mini omoospace."
    assert omoospace.description == "A mini omoospace."

    with pytest.raises(AttributeError):
        omoospace.creators = ["icrdr"]

    with pytest.raises(AttributeError):
        omoospace.softwares = ["Blender"]

    with pytest.raises(AttributeError):
        omoospace.works = ["Heart.fbx"]

    write_file(
        "AssetA.blend",
        "AssetB/Subspace.yml",
        "AssetB/001-modeling/AssetB.zpr",
        "AssetB/002-texturing/AssetB.spp",
        "AssetB/003-rendering/AssetB.blend",
        "AssetC/Subspace.yml",
        "AssetC/AssetC.blend",
        "AssetC/PartA.blend",
        "AssetC/PartB.blend",
        root_dir=omoospace.subspaces_path,
    )

    assert len(omoospace.entities) == 12
    tree_dict = omoospace.subspace_tree.to_dict()
    assert len(tree_dict) == 3

    for item in tree_dict:
        if item["data"].node_name == "AssetA":
            assert len(item["data"].entities) == 1
            assert len(item["data"].children) == 0
        elif item["data"].node_name == "AssetB":
            assert len(item["data"].entities) == 1
            assert len(item["data"].children) == 3
        elif item["data"].node_name == "AssetC":
            assert len(item["data"].entities) == 2
            assert len(item["data"].children) == 2


    # TODO: test other omoospace attributes.


def test_omoospace_mapping(bad_omoos_path: Path):
    omoospace = Omoospace(bad_omoos_path)
    assert omoospace.root_path == bad_omoos_path
    assert omoospace.subspaces_path == Path(bad_omoos_path, "Subspace")
    assert omoospace.contents_path == Path(bad_omoos_path, "Content")
    assert omoospace.profile_path == Path(bad_omoos_path, "Omoospace.yml")

    assert omoospace.contents_path.is_dir()
    assert omoospace.subspaces_path.is_dir()
    assert omoospace.profile_path.is_file()


def test_add_subspace(mini_omoos_path: Path):
    omoospace = Omoospace(mini_omoos_path)
    write_file(
        "Heart.blend",
        "Heart.v001.blend",
        "Heart_Valves.blend",
        "Heart_Valves.v001.spp",
        "Liver.zpr",
        root_dir=omoospace.subspaces_path,
    )
    subs_Heart = omoospace.add_subspace(name="heart", reveal_in_explorer=False)
    assert subs_Heart.name == "heart"

    # test collect entities feature.
    assert len(subs_Heart.entities) == 3
    assert len(subs_Heart.children) == 1
    assert len(list(subs_Heart.root_path.iterdir())) == 4

    subs_Valves = omoospace.add_subspace(
        name="valves",
        parent_dir=subs_Heart.root_path,
        description="The valves of heart.",
        reveal_in_explorer=False,
    )

    assert subs_Valves.route == ["Heart", "Valves"]
    assert subs_Valves.description == "The valves of heart."


def test_creator(mini_omoos_path: Path):
    omoospace = Omoospace(mini_omoos_path)
    write_file_content(
        (
            "Omoospace.yml",
            """
        name: Mini
        description: A mini omoospace.
        creators:
          - email: manan@abc.com
          - email: manan@abc.com
          - manan@abc.com
        """,
        ),
        root_dir=omoospace.root_path,
    )

    creator = omoospace.add_creator(
        email="manan@abc.com", name="manan", website="https://www.manan.com"
    )
    assert creator.name == "manan"
    assert omoospace.creators[0].name == "manan"

    creator.name = "Ma Nan"
    assert creator.name == "Ma Nan"
    assert omoospace.creators[0].name == "Ma Nan"

    creator.email = "icrdr@abc.com"
    creator = omoospace.get_creator("icrdr@abc.com")
    assert len(omoospace.creators) == 1
    assert creator.name == "Ma Nan"
    assert creator.role == None

    creator.role = "Director"
    assert omoospace.creators[0].role == "Director"


def test_software(mini_omoos_path: Path):
    omoospace = Omoospace(mini_omoos_path)
    software = omoospace.add_software(name="Blender", version="3.6.5")
    assert software.name == "Blender"
    assert omoospace.softwares[0].name == "Blender"

    software.version = "4.0.0"
    assert software.version == "4.0.0"
    assert omoospace.softwares[0].version == "4.0.0"

    software = omoospace.add_software(name="Houdini", version="19.5.577")

    assert omoospace.get_software("Blender").version == "4.0.0"
    assert omoospace.get_software("Houdini").version == "19.5.577"

    with pytest.raises(AttributeError):
        software.plugins = ["omoospace"]

    software.set_plugin(name="omoospace", version="0.1.5")
    assert len(software.plugins) == 1


def test_work(mini_omoos_path: Path):
    omoospace = Omoospace(mini_omoos_path)
    write_file(
        "Models/Heart/Heart.fbx",
        "Models/Heart/Textures/Heart.basecolor.png",
        "Models/Liver/Liver.gltf",
        "Models/Liver/Liver.png",
        "Models/Liver/Liver.bin",
        "Models/Lung.glb",
        root_dir=omoospace.contents_path,
    )
    work = omoospace.add_work(Path(omoospace.contents_path, "Models/Heart"))
    assert work.name == "Heart"
    assert len(work.items) == 1
    assert work.items[0] == "Models/Heart"
    assert omoospace.works[0].name == "Heart"
    assert omoospace.get_work("Heart").items[0] == "Models/Heart"

    work.add_item(
        Path(omoospace.contents_path, "Models/Liver"),
        Path(omoospace.contents_path, "Models/Liver"),
        Path(omoospace.contents_path, "Models/Lung.glb"),
    )
    assert len(omoospace.works[0].items) == 3
    Path(omoospace.contents_path, "Models/Lung.glb").unlink()
    assert len(omoospace.works[0].items) == 2

    with pytest.raises(AttributeError):
        work.items = ["Models/Liver"]

    work.set_items(
        Path(omoospace.contents_path, "Models/Liver"),
    )
    assert len(omoospace.works[0].items) == 1

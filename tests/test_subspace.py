import pytest
from pathlib import Path
from omoospace import ObjectiveType, extract_pathname, Omoospace, make_path, Opath
from omoospace.omoospace import Subspace
from tests.helper import factory_make_item

subspace = factory_make_item("Subspaces")


def test_add_subspace(mini_omoos_path: Opath):
    omoospace = Omoospace(mini_omoos_path)
    make_path(
        "Heart.blend",
        "Heart.v001.blend",
        "Heart_Valves.spp",
        "Heart_Valves.v001.spp",
        "Liver.zpr",
        under=omoospace.subspaces_dir,
    )
    make_heart = omoospace.add_subspace(name="heart")

    # "add_subspace" will collect subspaces that has same objective.
    # All files except "Liver.zpr" will move to Heart/
    assert Opath(omoospace.subspaces_dir, "Heart/Heart.blend").exists()
    assert Opath(omoospace.subspaces_dir, "Heart/Heart.v001.blend").exists()
    assert Opath(omoospace.subspaces_dir, "Heart/Heart_Valves.spp").exists()
    assert Opath(omoospace.subspaces_dir, "Heart/Heart_Valves.v001.spp").exists()
    assert Opath(omoospace.subspaces_dir, "Liver.zpr").exists()

    assert len(make_heart.subspaces) == 5
    assert "Heart" in make_heart.subspaces
    assert "Heart/Heart.blend" in make_heart.subspaces
    assert "Heart/Heart.v001.blend" in make_heart.subspaces
    assert "Heart/Heart_Valves.spp" in make_heart.subspaces
    assert "Heart/Heart_Valves.v001.spp" in make_heart.subspaces

    # Add subspace under heart.
    make_valves = omoospace.add_subspace("valves", under=make_heart)
    assert make_valves.pathname == "Heart_Valves"
    assert len(make_heart.subspaces) == 6

    # Heart_Valves.spp not move to Heart/Valves/
    assert Opath(omoospace.subspaces_dir, "Heart/Heart_Valves.spp").exists()
    assert Opath(omoospace.subspaces_dir, "Heart/Heart_Valves.v001.spp").exists()


@pytest.mark.parametrize(
    "subspace,expected",
    [
        ("Sc010_AssetA.blend", "Sc010_AssetA"),
        ("Sc010/AssetA.blend", "Sc010_AssetA"),
        ("Sc010_Shot0100/AssetA.blend", "Sc010_Shot0100_AssetA"),
        (
            "Sc010_Shot0100/Shot0100_AssetA.blend",
            "Sc010_Shot0100_AssetA",
        ),
        (
            "Sc010_Shot0100/Sc010_Shot0100_AssetA.blend",
            "Sc010_Shot0100_AssetA",
        ),
        ("PartA/AssetA_PartA.blend", "PartA_AssetA_PartA"),
        ("AssetA.001.blend", "AssetA"),
        ("AssetA.v001.blend", "AssetA"),
        ("Asset-A.v001.blend", "Asset-A"),
        ("AssetA.v001.autosave.blend", "AssetA"),
        ("头骨/头骨.blend", "头骨"),
        ("Asset A/AssetA.blend", "AssetA"),
        ("AssetA_AssetA.blend", "AssetA_AssetA"),
    ],
    indirect=["subspace"],
)
def test_extract_pathname(subspace: Opath, expected: str):
    assert extract_pathname(subspace) == expected


def test_extract_pathname2(empty_omoos_path: Path):
    assert Subspace(Opath(r"O:\OmooProjects\诺思兰德_塞多明基注射液\Subspaces\RND\测试Omoospace.blend")).pathname == "RND_测试Omoospace"
    omoospace = Omoospace(empty_omoos_path)
    other_subspaces_dir = Path(omoospace.root_dir, "src")
    make_path(
        "AssetA.blend",
        "Sc010/Sc010.blend",
        under=other_subspaces_dir,
    )

    assert extract_pathname(other_subspaces_dir / "AssetA.blend") == ""
    assert extract_pathname(".") == None
    omoospace.subspaces_dir = "src"
    assert omoospace.subspaces_dir == other_subspaces_dir
    assert extract_pathname(other_subspaces_dir / "AssetA.blend") == "AssetA"


def test_objective_node(empty_omoos_path: Path):
    make_path(
        "AssetA_PartA_v001.blend",
        under=Path(empty_omoos_path, "Subspaces", "Sc010_Shot0100"),
    )

    o_tree = Omoospace(empty_omoos_path).objective_tree
    o_PartA = o_tree.get("Sc010_Shot0100_AssetA_PartA")
    o_PartA = o_tree.get("PartA")

    # o_PartA is a file objective
    assert o_PartA.type == ObjectiveType.FILE
    assert o_PartA.name == "PartA"
    assert o_PartA.parent.name == "AssetA"
    assert o_PartA.parent.parent.name == "Shot0100"
    assert o_PartA.pathname == "Sc010_Shot0100_AssetA_PartA"
    assert len(o_PartA.subspaces) == 1

    # o_AssetA is a phantom objective
    o_AssetA = o_PartA.parent
    assert o_AssetA.name == "AssetA"
    assert o_AssetA.type == ObjectiveType.PHANTOM

    # o_Shot0100 is a directory objective
    o_Shot0100 = o_tree.get("Sc010_Shot0100")
    assert o_Shot0100 != None
    assert o_Shot0100.type == ObjectiveType.DIRECTORY
    assert len(o_Shot0100.subspaces) == 1


def test_objective_tree(empty_omoos_path: Path):
    omoospace = Omoospace(empty_omoos_path)
    make_path(
        "AssetA.blend",
        "Sc010_Shot0100/AssetB.v001.blend",
        "Sc010_Shot0100/AssetB.001.v002.blend",
        "Sc010_Shot0100/AssetB.001.blend",
        "Sc010_Shot0100/AssetC.blend",
        "Sc010/Sc010.blend",
        "Sc010_AssetD.blend",
        "Sc010/AssetE/AssetE_PartA.blend",
        under=omoospace.subspaces_dir,
    )
    o_tree = Omoospace(empty_omoos_path).objective_tree

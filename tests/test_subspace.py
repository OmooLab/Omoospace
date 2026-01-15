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
        ("Sc010_Prop01.blend", "Sc010_Prop01"),
        ("Sc010/Prop01.blend", "Sc010_Prop01"),
        ("Sc010_Shot0100/Prop01.blend", "Sc010_Shot0100_Prop01"),
        (
            "Sc010_Shot0100/Shot0100_Prop01.blend",
            "Sc010_Shot0100_Prop01",
        ),
        (
            "Sc010_Shot0100/Sc010_Shot0100_Prop01.blend",
            "Sc010_Shot0100_Prop01",
        ),
        ("Part01/Prop01_Part01.blend", "Part01_Prop01_Part01"),
        ("Prop01.001.blend", "Prop01"),
        ("Prop01.v001.blend", "Prop01"),
        ("Asset-A.v001.blend", "Asset-A"),
        ("Prop01.v001.autosave.blend", "Prop01"),
        ("头骨/头骨.blend", "头骨"),
        ("Prop01/Prop01.blend", "Prop01"),
        ("Prop01_Prop01.blend", "Prop01_Prop01"),
    ],
    indirect=["subspace"],
)
def test_extract_pathname(subspace: Opath, expected: str):
    assert extract_pathname(subspace) == expected


def test_extract_pathname2(empty_omoos_path: Path):
    omoospace = Omoospace(empty_omoos_path)
    other_subspaces_dir = Path(omoospace.root_dir, "src")
    make_path(
        "Prop01.blend",
        "Sc010/Sc010.blend",
        under=other_subspaces_dir,
    )

    assert extract_pathname(other_subspaces_dir / "Prop01.blend") == ""
    assert extract_pathname(".") == None
    omoospace.subspaces_dir = "src"
    assert omoospace.subspaces_dir == other_subspaces_dir
    assert extract_pathname(other_subspaces_dir / "Prop01.blend") == "Prop01"


def test_objective_node(empty_omoos_path: Path):
    make_path(
        "Prop01_Part01_v001.blend",
        under=Path(empty_omoos_path, "Subspaces", "Sc010_Shot0100"),
    )

    o_tree = Omoospace(empty_omoos_path).objective_tree
    o_Part01 = o_tree.get("Sc010_Shot0100_Prop01_Part01")
    o_Part01 = o_tree.get("Part01")

    # o_Part01 is a file objective
    assert o_Part01.type == ObjectiveType.FILE
    assert o_Part01.name == "Part01"
    assert o_Part01.parent.name == "Prop01"
    assert o_Part01.parent.parent.name == "Shot0100"
    assert o_Part01.pathname == "Sc010_Shot0100_Prop01_Part01"
    assert len(o_Part01.subspaces) == 1

    # o_Prop01 is a phantom objective
    o_Prop01 = o_Part01.parent
    assert o_Prop01.name == "Prop01"
    assert o_Prop01.type == ObjectiveType.PHANTOM

    # o_Shot0100 is a directory objective
    o_Shot0100 = o_tree.get("Sc010_Shot0100")
    assert o_Shot0100 != None
    assert o_Shot0100.type == ObjectiveType.DIRECTORY
    assert len(o_Shot0100.subspaces) == 1

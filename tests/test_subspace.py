import pytest
from pathlib import Path
from omoospace import SubspaceTree, SubspaceType, get_route
from omoospace import Route
from tests.helper import factory_omoospace_file_paths, write_file, write_file_content


file_paths = factory_omoospace_file_paths('Subspaces')


@pytest.mark.parametrize("file_paths,expected", [
    (["Seq010_AssetA.blend"],
     ['Seq010', 'AssetA']),

    (["Seq010/AssetA.blend"],
     ['Seq010', 'AssetA']),

    (["Seq010/AssetA.blend", "Seq010/Subspace.yml"],
     ['Seq010', 'AssetA']),

    (["Seq010_Shot0100/AssetA.blend"],
     ['Seq010', 'Shot0100', 'AssetA']),

    (["Seq010_Shot0100/Shot0100_AssetA.blend", "Seq010_Shot0100/Subspace.yml"],
     ['Seq010', 'Shot0100', 'AssetA']),

    (["Seq010_Shot0100/Seq010_Shot0100_AssetA.blend", "Seq010_Shot0100/Subspace.yml"],
     ['Seq010', 'Shot0100', 'AssetA']),

    (["AssetA.001.blend"], ['AssetA']),

    (["AssetA.v001.blend"], ['AssetA']),

    (["Asset-A.v001.blend"], ['Asset-A']),

    (["AssetA.v001.autosave.blend"], ['AssetA']),
    
    (["头骨/头骨.blend", "头骨/Subspace.yml"],
     ['头骨']),

    (["Asset A/AssetA.blend", "Asset A/Subspace.yml"],
     ['AssetA']),

    (["AssetA_AssetA.blend"],
     ['AssetA', 'AssetA']),

    (["Void_AssetA.blend"],
     ['Void', 'AssetA']),

    (["Void/Void_AssetA.blend"],
     ['Void', 'AssetA']),
    
    (["Void/AssetA.blend"],
     ['Void', 'AssetA']),

    (["Seq010_Shot0100/Void_AssetA.blend", "Seq010_Shot0100/Subspace.yml"],
     ['Void', 'Seq010', 'Shot0100', 'AssetA']),
    
    (["Void/Seq010_Shot0100/Void_AssetA.blend", "Void/Seq010_Shot0100/Subspace.yml"],
     ['Void', 'Seq010', 'Shot0100', 'AssetA']),

], indirect=['file_paths'])
def test_get_route(file_paths: list[Path], expected: Route):
    assert get_route(file_paths[0]) == expected


def test_subspace_node(empty_omoos_path: Path):
    PartA_file_path = write_file(
        "AssetA_PartA_v001.blend",
        root_dir=Path(empty_omoos_path, "Subspaces", "Seq010_Shot0100")
    )
    write_file_content(
        ("Subspace.yml", """
        description: The first shot of sequence 010.
        """),
        ("AssetA.Subspace.yml", """
        name: Heart
        description: A model of heart.
        """),
        root_dir=Path(empty_omoos_path, "Subspaces", "Seq010_Shot0100")
    )

    tree = SubspaceTree(PartA_file_path)
    subs_PartA = tree.get(["Seq010", "Shot0100", "AssetA", "PartA"])

    assert subs_PartA != None
    subs_PartA.name = 'Valves'
    assert subs_PartA.name == 'Valves'
    assert subs_PartA.profile_path == \
        Path(empty_omoos_path, "Subspaces/Seq010_Shot0100/AssetA_PartA.Subspace.yml")
    assert subs_PartA.profile_path.exists()
    assert subs_PartA.type == SubspaceType.FILE
    assert subs_PartA.node_name == 'PartA'
    assert subs_PartA.parent.node_name == 'AssetA'
    assert subs_PartA.parent.parent.node_name == 'Shot0100'
    assert subs_PartA.route == ["Seq010", "Shot0100", "AssetA", "PartA"]
    assert len(subs_PartA.entities) == 1

    subs_AssetA = subs_PartA.parent

    assert subs_AssetA.node_name == 'AssetA'
    assert subs_AssetA.type == SubspaceType.PHANTOM
    assert subs_AssetA.name == 'Heart'

    subs_PartB = subs_AssetA.add('PartB')
    assert len(subs_AssetA.children) == 2

    assert subs_PartB != None
    subs_PartB.name = '心脏'
    assert subs_PartB.name == 'PartB'
    assert subs_PartB.type == SubspaceType.DUMMY
    assert subs_PartB.node_name == 'PartB'
    assert subs_PartB.parent.node_name == 'AssetA'
    assert len(subs_PartB.entities) == 0

    subs_Shot0100 = tree.get(["Seq010", "Shot0100"])

    assert subs_Shot0100 != None
    assert subs_Shot0100.type == SubspaceType.DIRECTORY
    assert len(subs_Shot0100.entities) == 1

    subs_Seq010 = tree.get(["Seq010"])
    assert subs_Seq010.type == SubspaceType.PHANTOM
    assert len(subs_Shot0100.entities) == 1
    subs_Seq010.description = 'Seq010'
    assert subs_Seq010.profile_path == \
        Path(empty_omoos_path, "Subspaces/Seq010.Subspace.yml")
    assert subs_Seq010.profile_path.exists()

    tree_dict = tree.to_dict()
    assert tree_dict[0]['data'].node_name == "Seq010"
    assert tree_dict[0]['children'][0]['data'].node_name == "Shot0100"

    # if entity is deleted during process, entity of subsapce will also be removed.
    PartA_file_path.unlink(missing_ok=True)
    assert len(subs_AssetA.entities) == 0
    assert subs_AssetA.type == SubspaceType.DUMMY


def test_subspace_tree(empty_omoos_path: Path):
    subspaces_path = Path(empty_omoos_path, "Subspaces")
    write_file(
        "AssetA.blend",
        "Seq010_Shot0100/AssetB.v001.blend",
        "Seq010_Shot0100/AssetB.001.v002.blend",
        "Seq010_Shot0100/AssetB.001.blend",
        "Seq010_Shot0100/AssetC.blend",
        "Seq010/Seq010.blend",
        "Seq010_AssetD.blend",
        "Seq010/AssetE/AssetE_PartA.blend",
        root_dir=subspaces_path
    )
    tree = SubspaceTree(subspaces_path)
    tree_dict = tree.to_dict()
    assert len(tree_dict) == 2
    assert len(tree_dict[0]['children']) == 3

import pytest
from pathlib import Path
from omoospace.subspace import SubspaceTree, SubspaceType, get_route, get_route_str
from omoospace.types import Route
from tests.helper import factory_omoospace_file_paths, write_file, write_file_content


file_paths = factory_omoospace_file_paths('SourceFiles')


@pytest.mark.parametrize("file_paths,expected", [
    (["SQ010_AssetA.blend"],
     ['SQ010', 'AssetA']),

    (["SQ010/AssetA.blend"],
     ['AssetA']),

    (["SQ010/AssetA.blend", "SQ010/Subspace.yml"],
     ['SQ010', 'AssetA']),

    (["SQ010_SH0100/AssetA.blend", "SQ010_SH0100/Subspace.yml"],
     ['SQ010', 'SH0100', 'AssetA']),

    (["SQ010_SH0100/SH0100_AssetA.blend", "SQ010_SH0100/Subspace.yml"],
     ['SQ010', 'SH0100', 'AssetA']),

    (["SQ010_SH0100/SQ010_SH0100_AssetA.blend", "SQ010_SH0100/Subspace.yml"],
     ['SQ010', 'SH0100', 'AssetA']),

    (["AssetA_001.blend"], ['AssetA']),

    (["AssetA__v001.blend"], ['AssetA']),

    (["Asset-A__v001.blend"], ['Asset-A']),

    (["AssetA_v001_autosave.blend"], ['AssetA']),

    (["头骨/TouGu.blend", "头骨/Subspace.yml"],
     ['TouGu']),

    (["Asset A/AssetA.blend", "Asset A/Subspace.yml"],
     ['AssetA']),

    (["AssetA_AssetA.blend"],
     ['AssetA', 'AssetA']),

], indirect=['file_paths'])
def test_get_route(file_paths: list[Path], expected: Route):
    assert get_route(file_paths[0]) == expected


@pytest.mark.parametrize("file_paths,subsets,expected", [
    (["SQ010_AssetA.blend"],
     ['v001'],
     'SQ010_AssetA_v001'),

    (["SQ010/AssetA.blend", "SQ010/Subspace.yml"],
     ['LowRes'],
     'SQ010_AssetA_LowRes'),

    (["SQ010_SH0100/AssetA.blend", "SQ010_SH0100/Subspace.yml"],
     ['HighRes','v001'],
     'SQ010_SH0100_AssetA_HighRes_v001'),

    (["SQ010_SH0100/SH0100_AssetA.blend", "SQ010_SH0100/Subspace.yml"],
     [],
     'SQ010_SH0100_AssetA'),

    (["SQ010_SH0100/SQ010_SH0100_AssetA.blend", "SQ010_SH0100/Subspace.yml"],
     ['HighRes','v001'],
     'SQ010_SH0100_AssetA_HighRes_v001'),


    (["AssetA_AssetA.blend"],
     [],
     'AssetA_AssetA'),

], indirect=['file_paths'])
def test_get_route_str(file_paths: list[Path], subsets: list[str], expected: Route):
    assert get_route_str(file_paths[0],*subsets) == expected


def test_subspace_node(empty_omoos_path: Path):
    PartA_file_path = write_file(
        "AssetA_PartA_v001.blend",
        root_dir=Path(empty_omoos_path, "SourceFiles", "SQ010_SH0100")
    )
    write_file_content(
        ("Subspace.yml", """
        description: The first shot of sequence 010.
        """),
        ("AssetA.Subspace.yml", """
        name: Heart
        description: A model of heart.
        """),
        root_dir=Path(empty_omoos_path, "SourceFiles", "SQ010_SH0100")
    )

    tree = SubspaceTree(PartA_file_path)
    subs_PartA = tree.get(["SQ010", "SH0100", "AssetA", "PartA"])

    assert subs_PartA != None
    subs_PartA.name = 'Valves'
    assert subs_PartA.name == 'Valves'
    assert subs_PartA.profile_path == \
        Path(empty_omoos_path, "SourceFiles/SQ010_SH0100/AssetA_PartA.Subspace.yml")
    assert subs_PartA.profile_path.exists()
    assert subs_PartA.type == SubspaceType.FILE
    assert subs_PartA.node_name == 'PartA'
    assert subs_PartA.parent.node_name == 'AssetA'
    assert subs_PartA.parent.parent.node_name == 'SH0100'
    assert subs_PartA.route == ["SQ010", "SH0100", "AssetA", "PartA"]
    assert len(subs_PartA.entities) == 1

    subs_AssetA = subs_PartA.parent

    assert subs_AssetA.node_name == 'AssetA'
    assert subs_AssetA.type == SubspaceType.PHANTOM
    assert subs_AssetA.name == 'Heart'

    subs_PartB = subs_AssetA.add('PartB')
    assert len(subs_AssetA.children) == 2

    assert subs_PartB != None
    subs_PartB.name = '心脏'
    assert subs_PartB.name == None
    assert subs_PartB.type == SubspaceType.DUMMY
    assert subs_PartB.node_name == 'PartB'
    assert subs_PartB.parent.node_name == 'AssetA'
    assert len(subs_PartB.entities) == 0

    subs_SH0100 = tree.get(["SQ010", "SH0100"])

    assert subs_SH0100 != None
    assert subs_SH0100.type == SubspaceType.DIRECTORY
    assert len(subs_SH0100.entities) == 1

    subs_SQ010 = tree.get(["SQ010"])
    assert subs_SQ010.type == SubspaceType.PHANTOM
    assert len(subs_SH0100.entities) == 1
    subs_SQ010.description = 'SQ010'
    assert subs_SQ010.profile_path == \
        Path(empty_omoos_path, "SourceFiles/SQ010.Subspace.yml")
    assert subs_SQ010.profile_path.exists()

    tree_dict = tree.to_dict()
    assert tree_dict[0]['data'].node_name == "SQ010"
    assert tree_dict[0]['children'][0]['data'].node_name == "SH0100"

    # if entity is deleted during process, entity of subsapce will also be removed.
    PartA_file_path.unlink(missing_ok=True)
    assert len(subs_AssetA.entities) == 0
    assert subs_AssetA.type == SubspaceType.DUMMY


def test_subspace_tree(empty_omoos_path: Path):
    sourcefiles_path = Path(empty_omoos_path, "SourceFiles")
    write_file(
        "AssetA.blend",
        "SQ010_SH0100/Subspace.yml",
        "SQ010_SH0100/AssetB_v001_autosave.blend",
        "SQ010_SH0100/AssetB_v001.blend",
        "SQ010_SH0100/AssetB_v002.blend",
        "SQ010_SH0100/AssetB_001.blend",
        "SQ010_SH0100/AssetC.blend",
        "SQ010/Subspace.yml",
        "SQ010/SQ010.blend",
        "SQ010_AssetD.blend",
        "SQ010/AssetE/Subspace.yml",
        "SQ010/AssetE/AssetE_PartA.blend",
        root_dir=sourcefiles_path
    )
    tree = SubspaceTree(sourcefiles_path)
    tree_dict = tree.to_dict()
    assert len(tree_dict) == 2
    assert len(tree_dict[0]['children']) == 3

from pathlib import Path

import pytest
from omoospace import Omoospace, create_omoospace
from tests.helper import write_file, write_file_content


def test_create_omoospace():
    omoos = create_omoospace(
        name='new project',
        root_dir='temp',
        description='A new project for testing.',
        reveal_in_explorer=False
    )

    assert omoos.root_path == Path('temp', 'NewProject').resolve()
    assert omoos.name == 'new project'
    assert omoos.description == 'A new project for testing.'
    assert len(omoos.entities) == 0
    assert len(omoos.subspace_tree_dict) == 0


def test_omoospace(mini_omoos_path: Path):
    omoos = Omoospace(mini_omoos_path)
    assert omoos.root_path == mini_omoos_path
    assert omoos.sourcefiles_path == Path(mini_omoos_path, 'SourceFiles')
    assert omoos.contents_path == Path(mini_omoos_path, 'Contents')
    assert omoos.externaldata_path == Path(mini_omoos_path, 'ExternalData')
    assert omoos.stageddata_path == Path(mini_omoos_path, 'StagedData')
    assert omoos.references_path == Path(mini_omoos_path, 'References')
    assert omoos.profile_path == Path(mini_omoos_path, "Omoospace.yml")

    assert omoos.contents_path.is_dir()
    assert omoos.sourcefiles_path.is_dir()
    assert omoos.externaldata_path.is_dir()
    assert omoos.profile_path.is_file()

    assert omoos.name == 'Mini'
    assert omoos.description == 'A mini omoospace.'

    with pytest.raises(AttributeError):
        omoos.creators = ['icrdr']

    with pytest.raises(AttributeError):
        omoos.softwares = ['Blender']

    with pytest.raises(AttributeError):
        omoos.works = ['Heart.fbx']

    write_file(
        'AssetA.blend',
        'AssetB/Subspace.yml',
        'AssetB/001-modeling/AssetB.zpr',
        'AssetB/002-texturing/AssetB.spp',
        'AssetB/003-rendering/AssetB.blend',
        'AssetC/Subspace.yml',
        'AssetC/AssetC.blend',
        'AssetC/PartA.blend',
        'AssetC/PartB.blend',
        root_dir=omoos.sourcefiles_path
    )

    assert len(omoos.entities) == 9
    tree_dict = omoos.subspace_tree_dict
    assert len(tree_dict) == 3
    assert tree_dict[0]['data'].node_name == "AssetB"
    assert len(tree_dict[0]['data'].entities) == 4
    assert tree_dict[1]['data'].node_name == "AssetC"
    assert len(tree_dict[1]['data'].children) == 2

    # TODO: test other omoos attributes.


def test_add_subspace(mini_omoos_path: Path):
    omoos = Omoospace(mini_omoos_path)
    write_file(
        'Heart.blend',
        'Heart_v001.blend',
        'Heart_Valves.blend',
        'Heart_Valves_v001_autosave.spp',
        'Liver.zpr',
        root_dir=omoos.sourcefiles_path
    )
    subs_Heart = omoos.add_subspace(
        name="heart",
        reveal_in_explorer=False
    )
    assert subs_Heart.name == "heart"

    # test collect entities feature.
    assert len(subs_Heart.entities) == 3
    assert len(subs_Heart.children) == 1
    assert len(list(subs_Heart.root_path.iterdir())) == 4

    subs_Valves = omoos.add_subspace(
        name="valves",
        parent_dir=subs_Heart.root_path,
        description='The valves of heart.',
        reveal_in_explorer=False
    )

    assert subs_Valves.route == ['Heart', 'Valves']
    assert subs_Valves.description == 'The valves of heart.'


def test_add_process(mini_omoos_path: Path):
    omoos = Omoospace(mini_omoos_path)
    omoos.add_process(
        'modeling', 'texturing', 'shading', 'rendering',
        reveal_in_explorer=False
    )
    assert Path(omoos.sourcefiles_path, '001-Modeling').is_dir()
    assert Path(omoos.sourcefiles_path, '002-Texturing').is_dir()
    assert Path(omoos.sourcefiles_path, '003-Shading').is_dir()
    assert Path(omoos.sourcefiles_path, '004-Rendering').is_dir()

    omoos.add_process(
        'modeling', 'texturing', 'shading', 'rendering',
        reveal_in_explorer=False
    )

    omoos.add_process(
        "sculpting",
        parent_dir=Path(omoos.sourcefiles_path, '001-Modeling'),
        reveal_in_explorer=False
    )

    assert Path(omoos.sourcefiles_path, '001-Modeling', 'Sculpting').is_dir()
    assert len(omoos.subspace_tree_dict) == 0

    file_path = write_file(
        'Heart.zpr',
        root_dir=Path(omoos.sourcefiles_path, '001-Modeling', 'Sculpting')
    )
    subs_Heart = omoos.get_subspace(file_path)
    assert subs_Heart.route == ['Heart']


def test_creator(mini_omoos_path: Path):
    omoos = Omoospace(mini_omoos_path)
    write_file_content(
        ("Omoospace.yml", """
        name: Mini
        description: A mini omoospace.
        creators:
          - email: manan@abc.com
          - email: manan@abc.com
          - manan@abc.com
        """),
        root_dir=omoos.root_path)

    creator = omoos.add_creator(
        email='manan@abc.com',
        name='manan',
        website='https://www.manan.com'
    )
    assert creator.name == 'manan'
    assert omoos.creators[0].name == 'manan'

    creator.name = 'Ma Nan'
    assert creator.name == 'Ma Nan'
    assert omoos.creators[0].name == 'Ma Nan'

    creator.email = 'icrdr@abc.com'
    creator = omoos.get_creator('icrdr@abc.com')
    assert len(omoos.creators) == 1
    assert creator.name == 'Ma Nan'
    assert creator.role == None

    creator.role = 'Director'
    assert omoos.creators[0].role == 'Director'


def test_software(mini_omoos_path: Path):
    omoos = Omoospace(mini_omoos_path)
    software = omoos.add_software(
        name='Blender',
        version='3.6.5'
    )
    assert software.name == 'Blender'
    assert omoos.softwares[0].name == 'Blender'

    software.version = '4.0.0'
    assert software.version == '4.0.0'
    assert omoos.softwares[0].version == '4.0.0'

    software = omoos.add_software(
        name='Houdini',
        version='19.5.577'
    )

    assert omoos.get_software('Blender').version == '4.0.0'
    assert omoos.get_software('Houdini').version == '19.5.577'

    with pytest.raises(AttributeError):
        software.plugins = ['omoospace']

    software.set_plugin(
        name='omoospace',
        version='0.1.5'
    )
    assert len(software.plugins) == 1


def test_work(mini_omoos_path: Path):
    omoos = Omoospace(mini_omoos_path)
    write_file(
        'Models/Heart/Heart.fbx',
        'Models/Heart/Textures/Heart_BaseColor.png',
        'Models/Liver/Liver.gltf',
        'Models/Liver/Liver.png',
        'Models/Liver/Liver.bin',
        'Models/Lung.glb',
        root_dir=omoos.contents_path
    )
    work = omoos.add_work(
        Path(omoos.contents_path, 'Models/Heart')
    )
    assert work.name == 'Heart'
    assert len(work.items) == 1
    assert work.items[0] == 'Models/Heart'
    assert omoos.works[0].name == 'Heart'
    assert omoos.get_work('Heart').items[0] == 'Models/Heart'

    work.add_item(
        Path(omoos.contents_path, 'Models/Liver'),
        Path(omoos.contents_path, 'Models/Liver'),
        Path(omoos.contents_path, 'Models/Lung.glb')
    )
    assert len(omoos.works[0].items) == 3
    Path(omoos.contents_path, 'Models/Lung.glb').unlink()
    assert len(omoos.works[0].items) == 2

    with pytest.raises(AttributeError):
        work.items = ['Models/Liver']

    work.set_items(
        Path(omoos.contents_path, 'Models/Liver'),
    )
    assert len(omoos.works[0].items) == 1

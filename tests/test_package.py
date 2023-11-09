

from pathlib import Path
from omoospace.omoospace import Omoospace
from tests.helper import write_file, write_file_content


def test_export_package(mini_omoos_path: Path):
    omoos = Omoospace(mini_omoos_path)
    write_file(
        'Heart.blend',
        'Heart_v001.blend',
        'Heart_Valves.blend',
        'Heart_Valves_v001_autosave.spp',
        'Liver.zpr',
        root_dir=omoos.sourcefiles_path
    )
    write_file(
        'Models/Heart/Heart.fbx',
        'Models/Heart/Textures/Heart_BaseColor.png',
        'Models/Liver/Liver.gltf',
        'Models/Liver/Liver.png',
        'Models/Liver/Liver.bin',
        'Models/Lung.glb',
        root_dir=omoos.contents_path
    )

    pkg = omoos.export_package(
        Path(omoos.contents_path, 'Models/Heart'),
        name='Organs',
        export_dir='temp',
        reveal_when_success=False
    )
    assert pkg.root_path.is_dir()
    assert Path(pkg.root_path, 'Contents/Models/Heart/Textures').is_dir()
    assert Path(pkg.root_path, 'Contents/Models/Heart/Heart.fbx').is_file()
    assert pkg.name == 'Organs'
    assert pkg.description == None
    assert pkg.version == '0.1.0'

    pkg.description = 'An model package of organs.'
    assert pkg.description == 'An model package of organs.'


def test_import_package(mini_omoos_path: Path):
    omoos = Omoospace(mini_omoos_path)
    pkg_path = Path('temp', 'Organs').resolve()
    write_file(
        'Heart.glb',
        'Liver.glb',
        root_dir=Path(pkg_path, 'Contents/Models')
    )
    write_file_content(
        ("Package.yml", """
        name: Organs
        version: 0.1.0
        description: An empty omoospace.
        """),
        root_dir=pkg_path
    )
    omoos.import_package(
        pkg_path,
        reveal_when_success=False
    )

    assert Path(omoos.externaldata_path, 'Organs').is_dir()

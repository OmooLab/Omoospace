# Develop a Plugin

## Installation

This library requires Python version 3.9 or above (python official download link). You can use pyenv or conda for managing multiple Python versions on a single machine.

Run the following command to install omoospace:

```bash
pip install omoospace
```

## Omoospace

### Create a Omoospace

```python
from omoospace import create_omoospace

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
```

### Manage Omoospaces

Example omoospace:

```bash
path/to/MyProject
|-- Contents
|-- ExternalData
|-- SourceFiles
|   |-- AssetA.blend
|   |-- AssetB
|   |   |-- Subspace.yml
|   |   |-- 001-modeling
|   |   |   `-- AssetB.zpr
|   |   |-- 002-texturing
|   |   |   `-- AssetB.spp
|   |   `-- 003-rendering
|   |       `-- AssetB.blend
|   `-- AssetC
|       |-- Subspace.yml
|       |-- AssetC.blend
|       |-- PartA.blend
|       `-- PartB.blend
`-- Omoospace.yml
```

```python
from omoospace import Omoospace

omoos = Omoospace('path/to/MyProject')
assert omoos.root_path == 'path/to/MyProject'
assert omoos.sourcefiles_path == Path('path/to/MyProject', 'SourceFiles')
assert omoos.contents_path == Path('path/to/MyProject', 'Contents')
assert omoos.externaldata_path == Path('path/to/MyProject', 'ExternalData')
assert omoos.stageddata_path == Path('path/to/MyProject', 'StagedData')
assert omoos.references_path == Path('path/to/MyProject', 'References')
assert omoos.profile_path == Path('path/to/MyProject', "Omoospace.yml")

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

assert len(omoos.entities) == 9
tree_dict = omoos.subspace_tree_dict
assert len(tree_dict) == 3
assert tree_dict[0]['data'].node_name == "AssetB"
assert len(tree_dict[0]['data'].entities) == 4
assert tree_dict[1]['data'].node_name == "AssetC"
assert len(tree_dict[1]['data'].children) == 2
```

### Manage Subspaces

Example omoospace:

```bash
path/to/MyProject
|-- Contents
|-- ExternalData
|-- SourceFiles
|   |-- Heart.blend
|   |-- Heart_v001.blend
|   |-- Heart_Valves.blend
|   |-- Heart_Valves_v001_autosave.spp
|   `-- Liver.zpr
`-- Omoospace.yml
```

```python
from omoospace import Omoospace

omoos = Omoospace('path/to/MyProject')
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
```

### Manage Processes

```python
from omoospace import Omoospace

omoos = Omoospace('path/to/MyProject')
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
```

### Manage Creators

```python
from omoospace import Omoospace

omoos = Omoospace('path/to/MyProject')
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
```

### Manage Softwares

```python
from omoospace import Omoospace

omoos = Omoospace('path/to/MyProject')
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
```

### Manage Works

Example omoospace:

```bash
path/to/MyProject
|-- Contents
|   `-- Models
|       |-- Heart
|       |   |-- Textures
|       |   |   `-- Heart_BaseColor.png
|       |   `-- Heart.fbx
|       |-- Liver
|       |   |-- Liver.bin
|       |   |-- Liver.gltf
|       |   |-- Liver.png
|       `-- Lung.glb
|-- ExternalData
|-- SourceFiles
`-- Omoospace.yml
```

```python
from omoospace import Omoospace

omoos = Omoospace('path/to/MyProject')
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
```

## Subspace

### Get Source File Route

```python
from omoospace import get_route

assert get_route('SQ010/AssetA.blend') == ['SQ010', 'AssetA']
```

More examples:

| Files                                                               | Expected Result             |
| ------------------------------------------------------------------- | --------------------------- |
| SQ010_AssetA.blend                                                  | ['SQ010','AssetA']          |
| SQ010/AssetA.blend                                                  | ['AssetA']                  |
| SQ010/AssetA.blend<br>SQ010/Subspace.yml                            | ['SQ010','AssetA']          |
| SQ010_SH0100/AssetA.blend<br>SQ010_SH0100/Subspace.yml              | ['SQ010','SH0100','AssetA'] |
| SQ010_SH0100/SH0100_AssetA.blend<br>SQ010_SH0100/Subspace.yml       | ['SQ010','SH0100','AssetA'] |
| SQ010_SH0100/SQ010_SH0100_AssetA.blend<br>SQ010_SH0100/Subspace.yml | ['SQ010','SH0100','AssetA'] |
| SQ010_SH0100/SQ010_SH0100_AssetA.blend<br>SQ010_SH0100/Subspace.yml | ['SQ010','SH0100','AssetA'] |
| AssetA_001.blend                                                    | ['AssetA']                  |
| AssetA\_\_v001.blend                                                | ['AssetA']                  |
| Asset-A\_\_v001.blend                                               | ['AssetA']                  |
| AssetA_v001_autosave.blend                                          | ['AssetA']                  |
| AssetA_AssetA.blend                                                 | ['AssetA','AssetA']         |
| Asset A/AssetA.blend<br>Asset A/Subspace.yml                        | ['AssetA']                  |

### Get Source File Output Name

```python
from omoospace import get_route_str

assert get_route_str('SQ010/AssetA.blend','HighRes','v001') \
   == 'SQ010_SH0100_AssetA_HighRes_v001'
```

More examples:

| Files                                                  | Subsets           | Expected Result                    |
| ------------------------------------------------------ | ----------------- | ---------------------------------- |
| SQ010_AssetA.blend                                     | 'v001'            | 'SQ010_AssetA_v001'                |
| SQ010/AssetA.blend<br>SQ010/Subspace.yml               | 'LowRes'          | 'SQ010_AssetA_LowRes'              |
| SQ010_SH0100/AssetA.blend<br>SQ010_SH0100/Subspace.yml | 'HighRes', 'v001' | 'SQ010_SH0100_AssetA_HighRes_v001' |
| AssetA_AssetA.blend                                    |                   | 'AssetA_AssetA'                    |

## Utils

### Format a Name

```python
from omoospace import format_name

assert format_name('SQ010_SH0100_001') == 'SQ010_SH0100'
```

| Original Name         | Format Name  |
| --------------------- | ------------ |
| SQ010_SH0100_001      | SQ010_SH0100 |
| SQ010_SH0100_v001     | SQ010_SH0100 |
| Asset A v001          | AssetA       |
| Asset A autosave      | AssetA       |
| Asset_A autosave      | Asset_A      |
| Asset_a_autosave_001  | Asset_A      |
| Asset_a_autosave_v001 | Asset_A      |
| 头骨\_v001            | TouGu        |
| 头骨\_0001            | TouGu        |
| Asset 头骨\_0001      | AssetTouGu   |
| AssetA_bak3           | AssetA       |
| AssetA_bak001         | AssetA       |
| AssetA_recovered      | AssetA       |
| AssetA_recovered_bak1 | AssetA       |
| backup                |              |

### Reveal in File Explorer

```python
from omoospace import Omoospace, reveal_in_explorer

omoos = Omoospace("path/to/omoospace")
reveal_in_explorer(omoos.root_path)
```

Then it will open the directory of giving omoospace in the file explorer.

### Copy to Clipboard

```python
from omoospace import get_route_str, copy_to_clipboard

route_str = get_route_str('SQ010/AssetA.blend','HighRes','v001')
copy_to_clipboard(route_str)
```

Then you will get `SQ010_SH0100_AssetA_HighRes_v001` in your clipboard.

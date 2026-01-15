# Develop Addon with Python

## Add dependencies

omoospace requires Python version 3.10 or above.

```bash
uv add omoospace
```

## How to use

### Omoospace

```python
from omoospace import create_omoospace, Opath

omoospace = create_omoospace(
    "new project", 
    under="temp", 
    brief="A new project for testing."
)

# the name conversion rule is:
# 1. convert to "PascalCase"
# 2. remove special characters and spaces

# so the name "new project" is converted to "NewProject"
# "NewProject" is also the project folder name
assert omoospace.name == "NewProject"
assert omoospace.root_dir == Opath("temp", "NewProject")
assert omoospace.subspaces_dir == Opath("temp", "NewProject", "Subspaces")
assert omoospace.contents_dir == Opath("temp", "NewProject", "Contents")
assert omoospace.profile_file == Opath("temp", "NewProject", "Omoospace.yml")

# a empty project is created.
assert omoospace.brief == "A new project for testing."
assert len(omoospace.subspaces) == 0

# %$ is not allowed as a omoospace name.
with pytest.raises(ValueError):
    create_omoospace("%$", under="temp")
```

Example omoospace:

```bash
Project01
├── Contents
├── AssetA.blend
├── AssetB
│   ├── 001-ModelAssetB.zpr
│   ├── 002-TextureAssetB.spp
│   ╰── 003-RenderAssetB.blend
├── AssetC
│   ├── AssetC.blend
│   ├── PartA.blend
│   ╰── PartB.blend
╰── Omoospace.yml
```

```python
from omoospace import Omoospace, Opath

omoospace = Omoospace("ProjectRoot")
assert omoospace.root_dir == Opath("ProjectRoot")
assert omoospace.subspaces_dir == Opath("ProjectRoot")
assert omoospace.contents_dir == Opath("ProjectRoot", "Contents")
assert omoospace.profile_file == Opath("ProjectRoot", "Omoospace.yml")
assert omoospace.contents_dir.is_dir()
assert omoospace.subspaces_dir.is_dir()
assert omoospace.profile_file.is_file()

assert len(omoospace.subspaces) == 9
objective_tree = omoospace.objective_tree
assert objective_tree.count == 8
print(objective_tree.format())

# Project01
# ├── AssetA
# ├── AssetB
# │   ├── 001-ModelAssetB
# │   ├── 002-TextureAssetB
# │   ╰── 003-RenderAssetB
# ╰── AssetC
#     ├── PartA.blend
#     ╰── PartB.blend

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
```

### Subspace

Example omoospace:

```bash
Project02
├── Contents
├── Subspaces
│   ├── Heart.blend
│   ├── Heart_v001.blend
│   ├── Heart_Valves.blend
│   ├── Heart_Valves_v001_autosave.spp
│   ╰── Liver.zpr
╰── Omoospace.yml
```

```python

from omoospace import Omoospace, Opath

omoospace = Omoospace('path/to/Project')
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
```

```python
from omoospace import extract_pathname

assert extract_pathname("Sc010_AssetA.blend") == "Sc010_AssetA"
assert extract_pathname("SQ010/AssetA.blend") == "Sc010_AssetA"
assert extract_pathname("Sc010_Shot0100/AssetA.blend") == "Sc010_AssetA"
assert extract_pathname("Sc010_Shot0100/Shot0100_AssetA.blend") == "Sc010_Shot0100_AssetA"
assert extract_pathname("Sc010_Shot0100/Sc010_Shot0100_AssetA.blend") == "Sc010_Shot0100_AssetA"
assert extract_pathname("PartA/AssetA_PartA.blend") == "PartA_AssetA_PartA"
assert extract_pathname("AssetA.001.blend") == "AssetA"
assert extract_pathname("AssetA.v001.blend") == "AssetA"
assert extract_pathname("Asset-A.v001.blend") == "Asset-A"
assert extract_pathname("AssetA.v001.autosave.blend") == "AssetA"
assert extract_pathname("头骨/头骨.blend") == "头骨"
assert extract_pathname("Asset A/AssetA.blend") == "AssetA"
assert extract_pathname("AssetA_AssetA.blend") == "AssetA_AssetA"
```


### Maker

```python
# read makers
maker = omoospace.get_maker("马南001")
assert maker.email == "manan001@example.com"
assert maker.website == "https://www.manan.com"
maker = omoospace.get_maker("马南002")
assert maker.email == "manan002@example.com"
assert maker.website == None
maker.website = "https://www.manan2.com"
assert maker.website == "https://www.manan2.com"
assert maker.email == "manan002@example.com"
maker = omoospace.get_maker("偶魔数字")
assert maker.email == None
assert maker.website == "https://www.omoolab.xyz"

# add maker
maker = omoospace.add_maker("icrdr")
assert len(omoospace.makers) == 4
assert "icrdr" in omoospace.makers
assert omoospace.makers == ["马南001", "马南002", "偶魔数字", "icrdr"]
```

### Tool

```python
tool = omoospace.get_tool("Blender")
assert tool.version == "4.2.0"
assert tool.website == "https://www.blender.org"
assert tool.extensions == ["Omoospace", "BioxelNodes"]

tool = omoospace.get_tool("Houdini")
assert tool.version == "20.0.0"
assert tool.website == None
tool.version = "21.0.0"
assert tool.version == "21.0.0"
assert tool.website == None
tool.website = "https://www.houdini.com"
assert tool.version == "21.0.0"
assert tool.website == "https://www.houdini.com"

# edit tool Blender
tool = omoospace.get_tool("Blender")
tool.extensions = ["Omoospace"]
tool.version = ">3.6.5"
assert "BioxelNodes" not in tool.extensions

# get tool by name
assert omoospace.get_tool("Blender").version == ">3.6.5"

# remove tool
omoospace.remove_tool("Blender")
assert len(omoospace.tools) == 2
```

### Work
```python
from omoospace import Omoospace
omoospace = Omoospace('path/to/Project')

work = omoospace.get_work("超厉害动画")
assert work.brief == "一个超厉害的动画."
assert work.version == "1.0.0"
assert work.contents == [
    "视频/动画A.mp4",
    "图片/动画A_封面.png",
]
assert work.contributions["动画师"] == ["马南003", "马南002"]
assert work.contributions["动画导演"] == ["马南001"]

work = omoospace.get_work("超厉害模型")
assert work.brief == None
assert work.version == None
assert work.contents == ["模型/模型A/模型A.fbx", "模型/模型A/贴图"]
assert len(work.contributions) == 0
work.add_contribution("马南003", contribution="模型师")
assert work.contributions["模型师"] == ["马南003"]
assert work.contents == ["模型/模型A/模型A.fbx", "模型/模型A/贴图"]

work = omoospace.get_work("另一个超厉害模型")
assert work.brief == None
assert work.version == None
assert work.contents == ["模型/模型B.glb"]
assert len(work.contributions) == 0

work.brief = "一个超酷的模型."
assert work.brief == "一个超酷的模型."
assert work.contents == ["模型/模型B.glb"]

# set contributions
work.contributions = {
    "模型师": ["马南003", {"name": "马南002", "email": "manan2@example.com"}]
}
assert len(work.contributions["模型师"]) == 2
with pytest.raises(KeyError):
    assert len(work.contributions["主创"]) == 0

# delete content will affect work items
Opath(omoospace.contents_dir, "模型").remove()
assert len(work.contents) == 0

# remove work
omoospace.remove_work("另一个超厉害模型")
assert len(omoospace.works) == 2
```

### Opath
```python
root = mini_omoos_path
make_path(
    "AssetA.blend",
    "AssetB/001-ModelAssetB.zpr",
    "AssetB/002-TextureAssetB.spp",
    "AssetB/003-RenderAssetB.blend",
    "AssetC/AssetC.blend",
    "AssetC/PartA.blend",
    "AssetC/PartB.blend",
    under=root,
)

Opath(root / "AssetA.blend").copy_to(root / "Temp")
assert (root / "AssetA.blend").exists()
assert (root / "Temp" / "AssetA.blend").exists()

# if the same, return self
assert (
    Opath(root / "AssetA.blend").copy_to(root, overwrite=True)
    == root / "AssetA.blend"
)

# Asset.blend is already in Temp, copy fail
with pytest.raises(FileExistsError):
    Opath(root / "AssetA.blend").copy_to(root / "Temp")

# with overwrite=True, AssetA.blend in Temp will be overwritten
Opath(root / "AssetA.blend").copy_to(root / "Temp", overwrite=True)
assert (root / "Temp" / "AssetA.blend").exists()

# Asset.blend is already in Temp, move fail
with pytest.raises(FileExistsError):
    Opath(root / "AssetA.blend").move_to(root / "Temp")

# with overwrite=True, AssetA.blend in Temp will be overwritten
Opath(root / "AssetA.blend").move_to(root / "Temp", overwrite=True)
assert (root / "Temp" / "AssetA.blend").exists()
assert not (root / "AssetA.blend").exists()

# copy folder AssetC to Temp
Opath(root / "AssetC").copy_to(root / "Temp")
assert (root / "AssetC").exists()
assert (root / "Temp" / "AssetC").exists()
assert (root / "Temp" / "AssetC" / "PartA.blend").exists()
assert (root / "Temp" / "AssetC" / "PartB.blend").exists()

make_path("AssetC/PartC.blend", under=root)
# Asset.blend is already in Temp, copy fail
with pytest.raises(FileExistsError):
    Opath(root / "AssetC").copy_to(root / "Temp")

# copy folder AssetC to Temp
Opath(root / "AssetC").copy_to(root / "Temp", overwrite=True)
assert (root / "Temp" / "AssetC" / "PartC.blend").exists()
```

Reveal in Explorer
```python
from omoospace import Omoospace, reveal_directory

omoos = Omoospace("path/to/omoospace")
reveal_directory(omoos.root_dir)
```

### Oset
```python
omoospace = Omoospace(mini_omoos_path)

makers = Oset[Maker](
    [Maker(omoospace, "Alice"), Maker(omoospace, "Bob")], key="name"
)
assert "Alice" in makers
assert "Charlie" not in makers
assert Maker(omoospace, "Bob") in makers

# 测试添加重复属性值的对象（不会被添加）
makers.add(Maker(omoospace, "Alice"))
assert len(makers) == 2
assert "Alice" in makers
assert "Bob" in makers

# 2. 测试Work类型的Oset（验证通用性）
works = Oset[Work](
    [Work(omoospace, "Coding"), Work(omoospace, "Testing")], key="name"
)
assert "Coding" in works
assert Work(omoospace, "Testing") in works
assert "Design" not in works

```

### Utils

Normalize a Name
```python
from omoospace import normalize_name
assert normalize_name('Sc010_Shot0100.001') == 'Sc010_Shot0100'


### Copy to Clipboard

```python
from omoospace import copy_to_clipboard

copy_to_clipboard("text")
```

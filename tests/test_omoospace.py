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
        "Prop01.blend",
        "Prop02/001-ModelProp02.zpr",
        "Prop02/002-TextureProp02.spp",
        "Prop02/003-RenderProp02.blend",
        "Prop03/Prop03.blend",
        "Prop03/Part01.blend",
        "Prop03/Part02.blend",
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
        if o.name == "Prop01":
            assert len(o.subspaces) == 1
            assert len(o.children) == 0
        elif o.name == "Prop02":
            assert len(o.subspaces) == 1
            assert len(o.children) == 3
        elif o.name == "Prop03":
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


def test_omoospace_md_priority():
    """Test that Omoospace.md takes priority over Omoospace.yml when both exist."""
    omoos_path = Opath("temp", "MDPriorityProject").resolve()

    make_path(
        "contents/",
        {
            "Omoospace.md": """---
brief: From MD file
makers:
  TestMaker:
    email: test@example.com
---
# Content here is ignored
""",
            "Omoospace.yml": """
brief: From YAML file
""",
        },
        under=omoos_path,
    )

    omoospace = Omoospace(omoos_path)
    assert omoospace.root_dir == omoos_path
    # MD file should take priority
    assert omoospace.profile_file == Opath(omoos_path, "Omoospace.md")
    assert omoospace.brief == "From MD file"
    # Maker exists in MD frontmatter, can read without writing
    maker = omoospace.get_maker("TestMaker")
    assert maker.email == "test@example.com"


def test_omoospace_md_only():
    """Test that Omoospace works with only Omoospace.md present."""
    omoos_path = Opath("temp", "MDOnlyProject").resolve()

    make_path(
        "Contents/",
        {
            "Omoospace.md": """---
brief: MD only project
tools:
  Blender:
    version: "4.2.0"
---
# Just a markdown file
""",
        },
        under=omoos_path,
    )

    omoospace = Omoospace(omoos_path)
    assert omoospace.root_dir == omoos_path
    assert omoospace.profile_file == Opath(omoos_path, "Omoospace.md")
    assert omoospace.brief == "MD only project"
    # Tool exists in MD frontmatter, can read without writing
    tool = omoospace.get_tool("Blender")
    assert tool.version == "4.2.0"


def test_omoospace_yaml_fallback():
    """Test that Omoospace falls back to YAML when MD doesn't exist."""
    omoos_path = Opath("temp", "YAMLFallbackProject").resolve()

    make_path(
        "Contents/",
        {
            "Omoospace.yml": """
brief: YAML fallback project
tools:
  Houdini:
    version: "20.0"
""",
        },
        under=omoos_path,
    )

    omoospace = Omoospace(omoos_path)
    assert omoospace.root_dir == omoos_path
    assert omoospace.profile_file == Opath(omoos_path, "Omoospace.yml")
    assert omoospace.brief == "YAML fallback project"
    tool = omoospace.get_tool("Houdini")
    assert tool.version == "20.0"


def test_omoospace_md_empty_frontmatter_fallback():
    """Test that Omoospace falls back to YAML when MD has empty frontmatter."""
    omoos_path = Opath("temp", "EmptyFMFallbackProject").resolve()

    make_path(
        "Contents/",
        {
            "Omoospace.md": """# Just a title
No frontmatter here.
""",
            "Omoospace.yml": """
brief: Fallback from empty MD
""",
        },
        under=omoos_path,
    )

    omoospace = Omoospace(omoos_path)
    assert omoospace.root_dir == omoos_path
    # Should fall back to YAML since MD has no frontmatter
    assert omoospace.profile_file == Opath(omoos_path, "Omoospace.yml")
    assert omoospace.brief == "Fallback from empty MD"


def test_omoospace_md_read_only():
    """Test that Omoospace.md is read-only (writes redirect to YAML)."""
    omoos_path = Opath("temp", "MDReadOnlyProject").resolve()

    make_path(
        "Contents/",
        {
            "Omoospace.md": """---
brief: MD read-only test
---
# Markdown content
""",
        },
        under=omoos_path,
    )

    omoospace = Omoospace(omoos_path)
    assert omoospace.profile_file == Opath(omoos_path, "Omoospace.md")
    # Writing to MD should redirect to YAML file
    omoospace.brief = "Trying to write to MD"
    # After redirect, profile_file should be YAML
    assert omoospace.profile_file == Opath(omoos_path, "Omoospace.yml")
    assert omoospace.brief == "Trying to write to MD"

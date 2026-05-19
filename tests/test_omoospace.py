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
    assert omoospace.contents_dir == Opath(mini_omoos_path, "contents")
    assert omoospace.profile_file == Opath(mini_omoos_path, "OMOOSPACE.md")
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
    """Test that OMOOSPACE.md takes priority over Omoospace.yml when both exist."""
    omoos_path = Opath("temp", "MDPriorityProject").resolve()

    make_path(
        "contents/",
        {
            "OMOOSPACE.md": """---
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
    assert omoospace.profile_file == Opath(omoos_path, "OMOOSPACE.md")
    assert omoospace.brief == "From MD file"
    # Maker exists in MD frontmatter, can read without writing
    maker = omoospace.get_maker("TestMaker")
    assert maker.email == "test@example.com"


def test_omoospace_md_only():
    """Test that Omoospace works with only OMOOSPACE.md present."""
    omoos_path = Opath("temp", "MDOnlyProject").resolve()

    make_path(
        "contents/",
        {
            "OMOOSPACE.md": """---
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
    assert omoospace.profile_file == Opath(omoos_path, "OMOOSPACE.md")
    assert omoospace.brief == "MD only project"
    # Tool exists in MD frontmatter, can read without writing
    tool = omoospace.get_tool("Blender")
    assert tool.version == "4.2.0"


def test_omoospace_yaml_fallback():
    """Test that Omoospace falls back to YAML when MD doesn't exist."""
    omoos_path = Opath("temp", "YAMLFallbackProject").resolve()

    make_path(
        "contents/",
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


def test_omoospace_md_without_frontmatter():
    """Test that OMOOSPACE.md is used even without frontmatter block."""
    omoos_path = Opath("temp", "MDNoFrontmatterProject").resolve()

    make_path(
        "Contents/",
        {
            "OMOOSPACE.md": """# Just a title
No frontmatter here at all.
""",
            "Omoospace.yml": """
brief: This should be ignored
""",
        },
        under=omoos_path,
    )

    omoospace = Omoospace(omoos_path)
    assert omoospace.root_dir == omoos_path
    # OMOOSPACE.md should be used regardless of frontmatter presence
    assert omoospace.profile_file == Opath(omoos_path, "OMOOSPACE.md")


def test_omoospace_md_read_write():
    """Test that OMOOSPACE.md supports both read and write."""
    omoos_path = Opath("temp", "MDReadWriteProject").resolve()

    make_path(
        "contents/",
        {
            "OMOOSPACE.md": """---
brief: MD read-write test
---
# Markdown content
""",
        },
        under=omoos_path,
    )

    omoospace = Omoospace(omoos_path)
    assert omoospace.profile_file == Opath(omoos_path, "OMOOSPACE.md")
    # Writing to MD should stay on MD file
    omoospace.brief = "Now writing to MD"
    # Profile file should remain MD
    assert omoospace.profile_file == Opath(omoos_path, "OMOOSPACE.md")
    assert omoospace.brief == "Now writing to MD"


def test_omoospace_md_empty_frontmatter_read_write():
    """Test that OMOOSPACE.md with empty frontmatter can be read and written."""
    omoos_path = Opath("temp", "EmptyFMReadWrite").resolve()

    make_path(
        "Contents/",
        {
            "OMOOSPACE.md": """---
---
# Just a title
""",
        },
        under=omoos_path,
    )

    omoospace = Omoospace(omoos_path)
    # Empty frontmatter MD should still be recognized and used
    assert omoospace.profile_file == Opath(omoos_path, "OMOOSPACE.md")
    # Write should work and stay on MD file
    omoospace.brief = "New brief from test"
    assert omoospace.brief == "New brief from test"
    assert omoospace.profile_file == Opath(omoos_path, "OMOOSPACE.md")


def test_create_omoospace_generates_omoospace_md():
    """Test that create_omoospace generates OMOOSPACE.md by default."""
    omoospace = create_omoospace(
        "MDProject",
        under="temp",
        brief="Created with OMOOSPACE.md",
    )

    assert omoospace.profile_file == Opath("temp", "MDProject", "OMOOSPACE.md").resolve()
    assert omoospace.profile_file.exists()
    # Verify it's MD format (has frontmatter)
    content = omoospace.profile_file.read_text(encoding="utf-8")
    assert content.startswith("---")
    assert "brief: Created with OMOOSPACE.md" in content


def test_omoospace_md_roundtrip():
    """Test configuration roundtrip: read, modify, write, verify changes persist."""
    omoos_path = Opath("temp", "MDRoundtripProject").resolve()

    make_path(
        "contents/",
        {
            "OMOOSPACE.md": """---
brief: Initial brief
makers:
  TestDev:
    email: dev@example.com
---
# Project files
""",
        },
        under=omoos_path,
    )

    # Initial load
    omoospace = Omoospace(omoos_path)
    assert omoospace.profile_file == Opath(omoos_path, "OMOOSPACE.md")
    assert omoospace.brief == "Initial brief"
    assert omoospace.get_maker("TestDev").email == "dev@example.com"

    # Modify configuration
    omoospace.brief = "Updated brief"
    omoospace.add_maker("AnotherDev")

    # Reload to verify persistence
    omoospace2 = Omoospace(omoos_path)
    assert omoospace2.profile_file == Opath(omoos_path, "OMOOSPACE.md")
    assert omoospace2.brief == "Updated brief"
    assert omoospace2.get_maker("TestDev").email == "dev@example.com"
    assert omoospace2.get_maker("AnotherDev").email == None


def test_omoospace_md_with_subitems():
    """Test that OMOOSPACE.md can store makers, tools, works."""
    omoos_path = Opath("temp", "MDSubitemsProject").resolve()

    make_path(
        "contents/",
        {
            "OMOOSPACE.md": """---
brief: Subitems test
makers:
  LeadDev:
    email: lead@example.com
    website: https://lead.example.com
tools:
  Blender:
    version: "4.2.0"
    website: https://blender.org
works:
  TestVideo:
    brief: A test video
    version: "1.0.0"
---
# Content
""",
        },
        under=omoos_path,
    )

    omoospace = Omoospace(omoos_path)
    assert omoospace.brief == "Subitems test"

    maker = omoospace.get_maker("LeadDev")
    assert maker.email == "lead@example.com"
    assert maker.website == "https://lead.example.com"

    tool = omoospace.get_tool("Blender")
    assert tool.version == "4.2.0"
    assert tool.website == "https://blender.org"

    work = omoospace.get_work("TestVideo")
    assert work.brief == "A test video"
    assert work.version == "1.0.0"

    # Modify and persist
    tool.version = "4.3.0"
    omoospace.add_work({"name": "NewScene", "contents": ["Videos/new.mp4"]})

    # Reload and verify
    omoospace2 = Omoospace(omoos_path)
    assert omoospace2.get_tool("Blender").version == "4.3.0"
    assert omoospace2.get_work("NewScene") is not None


def test_create_omoospace_lowercase_defaults():
    """Test that create_omoospace uses lowercase directory names by default."""
    omoospace = create_omoospace(
        "LowercaseProject",
        under="temp",
        brief="Lowercase defaults test",
    )

    # Default directories should be lowercase
    assert omoospace.subspaces_dir.name == "subspaces"
    assert omoospace.contents_dir.name == "contents"
    assert omoospace.subspaces_dir.exists()
    assert omoospace.contents_dir.exists()


def test_omoospace_yaml_extension():
    """Test that Omoospace supports .yaml extension alongside .yml."""
    omoos_path = Opath("temp", "YAMLExtProject").resolve()

    make_path(
        "contents/",
        {
            "Omoospace.yaml": """
brief: From .yaml file
tools:
  Maya:
    version: "2024.0"
""",
        },
        under=omoos_path,
    )

    omoospace = Omoospace(omoos_path)
    assert omoospace.profile_file == Opath(omoos_path, "Omoospace.yaml")
    assert omoospace.brief == "From .yaml file"
    tool = omoospace.get_tool("Maya")
    assert tool.version == "2024.0"

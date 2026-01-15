import pytest
from omoospace import (
    normalize_name,
    copy_to_clipboard,
    Maker,
    Work,
    Omoospace,
    Opath,
    Oset,
    pyperclip,
)
from omoospace.utils import make_path


def test_opath(mini_omoos_path: Opath):
    root = mini_omoos_path
    make_path(
        "Prop01.blend",
        "Prop02/001-ModelProp02.zpr",
        "Prop02/002-TextureProp02.spp",
        "Prop02/003-RenderProp02.blend",
        "Prop03/Prop03.blend",
        "Prop03/Part01.blend",
        "Prop03/Part02.blend",
        under=root,
    )

    Opath(root / "Prop01.blend").copy_to(root / "Temp")
    assert (root / "Prop01.blend").exists()
    assert (root / "Temp" / "Prop01.blend").exists()

    # if the same, return self
    assert (
        Opath(root / "Prop01.blend").copy_to(root, overwrite=True)
        == root / "Prop01.blend"
    )

    # Asset.blend is already in Temp, copy fail
    with pytest.raises(FileExistsError):
        Opath(root / "Prop01.blend").copy_to(root / "Temp")

    # with overwrite=True, Prop01.blend in Temp will be overwritten
    Opath(root / "Prop01.blend").copy_to(root / "Temp", overwrite=True)
    assert (root / "Temp" / "Prop01.blend").exists()

    # Asset.blend is already in Temp, move fail
    with pytest.raises(FileExistsError):
        Opath(root / "Prop01.blend").move_to(root / "Temp")

    # with overwrite=True, Prop01.blend in Temp will be overwritten
    Opath(root / "Prop01.blend").move_to(root / "Temp", overwrite=True)
    assert (root / "Temp" / "Prop01.blend").exists()
    assert not (root / "Prop01.blend").exists()

    # copy folder Prop03 to Temp
    Opath(root / "Prop03").copy_to(root / "Temp")
    assert (root / "Prop03").exists()
    assert (root / "Temp" / "Prop03").exists()
    assert (root / "Temp" / "Prop03" / "Part01.blend").exists()
    assert (root / "Temp" / "Prop03" / "Part02.blend").exists()

    make_path("Prop03/PartC.blend", under=root)
    # Asset.blend is already in Temp, copy fail
    with pytest.raises(FileExistsError):
        Opath(root / "Prop03").copy_to(root / "Temp")

    # copy folder Prop03 to Temp
    Opath(root / "Prop03").copy_to(root / "Temp", overwrite=True)
    assert (root / "Temp" / "Prop03" / "PartC.blend").exists()


def test_oset(mini_omoos_path: Opath):
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


@pytest.mark.parametrize(
    "name, expected",
    [
        ("Sc010_001", "Sc010"),
        ("Sc010_Shot0100.v001", "Sc010_Shot0100"),
        ("Prop01 v001", "Prop01"),
        ("Prop01_autosave", "Prop01"),
        ("Prop01.autosave", "Prop01"),
        ("Asset_aa 001", "Asset_Aa"),
        ("Prop_01_autosave_v001", "Prop"),
        ("头骨2.v001", "头骨2"),
        ("头骨.2.0001", "头骨"),
        ("Prop头骨.0001", "Prop头骨"),
        ("Prop01-1.v3", "Prop01-1"),
        ("Prop01A.v3", "Prop01A"),
        ("Prop01a.v001", "Prop01a"),
        ("Prop01_recovered 1", "Prop01"),
        ("Prop01_recovered.v001", "Prop01"),
    ],
)
def test_normalize_name(name: str, expected: str):
    assert normalize_name(name) == expected


def test_copy_to_clipboard():
    try:
        copy_to_clipboard("The text to be copied to the clipboard.")
        assert pyperclip.paste() == "The text to be copied to the clipboard."
    except:
        pass

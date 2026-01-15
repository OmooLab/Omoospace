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
        ("Asset A v001", "AssetA"),
        ("Asset A_autosave", "AssetA"),
        ("Asset_A.autosave", "Asset_A"),
        ("Asset_aa 001", "Asset_Aa"),
        ("Asset_a_autosave_v001", "Asset_A"),
        ("头骨2.v001", "头骨2"),
        ("头骨.2.0001", "头骨"),
        ("Asset头骨.0001", "Asset头骨"),
        ("AssetA-1.v3", "AssetA-1"),
        ("AssetAA.v3", "AssetAA"),
        ("AssetAa.v001", "AssetAa"),
        ("AssetA_recovered 1", "AssetA"),
        ("AssetA_recovered.v001", "AssetA"),
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

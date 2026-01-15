import pytest
from omoospace import make_path, Opath, Omoospace
from shutil import copy


def test_en_profile():
    make_path(
        "Short01/Short01.blend",
        "Short01/CharA.blend",
        "Short02/Sc010.blend",
        "Short03/Prop01.c4d",
        "Short03/Prop01.blend",
        "Prop01.blend",
        "Contents/Models/Prop02/Prop02.fbx",
        "Contents/Models/Prop02/Textures/",
        "Contents/Models/Prop01.glb",
        "Contents/Videos/Short01.mp4",
        "Contents/Images/Short01_Cover.png",
        under="temp/AwesomeProject",
    )
    copy("tests/profile.en.yaml", "temp/AwesomeProject/Omoospace.yml")
    omoospace = Omoospace("temp/AwesomeProject")

    # read/write brief
    assert omoospace.brief == "An awesome IP project"
    omoospace.brief = "A fantastic project."
    assert omoospace.brief == "A fantastic project."
    assert omoospace.subspaces == [
        "Prop01.blend",
        "Short01",
        "Short01/Short01.blend",
        "Short01/CharA.blend",
        "Short03",
    ]

    # read notes
    assert omoospace.get_note("Client") == ["Tencent"]

    # add note to scope"Prop01"
    omoospace.add_note("Prop01", "Other note")
    assert omoospace.get_note("Prop01") == ["Other note"]

    # read makers
    maker = omoospace.get_maker("MaNan001")
    assert maker.email == "manan001@example.com"
    maker = omoospace.get_maker("MaNan002")
    assert maker.email == "manan002@example.com"
    assert maker.website == None
    maker = omoospace.get_maker("OmooLab")
    assert maker.email == "studio@omoolab.xyz"
    assert maker.website == "https://www.omoolab.xyz"

    # add maker
    maker = omoospace.add_maker("icrdr")
    assert len(omoospace.makers) == 4
    assert "icrdr" in omoospace.makers
    assert omoospace.makers == ["MaNan001", "MaNan002", "OmooLab", "icrdr"]

    # set email and website
    maker.email = "icrdr@abc.com"
    maker.website = "https://www.icrdr.com"
    assert maker.name == "icrdr"
    assert maker.email == "icrdr@abc.com"
    assert maker.website == "https://www.icrdr.com"

    # change name
    maker.name = "ICRDR"
    assert maker.name == "ICRDR"

    # remove maker
    omoospace.remove_maker("ICRDR")
    assert len(omoospace.makers) == 3

    # maker is removed, so it can not be removed again.
    with pytest.raises(AttributeError):
        maker.remove()

    tool = omoospace.get_tool("Houdini")
    assert tool.version == "20.0"
    assert tool.website == None

    tool = omoospace.get_tool("Blender")
    assert tool.version == "4.2.0"
    assert tool.website == "https://www.blender.org"
    assert tool.extensions == ["Omoospace", "BioxelNodes"]

    # edit tool Blender
    tool = omoospace.get_tool("Blender")
    tool.extensions = ["Omoospace"]
    assert "BioxelNodes" not in tool.extensions

    # get tool by name
    assert omoospace.get_tool("Blender").version == "4.2.0"

    # remove tool
    omoospace.remove_tool("Blender")
    assert len(omoospace.tools) == 2

    work = omoospace.get_work("AwesomeShort01")
    assert work.brief == "An awesome animated short."
    assert work.version == "1.0.0"
    assert work.contents == [
        "Videos/Short01.mp4",
        "Images/Short01_Cover.png",
    ]
    assert work.contributions["Animator"] == ["MaNan003", "MaNan002"]
    assert work.contributions["Director"] == ["MaNan001"]

    work = omoospace.get_work("AwesomeProp02")
    assert work.brief == None
    assert work.version == None
    assert work.contents == ["Models/Prop02/Prop02.fbx", "Models/Prop02/Textures"]
    assert len(work.contributions) == 0

    work.add_contribution("MaNan003", contribution="Modeler")
    assert work.contributions["Modeler"] == ["MaNan003"]
    assert work.contents == ["Models/Prop02/Prop02.fbx", "Models/Prop02/Textures"]

    # set contributions
    work.contributions = {
        "Modeler": ["manan", {"name": "manan2", "email": "manan2@example.com"}]
    }

    assert len(work.contributions["Modeler"]) == 2
    with pytest.raises(KeyError):
        assert len(work.contributions["Maker"]) == 0

    # delete content will affect work items
    Opath(omoospace.contents_dir, "Models").remove()
    assert len(work.contents) == 0

    # remove work
    omoospace.remove_work("AwesomeProp02")
    assert len(omoospace.works) == 2


def test_zh_profile():
    make_path(
        "动画短片01/动画短片01.blend",
        "动画短片01/角色A.blend",
        "道具01.blend",
        "Contents/Models/道具02/道具02.fbx",
        "Contents/Models/道具02/Textures/",
        "Contents/Models/道具01.glb",
        "Contents/Videos/动画短片01.mp4",
        "Contents/Images/动画短片01_封面.png",
        under="temp/超厉害IP项目",
    )
    copy("tests/profile.zh.yaml", "temp/超厉害IP项目/Omoospace.zh.yml")
    omoospace = Omoospace("temp/超厉害IP项目", language="zh")

    # read/write brief
    assert omoospace.brief == "一个超厉害的IP项目"
    omoospace.brief = "一个酷炫的项目"
    assert omoospace.brief == "一个酷炫的项目"
    assert omoospace.subspaces == [
        "道具01.blend",
        "动画短片01",
        "动画短片01/动画短片01.blend",
        "动画短片01/角色A.blend",
    ]

    # read notes
    assert omoospace.get_note("客户") == ["腾讯爸爸"]

    # read makers
    maker = omoospace.get_maker("马南001")
    assert maker.email == "manan001@example.com"
    maker = omoospace.get_maker("马南002")
    assert maker.email == "manan002@example.com"
    assert maker.website == None
    maker = omoospace.get_maker("偶魔数字")
    assert maker.email == "studio@omoolab.xyz"
    assert maker.website == "https://www.omoolab.xyz"

    tool = omoospace.get_tool("Houdini")
    assert tool.version == "20.0"
    assert tool.website == None

    tool = omoospace.get_tool("Blender")
    assert tool.version == "4.2.0"
    assert tool.website == "https://www.blender.org"
    assert tool.extensions == ["Omoospace", "BioxelNodes"]

    work = omoospace.get_work("超厉害短片01")
    assert work.brief == "一个超厉害的IP动画短片"
    assert work.version == "1.0.0"
    assert work.contents == [
        "Videos/动画短片01.mp4",
        "Images/动画短片01_封面.png",
    ]
    assert work.contributions["动画师"] == ["马南003", "马南002"]
    assert work.contributions["导演"] == ["马南001"]

    work = omoospace.get_work("超厉害道具02")
    assert work.brief == None
    assert work.version == None
    assert work.contents == ["Models/道具02/道具02.fbx", "Models/道具02/Textures"]
    assert len(work.contributions) == 0

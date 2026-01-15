import pytest
from omoospace import make_path, Opath, Omoospace


en_profile_content = """
brief: A great project.

ignore:
  - "Film02"
  - "Film03/Prop01.*"

notes:
  Film01_CharA:
    - "MaNan001: very good..."
    - "Open with Blender 5.0"
  Prop01: not game-ready.

makers:
  MaNan001:
    email: manan001@example.com
    website: https://www.manan.com
  MaNan002: manan002@example.com
  OmooLab:
    website: https://www.omoolab.xyz

tools:
  Blender:
    version: "v4.2.0"
    extensions:
      - Omoospace
      - BioxelNodes
    website: https://www.blender.org
  Houdini: "20.0.0"
  Omoospace:
    version: ">=0.2.0"
    website: https://omoolab.github.io/Omoospace/latest/

works:
  GreatFilm:
    brief: A great film.
    version: "1.0.0"
    contents:
      - Videos/Film01.mp4
      - Images/Film01_Cover.png
    contributions:
      Modeler:
        - MaNan003
      Animator: [MaNan002, MaNan003]
      Director: MaNan001
  GreatModel:
    - Models/Prop01/Prop01.fbx
    - Models/Prop01/Textures
  AnotherGreatModel: Models/Prop02.glb
"""


zh_profile_content = """
简述: 一个超厉害的项目.

记录列表:
  动画01_角色A:
    - "马南001: 做的不咋地..."
    - "请用 Blender 5.0 打开"
  道具01: 没法在游戏引擎中使用.

主创列表:
  马南001:
    邮箱: manan001@example.com
    网站: https://www.manan.com
  马南002: manan002@example.com
  偶魔数字:
    网站: https://www.omoolab.xyz

工具列表:
  Blender:
    版本: "v4.2.0"
    扩展列表:
      Omoospace: ">=0.2.0"
      BioxelNodes: "2.0.0"
    网站: https://www.blender.org
  Houdini: "20.0.0"
  Omoospace:
    网站: https://omoolab.github.io/Omoospace/latest/

作品列表:
  超厉害动画:
    简述: 一个超厉害的动画.
    版本: "1.0.0"
    内容列表:
      - 视频/动画01.mp4
      - 图片/动画01_封面.png
    贡献列表:
      模型师:
        - 马南003
      动画师: [马南002, 马南003]
      动画导演: 马南001
  超厉害模型:
    - 模型/道具01/道具01.fbx
    - 模型/道具01/贴图
  另一个超厉害模型: 模型/道具02.glb
"""


def test_en_profile():
    make_path(
        "Film01/Film01.blend",
        "Film01/CharA.blend",
        "Film02/Sc010.blend",
        "Film03/Prop01.c4d",
        "Film03/Prop01.blend",
        "Prop01.blend",
        "Contents/Models/Prop01/Prop01.fbx",
        "Contents/Models/Prop01/Textures/",
        "Contents/Models/Prop02.glb",
        "Contents/Videos/Film01.mp4",
        "Contents/Images/Film01_Cover.png",
        {
            "Omoospace.yml": en_profile_content,
        },
        under="temp/MiniProject",
    )

    omoospace = Omoospace("temp/MiniProject")

    # read/write brief
    assert omoospace.brief == "A great project."
    omoospace.brief = "A fantastic project."
    assert omoospace.brief == "A fantastic project."
    assert omoospace.subspaces == [
        "Prop01.blend",
        "Film01",
        "Film01/Film01.blend",
        "Film01/CharA.blend",
        "Film03",
    ]

    # read notes
    assert omoospace.get_note("Film01_CharA") == [
        "MaNan001: very good...",
        "Open with Blender 5.0",
    ]
    assert omoospace.get_note("Prop01") == ["not game-ready."]

    # add note to scope"Prop01"
    omoospace.add_note("Other note", "Prop01")
    assert omoospace.get_note("Prop01") == ["not game-ready.", "Other note"]

    # read makers
    maker = omoospace.get_maker("MaNan001")
    assert maker.email == "manan001@example.com"
    assert maker.website == "https://www.manan.com"
    maker = omoospace.get_maker("MaNan002")
    assert maker.email == "manan002@example.com"
    assert maker.website == None
    maker.website = "https://www.manan2.com"
    assert maker.website == "https://www.manan2.com"
    assert maker.email == "manan002@example.com"
    maker = omoospace.get_maker("OmooLab")
    assert maker.email == None
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

    work = omoospace.get_work("GreatFilm")
    assert work.brief == "A great film."
    assert work.version == "1.0.0"
    assert work.contents == [
        "Videos/Film01.mp4",
        "Images/Film01_Cover.png",
    ]
    assert work.contributions["Animator"] == ["MaNan003", "MaNan002"]
    assert work.contributions["Director"] == ["MaNan001"]

    work = omoospace.get_work("GreatModel")
    assert work.brief == None
    assert work.version == None
    assert work.contents == ["Models/Prop01/Prop01.fbx", "Models/Prop01/Textures"]
    assert len(work.contributions) == 0
    work.add_contribution("MaNan003", contribution="Modeler")
    assert work.contributions["Modeler"] == ["MaNan003"]
    assert work.contents == ["Models/Prop01/Prop01.fbx", "Models/Prop01/Textures"]

    work = omoospace.get_work("AnotherGreatModel")
    assert work.brief == None
    assert work.version == None
    assert work.contents == ["Models/Prop02.glb"]
    assert len(work.contributions) == 0

    work.brief = "A great model."
    assert work.brief == "A great model."
    assert work.contents == ["Models/Prop02.glb"]

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
    omoospace.remove_work("AnotherGreatModel")
    assert len(omoospace.works) == 2


def test_zh_profile():
    make_path(
        "动画01/动画01.blend",
        "动画01/角色A.blend",
        "道具01.blend",
        "Contents/模型/道具01/道具01.fbx",
        "Contents/模型/道具01/贴图/",
        "Contents/模型/道具02.glb",
        "Contents/视频/动画01.mp4",
        "Contents/图片/动画01_封面.png",
        {
            "Omoospace.zh.yml": zh_profile_content,
        },
        under="temp/MiniProject",
    )

    omoospace = Omoospace("temp/MiniProject", language="zh")
    # read/write brief
    assert omoospace.brief == "一个超厉害的项目."
    omoospace.brief = "一个超酷的项目."
    assert omoospace.brief == "一个超酷的项目."

    # read notes
    assert omoospace.get_note("动画01_角色A") == [
        "马南001: 做的不咋地...",
        "请用 Blender 5.0 打开",
    ]
    assert omoospace.get_note("道具01") == ["没法在游戏引擎中使用."]

    # add note to scope"Prop01"
    omoospace.add_note("其他记录", "道具01")
    assert omoospace.get_note("道具01") == ["没法在游戏引擎中使用.", "其他记录"]

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

    work = omoospace.get_work("超厉害动画")
    assert work.brief == "一个超厉害的动画."
    assert work.version == "1.0.0"
    assert work.contents == [
        "视频/动画01.mp4",
        "图片/动画01_封面.png",
    ]
    assert work.contributions["动画师"] == ["马南003", "马南002"]
    assert work.contributions["动画导演"] == ["马南001"]

    work = omoospace.get_work("超厉害模型")
    assert work.brief == None
    assert work.version == None
    assert work.contents == ["模型/道具01/道具01.fbx", "模型/道具01/贴图"]
    assert len(work.contributions) == 0
    work.add_contribution("马南003", contribution="模型师")
    assert work.contributions["模型师"] == ["马南003"]
    assert work.contents == ["模型/道具01/道具01.fbx", "模型/道具01/贴图"]

    work = omoospace.get_work("另一个超厉害模型")
    assert work.brief == None
    assert work.version == None
    assert work.contents == ["模型/道具02.glb"]
    assert len(work.contributions) == 0

    work.brief = "一个超酷的模型."
    assert work.brief == "一个超酷的模型."
    assert work.contents == ["模型/道具02.glb"]

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

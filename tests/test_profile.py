import pytest
from omoospace import make_path, Opath, Omoospace
from shutil import copy


def test_profile():
    make_path(
        "Short01/Short01.blend",
        "Short01/CharA.blend",
        "Short02/Sc010.blend",
        "Short03/Prop01.c4d",
        "Short03/Prop01.blend",
        "Prop01.blend",
        "contents/models/Prop02/Prop02.fbx",
        "contents/models/Prop02/Textures/",
        "contents/models/Prop01.glb",
        "contents/videos/Short01.mp4",
        "contents/images/Short01_Cover.png",
        under="temp/AwesomeProject",
    )
    copy("tests/profile.example.md", "temp/AwesomeProject/OMOOSPACE.md")
    omoospace = Omoospace("temp/AwesomeProject")

    # read/write description
    assert omoospace.description == "An awesome IP project"
    omoospace.description = "A fantastic project."
    assert omoospace.description == "A fantastic project."
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
    assert work.description == "An awesome animated short."
    assert work.version == "1.0.0"
    assert work.contents == [
        "videos/Short01.mp4",
        "images/Short01_Cover.png",
    ]
    assert work.contributions["Animator"] == ["MaNan003", "MaNan002"]
    assert work.contributions["Director"] == ["MaNan001"]

    work = omoospace.get_work("AwesomeProp02")
    assert work.description == None
    assert work.version == None
    assert work.contents == ["models/Prop02/Prop02.fbx", "models/Prop02/Textures"]
    assert len(work.contributions) == 0

    work.add_contribution("MaNan003", contribution="Modeler")
    assert work.contributions["Modeler"] == ["MaNan003"]
    assert work.contents == ["models/Prop02/Prop02.fbx", "models/Prop02/Textures"]

    # set contributions
    work.contributions = {
        "Modeler": ["manan", {"name": "manan2", "email": "manan2@example.com"}]
    }

    assert len(work.contributions["Modeler"]) == 2
    with pytest.raises(KeyError):
        assert len(work.contributions["Maker"]) == 0

    # delete content will affect work items
    Opath(omoospace.contents_dir, "models").remove()
    assert len(work.contents) == 0

    # remove work
    omoospace.remove_work("AwesomeProp02")
    assert len(omoospace.works) == 2

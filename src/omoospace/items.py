from typing import Optional, TypedDict, Union

from omoospace.common import ProfileItem
from omoospace.utils import AnyPath, Opath, Oset, make_path
from omoospace.validators import is_email, is_url, is_version


class MakerDict(TypedDict):
    name: str
    email: Optional[str]
    website: Optional[str]


class Maker(ProfileItem):
    """Maker

    Attributes:
        name (str): Maker name
        email (str, optional): Maker email
        website (str, optional): Maker website.
    """

    _dict_name = "makers"

    def __init__(self, omoospace, maker: Union[str, MakerDict, "Maker"]):
        if isinstance(maker, str):
            super().__init__(omoospace, maker)

        elif isinstance(maker, dict) and "name" in maker:
            super().__init__(omoospace, maker["name"])
            if "email" in maker:
                self.email = maker["email"]

            if "website" in maker:
                self.website = maker["website"]

        elif isinstance(maker.name, str):
            super().__init__(omoospace, maker.name)

            if maker.email:
                self.email = maker.email

            if maker.website:
                self.website = maker.website
        else:
            raise ValueError(f"{maker} is not a valid Maker.")

    @property
    def email(self) -> Optional[str]:
        """Get the email from the latest profile data."""
        if isinstance(self.data, str):
            return self.data

        return self.get("email")

    @email.setter
    def email(self, value: str):
        if value and (not is_email(value)):
            raise ValueError(f"{value} is not a valid email.")

        if isinstance(self.data, str):
            self.data = value

        self.set("email", value)

    @property
    def website(self) -> Optional[str]:
        """Get the website from the latest profile data."""
        return self.get("website")

    @website.setter
    def website(self, value: str):
        if value and (not is_url(value)):
            raise ValueError(f"{value} is not a valid url.")

        if isinstance(self.data, str):
            self.set("email", self.data)

        self.set("website", value)


class ToolDict(TypedDict):
    name: str
    version: Optional[str]
    website: Optional[str]
    extensions: Optional[Union[list[str], set[str]]]


class Tool(ProfileItem):
    """Tool

    Attributes:
        name (str): Tool name
        version (str): Tool version.
        website (str): Tool url.
        extensions (Union[list[str], set[str]], optional): Tool extensions.
    """

    _dict_name = "tools"

    def __init__(self, omoospace, tool: Union[str, ToolDict, "Tool"]):
        if isinstance(tool, str):
            super().__init__(omoospace, tool)

        elif isinstance(tool, dict) and "name" in tool:
            super().__init__(omoospace, tool["name"])
            if "version" in tool:
                self.version = tool["version"]

            if "website" in tool:
                self.website = tool["website"]

            if "extensions" in tool:
                self.extensions = tool["extensions"]

        elif isinstance(tool.name, str):
            super().__init__(omoospace, tool.name)

            if tool.version:
                self.version = tool.version

            if tool.website:
                self.website = tool.website

            if tool.extensions:
                self.extensions = tool.extensions
        else:
            raise ValueError(f"{tool} is not a valid Tool.")

    @property
    def version(self) -> Optional[str]:
        """Get the version from the latest profile data."""
        if isinstance(self.data, str):
            return self.data.removeprefix("v")

        return (v := self.get("version")) and v.removeprefix("v")

    @version.setter
    def version(self, value: str):
        if value and (not is_version(value)):
            raise ValueError(f"{value} is not a valid version.")

        version = value.removeprefix("v")

        if isinstance(self.data, str):
            self.data = version

        self.set("version", version)

    @property
    def website(self) -> Optional[str]:
        """Get the website from the latest profile data."""
        return self.get("website")

    @website.setter
    def website(self, value: str):
        if value and (not is_url(value)):
            raise ValueError(f"{value} is not a valid url.")

        if isinstance(self.data, str):
            self.set("version", self.data)

        self.set("website", value)

    @property
    def extensions(self) -> Oset[str]:
        """Oset[str]: Tool extensions set."""
        extensions = self.get("extensions") or []
        return Oset(extensions)

    @extensions.setter
    def extensions(self, value: Union[list[str], set[str]]):

        if isinstance(self.data, str):
            self.set("version", self.data)

        self.set("extensions", list(set(value)))


class WorkDict(TypedDict):
    name: str
    brief: Optional[str]
    version: Optional[str]
    contents: Optional[Union[list[str], set[str]]]
    contributions: Optional[
        Union[
            dict[str, Union[list[Union[str, MakerDict, Maker]], Oset[Maker]]],
            list[Union[str, MakerDict, Maker]],
            Oset[Maker],
        ]
    ]


class Work(ProfileItem):
    """Work"""

    _dict_name = "works"

    def __init__(self, omoospace, work: Union[str, WorkDict, "Work"]):
        if isinstance(work, str):
            super().__init__(omoospace, work)

        elif isinstance(work, dict) and "name" in work:
            super().__init__(omoospace, work["name"])
            if "brief" in work:
                self.brief = work["brief"]

            if "version" in work:
                self.version = work["version"]

            if "contents" in work:
                self.contents = work["contents"]

            if "contributions" in work:
                self.contributions = work["contributions"]

        elif isinstance(work.name, str):
            super().__init__(omoospace, work.name)

            if work.brief:
                self.brief = work.brief

            if work.version:
                self.version = work.version

            if work.contents:
                self.contents = work.contents

            if work.contributions:
                self.contributions = work.contributions
        else:
            raise ValueError(f"{work} is not a valid Work.")

    @property
    def brief(self) -> Optional[str]:
        """Get the brief from the latest profile data."""
        return self.get("brief")

    @brief.setter
    def brief(self, value: str):

        if isinstance(self.data, list):
            self.set("contents", self.data)
        if isinstance(self.data, str):
            self.set("contents", [self.data])

        self.set("brief", value)

    @property
    def version(self) -> Optional[str]:
        """Get the version from the latest profile data."""
        return (v := self.get("version")) and v.removeprefix("v")

    @version.setter
    def version(self, value: str):
        if value and (not is_version(value)):
            raise ValueError(f"{value} is not a valid version.")

        if isinstance(self.data, list):
            self.set("contents", self.data)
        if isinstance(self.data, str):
            self.set("contents", [self.data])

        self.set("version", value.removeprefix("v"))

    @property
    def contents(self) -> Oset[str]:
        """set[str]: Work contents set."""
        contents = []

        if isinstance(self.data, list):
            contents = self.data
        elif isinstance(self.data, str):
            contents = [self.data]
        elif isinstance(self.data, dict):
            contents = self.get("contents") or []

        contents = Oset(
            filter(
                lambda x: self._omoospace.is_content(self._omoospace.contents_dir / x),
                contents,
            )
        )
        return contents

    @contents.setter
    def contents(self, value: Union[list[str], set[str]]):
        contents = list(
            set(
                filter(
                    lambda x: self._omoospace.is_content(
                        self._omoospace.contents_dir / x
                    ),
                    value,
                )
            )
        )

        if isinstance(self.data, str) or isinstance(self.data, list):
            self.data = contents

        self.set("contents", contents)

    @property
    def contributions(self) -> dict[str, Oset[str]]:
        """dict[str, list[Maker]]: Work contributions list."""
        contributions_dict = self.get("contributions") or {}
        contributions = {}
        for contribution, names in contributions_dict.items():
            names = [names] if isinstance(names, str) else names
            contributions[contribution] = Oset[str](names)

        return contributions

    @contributions.setter
    def contributions(
        self,
        value: Union[
            dict[str, Union[list[Union[str, MakerDict, Maker]], Oset[Maker]]],
            list[Union[str, MakerDict, Maker]],
            Oset[Maker],
        ],
    ):
        # set makers to omoospace
        contributions = {}
        if isinstance(value, list):
            contributions["Maker"] = list(
                set([Maker(self._omoospace, maker).name for maker in value])
            )
        elif isinstance(value, dict):
            for contribution, makers in value.items():
                contributions[contribution] = list(
                    set([Maker(self._omoospace, maker).name for maker in makers])
                )
        elif isinstance(value, Oset):
            contributions["Maker"] = list(value.to_set())

        if isinstance(self.data, list):
            self.set("contents", self.data)
        if isinstance(self.data, str):
            self.set("contents", [self.data])

        self.set("contributions", contributions)

    def add_contribution(
        self,
        *makers: list[Union[str, MakerDict, Maker]],
        contribution: str = None,
    ):
        """Add contribution to this omoospace.

        Args:
            makers (list[Union[str, MakerDict, Maker]]): Makers list.
            contribution (str, optional): Contribution type. Defaults to "Maker".
        """
        contribution = contribution or self._key("Maker")

        contributions = self.contributions
        if contribution not in contributions:
            contributions[contribution] = Oset[str]()

        names = []
        for maker in makers:
            if isinstance(maker, Maker):
                names.append(maker.name)
            elif isinstance(maker, str):
                names.append(maker)
            elif isinstance(maker, MakerDict) and "name" in maker:
                names.append(maker["name"])

        contributions[contribution].update(names)
        self.contributions = contributions

    # def export(
    #     self,
    #     to: AnyPath = ".",
    #     reveal_in_explorer: bool = False,
    # ):

    #     work_path = Opath(to, self.name).resolve()

    #     # Check if work dir exists
    #     if work_path.is_dir():
    #         work_path.remove()

    #     items: list[Opath] = [self.contents_dir / i for i in self.contents]

    #     try:
    #         make_path(
    #             {
    #                 f"{self.name}/Package.yml": f"""
    #             name: {self.name}
    #             version: {self.version}
    #             """,
    #             },
    #             under=to,
    #         )

    #         for i in range(len(items)):
    #             item = items[i]
    #             item_relpath = item.relative_to(self.root_dir)
    #             item.copy_to(Opath(work_path, item_relpath))

    #     except Exception as err:
    #         # Delete all if failed.
    #         work_path.remove()
    #         raise Exception("Fail to export Package", err)

    #     if reveal_in_explorer:
    #         work_path.reveal_in_explorer()

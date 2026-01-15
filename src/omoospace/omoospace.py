from enum import Enum
from typing import Optional, Union
from nutree import Tree, Node
from omoospace.common import Profile, NodeData
from omoospace.items import (
    Maker,
    MakerDict,
    Tool,
    ToolDict,
    Work,
    WorkDict,
)
from omoospace.language import ALLOWED_LANGS, Language
from omoospace.utils import Oset, make_path, normalize_name, Opath, AnyPath
from omoospace.validators import is_ignore


class ObjectiveType(Enum):
    DIRECTORY = "directory"
    FILE = "file"
    PHANTOM = "phantom"


class Objective:
    """Objective represents a node in the objective tree structure.

    This class encapsulates a node in the objective hierarchy, providing
    properties and methods to access and manipulate its data, subspaces,
    and relationships with other objectives.
    """

    def __init__(self, node: Node):
        """Initialize an Objective instance.

        Args:
            node (Node): The underlying nutree Node object that this
                Objective wraps.
        """
        self._node = node

    def __repr__(self) -> str:
        """Return a string representation of the Objective.

        Returns:
            str: The name of the objective.
        """
        return self.name

    def __contains__(self, name: str) -> bool:
        """Implement ``name in tree`` syntax to check for node existence."""
        return bool(self._node.find(match=lambda n: n.data.name == name))

    def __iter__(self):
        """Make ``for obj in tree`` iterate over all nodes."""
        iter = self._node.__iter__()
        return (Objective(n) for n in iter)

    @property
    def name(self) -> str:
        """str: Objective node name."""
        return self._node.data.name

    @property
    def root_dir(self) -> Opath:
        """Opath: Objective root_dir path (directory subspace only)."""
        for subspace in self.subspaces:
            if subspace.is_dir():
                return subspace
        return None

    @property
    def type(self) -> ObjectiveType:
        """ObjectiveType: Objective type."""

        not_phantom = False
        for subspace in self.subspaces:
            names = normalize_name(subspace.stem).split("_")
            if self.name == names[-1]:
                not_phantom = True
                break

        if not_phantom:
            return ObjectiveType.DIRECTORY if self.root_dir else ObjectiveType.FILE
        else:
            return ObjectiveType.PHANTOM

    @property
    def subspaces(self) -> Oset["Subspace"]:
        """list[Opath]: Objective subspaces."""
        return Oset(
            [Subspace(subspace) for subspace in self._node.data.subspaces],
            key="path",
        )

    @property
    def pathname(self) -> str:
        """str: Objective path name."""
        parts = self.path.split("/")[1:]
        return "_".join(parts)

    @property
    def path(self) -> str:
        """str: Objective path."""
        return self._node.path

    @property
    def parent(self) -> "Objective":
        """Objective: Parent subspace."""
        node = self._node.parent
        return Objective(node) if node else None

    @property
    def children(self) -> list["Objective"]:
        """list["Objective"]: Children subspace."""
        nodes = self._node.children
        return [Objective(node) for node in nodes]


class ObjectiveTree:
    """Objective tree structure for managing objectives hierarchy."""

    def __init__(self, omoospace: "Omoospace"):
        self._tree = Tree()
        self.omoospace = omoospace
        for subspace in self.omoospace.subspaces:
            node_iter: Union[Node, Tree] = self._tree

            # extract objective data list from the subspace.
            path_data = Omoospace.extract_path_data(subspace)

            # add single objective path from top to bottom to the tree.
            for data in path_data:
                node = next(
                    (n for n in node_iter.children if n.data.name == data.name), None
                )

                if node is None:
                    node = node_iter.add(data)
                else:
                    node.data.subspaces = list(
                        set(node.data.subspaces + data.subspaces)
                    )

                node_iter = node

    def __contains__(self, name: str) -> bool:
        """Implement ``name in tree`` syntax to check for node existence."""
        return bool(self._tree.find(match=lambda n: n.data.name == name))

    def __len__(self):
        """Make ``len(tree)`` return the number of nodes
        (also makes empty trees falsy)."""
        return self._tree.__len__()

    def __iter__(self):
        """Make ``for obj in tree`` iterate over all nodes."""
        iter = self._tree.__iter__()
        return (Objective(n) for n in iter)

    @property
    def count(self) -> int:
        """Get the number of nodes in the tree.

        Returns:
            int: The number of nodes in the tree.
        """
        return self._tree.count

    def format(self, *, repr=None, style=None, join="\n") -> str:
        """Format the objective tree to a string.

        Returns:
            str: The formatted objective tree string.
        """
        return self._tree.format(
            repr=repr, style=style, title=self.omoospace.name, join=join
        )

    def get(self, name_or_pathname: str) -> Optional[Objective]:
        """Get objective by path name.

        Args:
            name_or_pathname (str): Input path name to locate the objective.

        Returns:
            Objective: The found objective, or None if not found.
        """

        n = self._tree.find(match=lambda node: node.data.name == name_or_pathname)
        if n is None:
            n = self._tree.find(
                match=lambda node: node.path
                == "/" + "/".join(name_or_pathname.split("_"))
            )

        return Objective(n) if n else None


class Subspace(Opath):
    """Subspace class."""

    @property
    def path(self) -> str:
        """str: Relative path string of this subspace."""
        # get path of this subspace to the subspaces folder
        omoospace = Omoospace(self)
        path = self.relative_to(omoospace.subspaces_dir)
        return path.as_posix()

    @property
    def pathname(self) -> str:
        """str: Pathname of this subspace."""
        return Omoospace.extract_pathname(self)

    @property
    def objective(self) -> Objective:
        """Objective: Objective of this subspace."""
        return Omoospace.extract_objective(self)

    @property
    def subspaces(self) -> Oset["Subspace"]:
        """list[Opath]: Objective subspaces."""
        omoospace = Omoospace(self)

        # get all subspaces which has same pathname prefix as this subspace
        subspaces = Oset[Subspace](key="path")
        for s in omoospace.subspaces:
            if s.pathname.startswith(self.pathname):
                subspaces.add(s)

        return subspaces


class Omoospace(Profile):
    """The main class representing an Omoospace instance.

    An Omoospace class instance always refers to an existing Omoospace directory, not a dummy.

    Usage:
    ```python
    omoospace = Omoospace('path/to/omoospace')
    ``
    """

    def __init__(self, detect_dir: AnyPath, language: Language = None):
        """Initialize from an existing Omoospace."""

        if language and language not in ALLOWED_LANGS:
            raise ValueError(f"{language} is not a valid language.")

        detect_path = Opath(detect_dir).resolve()
        detect_path_parents = [detect_path, *detect_path.parents]

        for detect_path_parent in detect_path_parents:
            # Find a file named 'Omoospace' with any extension (or no extension)
            candidates = list(Opath(detect_path_parent).glob("Omoospace.*"))
            candidates = [c for c in candidates if c.is_file()]
            if len(candidates) == 0:
                continue

            self.root_dir = detect_path_parent
            if language:
                self.profile_file = self.root_dir / f"Omoospace.{language}.yml"
                return
            else:
                default = self.root_dir / f"Omoospace.yml"
                self.profile_file = next(
                    (c for c in candidates if c.suffix == ".yml"), default
                )
                return

        raise FileNotFoundError(f"Omoospace not found in {detect_dir}")

    @classmethod
    def extract_path_data(cls, path: AnyPath) -> list[NodeData]:
        """Extract objective data from a subspace.

        Args:
            path (AnyPath): The subspace to extract objectives from.

        Returns:
            list[NodeData]: The list of objective data extracted from the subspace.
        """
        subspace = Opath(path).resolve()
        omoospace = cls(subspace)

        if not omoospace.is_subspace(subspace):
            raise ValueError(f"{subspace} is not a valid subspace.")

        # Get path parts. remove those directory that is not subspace.
        subspaces = [subspace]
        for parent in subspace.parents:
            if omoospace.is_subspace(parent):
                subspaces.append(parent)
        subspaces.reverse()

        # init objectives list
        objectives: list[NodeData] = []

        for subspace in subspaces:
            prev_names = [d.name for d in objectives]
            prev_count = len(prev_names)

            # Normalize subspace name for objective name
            subspace_name = normalize_name(subspace.stem)

            # Objective names are the strings that splited by "_".
            # e.g. `Seq010_Shot0100.blend` has two objective (names): `Seq010` and `Shot0100`
            names: list[str] = subspace_name.split("_")

            # clip matched path names as mush as possible.
            # e.g. path: ['Seq010'], enity name: `Seq010_Shot0100.blend`
            # `Seq010` is the matched namespace, which will be cliped.
            for i in range(prev_count):
                suffix = "_".join(prev_names[i:])
                prefix = "_".join(names[: prev_count - i])
                if suffix == prefix:
                    names = names[prev_count - i :]
                    break

            # Append objective to list
            for name in names:
                objectives.append(NodeData(name, [subspace]))

            # Sometimes all namspaces are cliped. but still need to append subspace
            if len(names) == 0:
                objectives[-1].subspaces.append(subspace)

        return objectives

    @classmethod
    def extract_pathname(cls, path: AnyPath) -> str:
        """Get subspace's pathname.

        Args:
            path (AnyPath): Input path name to locate the objective.

        Returns:
            str: Objective pathname.
        """
        path_data = cls.extract_path_data(path)
        return "_".join([d.name for d in path_data])

    @classmethod
    def extract_objective(cls, path: AnyPath) -> Optional[Objective]:
        """Get objective by objective path or subspace.

        Args:
            path (AnyPath): Input path name to locate the objective.

        Returns:
            Optional[Objective]: The wanted objective.
        """
        pathname = cls.extract_pathname(path)
        omoospace = cls(path)
        return omoospace.objective_tree.get(pathname)

    @property
    def language(self) -> str:
        """str: Omoospace language."""
        parts = self.profile_file.stem.split(".")
        return parts[-1] if len(parts) > 1 else "en"

    @property
    def _profile(self) -> Profile:
        """Get the profile of the Omoospace.

        Returns:
            Profile: The profile of the Omoospace.
        """
        return Profile(self.profile_file)

    @property
    def name(self) -> str:
        """str: Omoospace name."""
        return self.root_dir.name

    @property
    def brief(self) -> str:
        """str: Omoospace name. Prefer Omoospace.yml, fallback to folder name."""
        brief = self.get("brief")
        return brief or self.name

    @brief.setter
    def brief(self, value):
        """Set the Omoospace brief.

        Args:
            value (str): The new brief to set for the Omoospace.
        """
        self.set("brief", value)

    @property
    def subspaces_dir(self) -> Opath:
        """Opath: Subspaces directory path."""
        subspaces_dirname = self.get("subspaces_dir") or "Subspaces"
        subspaces_dir = self.root_dir / subspaces_dirname
        return subspaces_dir if subspaces_dir.is_dir() else self.root_dir

    @subspaces_dir.setter
    def subspaces_dir(self, value):
        """Set the subspaces directory mapping.

        Args:
            value (str): The new directory name to map to 'Subspaces'.
        """
        self.set("subspaces_dir", value)

    @property
    def contents_dir(self) -> Opath:
        """Opath: Contents directory path."""
        contents_dirname = self.get("contents_dir") or "Contents"
        return self.root_dir / contents_dirname

    @contents_dir.setter
    def contents_dir(self, value):
        """Set the contents directory mapping.

        Args:
            value (str): The new directory name to map to 'Contents'.
        """
        self.set("contents_dir", value)

    @property
    def makers(self) -> Oset[Maker]:
        """Oset[Maker]: Maker set."""
        makers_dict = self.get("makers") or {}
        return Oset[Maker]([Maker(self, name) for name in makers_dict.keys()])

    @property
    def tools(self) -> Oset[Tool]:
        """Oset[Tool]: Tool set."""
        tools_dict = self.get("tools") or {}
        return Oset[Tool]([Tool(self, name) for name in tools_dict.keys()])

    @property
    def works(self) -> Oset[Work]:
        """Oset[Work]: Work set."""
        works_dict = self.get("works") or {}
        return Oset[Work]([Work(self, name) for name in works_dict.keys()])

    @property
    def subspaces(self) -> Oset[Subspace]:
        """Oset[Subspace]: the subspaces in the subspaces directory."""
        return Oset(
            [
                Subspace(p)
                for p in self.subspaces_dir.get_children()
                if self.is_subspace(p)
            ],
            key="path",
        )

    @property
    def objective_tree(self) -> ObjectiveTree:
        """ObjectiveTree: The objective tree of this omoospace."""
        return ObjectiveTree(self)

    def is_subspace(self, path: AnyPath, require_exists: bool = True) -> bool:
        """Check if a path is a subspace.

        Args:
            path (AnyPath): The path to check.
            require_exists (bool, optional): Whether to require the path to exist.
                Defaults to True.

        Returns:
            bool: True if the path is a subspace, False otherwise.
        """
        path = Opath(path).resolve()

        exists = path.exists() if require_exists else True
        in_subspaces = path.is_under(self.subspaces_dir)
        not_profile_file = not (
            path.name.startswith("Omoospace.") and path.parent == self.root_dir
        )
        not_readme = "README.md" not in path.name
        not_contents = not path.is_under(self.contents_dir, or_equal=True)

        # Early exit if basic conditions aren't met
        if not (
            exists and in_subspaces and not_contents and not_profile_file and not_readme
        ):
            return False

        # Get ignore patterns from YAML
        ignore = self.get("ignore")
        if not ignore:
            return True

        n = path.relative_to(self.subspaces_dir).as_posix()
        return not is_ignore(n, ignore)

    def is_content(self, path: AnyPath, require_exists: bool = True) -> bool:
        """Check if path is contents item

        Args:
            path (AnyPath): Input path to check.
            require_exists (bool, optional): Whether to require the path to exist.
                Defaults to True.

        Returns:
            bool: True if the path is a content item, False otherwise.
        """
        path = Opath(path).resolve()

        exists = path.exists() if require_exists else True
        in_contents = path.is_under(self.contents_dir)

        return exists and in_contents

    def is_item(self, path: AnyPath, require_exists: bool = True) -> bool:
        """Check if path is this omoospace item.

        Args:
            path (AnyPath): Input path to check.
            require_exists (bool, optional): Whether to require the path to exist.
                Defaults to True.

        Returns:
            bool: True if the path is an Omoospace item, False otherwise.
        """
        path = Opath(path).resolve()
        exists = path.exists() if require_exists else True
        in_omoospace = path.is_under(self.root_dir)
        not_profile_file = "Omoospace." not in path.name

        return exists and in_omoospace and not_profile_file

    def add_subspace(
        self,
        name: str,
        under: str = None,
        collect_children: bool = True,
        reveal_in_explorer: bool = False,
    ) -> Subspace:
        """Add subspace to this omoospace."""
        parent_path = Opath(under).resolve() if under else self.subspaces_dir

        # Check if is valid folder
        if not parent_path.is_dir():
            raise FileExistsError(f"{under} already exists.")

        # Check if is in Subspaces
        if not Opath(parent_path).is_under(self.subspaces_dir, or_equal=True):
            raise ValueError(f"{under} is not a valid place.")

        subspace_name = normalize_name(name)
        subspace = Opath(parent_path, subspace_name).resolve()

        # Check if exists
        if subspace.is_dir():
            raise FileExistsError(f"{subspace} already exists.")

        # create subspace folder
        try:
            make_path(
                f"{subspace_name}/",
                under=parent_path,
            )
        except Exception as err:
            raise err

        # collect children that matched.
        if collect_children:
            children = parent_path.get_children(recursive=False)

            def is_match(child: Opath):
                not_itself = child.name != subspace_name
                is_match = False

                child_node_names = normalize_name(child.name).split("_")
                subspace_node_names = subspace_name.split("_")
                for i in range(len(subspace_node_names)):
                    subspace_suffix = "_".join(subspace_node_names[i:])
                    child_prefix = "_".join(
                        child_node_names[: len(subspace_node_names) - i]
                    )
                    if subspace_suffix == child_prefix:
                        is_match = True
                        break

                return not_itself and is_match

            # Remove subspace that not match the name
            children = list(filter(is_match, children))

            for child in children:
                try:
                    child.move_to(subspace)
                except Exception as err:
                    raise err

        if reveal_in_explorer:
            subspace.reveal_in_explorer()

        return Subspace(subspace)

    def get_note(self, scope: str) -> Optional[list[str]]:
        """Get note by name."""
        notes_dict = self.get("notes") or {}
        notes = notes_dict.get(scope) or []
        # if notes_dict.get(scope) is not a list, change to a list
        if not isinstance(notes, list):
            notes = [notes]

        return notes

    def add_note(self, note: str, scope: str = None):
        """Add note to this omoospace.

        Args:
            note (str): Note content.
        """
        notes_dict = self.get("notes") or {}
        nodes = self.get_note(scope)

        notes_dict[scope] = nodes + [note]
        self.set("notes", notes_dict)

    def get_maker(self, name: str) -> Optional[Maker]:
        """Get maker by name."""
        return self.makers.get(name)

    def add_maker(self, maker: Union[str, MakerDict, Maker]) -> Maker:
        """Add maker if not exists."""
        return Maker(self, maker)

    def remove_maker(self, name: str):
        """Remove maker."""
        (c := self.get_maker(name)) and c.remove()

    def get_tool(self, name: str) -> Optional[Tool]:
        """Get Tool by name."""
        return self.tools.get(name)

    def add_tool(self, tool: Union[str, ToolDict, Tool]) -> Tool:
        """Add tool if not exists."""
        return Tool(self, tool)

    def remove_tool(self, name: str):
        """Remove tool from this omoospace."""
        # Update profile
        (t := self.get_tool(name)) and t.remove()

    def get_work(self, name: str) -> Optional[Work]:
        """Get Work by name."""
        return self.works.get(name)

    def add_work(self, *work: Union[list[str], str, WorkDict, Work]) -> Work:
        """Set work if not exists."""
        if all(isinstance(arg, str) for arg in work):
            contents = list(set(work))
            name = contents[0].split("/")[-1].split(".")[0]
            return Work(self, {"name": name, "contents": contents})

        elif len(work) == 1 and isinstance(work[0], dict) and "name" in work[0]:
            return Work(self, work[0])

        elif len(work) == 1 and isinstance(work[0].name, str):
            return Work(self, work[0])

        else:
            raise ValueError(f"{work} is not a valid work.")

    def remove_work(self, name: str):
        """Remove work from this omoospace."""
        # Update profile
        (w := self.get_work(name)) and w.remove()

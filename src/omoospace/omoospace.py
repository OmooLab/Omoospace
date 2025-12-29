from pathlib import Path
import shutil
from typing import TypedDict, Union, get_args
from zipfile import ZipFile

from omoospace.directory import DirectoryTree, Entity, Route, Structure
from omoospace.exceptions import (
    CreateFailed,
    EmptyError,
    ExistsError,
    InvalidError,
    MoveFailed,
    NotFoundError,
    NotIncludeError,
)
from omoospace.package import Package
from omoospace.subspace import Subspace, SubspaceTree, get_entities, get_route
from omoospace.common import ProfileContainer, ProfileItem, ProfileItemList, yaml
from omoospace.utils import (
    format_name,
    remove_duplicates,
    reveal_directory,
    is_subpath,
    copy_to,
)

from omoospace.validators import is_email, is_url, is_version


class Creator(ProfileItem):
    """Creator

    Attributes:
        email (str): Creator email
        name (str): Creator name
        website (str, optional): Creator website.
        role (str, optional): Creator role in omoospace.
    """

    name: str
    email: str
    role: str
    website: str
    _item_list_key = "creators"
    _item_id_key = "email"


class Plugin(TypedDict):
    name: str
    version: str


class Software(ProfileItem):
    """Software

    Attributes:
        name (str): Software name
        version (str): Software version.
    """

    name: str
    version: str
    _item_list_key = "softwares"
    _item_id_key = "name"

    @property
    def plugins(self) -> list[Plugin]:
        """list[Plugin]: Software plugin list."""
        plugins = self._get_data("plugins") or []
        # remove plugin that is not dict
        plugins = [plugin for plugin in plugins if isinstance(plugin, dict)]

        # remove plugin that key value is None
        plugins = [plugin for plugin in plugins if plugin.get("name")]

        # remove duplicates in key
        plugins = remove_duplicates(plugins, "name")

        # reassign modified data
        self._set_data("plugins", plugins)

        return plugins

    def set_plugin(self, name: str, version: str):
        """Add or change plugin.

        Args:
            name (str): Plugin name.
            version (str): Plugin version.
        """
        plugins = self.plugins
        for i, plugin in enumerate(plugins):
            if plugin["name"] == name:
                plugins[i] == {"name": name, "verison": version}
                self._set_data("plugins", plugins)
                return

        plugins.append({"name": name, "verison": version})
        self._set_data("plugins", plugins)


class Work(ProfileItem):
    """Work

    Attributes:
        name (str): Work name.
        description (str): Work description.
    """

    name: str
    description: str
    _item_list_key = "works"
    _item_id_key = "name"

    @property
    def items(self) -> list[str]:
        """list[str]: Work item list."""
        items = self._get_data("items")

        # to remove invaild items
        item_paths = self._container._to_work_item_paths(items)
        vaild_items = self._container._to_work_items(item_paths)

        self._set_data("items", vaild_items)
        return vaild_items

    def add_item(self, *items: str):
        """Add item to this work.

        Args:
            *items (str): Item paths.
        """
        items = self._container._to_work_items(items)
        # remove duplicates
        self._set_data("items", list(dict.fromkeys([*self.items, *items])))

    def set_items(self, *items: str):
        """Set items to this work. Replace current itmes.

        Args:
            *items (str): Item paths.
        """
        items = self._container._to_work_items(items)
        self._set_data("items", items)


class OmoospaceStructure(TypedDict):
    Contents: dict
    Subspaces: dict


class OmoospaceTree(DirectoryTree):

    MAIN_DIRS = ["Contents", "Subspaces", "References", "Void"]

    def __init__(self, structure: Structure = None) -> None:
        self.structure = structure or {}
        for dirname in self.MAIN_DIRS:
            if self.structure.get(dirname) is None:
                self.structure[dirname] = None
        super().__init__(structure=self.structure)


class Omoospace(ProfileContainer):
    """The class of omoospace.

    An omoospace class instance is always refer to a existed omoospace directory, not dummy.

    Usage:
    ```python
    omoospace = Omoospace('path/to/omoospace')
    print(omoospace.root_path)
    # >>> path/to/omoospace
    ```

    Attributes:
        name (str): Omoospace name.
        description (str): Omoospace description.
    """

    name: str
    description: str

    def __init__(self, detect_dir: str):
        """Initialize from existed omoospace.

        Args:
            detect_dir (str): The start directory for detecting omoospace. It could be the subdirectories of omoospace.

        Attributes:
            name (str): Omoospace's name.
            description (str): Omoospace's description.

        Raises:
            NotFoundError: No omoospace detected.
        """
        detect_path = Path(detect_dir).resolve()
        detect_path_parents = [detect_path, *detect_path.parents]
        omoospace_path = None
        for detect_path_parent in detect_path_parents:
            # Find a file named 'Omoospace' with any extension (or no extension)
            candidates = list(Path(detect_path_parent).glob("Omoospace.*"))
            for candidate in candidates:
                if candidate.is_file():
                    omoospace_path = detect_path_parent
                    break
            if omoospace_path:
                break

        if not omoospace_path:
            raise NotFoundError("omoospace", detect_dir)

        # path assignment
        self.root_path = omoospace_path

    def __check_parent_dir(self, parent_dir: str):
        parent_path = Path(parent_dir).resolve() if parent_dir else self.subspaces_path

        # Check if is valid directory
        if not parent_path.is_dir():
            raise ExistsError(parent_dir)

        # Check if is in Subspaces
        if not is_subpath(parent_path, self.subspaces_path, or_equal=True):
            raise NotIncludeError(parent_dir, "Subspaces")

        return parent_path

    def _to_work_items(self, items: list[str]) -> list[str]:

        items = [Path(item).resolve() for item in items]
        items = list(filter(self.is_contents_item, items))
        items = [str(item.relative_to(self.contents_path).as_posix()) for item in items]
        return list(dict.fromkeys(items))

    def _to_work_item_paths(self, items: list[str]) -> list[Path]:

        items = [Path(self.contents_path, item).resolve() for item in items]
        items = list(filter(self.is_contents_item, items))

        return list(dict.fromkeys(items))

    @property
    def name(self) -> str:
        """str: Omoospace name. Prefer Omoospace.yml, fallback to folder name."""
        name = self._get_data("name")
        return name if name else self.root_path.name

    @property
    def subspaces_path(self) -> Path:
        """Path: Subspaces directory path."""
        subspaces_dirname = self._get_data("subspaces_mapping") or "Subspaces"
        return Path(self.root_path, subspaces_dirname).resolve()

    @property
    def contents_path(self) -> Path:
        """Path: Contents directory path."""
        contents_dirname = self._get_data("contents_mapping") or "Contents"
        return Path(self.root_path, contents_dirname).resolve()

    @property
    def references_path(self) -> Path:
        """Path: References directory path."""
        references_dirname = self._get_data("references_mapping") or "References"
        return Path(self.root_path, references_dirname).resolve()

    @property
    def void_path(self) -> Path:
        """Path: Void directory path."""
        void_dirname = self._get_data("void_mapping") or "Void"

        return Path(self.root_path, void_dirname).resolve()

    @property
    def profile_path(self) -> Path:
        """Path: Omoospace.yml file path."""
        return Path(self.root_path, "Omoospace.yml").resolve()

    @property
    def creators(self) -> list[Creator]:
        """list[Creator]: Creator List"""
        return self._get_item_list(Creator)

    @property
    def softwares(self) -> list[Software]:
        """list[Software]: Software List"""
        return self._get_item_list(Software)

    @property
    def works(self) -> list[Work]:
        """list[Work]: Work List"""
        return self._get_item_list(Work)

    @property
    def entities(self) -> list[Entity]:
        """list[Entity]: the subspace entities in the subspaces directory."""
        return get_entities(search_dir=self.subspaces_path)

    @property
    def subspace_tree(self) -> SubspaceTree:
        """SubspaceTree: The subspace tree of this omoospace."""
        return SubspaceTree(self.subspaces_path)

    @property
    def directory_tree(
        self,
    ) -> DirectoryTree:
        """DirectoryTree: The directory tree of this omoospace."""
        return DirectoryTree(search_dir=self.root_path)

    @property
    def imported_packages(self) -> list[Package]:
        """list[Package]: The imported package list of this omoospace."""
        packages_path = Path(self.contents_path, "Packages").resolve()
        subdirs = [subdir for subdir in packages_path.iterdir() if subdir.is_dir()]

        # Collect all Packages in Contents
        packages = []
        for subdir in subdirs:
            profile_file_path = Path(subdir, "Package.yml").resolve()
            if profile_file_path.is_file():
                packages.append(Package(subdir))

        return packages

    def is_contents_item(self, path: Path) -> bool:
        """Check if path is contents item

        Args:
            path (Path): Input

        Returns:
            bool: result
        """
        exists = path.exists()
        in_contents = is_subpath(path, self.contents_path)
        return exists and in_contents

    def is_omoospace_item(self, path: Path) -> bool:
        """Check if path is this omoospace item

        Args:
            path (Path): Input

        Returns:
            bool: result
        """
        exists = path.exists()
        in_omoospace = is_subpath(path, self.root_path)
        not_in_stagedata = not is_subpath(path, self.void_path, or_equal=True)

        not_profile_file = (
            "Omoospace.yml" != path.name
            and "Package.yml" != path.name
            and "Subspace.yml" not in path.name
        )

        return exists and in_omoospace and not_in_stagedata and not_profile_file

    def print_subspace_tree(self):
        """Print the subspace tree."""
        print(self.subspace_tree.format(title=self.name))

    def get_subspace(self, identify: Union[Route, str]) -> Subspace:
        """Get subspace by route or entity.

        Args:
            identify (Union[Route, str]): Could be route or entity path

        Returns:
            Subspace: The wanted subspace.
        """
        route = (
            identify if isinstance(identify, get_args(Route)) else get_route(identify)
        )
        return self.subspace_tree.get(route)

    def add_subspace(
        self,
        name: str,
        parent_dir: str = None,
        description: str = None,
        reveal_in_explorer: bool = True,
        collect_entities: bool = True,
    ) -> Subspace:
        """Add subspace to this omoospace.

        Args:
            name (str): Subspace name
            parent_dir (str, optional): Add subspace to which directory. Defaults to None.
            description (str): str = Subspace description. Defaults to None.
            reveal_in_explorer (bool, optional): Whether open directory after or not. Defaults to True.
            collect_entities (bool, optional): Whether collect relative entities into it or not. Defaults to True.

        Raises:
            ExistsError: Target path already has one.
            NotIncludeError: Parent directory is outside Subspaces.
            MoveFailed: Cannot move files.
            CreateFailed: Cannot create directory.

        Returns:
            Subspace: New added subspace.
        """
        parent_path = self.__check_parent_dir(parent_dir)

        subs_dirname = format_name(name)
        subs_path = Path(parent_path, subs_dirname).resolve()
        subs_profile_path = Path(subs_path, "Subspace.yml")

        # Check if is exists
        if subs_path.is_dir():
            raise ExistsError(subs_path)

        subs_profile = {"name": name, "description": description}

        # create directory
        try:
            subs_path.mkdir(parents=True, exist_ok=True)
            with subs_profile_path.open("w", encoding="utf-8") as file:
                yaml.dump(subs_profile, file)
        except Exception as err:
            raise CreateFailed("subspace directory")

        # collect entities that matched.
        if collect_entities:
            try:
                entities = get_entities(parent_path, recursive=False)

                def is_match(entity: Entity):
                    entity_name = entity.stem
                    not_itself = entity_name != subs_dirname

                    is_match = False
                    entity_node_names = format_name(entity_name).split("_")
                    subs_node_names = subs_dirname.split("_")
                    for i in range(len(subs_node_names)):
                        subs_suffix = "_".join(subs_node_names[i:])
                        entity_prefix = "_".join(
                            entity_node_names[: len(subs_node_names) - i]
                        )
                        if subs_suffix == entity_prefix:
                            is_match = True
                            break
                    return not_itself and is_match

                # Remove entity that not match the name
                entities = list(filter(is_match, entities))

                for entity in entities:
                    shutil.move(entity, Path(subs_path, entity.name).resolve())
            except:
                raise MoveFailed("entities")

        if reveal_in_explorer:
            reveal_directory(subs_path)

        return self.get_subspace(subs_path)

    def get_creator(self, email: str) -> Creator:
        """Get Creator by email."""
        return ProfileItemList(self.creators).find("email", email)

    def get_software(self, name: str) -> Software:
        """Get Software by name."""
        return ProfileItemList(self.softwares).find("name", name)

    def get_work(self, name: str) -> Work:
        """Get Work by name."""
        return ProfileItemList(self.works).find("name", name)

    def add_creator(
        self,
        name: str,
        email: str,
        role: str = None,
        website: str = None,
    ) -> Creator:
        """Add creator to this omoospace.

        Args:
            email (str): Creator email
            name (str): Creator name
            website (str, optional): Creator website. Defaults to None.
            role (str, optional): Creator role in omoospace. Defaults to None.

        Raises:
            InvalidError: Invalid email.
            InvalidError: Invalid website.

        Returns:
            Creator: New added creator.
        """
        if not is_email(email):
            raise InvalidError(email, "email")

        if website and (not is_url(website)):
            raise InvalidError(email, "url")

        creator = Creator(
            {"email": email, "name": name, "website": website, "role": role},
            container=self,
        )

        self._set_profile_data(creator)

        return creator

    def add_software(
        self,
        name: str,
        version: str,
        plugins: list[Plugin] = None,
    ) -> Software:
        """Add software to this omoospace.

        Args:
            name (str): Software name
            version (str): Software version.
            plugins (list[Plugin], optional): Software plugins. Defaults to None.

        Raises:
            InvalidError: Invalid version.
            InvalidError: Invalid plugin.

        Returns:
            Software: New added software.
        """

        if not is_version(version):
            raise InvalidError(version, "version")

        for plugin in plugins or []:
            if (not plugin.get("name")) or (not plugin.get("version")):
                raise InvalidError(plugin, "plugin")

        software = Software(
            {"name": name, "version": version, "plugins": plugins}, container=self
        )

        self._set_profile_data(software)

        return software

    def add_work(self, *items: str, name: str = None, description: str = None) -> Work:
        """Add work to this omoospace.

        Args:
            *items (list[str]): Work items.
            name (str): Work name. Defaults to None.
            description (str, optional): Work description. Defaults to None.

        Returns:
            Work: New added work.
        """

        items = self._to_work_items(items)
        name = name or format_name(items[0].split("/")[-1])

        work = Work(
            {"name": name, "description": description, "items": items}, container=self
        )

        self._set_profile_data(work)

        return work

    def export_package(
        self,
        *items: str,
        name: str = None,
        export_dir: str = ".",
        description: str = None,
        version: str = "0.1.0",
        reveal_in_explorer: bool = True,
        overwrite_existing: bool = True,
    ) -> Package:
        """Export a package.

        Args:
            *items (str): Items to export.
            name (str, optional): Package name. Defaults to None.
            export_dir (str, optional): Package export directory. Defaults to None.
            description (str, optional): Package description. Defaults to None.
            reveal_in_explorer (bool, optional): Whether open directory after or not. Defaults to True.
            overwrite_existing (bool, optional): Whether overwrite existing or not. Defaults to True.

        Raises:
            ExistsError: Target path already exists.
            NotFoundError: No vaild item found.

        Returns:
            Package: New exported package.
        """
        name = name or self.name
        pkg_dirname = format_name(name)
        pkg_path = Path(export_dir, pkg_dirname).resolve()

        # Check if package dir exists
        if pkg_path.is_dir():
            if overwrite_existing:
                # TODO: increase version
                shutil.rmtree(pkg_path, ignore_errors=True)
            else:
                raise ExistsError("package", pkg_path)

        items: list[Path] = [Path(item).resolve() for item in items]
        items = list(filter(self.is_omoospace_item, items))

        # Check if is enouph items
        if len(items) == 0:
            raise NotFoundError("vaild item")

        pkg_profile = {
            "name": name,
            "version": version,
            "description": description,
            "creators": self.creators,
        }

        try:
            pkg_path.mkdir(parents=True, exist_ok=True)
            pkg_profile_path = Path(pkg_path, "Package.yml")

            with pkg_profile_path.open("w", encoding="utf-8") as file:
                yaml.dump(pkg_profile, file)

            for i in range(len(items)):
                item = items[i]
                item_relpath = item.relative_to(self.root_path)
                copy_to(item, Path(pkg_path, item_relpath))

        except Exception as err:
            # Delete all if failed.
            shutil.rmtree(pkg_path, ignore_errors=True)
            raise Exception("Fail to export Package", err)

        if reveal_in_explorer:
            reveal_directory(pkg_path)

        return Package(pkg_path)

    def import_package(
        self,
        package_path: str,
        reveal_in_explorer: bool = True,
        overwrite_existing: bool = True,
    ):
        """Imports the package into the Contents directory.

        Args:
            package_path (str): Package directory.
            reveal_in_explorer (bool, optional): Whether open directory after or not. Defaults to True.
            overwrite_existing (bool, optional): Whether overwrite existing or not. Defaults to True.

        Raises:
            ExistsError: Target path already exists.
        """
        # get package form import directory
        package_path = Path(package_path).resolve()
        package = Package(package_path)

        # check if destination directory exists
        pkg_path = Path(
            self.root_path, "Contents", "Packages", format_name(package.name)
        )
        if pkg_path.is_dir():
            if overwrite_existing:
                shutil.rmtree(pkg_path, ignore_errors=True)
            else:
                raise ExistsError("package", pkg_path)

        if package_path.suffix == ".zip":
            with ZipFile(package_path, "r") as zip:
                zip.extractall(pkg_path)
        else:
            copy_to(package_path, pkg_path)

        if reveal_in_explorer:
            reveal_directory(pkg_path)


def create_omoospace(
    name: str,
    root_dir: str = ".",
    description: str = None,
    chinese_to_pinyin: bool = False,
    reveal_in_explorer: bool = False,
) -> Omoospace:
    """Create an omoospace.

    Args:
        name (str): Omoospace name
        root_dir (str, optional): Add omoospace to which directory. Defaults to '.'.
        description (str, optional): Omoospace description. Defaults to None.
        reveal_in_explorer (bool, optional): Whether open directory after or not. Defaults to True.
        chinese_to_pinyin (bool, optional): Whether convert chinese to pinyin. Defaults to False.
    Raises:
        ExistsError: Target path already exists.
        CreateFailed: Fail to create directories.

    Returns:
        Omoospace: New created omoospace.
    """
    dirname = format_name(name, chinese_to_pinyin=chinese_to_pinyin)
    root_path = Path(root_dir, dirname).resolve()

    # Check if omoospace exists
    if root_path.is_dir():
        raise ExistsError("omoospace", root_dir)

    profile = {
        "name": name,  # can be any name style
        "description": description,
    }

    try:
        # create dirs
        OmoospaceTree(None).make_dirs(root_path)
        profile_path = Path(root_path, "Omoospace.yml")
        with profile_path.open("w", encoding="utf-8") as file:
            yaml.dump(profile, file)

        readme_path = Path(root_path, "README.md")
        with readme_path.open("w", encoding="utf-8") as file:
            file.write(f"# {name}\n{description or ''}\n")

    except Exception as err:
        shutil.rmtree(root_path, ignore_errors=True)
        raise CreateFailed("omoospace directories")

    if reveal_in_explorer:
        reveal_directory(root_path)

    return Omoospace(root_path)

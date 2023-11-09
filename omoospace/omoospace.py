
from pathlib import Path
import shutil
from typing import TypedDict, Union, get_args
from zipfile import ZipFile

from omoospace.directory import DirectoryTree
from omoospace.exceptions import CreateFailed, EmptyError, ExistsError, InvalidError, MoveFailed, NotFoundError, NotIncludeError
from omoospace.package import Package
from omoospace.subspace import Subspace, SubspaceTree, get_entities, get_route
from omoospace.common import ProfileContainer, ProfileItem, ProfileItemList, yaml
from omoospace.utils import format_name, remove_duplicates, reveal_in_explorer, is_subpath, copy_to
from omoospace.types import Entity, Item, PathLike, Route, Structure
from omoospace.validators import is_email, is_url


class Creator(ProfileItem):
    name: str
    email: str
    role: str
    website: str
    item_list_key = 'creators'
    item_id_key = 'email'


class Work(ProfileItem):
    name: str
    description: str
    item_list_key = 'works'
    item_id_key = 'name'

    @property
    def items(self):
        items = self._get_data('items')

        # to remove invaild items
        item_paths = self._container._to_work_item_paths(items)
        vaild_items = self._container._to_work_items(item_paths)

        self._set_data('items', vaild_items)
        return vaild_items

    def add_item(self, *items: PathLike):
        items = self._container._to_work_items(items)
        # remove duplicates
        self._set_data('items', list(dict.fromkeys([*self.items, *items])))

    def set_items(self, *items: PathLike):
        items = self._container._to_work_items(items)
        self._set_data('items', items)


class Software(ProfileItem):
    name: str
    version: str
    item_list_key = 'softwares'
    item_id_key = 'name'

    @property
    def plugins(self):
        plugins = self._get_data('plugins') or []
        # remove plugin that is not dict
        plugins = [plugin for plugin in plugins
                   if isinstance(plugin, dict)]

        # remove plugin that key value is None
        plugins = [plugin for plugin in plugins
                   if plugin.get('name')]

        # remove duplicates in key
        plugins = remove_duplicates(plugins, 'name')

        # reassign modified data
        self._set_data('plugins', plugins)

        return plugins

    def set_plugin(self, name: str, version: str):
        plugins = self.plugins
        for i, plugin in enumerate(plugins):
            if plugin['name'] == name:
                plugins[i] == {"name": name, "verison": version}
                self._set_data('plugins', plugins)
                return

        plugins.append({"name": name, "verison": version})
        self._set_data('plugins', plugins)


class OmoospaceStructure(TypedDict):
    Contents: dict
    SourceFiles: dict


class OmoospaceTree(DirectoryTree):

    MAIN_DIRS = [
        "Contents",
        "ExternalData",
        "SourceFiles",
        "References",
        "StagedData"
    ]

    def __init__(self, structure: Structure = None) -> None:
        self.structure = structure or {}
        for dirname in self.MAIN_DIRS:
            if self.structure.get(dirname) is None:
                self.structure[dirname] = None
        super().__init__(structure=self.structure)


class Omoospace(ProfileContainer):
    """The class of omoospace.

    An omoospace class instance is always refer to a existed omoospace directory, not in ideal. 

    Attributes:
        name (str): Omoospace's name.
        description (str): Omoospace's description.
        creators (list[Creator]): Creator list.
        softwares (list[Software]): Software list.
        works (list[Work]): Work list.
        root_path (Path): Root path.
        sourcefiles_path (Path): SourceFiles directory path.
        contents_path (Path): Contents directory path.
        externaldata_path (Path): ExternalData directory path.
        stageddata_path (Path): StagedData directory path.
        references_path (Path): Reference directory path.
        profile_path (Path): Omoospace.yml file path.
    """

    name: str
    description: str

    def __init__(self, detect_dir: PathLike):
        """Initialize from existed omoospace directory.

        Args:
            detect_dir (PathLike): The start directory for detecting omoospace. It could be the subdirectories of omoospace.

        Raises:
            NotFoundError: No omoospace detected.
        """
        detect_path = Path(detect_dir).resolve()
        detect_path_parents = [detect_path, *detect_path.parents]
        omoos_path = None
        for detect_path_parent in detect_path_parents:
            omoos_profile_path = Path(detect_path_parent, 'Omoospace.yml')
            if omoos_profile_path.exists():
                omoos_path = detect_path_parent
                break
        if not omoos_path:
            raise NotFoundError("omoospace", detect_dir)

        # path assignment
        self.root_path = omoos_path
        self.sourcefiles_path = Path(self.root_path, 'SourceFiles').resolve()
        self.contents_path = Path(self.root_path, 'Contents').resolve()
        self.externaldata_path = Path(self.root_path, 'ExternalData').resolve()
        self.stageddata_path = Path(self.root_path, 'StagedData').resolve()
        self.references_path = Path(self.root_path, 'References').resolve()
        self.profile_path = Path(self.root_path, "Omoospace.yml").resolve()

    def __check_parent_dir(self, parent_dir: PathLike):
        parent_path = Path(parent_dir).resolve(
        ) if parent_dir else self.sourcefiles_path

        # Check if is valid directory
        if not parent_path.is_dir():
            raise ExistsError(parent_dir)

        # Check if is in SourceFiles
        if not is_subpath(parent_path, self.sourcefiles_path, or_equal=True):
            raise NotIncludeError(parent_dir, "SourceFiles")

        return parent_path

    def _to_work_items(self, items: list[PathLike]) -> list[str]:

        items = [Path(item).resolve() for item in items]
        items = list(filter(self.is_contents_item, items))
        items = [str(item.relative_to(self.contents_path).as_posix())
                 for item in items]
        return list(dict.fromkeys(items))

    def _to_work_item_paths(self, items: list[str]) -> list[Path]:

        items = [Path(self.contents_path, item).resolve() for item in items]
        items = list(filter(self.is_contents_item, items))

        return list(dict.fromkeys(items))

    @property
    def creators(self):
        return self._get_item_list(Creator)

    @property
    def works(self):
        return self._get_item_list(Work)

    @property
    def softwares(self):
        return self._get_item_list(Software)

    @property
    def entities(self) -> list[Entity]:
        """list[Entity]: the subspace entities in the sourcefiles directory."""
        return get_entities(search_dir=self.sourcefiles_path)

    @property
    def subspace_tree(self) -> SubspaceTree:
        """SubspaceTree: The subspace tree."""
        return SubspaceTree(self.sourcefiles_path)

    @property
    def subspace_tree_dict(self) -> dict:
        """dict: The dict of subspace tree."""
        return self.subspace_tree.to_dict()

    @property
    def directory_tree(self,) -> DirectoryTree:
        """DirectoryTree: The directory tree."""
        return DirectoryTree(search_dir=self.root_path)

    @property
    def imported_packages(self) -> list[Package]:
        """list[Package]: The list of Package objects that are imported from ExternalData."""
        subdirs = [subdir for subdir in self.externaldata_path.iterdir()
                   if subdir.is_dir()]

        # Collect all Packages in ExternalData
        packages = []
        for subdir in subdirs:
            profile_file_path = Path(subdir, 'Package.yml').resolve()
            if profile_file_path.is_file():
                packages.append(Package(subdir))

        return packages

    def is_contents_item(self, item: Item) -> bool:
        exists = item.exists()
        in_contents = is_subpath(item, self.contents_path)
        return exists and in_contents

    def is_omoospace_item(self, item: Item) -> bool:
        exists = item.exists()
        in_omoospace = is_subpath(item, self.root_path)
        not_in_stagedata = not is_subpath(
            item, self.stageddata_path, or_equal=True)

        not_profile_file = \
            'Omoospace.yml' != item.name \
            and 'Package.yml' != item.name \
            and 'Subspace.yml' not in item.name

        return exists and in_omoospace and not_in_stagedata and not_profile_file

    def get_subspace(self, identify: Union[Route, PathLike]):
        if isinstance(identify, get_args(Route)):
            route = identify
            return self.subspace_tree.get(route)
        elif isinstance(identify, get_args(PathLike)):
            route = get_route(identify)
            return self.subspace_tree.get(route)
        else:
            raise TypeError

    def add_subspace(
        self,
        name: str,
        parent_dir: PathLike = None,
        description: str = None,
        reveal_when_success: bool = True,
        collect_entities: bool = True
    ) -> Subspace:
        """Add or update subspace to this omoospace.

        Args:
            subspace (str): [description]
            parent_dir (PathLike, optional): [description]. Defaults to None.
            reveal_when_success (bool, optional): [description]. Defaults to True.
            collect_entities (bool, optional): [description]. Defaults to True.

        Raises:
            ExistsError: [description]
            NotIncludeError: [description]
            MoveFailed: [description]

        Returns:
            Path: [description]
        """
        parent_path = self.__check_parent_dir(parent_dir)

        subs_dirname = format_name(name)
        subs_path = Path(parent_path, subs_dirname).resolve()
        subs_profile_path = Path(subs_path, 'Subspace.yml')

        # Check if is exists
        if subs_path.is_dir():
            raise ExistsError(subs_path)

        subs_profile = {
            "name": name,
            "description": description
        }

        # create directory
        subs_path.mkdir(parents=True, exist_ok=True)
        with subs_profile_path.open('w', encoding='utf-8') as file:
            yaml.dump(subs_profile, file)

        # collect entities that matched.
        if (collect_entities):
            try:
                entities = get_entities(
                    parent_path, recursive=False)

                def is_match(entity: Entity):
                    entity_name = entity.stem
                    not_itself = entity_name != subs_dirname

                    is_match = False
                    entity_node_names = format_name(entity_name).split('_')
                    subs_node_names = subs_dirname.split('_')
                    for i in range(len(subs_node_names)):
                        subs_suffix = '_'.join(subs_node_names[i:])
                        entity_prefix = '_'.join(
                            entity_node_names[:len(subs_node_names) - i])
                        if subs_suffix == entity_prefix:
                            is_match = True
                            break
                    return not_itself and is_match

                # Remove entity that not match the name
                entities = list(filter(is_match, entities))

                for entity in entities:
                    shutil.move(
                        entity,
                        Path(subs_path, entity.name).resolve()
                    )
            except:
                raise MoveFailed('entities')

        if reveal_when_success:
            reveal_in_explorer(subs_path)

        return self.get_subspace(subs_path)

    def add_process(
        self,
        process: Union[Structure, list[str], str],
        parent_dir: PathLike = None,
        add_sequence_number=True,
        reveal_when_success: bool = True
    ):
        """Add or update process to this omoospace.

        Args:
            process (Union[Structure, list[str], str]): [description]
            parent_dir (PathLike, optional): [description]. Defaults to None.
            reveal_when_success (bool, optional): [description]. Defaults to True.

        Raises:
            ExistsError: [description]
            NotIncludeError: [description]
            CreateFailed: [description]

        Returns:
            Path: [description]
        """
        parent_path = self.__check_parent_dir(parent_dir)

        process_structure = {}
        if isinstance(process, get_args(Structure)):
            process_structure = process
        elif isinstance(process, str):
            process_dirname = format_name(process)
            process_structure[process_dirname] = None
        elif isinstance(process, list):
            for i, p in enumerate(process):
                dirname = format_name(p)
                if add_sequence_number:
                    dirname = '%03d-%s' % (i+1, dirname)
                process_structure[dirname] = None
        else:
            raise TypeError

        try:
            DirectoryTree(process_structure).make_dirs(parent_path)
        except Exception as err:
            raise CreateFailed("process directories")

        if reveal_when_success:
            reveal_in_explorer(parent_path)

    def get_creator(self, email: str):
        return ProfileItemList(self.creators).find('email', email)

    def get_software(self, name: str):
        return ProfileItemList(self.softwares).find('name', name)

    def get_work(self, name: str):
        return ProfileItemList(self.works).find('name', name)

    def add_creator(
        self,
        email: str,
        name: str,
        website: str = None,
        role: str = None,
    ):
        """Add or update creator to this omoospace."""
        if not is_email(email):
            raise InvalidError(email, 'email')

        if website and (not is_url(website)):
            raise InvalidError(email, 'url')

        creator = Creator({
            'email': email,
            'name': name,
            'website': website,
            'role': role
        }, container=self)

        self._set_profile_data(creator)

        return creator

    def add_software(
        self,
        name: str,
        version: str,
        plugins: list[dict] = None,
    ):
        """Add or update software to this omoospace."""

        software = Software({
            'name': name,
            'version': version,
            'plugins': plugins
        }, container=self)

        self._set_profile_data(software)

        return software

    def add_work(
        self,
        *items: PathLike,
        name: str = None,
        description: str = None
    ):
        """Add or update work to this omoospace."""

        items = self._to_work_items(items)
        name = name or format_name(items[0].split('/')[-1])

        work = Work({
            "name": name,
            "description": description,
            "items": items
        }, container=self)

        self._set_profile_data(work)

        return work

    def export_package(
        self,
        *items: PathLike,
        name: str = None,
        export_dir: PathLike = '.',
        description: str = None,
        version: str = '0.1.0',
        reveal_when_success: bool = True,
        overwrite_existing: bool = True
    ) -> Package:
        """Export a package.

        Args:
            *items (list[PathLike]): [description]
            name (str, optional): [description]. Defaults to None.
            export_dir (PathLike, optional): [description]. Defaults to None.
            description (str, optional): [description]. Defaults to None.
            reveal_when_success (bool, optional): [description]. Defaults to True.
            overwrite_existing (bool, optional): [description]. Defaults to True.

        Returns:
            Package: [description]
        """
        name = name or self.name
        pkg_dirname = format_name(name)
        pkg_path = Path(export_dir, pkg_dirname).resolve()

        # Check if package dir exists
        if (pkg_path.is_dir()):
            if (overwrite_existing):
                # TODO: increase version
                shutil.rmtree(pkg_path, ignore_errors=True)
            else:
                raise ExistsError('package', pkg_path)

        items: list[Path] = [Path(item).resolve() for item in items]
        items = list(filter(self.is_omoospace_item, items))

        # Check if is enouph items
        if (len(items) == 0):
            raise Exception('Export Failed, at least one item')

        pkg_profile = {
            "name": name,
            "version": version,
            "description": description,
            "creators": self.creators,
        }

        try:
            pkg_path.mkdir(parents=True, exist_ok=True)
            pkg_profile_path = Path(pkg_path, 'Package.yml')

            with pkg_profile_path.open('w', encoding='utf-8') as file:
                yaml.dump(pkg_profile, file)

            for i in range(len(items)):
                item = items[i]
                item_relpath = item.relative_to(self.root_path)
                copy_to(item, Path(pkg_path, item_relpath))

        except Exception as err:
            # Delete all if failed.
            shutil.rmtree(pkg_path, ignore_errors=True)
            raise Exception("Fail to export Package", err)

        if reveal_when_success:
            reveal_in_explorer(pkg_path)

        return Package(pkg_path)

    def import_package(
        self,
        import_dir: PathLike,
        reveal_when_success: bool = True,
        overwrite_existing: bool = True
    ):
        """Imports the package into the ExternalData directory.

        Args:
            import_dir (PathLike): [description]
            reveal_when_success (bool, optional): [description]. Defaults to True.
            overwrite_existing (bool, optional): [description]. Defaults to True.

        Raises:
            ExistsError: [description]
        """
        # get package form import directory
        import_path = Path(import_dir).resolve()
        package = Package(import_path)

        # check if destination directory exists
        pkg_path = Path(
            self.root_path, 'ExternalData', format_name(package.name))
        if (pkg_path.is_dir()):
            if (overwrite_existing):
                shutil.rmtree(pkg_path, ignore_errors=True)
            else:
                raise ExistsError('package', pkg_path)

        if (import_path.suffix == ".zip"):
            with ZipFile(import_path, 'r') as zip:
                zip.extractall(pkg_path)
        else:
            copy_to(import_path, pkg_path)

        if reveal_when_success:
            reveal_in_explorer(pkg_path)


def create_omoospace(
    name: str,
    root_dir: PathLike = '.',
    description: str = None,
    structure: OmoospaceStructure = None,
    reveal_when_success: bool = True
):
    """Create a Omoospace .

    Args:
        name (str): [description]
        create_dir (PathLike, optional): [description]. Defaults to '.'.
        description (str, optional): [description]. Defaults to None.
        structure (OmoospaceStructure, optional): [description]. Defaults to None.
        reveal_when_success (bool, optional): [description]. Defaults to True.

    Raises:
        ExistsError: [description]
        Exception: [description]

    Returns:
        [type]: [description]
    """
    omoos_dirname = format_name(name)
    omoos_path = Path(root_dir, omoos_dirname).resolve()

    # Check if omoospace exists
    if (omoos_path.is_dir()):
        raise ExistsError('omoospace', root_dir)

    # write omoospace profile to yml
    omoos_profile = {
        "name": name,  # can be any name style
        "description": description,
    }

    try:
        # create dirs
        OmoospaceTree(structure).make_dirs(omoos_path)
        omoos_profile_path = Path(omoos_path, 'Omoospace.yml')
        with omoos_profile_path.open('w', encoding='utf-8') as file:
            yaml.dump(omoos_profile, file)

    except Exception as err:
        shutil.rmtree(omoos_path, ignore_errors=True)
        raise CreateFailed("omoospace directories")

    if reveal_when_success:
        reveal_in_explorer(omoos_path)

    return Omoospace(omoos_path)

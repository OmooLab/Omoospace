
from pathlib import Path
import os
import shutil
import yaml
from zipfile import ZipFile

from rich.progress import track
from omoospace.directory import DirectoryTree
from omoospace.exceptions import CreationError, EmptyError, ExistsError, InvalidError, NotFoundError, NotIncludeError
from omoospace.package import Package
from omoospace.subspace import SubspaceTree
from omoospace.ui import console
from omoospace import ui
from omoospace.utils import format_name, reveal_in_explorer, is_subpath, PathLike, copy_to_path
from omoospace.types import Entity, Item, OmoospaceInfo, PackageInfo, Route, Structure, SubspaceInfo

# TODO: more color in subspace route
# TODO: package link in summary list

# TODO: add softwares and creators in summary list
# TODO: print subspaces or packages or tree only

# TODO: annition to class and funtion


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


class Omoospace:
    def __init__(self, detect_dir: PathLike):
        """Initialize Omoospace configuration .

        Args:
            detect_dir (PathLike): The start directory for detecting omoospace. It could be the subdirectories of omoospace.

        Raises:
            Exception: No omoospace detected.
        """
        detect_path = Path(detect_dir).resolve()
        detect_path_parents = [detect_path, *detect_path.parents]
        omoospace_path = None
        for detect_path_parent in detect_path_parents:
            omoospace_info_path = Path(detect_path_parent, 'Omoospace.yml')
            if omoospace_info_path.exists():
                with omoospace_info_path.open('r', encoding='utf-8') as file:
                    omoospace_info = yaml.safe_load(file)
                    omoospace_path = detect_path_parent
                break
        if not omoospace_path:
            raise NotFoundError("omoospace", detect_dir)

        # path assignment
        self.root_path = omoospace_path
        self.sourcefiles_path = Path(self.root_path, 'SourceFiles').resolve()
        self.contents_path = Path(self.root_path, 'Contents').resolve()
        self.externaldata_path = Path(self.root_path, 'ExternalData').resolve()
        self.stageddata_path = Path(self.root_path, 'StagedData').resolve()
        self.references_path = Path(self.root_path, 'References').resolve()

        # info assignment
        self.name = omoospace_info.get('name')
        self.description = omoospace_info.get('description')
        self.creators = omoospace_info.get('creators')
        self.softwares = omoospace_info.get('softwares')
        self.works = omoospace_info.get('works')

    @staticmethod
    def is_entity(path: Path) -> bool:
        """Return true if path is a subspace entity .

        Args:
            path (Entity): The path to be checked.

        Returns:
            bool: Return ture if is valid entity.
        """
        path = path.resolve()
        if path.is_dir():
            is_subspace = Path(path, 'Subspace.yml').is_file()
            is_void = 'Void' in path.name.split("_")
            return is_subspace or is_void
        else:
            not_marker = path.name != 'Subspace.yml'
            return not_marker

    def get_route(self, entity: Entity) -> Route:
        """Returns the route for the given entity .

        Args:
            entity (Entity): The entity to deal with.

        Returns:
            Route: A subspace route object to the given entity.
        """
        entity = entity.resolve()
        if not is_subpath(entity, self.sourcefiles_path):
            raise NotIncludeError("This entity", "SourceFiles")

        # Get relpath parts. remove those directory that is not entity.
        valid_parents = []
        for parent in entity.parents:
            if parent == self.sourcefiles_path:
                break

            if self.is_entity(parent):
                valid_parents.append(parent)
        valid_parents.reverse()

        path_parts = [format_name(valid_parent.stem)
                      for valid_parent in valid_parents]
        path_parts.append(format_name(entity.stem))

        # Get route nodes. remove duplicate prefix.
        route: Route = []
        for part_name in path_parts:
            namespaces = part_name.split('_')
            for i in range(len(route)):
                route_str_suffix = '_'.join(route[i:])
                name_prefix = '_'.join(namespaces[:len(route) - i])
                if route_str_suffix == name_prefix:
                    # clip matched prefix spaces
                    namespaces = namespaces[len(route) - i:]
                    break

            route.extend(namespaces if part_name != "" else [])

        # Concat namespaces after "Void".
        for i in range(len(route)):
            if route[i] == "Void":
                remaining = "".join(route[i+1:])
                route = route[:i+1]
                if remaining:
                    route.append(remaining)
                break
        return route

    def get_entities(
        self,
        search_dir: PathLike = None,
        recursive: bool = True
    ) -> list[Entity]:
        """Get all entities in the source files.

        Args:
            search_dir (PathLike, optional): [description]. Defaults to None.
            recursive (bool, optional): [description]. Defaults to True.

        Raises:
            Exception: [description]

        Returns:
            list[Entity]: [description]
        """
        search_dir: Path = Path(search_dir).resolve() \
            if search_dir else self.sourcefiles_path
        if not is_subpath(search_dir, self.sourcefiles_path, or_equal=True):
            raise NotIncludeError("Search directory", "SourceFiles")

        entities: list[Path] = []
        if recursive:
            # FIXME: replace this with Path.walk (python 3.12)
            # https://docs.python.org/3/library/pathlib.html
            for root, dirs, files in os.walk(search_dir):
                for path in [*dirs, *files]:
                    child = Path(root, path).resolve()
                    if self.is_entity(child):
                        entities.append(child)
        else:
            for child in search_dir.iterdir():
                child = child.resolve()
                if self.is_entity(child):
                    entities.append(child)
        return entities

    @property
    def entities(self) -> list[Path]:
        return self.get_entities()

    @property
    def subspace_tree(self) -> SubspaceTree:
        return self.get_subspace_tree(*self.entities)

    def get_subspace_tree(
        self,
        *entities: Entity
    ) -> SubspaceTree:
        """Get subspaces based on entities.

        Args:
            entities (list[Entity]): [description]

        Returns:
            SubspaceTree: Subspaces
        """
        return SubspaceTree(*entities, omoospace=self)

    @property
    def packages(self) -> list[Package]:
        """A dictionary of packages.

        Returns:
            list[Package]: A dictionary of packages.
        """
        subdirs = [subdir for subdir in self.externaldata_path.iterdir()
                   if subdir.is_dir()]

        # Collect all Packages in ExternalData
        packages = []
        for subdir in subdirs:
            info_filepath = Path(subdir, 'Package.yml').resolve()
            if info_filepath.is_file():
                packages.append(Package(subdir))

        return packages

    def add_subspace(
            self,
            name: str,
            parent_dir: PathLike,
            info: SubspaceInfo = None,
            reveal_when_success: bool = True,
            collect_entities: bool = True
    ) -> Path:
        """Add a subspace to the source directory .

        Args:
            name (str): [description]
            parent_dir (PathLike): [description]
            reveal_when_success (bool, optional): [description]. Defaults to True.
            collect_entities (bool, optional): [description]. Defaults to True.

        Raises:
            Exception: Name cannot be empty.
            Exception: Parent directory is invalid.
            Exception: Parent directory is out of SourceFiles.

        Return:
            Path
        """
        parent_path = Path(parent_dir).resolve()
        # Check if name is empty
        if not len(name) > 0:
            raise EmptyError("name")

        # Check if is valid directory
        if not parent_path.is_dir():
            raise ExistsError(parent_dir)

        # Check if is in SourceFiles
        if not is_subpath(parent_path, self.sourcefiles_path, or_equal=True):
            raise NotIncludeError(parent_dir, "SourceFiles")

        subspace_dirname = format_name(name)
        subspace_path = Path(parent_path, subspace_dirname).resolve()

        # write subspace info to yml
        info = info or {}
        subspace_info: SubspaceInfo = {
            "name": info.get("name") or name,  # can be any name style
            "comments": info.get("comments")
        }

        # make subspace dir
        subspace_path.mkdir(parents=True, exist_ok=True)
        subspace_info_path = Path(subspace_path, 'Subspace.yml')
        with subspace_info_path.open('w', encoding='utf-8') as file:
            yaml.safe_dump(subspace_info, file,
                           sort_keys=False, allow_unicode=True)

        if (collect_entities):
            entities = self.get_entities(parent_path, recursive=False)

            def is_match(entity: Entity):
                entity_stem = entity.stem
                not_itself = entity_stem != subspace_dirname

                is_match = False
                entity_namespaces = format_name(entity_stem).split('_')
                subspace_namespaces = subspace_dirname.split('_')
                for i in range(len(subspace_namespaces)):
                    subspace_suffix = '_'.join(subspace_namespaces[i:])
                    entity_prefix = '_'.join(
                        entity_namespaces[:len(subspace_namespaces) - i])
                    if subspace_suffix == entity_prefix:
                        is_match = True
                        break
                return not_itself and is_match

            # Remove entity that not match the name
            entities = list(filter(is_match, entities))

            for entity in entities:
                shutil.move(entity, Path(subspace_path, entity.name).resolve())

        if reveal_when_success:
            reveal_in_explorer(subspace_path)

        return subspace_path

    def is_valid_item(self, item: Item) -> bool:
        """Return True if the item is a valid file or not .

        Args:
            item (Item): [description]

        Returns:
            bool: [description]
        """
        exists = item.exists()
        in_omoospace = is_subpath(item, self.root_path)
        not_in_stagedata = not is_subpath(
            item, self.stageddata_path, or_equal=True)
        not_omoospace_yml = item.name != "Omoospace.yml"
        return exists and in_omoospace and not_omoospace_yml and not_in_stagedata

    def export_package(
        self,
        items: list[PathLike],
        name: str = None,
        export_dir: PathLike = None,
        info: PackageInfo = None,
        reveal_when_success: bool = True,
        overwrite_existing: bool = True
    ):
        name = name or self.name
        export_path = Path(export_dir).resolve() if export_dir \
            else Path(self.root_path, 'StagedData', 'Packages').resolve()
        package_dirname = format_name(name)
        package_path = Path(export_path, package_dirname).resolve()

        # Check if package dir exists
        if (package_path.is_dir()):
            if (overwrite_existing):
                shutil.rmtree(package_path, ignore_errors=True)
            else:
                raise ExistsError('package', package_path)

        items: list[Path] = [Path(item).resolve() for item in items]
        items = list(filter(self.is_valid_item, items))

        # Check if is enouph items
        if (len(items) == 0):
            raise Exception('Export Failed, at least one item')

        info = info or {}
        package_info = {
            "name": info.get("name") or name,
            "version": info.get("version"),
            "description": info.get("description"),
            "creators": self.creators,
        }

        try:
            package_path.mkdir(parents=True, exist_ok=True)
            package_info_path = Path(package_path, 'Package.yml')
            package_md_path = Path(package_path, 'README.md')

            with package_info_path.open('w', encoding='utf-8') as file:
                yaml.safe_dump(package_info, file,
                               sort_keys=False, allow_unicode=True)

            with package_md_path.open('w', encoding='utf-8') as file:
                file.write('# %s\n' % package_info.get("name"))
                file.write("%s\n" % package_info.get("description") or "")
                file.write('## Package Info\n')
                file.write('**version:** %s  \n' %
                           package_info.get("version") or "")
                file.write('**creators:**\n')
                for author in package_info.get("creators") or []:
                    file.write("- %s\n" % author.get("name") or "Unknow")
                file.write('## Items List\n')
                for item in items:
                    file.write("- %s\n" % item)

            for i in track(range(len(items)), description="Processing..."):
                item = items[i]
                item_relpath = item.relative_to(self.root_path)
                copy_to_path(item, Path(package_path, item_relpath))

        except Exception as err:
            # Delete all if failed.
            shutil.rmtree(package_path, ignore_errors=True)
            raise Exception("Fail to export Package", err)

        if reveal_when_success:
            reveal_in_explorer(package_path)

        return Package(package_path)

    def import_package(
        self,
        import_dir: PathLike,
        reveal_when_success: bool = True,
        overwrite_existing: bool = True
    ):
        # get package form import directory
        import_path = Path(import_dir).resolve()
        package = Package(import_path)

        # check if destination directory exists
        package_path = Path(
            self.root_path, 'ExternalData', format_name(package.name))
        if (package_path.is_dir()):
            if (overwrite_existing):
                shutil.rmtree(package_path, ignore_errors=True)
            else:
                raise ExistsError('package', package_path)

        if (import_path.suffix == ".zip"):
            with ZipFile(import_path, 'r') as zip:
                zip.extractall(package_path)
        else:
            copy_to_path(import_path, package_path)

        if reveal_when_success:
            reveal_in_explorer(package_path)

    def show_summary(
        self,
        output_dir: PathLike = None,
        reveal_when_success: bool = True,
    ):
        """Print a summary of the omoospace.

        Args:
            output_dir (PathLike, optional): [description]. Defaults to None.
        """
        packages = self.packages
        subspace_tree = self.subspace_tree

        ui_packages = ui.Table(
            "Directory", "Description",
            rows=[[package.name, package.description]
                  for package in packages]
        )

        console.print(ui.Board(
            ui.Info("Name", "%s [dim](%s)[/dim]" %
                    (self.name, self.root_path)),
            ui.Info("Description", self.description),
            ui.Info("Subspace Tree", subspace_tree.render_tree()),
            ui.Info("Subspace Entities", subspace_tree.render_table()),
            ui.Info("Imported Package List", ui_packages),
            title="Summary"
        ))

        if (output_dir):
            subspace_tree.draw_graph(output_dir, reveal_when_success)

    @classmethod
    def create(
        cls,
        name: str,
        create_dir: PathLike = '.',
        info: OmoospaceInfo = None,
        structure: Structure = None,
        reveal_when_success: bool = True
    ):
        """Create a Omoospace .

        Args:
            name (str): [description]
            create_dir (PathLike, optional): [description]. Defaults to '.'.
            info (OmoospaceInfo, optional): [description]. Defaults to None.
            structure (OmoospaceStructure, optional): [description]. Defaults to None.
            reveal_when_success (bool, optional): [description]. Defaults to True.

        Raises:
            ExistsError: [description]
            Exception: [description]

        Returns:
            [type]: [description]
        """
        omoospace_dirname = format_name(name)
        omoospace_path = Path(create_dir, omoospace_dirname).resolve()

        # Check if omoospace exists
        if (omoospace_path.is_dir()):
            raise ExistsError('omoospace', create_dir)

        # write omoospace info to yml
        info = info or {}
        omoospace_info: OmoospaceInfo = {
            "name": info.get("name") or name,  # can be any name style
            "description": info.get("description"),
            "creators": info.get("creators"),
            "softwares": info.get("softwares"),
            "works": info.get("works"),
        }

        try:
            # create dirs
            OmoospaceTree(structure).make_dirs(omoospace_path)
            omoospace_info_path = Path(
                omoospace_path, 'Omoospace.yml').resolve()
            with omoospace_info_path.open('w', encoding='utf-8') as file:
                yaml.safe_dump(omoospace_info, file,
                               sort_keys=False, allow_unicode=True)
        except Exception as err:
            shutil.rmtree(omoospace_path, ignore_errors=True)
            raise CreationError(err, staff="omoospace directories")

        if reveal_when_success:
            reveal_in_explorer(omoospace_path)

        return cls(omoospace_path)

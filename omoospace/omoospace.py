
from pathlib import Path
import os
import shutil
import yaml
from zipfile import ZipFile
from colorama import Fore, Style
from enum import Enum
from typing import TypedDict


from rich.progress import track
from omoospace.ui import ui_table, console, ui_info, ui_board, ui_grid, ui_panel
from omoospace.utils import format_name, reveal_in_explorer, is_subpath, PathLike, copy_to_path
from omoospace.tree import Tree
from omoospace.graph import draw_graph

# TODO: more color in subspace route
# TODO: package link in summary list

# TODO: add softwares and creators in summary list
# TODO: print subspaces or packages or tree only

# TODO: annition to class and funtion


Entity = Path

Item = Path

Route = list[str]


class NotFoundError(Exception):
    def __init__(self, staff: str, dir: str):
        self.message = "No %s detected in '%s'" % (staff, dir)
        super().__init__(self.message)


class ExistsError(Exception):
    def __init__(self, staff: str, dir: str):
        self.message = "%s already exists in '%s'" % (staff, dir)
        super().__init__(self.message)


class Work(TypedDict):
    name: str
    path: str


class Creator(TypedDict):
    name: str
    email: str
    role: str
    website: str


class Plugin(TypedDict):
    name: str
    version: str


class Softerware(TypedDict):
    name: str
    version: str
    plugins: list[Plugin]


class OmoospaceInfo(TypedDict):
    description: str
    creators: list[Creator]
    softwares: list[Softerware]
    works: list[Work]


class OmoospaceStructure(TypedDict):
    contents: dict
    sourcefiles: dict


class PackageInfo(TypedDict):
    description: str
    version: str
    creators: list[Creator]


class SubspaceType(Enum):
    DIRECTORY = "directory"
    FILE = "file"
    PHANTOM = "phantom"


class Subspace(TypedDict):
    route: Route
    parent: Route
    entities: list[Entity]
    path: Path
    type: SubspaceType
    flow: int


class Package:
    def __init__(self, dir: PathLike):
        package_path = Path(dir).resolve()
        if (package_path.suffix == ".zip"):
            with ZipFile(package_path, 'r') as zip:
                try:
                    with zip.open('Package.yml') as file:
                        package_info = yaml.safe_load(file)
                except:
                    raise NotFoundError("package", dir)
        else:
            package_info_path = Path(package_path, 'Package.yml')
            if package_info_path.exists():
                with package_info_path.open('r', encoding='utf-8') as file:
                    package_info = yaml.safe_load(file)
            else:
                raise NotFoundError("package", dir)

        self.root_path = package_path
        self.name = package_info.get('name')
        self.description = package_info.get('description')
        self.version = package_info.get('version')
        self.creators = package_info.get('creators')


class Omoospace:
    MAIN_DIRS = [
        "Contents",
        "ExternalData",
        "SourceFiles",
        "References",
        "StagedData"
    ]

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

    @classmethod
    def make_dirs(
            cls,
            dir: PathLike,
            subdirs: dict[str, any] = {},
            is_subspace: bool = False):
        """Create all subdirectories in a directory.

        Args:
            dir (PathLike): The directory to create.
            subdirs (dict[str, any], optional): The subdirectories under that directory. Defaults to {}.
            is_subspace (bool, optional): If true, '.subspace' marker file will be created in that dicrectory. Defaults to False.
        """
        path = Path(dir).resolve()
        path.mkdir(parents=True, exist_ok=True)
        if is_subspace:
            # make .subspace in it
            if 'Void' not in path.name.split("_"):
                with Path(path, ".subspace").open('w') as file:
                    pass

        subdirs = subdirs or {}  # avoid None
        for subdir_name, subdir_subdir in subdirs.items():
            is_subspace = subdir_name.startswith('*')
            subdir_name = subdir_name.removeprefix("*")
            subdir_path = Path(path, subdir_name)

            # if subdir_subdir not empty, continue make dir
            cls.make_dirs(subdir_path, subdir_subdir, is_subspace)

    @staticmethod
    def is_entity(path: Path) -> bool:
        """Return true if path is a subspace entity .

        Args:
            path (Entity): The path to be checked.

        Returns:
            bool: Return ture if is valid entity.
        """
        if path.is_dir():
            is_subspace = Path(path, '.subspace').exists()
            is_void = 'Void' in path.name.split("_")
            if is_subspace or is_void:
                return True
        else:
            if path.parts[-1] != '.subspace':
                return True
        return False

    def get_route(self, entity: Entity) -> Route:
        """Returns the route for the given entity .

        Args:
            entity (Entity): The entity to deal with.

        Returns:
            Route: A subspace route object to the given entity.
        """
        relpath = entity.relative_to(self.sourcefiles_path)

        # Get relpath parts. remove those directory that is not entity.
        valid_parents = [parent for parent in relpath.parents
                         if self.is_entity(parent)]
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
    ) -> list[Path]:
        search_dir: Path = Path(search_dir).resolve() \
            if search_dir else self.sourcefiles_path
        if not is_subpath(search_dir, self.sourcefiles_path, or_equal=True):
            raise Exception("Search directory is out of SourceFiles")

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
    def subspaces(self) -> dict[str, Subspace]:
        return self.get_subspaces(*self.entities)

    def get_subspaces(
        self,
        *entities: list[Entity]
    ) -> dict[str, Subspace]:
        """Get subspaces based on entities.

        Args:
            entities (list[Entity]): [description]

        Returns:
            dict[str, Subspace]: Subspaces
        """
        subspace_dict: dict[str, Subspace] = {}
        for entity in entities:
            entity_route = self.get_route(entity)
            # create all subspace in route
            for i in range(len(entity_route)):
                is_end_node = i == len(entity_route)-1
                subspace_route = entity_route[:i+1]
                subspace_parent = entity_route[:i] if i != 0 else None
                subspace_route_str = "_".join(subspace_route)
                subspace = subspace_dict.get(subspace_route_str) \
                    or Subspace(
                    route=subspace_route,
                    parent=subspace_parent,
                    entities=[],
                    flow=0
                )
                if is_end_node:
                    subspace["entities"].append(entity)

                # what ever is end node or not, all nodes are passed through
                subspace["flow"] += 1
                subspace_dict[subspace_route_str] = subspace

        # set subspace type base on entities
        for subspace in subspace_dict.values():
            if (len(subspace["entities"]) == 0):
                subspace["type"] = SubspaceType.PHANTOM
            else:
                subspace["type"] = SubspaceType.FILE
                for entity in subspace["entities"]:
                    if (entity.is_dir()):
                        subspace["type"] = SubspaceType.DIRECTORY

        subspace_dict = dict(sorted(subspace_dict.items()))
        return subspace_dict

    def get_subspace_tree(self) -> Tree:
        """
        build subspace tree
        """
        subspace_dict = self.subspaces
        subspace_tree = Tree()

        for route in subspace_dict.keys():
            subspace_tree.add(route.split("_"))

        return subspace_tree

    @property
    def packages(self) -> dict[str, Package]:
        """A dictionary of packages.

        Returns:
            dict[str,Package]: A dictionary of packages.
        """
        subdirs = [subdir for subdir in self.externaldata_path.iterdir()
                   if subdir.is_dir()]

        # Collect all Packages in ExternalData
        package_dict = {}
        for subdir in subdirs:
            info_filepath = Path(subdir, 'Package.yml')
            if info_filepath.exists():
                package_relpath = subdir.relative_to(self.externaldata_path)
                package_dict[package_relpath] = Package(subdir)

        return package_dict

    def add_subspace(
            self,
            name: str,
            parent_dir: PathLike,
            reveal_when_success: bool = True,
            collect_entities: bool = True
    ) -> dict[str, Subspace]:
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
            dict[str, Subspace]
        """
        parent_path = Path(parent_dir).resolve()
        # Check if name is empty
        if not len(name) > 0:
            raise Exception(message="Name cannot be empty.")

        # Check if is valid directory
        if not parent_path.is_dir():
            raise Exception(message="'%s' is invalid dir." % parent_dir)

        # Check if is in SourceFiles
        if not is_subpath(parent_path, self.sourcefiles_path, or_equal=True):
            raise Exception(message="'%s' is out of SourceFiles." % parent_dir)

        subspace_name = format_name(name)
        subspace_path = Path(parent_path, subspace_name).resolve()

        # make subspace dir
        self.make_dirs(subspace_path, is_subspace=True)

        if (collect_entities):
            entities = self.get_entities(parent_path, recursive=False)

            def is_match(entity: Entity):
                entity_stem = entity.stem
                not_itself = entity_stem != name

                is_match = False
                entity_namespaces = format_name(entity_stem).split('_')
                subspace_namespaces = subspace_name.split('_')
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

        return self.get_subspaces(subspace_path)

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
        package_name = name or self.name
        export_path = Path(export_dir).resolve() if export_dir \
            else Path(self.root_path, 'StagedData', 'Packages').resolve()
        package_path = Path(export_path, format_name(package_name)).resolve()

        # Check if package dir exists
        if (package_path.is_dir()):
            if (overwrite_existing):
                shutil.rmtree(package_path)
            else:
                raise ExistsError('package', package_path)

        items: list[Path] = [Path(item).resolve() for item in items]
        items = list(filter(self.is_valid_item, items))

        # Check if is enouph items
        if (len(items) == 0):
            raise Exception('Export Failed, at least one item')

        package_info = {
            "name": package_name,
            "version": info.get("version"),
            "description": info.get("description"),
            "creators": self.creators,
        }

        try:
            console.print('')
            self.make_dirs(package_path)
            package_info_path = Path(package_path, 'Package.yml')
            package_md_path = Path(package_path, 'README.md')

            with package_info_path.open('w', encoding='utf-8') as file:
                yaml.safe_dump(package_info, file, sort_keys=False)

            with package_md_path.open('w', encoding='utf-8') as file:
                file.write('# %s\n' % package_name)
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
            shutil.rmtree(package_path)
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
                shutil.rmtree(package_path)
            else:
                raise ExistsError('package', package_path)

        if (import_path.suffix == ".zip"):
            with ZipFile(import_path, 'r') as zip:
                zip.extractall(package_path)
        else:
            copy_to_path(import_path, package_path)

        if reveal_when_success:
            reveal_in_explorer(package_path)

    def show_summary(self, output_dir: PathLike = None):
        subspace_dict = self.subspaces
        package_dict = self.packages
        subspace_tree = self.get_subspace_tree()

        ui_subspace_list = ui_table(
            "Route",
            "Parent",
            "Entities",
            "Type"
        )

        def ui_entity_link(entity: Entity):
            path = entity if entity.is_dir() else entity.parent
            name = Path(entity).parts[-1]
            return "[link=%s]%s[/link]" % (path, name)

        for subspace in subspace_dict.values():
            ui_subspace_list.add_row(
                ' > '.join(subspace["route"]),
                ' > '.join(subspace["parent"])
                if subspace["parent"] else "(Root)",
                "\n".join([ui_entity_link(entity)
                           for entity in subspace["entities"]]),
                subspace["type"].value
            )

        ui_package_list = ui_table("Directory", "Description")
        for package in package_dict.values():
            ui_package_list.add_row(
                package.name,
                package.description
            )

        def custom_key(nodes) -> str:
            route = "_".join(nodes)
            subspace = subspace_dict.get(route)
            node = nodes[-1]
            if subspace["type"] == SubspaceType.DIRECTORY:
                return "📁 [bright]%s (%s)" % \
                    (node, ui_entity_link(subspace["entities"][0]))
            elif subspace["type"] == SubspaceType.PHANTOM:
                return "⭕ [dim]%s" % node
            else:
                return "📄 [dim i]%s (%s)" % \
                    (node, ui_entity_link(subspace["entities"][0]))

        tree_instruction = "⭕ [dim]--- phantom subspace\nwhich has no entity.\n\n" \
            + "📁 --- [bright]direcotry subspace[/bright]\nwhich contains .subspace file.\n\n" \
            + "📄 --- [i]file subspace[/i]\nwhich refers to a leaf file.[/dim]"

        ui_tree = ui_grid(
            subspace_tree.ui(root="🏠 [dim](Root)[/dim]",
                             custom_key=custom_key),
            ui_panel(tree_instruction, 'instruction')
        )

        console.print(ui_board(
            ui_info("Name", "%s [dim](%s)[/dim]" %
                    (self.name, self.root_path)),
            ui_info("Description", self.description),
            ui_info("Subspace Tree", ui_tree),
            ui_info("Subspace List", ui_subspace_list),
            ui_info("Imported Package List", ui_package_list),
            title="Summary"
        ))

        if (output_dir):
            node_dict = {
                ".": {
                    "name": "(Root)",
                    "content": " (Root) ",
                    "color": "#BEBEBE",
                    "size": 20,
                    "level": 0,
                    "border_width": 0,
                }
            }
            for subspace in subspace_dict.values():
                route_str = "_".join(subspace["route"])
                parent_str = "_".join(
                    subspace["parent"]) if subspace.get("parent") else "."
                if (subspace["type"] == SubspaceType.PHANTOM):
                    color = "#939393"
                    entities = ["&nbsp(None)&nbsp"]
                elif (subspace["type"] == SubspaceType.DIRECTORY):
                    color = "#F6B330"
                    entities = [
                        "&nbsp<a href='%s' target='_blank'>%s</a>&nbsp"
                        % (entity.as_uri(), str(entity.relative_to(self.sourcefiles_path)))
                        for entity in subspace["entities"]]
                else:
                    color = "#585858"
                    entities = [
                        "&nbsp<a href='%s' target='_blank'>%s</a>&nbsp"
                        % (entity.parent.as_uri(), str(entity.relative_to(self.sourcefiles_path)))
                        for entity in subspace["entities"]]

                node_dict[route_str] = {
                    "name": subspace["route"][-1],
                    "parent": parent_str,
                    "content": "<br>".join(entities),
                    "color": color,
                    "size": 5+subspace["flow"],
                    "level": len(subspace["route"]),
                    "border_width": 0,
                    "edge_width": 5+subspace["flow"],
                    "edge_color": '#3F3F3F',
                }
            draw_graph(node_dict,
                       bgcolor="#111112",
                       font_color="#F4F4F4",
                       output_dir=output_dir)

    @classmethod
    def create(
        cls,
        name: str,
        create_dir: PathLike = '.',
        info: OmoospaceInfo = None,
        structure: OmoospaceStructure = None,
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
        omoospace_path = Path(create_dir, format_name(name)).resolve()

        # Check if omoospace exists
        if (omoospace_path.is_dir()):
            raise ExistsError('omoospace', create_dir)

        try:
            # create root dir
            cls.make_dirs(omoospace_path)

            # create main dirs
            for dirname in Omoospace.MAIN_DIRS:
                cls.make_dirs(Path(omoospace_path, dirname))

            # use dict not list, for subdir structure.
            if (structure):
                # create contents subdirs
                contents_path = Path(omoospace_path, 'Contents')
                contents_subdirs = structure.get("contents") or {}
                cls.make_dirs(contents_path, contents_subdirs)

                # create contents subdirs
                sourcefiles_path = Path(omoospace_path, 'SourceFiles')
                sourcefiles_subdirs = structure.get("sourcefiles") or {}
                cls.make_dirs(sourcefiles_path, sourcefiles_subdirs)

            # write omoospace info to yml
            omoospace_info: OmoospaceInfo = {
                "name": name,  # can be any name style
                "description": info.get("description"),
                "creators": info.get("creators"),
                "softwares": info.get("softwares"),
                "works": info.get("works"),
            }

            omoospace_info_path = Path(
                omoospace_path, 'Omoospace.yml').resolve()
            with omoospace_info_path.open('w', encoding='utf-8') as file:
                yaml.safe_dump(omoospace_info, file, sort_keys=False)
        except Exception as err:
            shutil.rmtree(omoospace_path)
            raise Exception("Fail to create dirs", err)

        if reveal_when_success:
            reveal_in_explorer(omoospace_path)

        return cls(omoospace_path)

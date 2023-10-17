
from pathlib import Path
import shutil
from typing import Union
from zipfile import ZipFile

from rich.progress import track
from omoospace.directory import DirectoryTree
from omoospace.exceptions import CreateFailed, EmptyError, ExistsError, MoveFailed, NotFoundError, NotIncludeError
from omoospace.package import Package
from omoospace.subspace import SubspaceTree
from omoospace.common import console, yaml
from omoospace.ui import Board, Card, Info, ItemList, Table
from omoospace.utils import format_name, replace_or_append, reveal_in_explorer, is_subpath, PathLike, copy_to_path
from omoospace.types import Creator, Entity, Item, OmoospaceInfo, PackageInfo, Software, Structure, SubspaceInfo, Work

# TODO: package link in summary list

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
        info_path (Path): Omoospace.yml file path.
    """

    name: str
    description: str
    creators: list[Creator]
    softwares: list[Software]
    works: list[Work]

    def __init__(self, detect_dir: PathLike):
        """Initialize from existed omoospace directory.

        Args:
            detect_dir (PathLike): The start directory for detecting omoospace. It could be the subdirectories of omoospace.

        Raises:
            NotFoundError: No omoospace detected.
        """
        detect_path = Path(detect_dir).resolve()
        detect_path_parents = [detect_path, *detect_path.parents]
        omoospace_path = None
        for detect_path_parent in detect_path_parents:
            omoospace_info_path = Path(detect_path_parent, 'Omoospace.yml')
            if omoospace_info_path.exists():
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
        self.info_path = Path(self.root_path, "Omoospace.yml").resolve()

    def __read_info_file(self) -> OmoospaceInfo:
        with self.info_path.open('r', encoding='utf-8') as file:
            # aviod empty or invalid ifle
            info = yaml.load(file) or {}
        return info

    def __write_info_file(self, info: OmoospaceInfo):
        with self.info_path.open('w', encoding='utf-8') as file:
            yaml.dump(info, file)

    def __getattr__(self, name):
        if name in OmoospaceInfo.__annotations__.keys():
            info = self.__read_info_file()
            # FIXME: list attribute is not None but empty list.
            # may have better solution.
            if name[-1] == "s":
                return info.get(name) or []
            else:
                return info.get(name)

        return object.__getattribute__(self, name)

    def __setattr__(self, name, value):
        if name in OmoospaceInfo.__annotations__.keys():
            info = self.__read_info_file()
            info[name] = value
            self.__write_info_file(info)
        object.__setattr__(self, name, value)

    def is_omoospace_item(self, item: Item) -> bool:
        exists = item.exists()
        in_omoospace = is_subpath(item, self.root_path)
        not_in_stagedata = not is_subpath(
            item, self.stageddata_path, or_equal=True)
        not_omoospace_yml = item.name != "Omoospace.yml"
        return exists and in_omoospace and not_omoospace_yml and not_in_stagedata

    @property
    def subspace_entities(self) -> list[Entity]:
        """list[Entity]: the subspace entities in the sourcefiles directory."""
        return SubspaceTree.get_entities(search_dir=self.sourcefiles_path)

    @property
    def subspace_tree(self) -> SubspaceTree:
        """SubspaceTree: The subspace tree."""
        return SubspaceTree(search_dir=self.sourcefiles_path)

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
            info_filepath = Path(subdir, 'Package.yml').resolve()
            if info_filepath.is_file():
                packages.append(Package(subdir))

        return packages

    def set_subspace(
            self,
            subspace: Union[SubspaceInfo, str],
            parent_dir: PathLike = None,
            reveal_when_success: bool = True,
            collect_entities: bool = True
    ) -> Path:
        """Add or update subspace to this omoospace.

        Args:
            subspace (Union[SubspaceInfo, str]): [description]
            parent_dir (PathLike, optional): [description]. Defaults to None.
            reveal_when_success (bool, optional): [description]. Defaults to True.
            collect_entities (bool, optional): [description]. Defaults to True.

        Raises:
            ExistsError: [description]
            NotIncludeError: [description]
            EmptyError: [description]
            EmptyError: [description]
            EmptyError: [description]
            MoveFailed: [description]

        Returns:
            Path: [description]
        """

        parent_path = Path(parent_dir).resolve(
        ) if parent_dir else self.sourcefiles_path

        # Check if is valid directory
        if not parent_path.is_dir():
            raise ExistsError(parent_dir)

        # Check if is in SourceFiles
        if not is_subpath(parent_path, self.sourcefiles_path, or_equal=True):
            raise NotIncludeError(parent_dir, "SourceFiles")
        # FIXME: using SubspaceInfo need more code base on typing.
        # do it later.
        if isinstance(subspace, dict):
            # Check if name is empty
            if not subspace.get("name"):
                raise EmptyError("name")
            if not len(subspace.get("name")) > 0:
                raise EmptyError("name")
            subspace_info = subspace
            subspace_pathname = format_name(subspace.get("name"))
        else:
            if not len(subspace) > 0:
                raise EmptyError("name")

            subspace_info = {
                "name": subspace,
                "comments": None
            }
            subspace_pathname = format_name(subspace)

        subspace_path = Path(parent_path, subspace_pathname).resolve()

        # make subspace dir
        subspace_path.mkdir(parents=True, exist_ok=True)
        subspace_info_path = Path(subspace_path, 'Subspace.yml')
        with subspace_info_path.open('w', encoding='utf-8') as file:
            yaml.dump(subspace_info, file)

        if (collect_entities):
            try:
                entities = SubspaceTree.get_entities(
                    parent_path, recursive=False)

                def is_match(entity: Entity):
                    entity_stem = entity.stem
                    not_itself = entity_stem != subspace_pathname

                    is_match = False
                    entity_namespaces = format_name(entity_stem).split('_')
                    subspace_namespaces = subspace_pathname.split('_')
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
                    shutil.move(entity, Path(
                        subspace_path, entity.name).resolve())
            except:
                raise MoveFailed('entities')

        if reveal_when_success:
            reveal_in_explorer(subspace_path)

        return subspace_path

    def set_process(
            self,
            process: Union[Structure, list[str], str],
            parent_dir: PathLike = None,
            reveal_when_success: bool = True
    ) -> Path:
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
        parent_path = Path(parent_dir).resolve(
        ) if parent_dir else self.sourcefiles_path

        # Check if is valid directory
        if not parent_path.is_dir():
            raise ExistsError(parent_dir)

        # Check if is in SourceFiles
        if not is_subpath(parent_path, self.sourcefiles_path, or_equal=True):
            raise NotIncludeError(parent_dir, "SourceFiles")

        if isinstance(process, str):
            process = [process]

        if isinstance(process, list):
            process_structure = {}
            for p in process:
                process_structure[p] = None
        else:
            process_structure = process

        try:
            DirectoryTree(process_structure).make_dirs(parent_path)
        except Exception as err:
            raise CreateFailed("process directories")

        if reveal_when_success:
            reveal_in_explorer(parent_path)

    def set_creator(self, creator: Creator):
        """Add or update creator to this omoospace.

        Args:
            creator (Creator): [description]
        """
        creators = self.creators or []
        self.creators = replace_or_append(creators, creator, 'email')

    def set_software(self, software: Software):
        """Add or update software to this omoospace.

        Args:
            software (Software): [description]
        """
        softwares = self.softwares or []
        self.softwares = replace_or_append(softwares, software, 'name')

    def set_work(self, work: Work):
        """Add or update work to this omoospace.

        Args:
            work (Work): [description]

        Raises:
            NotFoundError: [description]
            NotFoundError: [description]
        """
        if "paths" not in work.keys():
            raise NotFoundError("paths", work)

        paths = [Path(path).resolve() for path in work["paths"]]
        paths = [path for path in paths
                 if path.exists() and is_subpath(path, self.contents_path)]

        if len(paths) == 0:
            raise NotFoundError("valid paths", work)

        relpaths = [path.relative_to(self.contents_path) for path in paths]

        work = {
            "name": work.get("name") or relpaths[0].stem,
            "paths": [str(relpath.as_posix())for relpath in relpaths]
        }
        works = self.works or []
        self.works = replace_or_append(works, work, 'name')

    def export_package(
        self,
        items: list[PathLike],
        name: str = None,
        export_dir: PathLike = None,
        info: PackageInfo = None,
        reveal_when_success: bool = True,
        overwrite_existing: bool = True
    ) -> Package:
        """Export a package.

        Args:
            items (list[PathLike]): [description]
            name (str, optional): [description]. Defaults to None.
            export_dir (PathLike, optional): [description]. Defaults to None.
            info (PackageInfo, optional): [description]. Defaults to None.
            reveal_when_success (bool, optional): [description]. Defaults to True.
            overwrite_existing (bool, optional): [description]. Defaults to True.

        Raises:
            ExistsError: [description]
            Exception: [description]
            Exception: [description]

        Returns:
            Package: [description]
        """
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
        items = list(filter(self.is_omoospace_item, items))

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
                yaml.dump(package_info, file)

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
        imported_packages = self.imported_packages
        subspace_tree = self.subspace_tree

        ui_creators = ItemList([
            "%s [dim]%s[/dim]" % (creator.get("name"), creator.get("role"))
            for creator in self.creators])
        ui_softwares = ItemList([
            "%s [dim]%s[/dim]" % (software.get("name"),
                                  software.get("version"))
            for software in self.softwares])

        ui_works = Table(
            "Name",
            "Paths"
        )

        for work in self.works:
            ui_works.add_row(
                work.get("name"),
                "\n".join(work.get("paths") or [])
            )

        console.print(Board(
            Info("Name", "%s [dim](%s)[/dim]" %
                 (self.name, self.root_path)),
            Info("Description", self.description),
            Info("Creators", ui_creators),
            Info("Softwares", ui_softwares),
            Info("Works", ui_works),
            Info("Subspace Tree", subspace_tree.render_tree()),
            Info("Subspace Entities", subspace_tree.render_table()),
            title="Summary"
        ))

        if (output_dir):
            subspace_tree.draw_graph(output_dir, reveal_when_success)

    def show_info(self):
        """Show profile of this omoospace.
        """
        ui_creators = ItemList([
            "%s [dim]%s[/dim]" % (creator.get("name"), creator.get("role"))
            for creator in self.creators])
        ui_softwares = ItemList([
            "%s [dim]%s[/dim]" % (software.get("name"),
                                  software.get("version"))
            for software in self.softwares])
        ui_works = Table(
            "Name",
            "Paths"
        )
        # TODO: add [link] to path
        for work in self.works:
            ui_works.add_row(
                work.get("name"),
                "\n".join(work.get("paths") or [])
            )
        console.print(Board(
            Info("Name", "%s [dim](%s)[/dim]" %
                 (self.name, self.root_path)),
            Info("Description", self.description),
            Info("Creators", ui_creators),
            Info("Softwares", ui_softwares),
            Info("Works", ui_works),
            title="Info"
        ))

    def show_subspace_tree(self):
        """Shows the subspace tree.
        """
        subspace_tree = self.subspace_tree
        console.print(Board(
            subspace_tree.render_tree(),
            title="Subspace Tree"
        ))

    def show_directory_tree(self):
        """Shows the directory tree.
        """
        directory_tree = self.directory_tree
        console.print(Board(
            directory_tree.render_tree(),
            title="Directory Tree"
        ))

    def show_imported_packages(self):
        """Show imported packages.
        """
        imported_packages = self.imported_packages
        ui_imported_packages = Table(
            "Directory", "Description",
            rows=[[package.name, package.description]
                  for package in imported_packages]
        )
        console.print(Board(
            ui_imported_packages,
            title="Imported Packages"
        ))

    def show_subspace_entities(self):
        """Shows the subspace entities.
        """
        subspace_tree = self.subspace_tree
        console.print(Board(
            subspace_tree.render_table(),
            title="Subspace Entities"
        ))

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
                yaml.dump(omoospace_info, file)
        except Exception as err:
            shutil.rmtree(omoospace_path, ignore_errors=True)
            raise CreateFailed("omoospace directories")

        if reveal_when_success:
            reveal_in_explorer(omoospace_path)

        return cls(omoospace_path)


import os
from typing import Union
from nutree import Tree, Node
from pathlib import Path
from omoospace.exceptions import InvalidError, NotFoundError, NotIncludeError
from omoospace.types import Structure, PathLike
from omoospace.utils import format_name, is_subpath
from omoospace.validators import is_entity


class Directory():
    def __init__(
        self,
        path: Path,
        is_subspace: bool = False,
    ):
        self.path = path
        self.is_subspace = is_subspace

    def __repr__(self):
        return self.path.name


class DirectoryTree(Tree):
    def __init__(self, structure: Structure = None, search_dir: PathLike = None):
        self.root_path = None
        super().__init__()
        if structure:
            self.from_structure(structure)
        if search_dir:
            self.from_dir(search_dir)

    def from_structure(
        self,
        structure: Structure,
        parent_dir: PathLike = None
    ):
        if parent_dir:
            node = self.add_dir(parent_dir)
        else:
            node = self
        self.__from_structure(node, structure)

    def from_dir(
        self,
        search_dir: PathLike,
        recursive: bool = True
    ):
        self.root_path = Path(search_dir).resolve()
        directories = self.get_dirs(search_dir, recursive=recursive)
        for directory in directories:
            self.add_dir(directory)

    def add_dir(self, dir: PathLike):
        path = Path(dir).resolve()
        if not path.is_dir():
            raise InvalidError(path, 'directory')
        if not self.root_path:
            raise NotFoundError('root directory')
        if self.root_path == path:
            return self
        if not is_subpath(path, self.root_path):
            raise NotIncludeError(path, 'root directory')

        relpath = path.relative_to(self.root_path)
        directory_paths = [relpath, *list(relpath.parents)[:-1]]
        directory_paths.reverse()
        node = self
        for directory_path in directory_paths:
            node_path = "/"+str(directory_path.as_posix())
            directory_node = self.find(
                match=lambda node: node.path == node_path
            )
            if not directory_node:
                is_subspace = is_entity(
                    Path(self.root_path, directory_path))
                directory = Directory(
                    path=directory_path,
                    is_subspace=is_subspace
                )
                directory_node = node.add(directory)
            node = directory_node
        return node

    @classmethod
    def get_dirs(
        cls,
        search_dir: PathLike,
        recursive: bool = True
    ) -> list[Path]:
        search_path: Path = Path(search_dir).resolve()
        directories: list[Path] = []

        if recursive:
            # FIXME: replace this with Path.walk (python 3.12)
            # https://docs.python.org/3/library/pathlib.html
            for root, dirs, files in os.walk(search_path):
                for dir in dirs:
                    child = Path(root, dir).resolve()
                    directories.append(child)
        else:
            for child in search_path.iterdir():
                directories.append(child)
        return directories

    def make_dirs(self, root_dir: PathLike = None):
        if not self.root_path and not root_dir:
            raise NotFoundError('root directory')
        self.__make_dirs(
            path=Path(root_dir) or self.root_path,
            node=self
        )

    @classmethod
    def __make_dirs(
        cls,
        path: Path,
        node: Union[Tree, Node],
        is_subspace: bool = False
    ):
        if (isinstance(node, Node)):
            dirpath = Path(path, node.path.removeprefix("/")).resolve()
            is_subspace = node.data.is_subspace
        else:
            dirpath = path.resolve()

        dirpath.mkdir(parents=True, exist_ok=True)
        if is_subspace:
            with Path(dirpath, "Subspace.yml").open('w') as file:
                pass

        for sub_node in node:
            cls.__make_dirs(path, node=sub_node)

    def __from_structure(
        self,
        node: Union[Tree, Node],
        structure: Structure,
    ):
        for key in structure.keys():
            parent_path = node.path if isinstance(node, Node) else "."
            directory_name = format_name(key)
            directory_path = Path(parent_path, directory_name)
            node_path = "/"+str(directory_path.as_posix())
            directory_node = self.find(
                match=lambda node: node.path == node_path
            )
            if not directory_node:
                is_subspace = key[0] == "*" \
                    or "Void" in directory_name.split("_")
                directory = Directory(
                    path=directory_path,
                    is_subspace=is_subspace
                )
                directory_node = node.add(directory)
            sub_structure = structure[key]
            if sub_structure:
                self.__from_structure(
                    node=directory_node,
                    structure=sub_structure,
                )


from os import PathLike
from nutree import Tree, Node
from pathlib import Path
from omoospace.types import Structure
from omoospace import ui
from omoospace.utils import format_name


class Directory():
    def __init__(self, name: str, path: Path = None, is_subspace: bool = False):
        self.name = format_name(name)
        self.path = path or Path(self.name)
        self.is_subspace = is_subspace

    def __repr__(self):
        return "🎯 %s" % self.name if self.is_subspace else \
            "📂 %s" % self.name


class DirectoryTree(Tree):
    def __init__(self, structure: Structure = None, root_dir: PathLike = None):
        super().__init__(calc_data_id=self.__calc_id)
        if structure:
            self.__set_from_structure(self, structure)
        if root_dir:
            root_path = Path(root_dir).resolve()
            self.__set_from_path(root_path)

    def __set_from_path(self, path: Path):
        pass

    def make_dirs(self, root_dir: PathLike, is_subspace: bool = False):
        self.__make_dirs(
            path=Path(root_dir),
            node=self,
            is_subspace=is_subspace
        )

    @classmethod
    def __make_dirs(
        cls,
        path: Path,
        node: Tree | Node,
        is_subspace: bool = False
    ):
        """Create all subdirectories in a directory.

        Args:
            dir (PathLike): The directory to create.
            subdirs (dict[str, any], optional): The subdirectories under that directory. Defaults to {}.
            is_subspace (bool, optional): If true, 'Subspace.yml' will be created in that dicrectory. Defaults to False.
        """

        if (isinstance(node, Node)):
            dirpath = Path(path, node.data.path).resolve()
            is_subspace = node.data.is_subspace
        else:
            dirpath = path.resolve()

        dirpath.mkdir(parents=True, exist_ok=True)
        if is_subspace:
            with Path(dirpath, "Subspace.yml").open('w') as file:
                pass

        for sub_node in node:
            cls.__make_dirs(path, node=sub_node)

    @classmethod
    def __set_from_structure(
        cls,
        node: Tree | Node,
        structure: Structure,
        path: Path = Path(".")
    ):
        for dirname in structure.keys():
            name = format_name(dirname)
            sub_path = Path(path, name)
            is_subspace = dirname[0] == "*" or "Void" in name.split("_")
            sub_node = node.add(Directory(
                name=dirname,
                path=sub_path,
                is_subspace=is_subspace
            ))
            sub_structure = structure[dirname]
            if sub_structure:
                cls.__set_from_structure(
                    node=sub_node,
                    structure=sub_structure,
                    path=sub_path
                )

    @staticmethod
    def __calc_id(tree, data):
        if isinstance(data, Directory):
            return str(data.path)
        return hash(data)

    def render_tree(self):

        label_dict = {
            "📂": "ordinary direcotry\nwhich is for file classification.",
            "🎯": "subspace direcotry\nwhich is for presenting subspace.",
        }
        return ui.Grid(
            self.format(title="(Root)"),
            ui.Instruction(label_dict)
        )


# from collections import defaultdict
# from typing import Callable
# from rich.tree import Tree as UITree
# Route = list[str]
# TreeDict = dict
# class Tree:
#     # https://gist.github.com/hrldcpr/2012250#one-line-tree-in-python

#     def __init__(self, dict: dict):
#         # init new tree using tree class which created by defaultdict.
#         self.__tree = self.__tree_class()
#         self.__routes: dict[Route, dict] = []
#         if dict:
#             self.__set_tree(self.__tree, self.__routes, dict)

#     @classmethod
#     def __set_tree(
#         cls,
#         tree: dict,
#         route_dict: dict[Route, dict],
#         dict: dict,
#         pre_route: Route = [],
#     ):
#         for key in dict.keys():
#             subtree = tree[key]
#             subdict = dict[key]
#             route = pre_route.append(key)
#             route_dict[route] = None
#             if subdict:
#                 cls.__set_tree(
#                     tree=subtree,
#                     dict=subdict,
#                     route_dict=route_dict,
#                     pre_route=route
#                 )

#     def __getitem__(self, key):
#         return self.__tree[key]

#     @classmethod
#     def __tree_class(cls) -> TreeDict:
#         """Return tree class using defaultdict as class factory.

#         Returns:
#             dict: [description]
#         """
#         return defaultdict(cls.__tree_class)

#     # def set_route(self, route: list[str],):
#     #     self.__add(self.__tree, nodes)

#     # def get_route(self, route: list[str],):
#     #     self.__add(self.__tree, nodes)

#     @staticmethod
#     def __add(subtree, nodes):
#         for node in nodes:
#             subtree = subtree[node]

#     @classmethod
#     def __to_dict(cls, subtree: dict):
#         return {key: cls.__to_dict(subtree[key]) for key in subtree}

#     @classmethod
#     def __str(
#         cls,
#         subtree: dict,
#         custom_key: Callable[[list], str] = lambda nodes: nodes[-1],
#         _prefix="",
#         _nodes: list = []
#     ):
#         """ print a tree """
#         print__string = ""
#         keys = list(subtree.keys())
#         for n in range(len(keys)):
#             key = keys[n]
#             is_last = n == len(keys) - 1
#             end_prefix = "`-- " if is_last else "|-- "
#             next_prefix = _prefix + "    " if is_last else _prefix + "|    "

#             next_nodes = _nodes.copy()
#             next_nodes.append(key)
#             print__string += "\n" + \
#                 _prefix + end_prefix + custom_key(next_nodes)
#             print__string += cls.__str(
#                 subtree[key],
#                 custom_key=custom_key,
#                 _prefix=next_prefix,
#                 _nodes=next_nodes
#             )
#         return print__string

#     @property
#     def dict(self) -> dict:
#         """Returns trees are either values or a builtin python dict."""
#         return self.__to_dict(self.__tree)

#     @classmethod
#     def __ui(
#         cls,
#         ui_sbutree: UITree,
#         subtree: dict,
#         custom_key: Callable[[list], str] = lambda nodes: nodes[-1],
#         _nodes: list = []
#     ):
#         keys = list(subtree.keys())
#         for n in range(len(keys)):
#             key = keys[n]
#             next_nodes = _nodes.copy()
#             next_nodes.append(key)
#             cls.__ui(
#                 ui_sbutree=ui_sbutree.add(custom_key(next_nodes)),
#                 subtree=subtree[key],
#                 custom_key=custom_key,
#                 _nodes=next_nodes
#             )
#         return ui_sbutree

#     def ui(
#         self,
#         root="(Root)",
#         custom_key: Callable[[list], str] = lambda nodes: nodes[-1]
#     ):
#         ui_tree = UITree(root)
#         return self.__ui(ui_tree, self.__tree, custom_key=custom_key)

#     def print(
#         self,
#         custom_key: Callable[[list], str] = lambda nodes: nodes[-1],
#         verbose: bool = True
#     ):
#         print__string = "(Root)" + self.__str(self.__tree,
#                                               custom_key=custom_key)
#         if verbose:
#             print(print__string)
#         return print__string

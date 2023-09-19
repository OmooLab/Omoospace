from collections import defaultdict
from typing import Callable
from rich.tree import Tree as UITree


class Tree:
    # https://gist.github.com/hrldcpr/2012250#one-line-tree-in-python
    """
    Returns mutable trees structure, allowing for the following:
    tree = TreeDict()
    """

    def __init__(self):
        self._tree = self._init_tree()

    def __getitem__(self, key):
        return self._tree[key]

    def __str__(self):
        return self.print(verbose=False)

    @staticmethod
    def _add(subtree, nodes):
        for node in nodes:
            subtree = subtree[node]

    @classmethod
    def _init_tree(cls) -> dict:
        return defaultdict(cls._init_tree)

    @classmethod
    def _to_dict(cls, subtree: dict):
        return {key: cls._to_dict(subtree[key]) for key in subtree}

    @classmethod
    def _str(
        cls,
        subtree: dict,
        custom_key: Callable[[list], str] = lambda nodes: nodes[-1],
        _prefix="",
        _nodes: list = []
    ):
        """ print a tree """
        print_string = ""
        keys = list(subtree.keys())
        for n in range(len(keys)):
            key = keys[n]
            is_last = n == len(keys) - 1
            end_prefix = "`-- " if is_last else "|-- "
            next_prefix = _prefix + "    " if is_last else _prefix + "|    "

            next_nodes = _nodes.copy()
            next_nodes.append(key)
            print_string += "\n" + \
                _prefix + end_prefix + custom_key(next_nodes)
            print_string += cls._str(
                subtree[key],
                custom_key=custom_key,
                _prefix=next_prefix,
                _nodes=next_nodes
            )
        return print_string

    def add(self, nodes: list):
        self._add(self._tree, nodes)

    @property
    def dict(self) -> dict:
        """Returns trees are either values or a builtin python dict."""
        return self._to_dict(self._tree)

    @classmethod
    def _ui(
        cls,
        ui_sbutree: UITree,
        subtree: dict,
        custom_key: Callable[[list], str] = lambda nodes: nodes[-1],
        _nodes: list = []
    ):
        keys = list(subtree.keys())
        for n in range(len(keys)):
            key = keys[n]
            next_nodes = _nodes.copy()
            next_nodes.append(key)
            cls._ui(
                ui_sbutree=ui_sbutree.add(custom_key(next_nodes)),
                subtree=subtree[key],
                custom_key=custom_key,
                _nodes=next_nodes
            )
        return ui_sbutree

    def ui(
        self,
        root="(Root)",
        custom_key: Callable[[list], str] = lambda nodes: nodes[-1]
    ):
        ui_tree = UITree(root)
        return self._ui(ui_tree, self._tree, custom_key=custom_key)

    def print(
        self,
        custom_key: Callable[[list], str] = lambda nodes: nodes[-1],
        verbose: bool = True
    ):
        print_string = "(Root)" + self._str(self._tree, custom_key=custom_key)
        if verbose:
            print(print_string)
        return print_string

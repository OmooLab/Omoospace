
import os
from pathlib import Path
from typing import Union
from nutree import Tree

from omoospace.graph import draw_graph
from omoospace.types import Entity, PathLike, Route, SubspaceInfo, SubspaceType
from omoospace.common import console, yaml
from omoospace.ui import Grid, Instruction, Table
from omoospace.utils import format_name


class Subspace():
    def __init__(
        self,
        name: str,
        info: SubspaceInfo = None,
    ):
        self.pathname = name
        self.entities: list[Entity] = []
        self.flow: int = 0
        self.type: SubspaceType = None

        if isinstance(info, str):
            self.name = name
            self.comments = [info]
        elif isinstance(info, list):
            self.name = name
            self.comments = info
        elif isinstance(info, dict):
            self.name = info.get('name') or name
            comments = info.get('comments')
            if isinstance(comments, str) and comments:
                self.comments = [comments]
            elif isinstance(comments, list):
                self.comments = [*comments]
            else:
                self.comments = []
        else:
            self.name = name
            self.comments = []

    def __repr__(self):
        return self.pathname

    @property
    def ui_name(self):
        if self.type == SubspaceType.DIRECTORY:
            icon = "📁"
            link = self.entities[0]
            name_str = "[link=%s]%s[/link]" % (link, self.name)
        elif self.type == SubspaceType.FILE:
            icon = "📄"
            link = self.entities[0].parent
            name_str = "[link=%s]%s[/link]" % (link, self.name)
        elif self.type == SubspaceType.PHANTOM:
            icon = "💿"
            name_str = self.name
        else:
            icon = "⛔"
            name_str = self.name

        if self.pathname == self.name:
            pathname_str = ""
        else:
            pathname_str = " [dim](%s)[/dim]" % self.pathname
        return "%s %s%s" % (icon, name_str, pathname_str)

    @property
    def html_name(self):
        if self.pathname == self.name:
            pathname_str = ""
        else:
            pathname_str = " (%s)" % self.pathname
        return "%s%s" % (self.name, pathname_str)

    @property
    def ui_comments(self):
        return ["[dim]- %s[/dim]" %
                comment for comment in self.comments]

    @property
    def ui_entities(self):
        entity_links: list[str] = []
        for entity in self.entities:
            entity_path = entity if entity.is_dir() else entity.parent
            entity_links.append("[link=%s]%s[/link]" %
                                (entity_path, entity.name))
        return entity_links

    @property
    def html_entities(self):
        entity_links: list[str] = []
        for entity in self.entities:
            entity_links.append("&nbsp<a href='%s' target='_blank'>%s</a>&nbsp"
                                % (entity, entity.name))
        return entity_links


class SubspaceTree(Tree):
    def __init__(
        self,
        search_dir: PathLike
    ):
        super().__init__()
        if (search_dir):
            self.from_dir(search_dir)

    def from_dir(
        self,
        search_dir: PathLike,
        recursive: bool = True
    ):
        entities = self.get_entities(search_dir, recursive=recursive)
        for entity in entities:
            self.add_entity(entity)

    def add_entity(self, entity: Entity):
        entity = entity.resolve()

        # Get relpath parts. remove those directory that is not entity.
        entities = [entity]
        for parent in entity.parents:
            if self.is_entity(parent):
                entities.append(parent)
        entities.reverse()

        parts = [{
            "name": format_name(entity.stem),
            "entity": entity
        } for entity in entities]

        # Get route nodes. remove duplicate prefix.
        route: Route = []
        node = self
        for part in parts:
            part_name: str = part["name"]
            part_entity: Entity = part["entity"]

            namespaces: list[str] = part_name.split('_')
            subspace_info_path = Path(part_entity, "Subspace.yml").resolve()

            # clip matched prefix spaces
            for i in range(len(route)):
                route_str_suffix = '_'.join(route[i:])
                name_prefix = '_'.join(namespaces[:len(route) - i])
                if route_str_suffix == name_prefix:
                    namespaces = namespaces[len(route) - i:]
                    break

            # create or get subspace by namespace
            for i in range(len(namespaces)):
                is_last = i == len(namespaces)-1
                subspace_route = route + namespaces[:i+1]
                node_path = "/" + "/".join(subspace_route)
                subspace_node = self.find(
                    match=lambda node: node.path == node_path
                )
                if not subspace_node:
                    if is_last and subspace_info_path.is_file():
                        with subspace_info_path.open('r', encoding='utf-8') as file:
                            subspace_info = yaml.load(file) or {}
                    else:
                        subspace_info = {}
                    subspace = Subspace(
                        name=namespaces[i],
                        info=subspace_info,
                    )
                    subspace_node = node.add(subspace)

                # if is last, add enitity to it.
                if is_last and part_entity not in subspace_node.data.entities:
                    subspace_node.data.entities.append(part_entity)

                # assign type
                subspace_type = subspace_node.data.type
                if is_last and part_entity.is_dir():
                    subspace_node.data.type = SubspaceType.DIRECTORY
                elif subspace_type != SubspaceType.DIRECTORY \
                        and is_last and part_entity.is_file():
                    subspace_node.data.type = SubspaceType.FILE
                elif subspace_type != SubspaceType.DIRECTORY \
                        and subspace_type != SubspaceType.FILE\
                        and part_entity.exists():
                    subspace_node.data.type = SubspaceType.PHANTOM

                # what ever is end node or not, all nodes are passed through.
                subspace_node.data.flow += 1

                node = subspace_node
            route.extend(namespaces)

    @classmethod
    def get_entities(
        cls,
        search_dir: PathLike,
        recursive: bool = True
    ) -> list[Entity]:
        search_path: Path = Path(search_dir).resolve()
        entities: list[Entity] = []
        if recursive:
            # FIXME: replace this with Path.walk (python 3.12)
            # https://docs.python.org/3/library/pathlib.html
            for root, dirs, files in os.walk(search_path):
                for path in [*dirs, *files]:
                    child = Path(root, path).resolve()
                    if cls.is_entity(child):
                        entities.append(child)
        else:
            for child in search_path.iterdir():
                if cls.is_entity(child):
                    entities.append(child)
        return entities

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

    def render_tree(self):

        label_dict = {
            "📁": "direcotry subspace\nwhich contains Subspace.yml.",
            "📄": "file subspace\nwhich refers to a leaf file.",
            "💿": "phantom | unknown subspace\nwhich has no entity.",
            "⛔": "virtual subspace\nwhich have not created yet."
        }

        return Grid(
            self.format(repr="{node.data.ui_name}", title="(Root)"),
            Instruction(label_dict)
        )

    def render_table(self):
        table = Table(
            "Subspace",
            "Comments",
            "Entities"
        )

        for node in self:
            subspace: Subspace = node.data
            table.add_row(
                subspace.ui_name,
                "\n".join(subspace.ui_comments),
                "\n".join(subspace.ui_entities)
            )
        return table

    def draw_graph(
        self,
        output_dir: PathLike,
        reveal_when_success: bool = True
    ):
        node_dict = {
            ".": {
                "name": "(Root)",
                "content": "&nbsp(Root)&nbsp",
                "color": "#BEBEBE",
                "size": 20,
                "level": 0,
                "border_width": 0,
            }
        }
        for node in self:
            subspace: Subspace = node.data
            parent: Subspace = node.parent.data if node.parent else None

            if (subspace.type == SubspaceType.PHANTOM):
                color = "#939393"
            elif (subspace.type == SubspaceType.DIRECTORY):
                color = "#F6B330"
            else:
                color = "#585858"

            node_dict[node.path] = {
                "name": subspace.html_name,
                "parent": node.parent.path if parent else ".",
                "content": "<br>".join(subspace.html_entities),
                "color": color,
                "size": 5+subspace.flow,
                # "level": node.depth,
                "border_width": 0,
                "edge_width": 5+subspace.flow,
                "edge_color": '#3F3F3F',
            }

        draw_graph(
            node_dict,
            bgcolor="#111112",
            font_color="#F4F4F4",
            output_dir=output_dir,
            reveal_when_success=reveal_when_success
        )

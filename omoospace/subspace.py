
from pathlib import Path
from nutree import Tree
import yaml
from omoospace.graph import draw_graph
from omoospace.types import Entity, PathLike, Route, SubspaceInfo, SubspaceType
from omoospace import ui, console


class Subspace():
    __name: str
    __comments: list[str]

    def __init__(
        self,
        route: Route,
        info: SubspaceInfo,
    ):
        self.route = route
        self.entities: list[Entity] = []
        self.flow: int = 0
        self.type: SubspaceType = None

        if isinstance(info, str):
            self.name = route[-1]
            self.comments = [info]
        elif isinstance(info, list):
            self.name = route[-1]
            self.comments = info
        elif isinstance(info, dict):
            self.name = info.get('name') or route[-1]
            comments = info.get('comments')
            if isinstance(comments, str) and comments:
                self.comments = [comments]
            elif isinstance(comments, list):
                self.comments = [*comments]
            else:
                self.comments = []
        else:
            self.name = route[-1]
            self.comments = []

    def __repr__(self):
        return self.route[-1]

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
            icon = "⭕"
            name_str = self.name
        else:
            icon = "🆕"
            name_str = self.name

        if self.route[-1] == self.name:
            route_str = ""
        else:
            route_str = " [dim](%s)[/dim]" % self.route[-1]
        return "%s %s" % (icon, name_str)+route_str

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
        *entities: Entity,
        omoospace: "Omoospace"
    ):
        self.omoospace = omoospace
        super().__init__(calc_data_id=self.__calc_id)
        for entity in entities:
            entity_route: Route = self.omoospace.get_route(entity)
            subspace_info_path = Path(entity, "Subspace.yml").resolve()
            # create all node as subspace in route
            for i in range(len(entity_route)):
                is_last = i == len(entity_route)-1
                is_first = i == 0

                subspace_route = entity_route[:i+1]
                parent_route = entity_route[:i]
                parent_node = self if is_first else self.find(
                    data_id="_".join(parent_route))

                if is_last and subspace_info_path.is_file():
                    with subspace_info_path.open('r', encoding='utf-8') as file:
                        subspace_info = yaml.safe_load(file) or {}
                else:
                    subspace_info = {}

                subspace_node = self.find(data_id="_".join(subspace_route))
                if not subspace_node:
                    subspace = Subspace(
                        route=subspace_route,
                        info=subspace_info,
                    )
                    subspace_node = parent_node.add(subspace)

                # if is last, add enitity to it.
                if is_last:
                    subspace_node.data.entities.append(entity)

                # what ever is end node or not, all nodes are passed through.
                subspace_node.data.flow += 1

        for node in self:
            subspace = node.data
            if (len(subspace.entities) == 0):
                subspace.type = SubspaceType.PHANTOM
            else:
                subspace.type = None
                for entity in subspace.entities:
                    if (entity.is_file()):
                        subspace.type = SubspaceType.FILE
                    if (entity.is_dir()):
                        subspace.type = SubspaceType.DIRECTORY
                        break

    @staticmethod
    def __calc_id(tree, data):
        if isinstance(data, Subspace):
            return "_".join(data.route)
        return hash(data)

    def render_tree(self):

        label_dict = {
            "📁": "direcotry subspace\nwhich contains Subspace.yml.",
            "📄": "file subspace\nwhich refers to a leaf file.",
            "⭕": "phantom | unknown subspace\nwhich has no entity.",
            "🆕": "new subspace\nwhich have not created yet."
        }

        return ui.Grid(
            self.format(repr="{node.data.ui_name}", title="(Root)"),
            ui.Instruction(label_dict)
        )

    def render_table(self):
        table = ui.Table(
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
                "content": " (Root) ",
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

            node_dict[node.data_id] = {
                "name": subspace.name,
                "parent": node.parent.data_id if parent else ".",
                "content": "<br>".join(subspace.html_entities),
                "color": color,
                "size": 5+subspace.flow,
                "level": len(subspace.route),
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

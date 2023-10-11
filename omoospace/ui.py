
from rich.table import Table as R_Table, Column
from rich.panel import Panel
from rich.console import Group
from rich import box
from rich.console import Console
from rich.theme import Theme

custom_theme = Theme({
    "bright": "#ffd700",
    "dim_bright": "#808080",
    "dim": "#808080",
    "warning": "bold #ffffff on #ffd700",
    "danger": "bold #ffffff on red",
    "cheer": "bold #ffffff on blue"
})
console = Console(theme=custom_theme)


class Card(Panel):
    def __init__(self, renderable, title=None):
        super().__init__(
            renderable,
            title=title
        )


class Board(Panel):
    def __init__(self, *renderables, title=None) -> None:
        content = Group(*renderables)
        super().__init__(
            content,
            title=title,
            expand=True,
            padding=(1, 3),
            box=box.ROUNDED
        )


class Info(R_Table):
    def __init__(self, key, value) -> None:
        super().__init__(
            box=box.ROUNDED,
            show_edge=False,
            show_header=False,
            title=key,
            title_style="b i",
            title_justify="left",
            padding=(0, 0, 1, 0),
            expand=True
        )
        self.add_column("")
        self.add_row(value)


class Instruction(Card):
    def __init__(self, label_dict: dict[str, str]) -> None:
        labels = ["[dim]%s --- %s" % (key, value)
                  for key, value in label_dict.items()]
        super().__init__(
            "\n\n".join(labels), title='instruction'
        )


class Table(R_Table):
    def __init__(self, *headers: list[Column | dict | str], title=None, rows: list[list] = []):
        headers = [Column(**header)if isinstance(header, dict)
                   else Column(header) for header in headers]
        super().__init__(
            *headers,
            title=title,
            box=box.ROUNDED,
            header_style="i",
            expand=True
        )
        for row in rows:
            self.add_row(*row)


class Grid(R_Table):
    def __init__(self, *columns, vertical="top", expand=True):
        # grid = Columns(renderables)
        super().__init__(
            box=box.SIMPLE,
            show_header=False,
            show_edge=False,
            padding=(0, 0),
            expand=expand
        )
        renderables = []
        for column in columns:
            if isinstance(column, dict):
                ui = column.get('ui')
                kwargs = column.get('kwargs')
            else:
                ui = column
                kwargs = {
                    "header": "",
                    "vertical": vertical,
                }
            self.add_column(**kwargs)
            renderables.append(ui)
        self.add_row(*renderables)


class Transfer(Grid):
    def __init__(self, left_list, right_list, left_header="Left", right_header="Right"):
        super().__init__(
            Panel(
                "\n".join(["? %s" % item for item in left_list]),
                title=left_header,
                style="bright",
                border_style="white",
                padding=(1, 4)
            ),
            {"ui": "=>", "kwargs": {"justify": "center", "vertical": "middle"}},
            Panel(
                "\n".join(["√ %s" % item for item in right_list]),
                title=right_header,
                style="dim",
                border_style="white",
                padding=(1, 4)
            ),
            vertical="middle",
            expand=False
        )


# def ui_info(key, value):
#     ui = Table(
#         box=box.ROUNDED,
#         show_edge=False,
#         show_header=False,
#         title=key,
#         title_style="b i",
#         title_justify="left",
#         padding=(0, 0, 1, 0),
#         expand=True
#     )
#     ui.add_column("")
#     ui.add_row(value)
#     return ui


# def ui_instruction(label_dict: dict[str, str]):
#     labels = ["[dim]%s --- %s" % (key, value)
#               for key, value in label_dict.items()]
#     return ui_panel("\n\n".join(labels), 'instruction')


# def ui_table(*headers: "Column", title=None):
#     headers = [Column(**header)if isinstance(header, dict)
#                else Column(header) for header in headers]
#     return Table(*headers, title=title, box=box.ROUNDED,
#                  header_style="i", expand=True)


# def ui_grid(*columns, vertical="top", expand=True):
#     # grid = Columns(renderables)
#     grid = Table(
#         box=box.SIMPLE,
#         show_header=False,
#         show_edge=False,
#         padding=(0, 0),
#         expand=expand
#     )
#     renderables = []
#     for column in columns:
#         if isinstance(column, dict):
#             ui = column.get('ui')
#             kwargs = column.get('kwargs')
#         else:
#             ui = column
#             kwargs = {
#                 "header": "",
#                 "vertical": vertical,
#             }
#         grid.add_column(**kwargs)
#         renderables.append(ui)
#     grid.add_row(*renderables)
#     return grid


# def ui_transfer(left_list, right_list, left_header="Left", right_header="Right"):
#     transfer = ui_grid(
#         Panel(
#             "\n".join(["? %s" % item for item in left_list]),
#             title=left_header,
#             style="bright",
#             border_style="white",
#             padding=(1, 4)
#         ),
#         {"ui": "=>", "kwargs": {"justify": "center", "vertical": "middle"}},
#         Panel(
#             "\n".join(["√ %s" % item for item in right_list]),
#             title=right_header,
#             style="dim",
#             border_style="white",
#             padding=(1, 4)
#         ),
#         vertical="middle",
#         expand=False
#     )
#     return transfer


# def ui_panel(renderable, title=None):
#     return Panel(renderable, title=title)


# def ui_board(*renderables, title=None):
#     content = Group(*renderables)
#     return Panel(content, title=title, expand=True, padding=(1, 3), box=box.ROUNDED)

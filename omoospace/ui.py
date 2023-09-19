
from rich.table import Table, Column
from rich.panel import Panel
from rich.console import Group
from rich.text import Text
from rich import box
from rich.console import Console
from rich.theme import Theme
from rich.padding import Padding
from rich.layout import Layout
from rich.columns import Columns

custom_theme = Theme({
    "bright": "#ffd700",
    "dim_bright": "#808080",
    "dim": "#808080",
    "warning": "bold #ffffff on #ffd700",
    "danger": "bold #ffffff on red",
    "cheer": "bold #ffffff on blue"
})
console = Console(theme=custom_theme)


def ui_info(key, value):
    ui = Table(
        box=box.ROUNDED,
        show_edge=False,
        show_header=False,
        title=key,
        title_style="b i",
        title_justify="left",
        padding=(0, 0),
        expand=True
    )
    ui.add_column("")
    ui.add_row(value)
    return Padding(ui, (0, 0, 1, 0))


def ui_table(*headers: "Column", title=None):
    headers = [Column(**header)if isinstance(header, dict)
               else Column(header) for header in headers]
    ui = Table(*headers, title=title, box=box.ROUNDED,
               header_style="i", expand=True)
    return ui


def ui_grid(*columns, vertical="top", expand=True):
    # grid = Columns(renderables)
    grid = Table(
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
        grid.add_column(**kwargs)
        renderables.append(ui)
    grid.add_row(*renderables)
    return grid


def ui_transfer(left_list, right_list, left_header="Left", right_header="Right"):
    transfer = ui_grid(
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
    return transfer


def ui_panel(renderable, title=None):
    return Panel(renderable, title=title)


def ui_board(*renderables, title=None):
    content = Group(*renderables)
    return Panel(content, title=title, expand=True, padding=(1, 3), box=box.ROUNDED)

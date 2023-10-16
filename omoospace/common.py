from rich.theme import Theme
from rich.console import Console
from ruamel.yaml import YAML

yaml = YAML()
yaml.indent(sequence=4, offset=2)

custom_theme = Theme({
    "bright": "#ffd700",
    "dim_bright": "#808080",
    "dim": "#808080",
    "warning": "bold #ffffff on #ffd700",
    "danger": "bold #ffffff on red",
    "cheer": "bold #ffffff on blue"
})
console = Console(theme=custom_theme)

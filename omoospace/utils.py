import re
import os
from pathlib import Path
import shutil
from pypinyin import lazy_pinyin
from omoospace.types import PathLike
from omoospace import console, ui


def format_name(string: str, verbose=False):
    debug_info = ui.Table(
        {"header": "Step", "justify": "right"},
        {"header": "Result", "justify": "left", "style": "highlight"}
    )
    debug_info.add_row("Original", string)

    # [A-Za-z0-9_-] only
    string = re.sub(r'[^\w-]', ' ', string)
    parts = [string for string in string.split()]
    debug_info.add_row("to Parts",
                       " [white]|[/white] ".join(parts))

    # Chinese character to pinyin
    parts = [char
             for string in parts
             for char in lazy_pinyin(string)]

    debug_info.add_row("to PinYin",
                       " [white]|[/white] ".join(parts))

    # to PascalCase
    parts = [string.title() if string.islower() else string
             for string in parts]
    debug_info.add_row("to PascalCase",
                       " [white]|[/white] ".join(parts))
    string = ''.join(parts)
    if (verbose):
        console.print(debug_info)
    return string


def reveal_in_explorer(dir: str):
    try:
        os.startfile(Path(dir).resolve())
    except Exception as err:
        print("Fail to reveal", err)


def is_subpath(child: PathLike, parent: PathLike, or_equal=False):
    """Return True if child is a subpath of parent .

    Args:
        child (str): [description]
        parent (str): [description]
        or_equal (bool, optional): [description]. Defaults to False.

    Returns:
        [type]: [description]
    """
    parent = Path(parent).resolve()
    child = Path(child).resolve()
    is_subpath = parent in child.parents
    is_equal = parent == child
    if or_equal:
        return is_subpath or is_equal
    else:
        return is_subpath


def copy_to_path(src: PathLike, dst: PathLike):
    """Copies the contents form src to dst .

    Args:
        src (Path): [description]
        dst (Path): [description]
    """
    src = Path(src).resolve()
    dst = Path(dst).resolve()
    dst.parent.mkdir(parents=True, exist_ok=True)
    if src.is_dir():
        shutil.copytree(src, dst)
    else:
        shutil.copy(src, dst)

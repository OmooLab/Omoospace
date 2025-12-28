import re
import os
from pathlib import Path
import shutil
from pypinyin import lazy_pinyin
from omoospace.validators import (
    is_autosave,
    is_number,
    is_version,
    is_recovered,
    is_buckup,
)
from omoospace import pyperclip


def format_name(string: str, chinese_to_pinyin: bool = False) -> str:
    def is_semantic(s: str):
        return not (
            is_number(s)
            or is_version(s)
            or is_autosave(s)
            or is_recovered(s)
            or is_buckup(s)
        )

    # Remove everything after the first "."
    string = string.split(".", 1)[0]

    result_parts = []
    for part in string.split("_"):
        words = [w for w in re.split(r"\s+", part) if is_semantic(w)]
        if not words:
            continue
        cleaned = re.sub(r"[^\w-]", " ", " ".join(words))
        if chinese_to_pinyin:
            cleaned = " ".join(lazy_pinyin(cleaned))
        # PascalCase: preserve original capitalization for multi-letter words, single letters uppercase
        pascal = ""
        for w in cleaned.split():
            if len(w) == 1:
                pascal += w.upper()
            else:
                pascal += w[0].upper() + w[1:]
        if pascal:
            result_parts.append(pascal)

    return "_".join(result_parts)


def remove_duplicates(list, key):
    seen = set()
    new_list = []
    for d in list:
        if d[key] not in seen:
            seen.add(d[key])
            new_list.append(d)
    return new_list


def reveal_directory(dst: str):
    """Open the directory in file exploarer

    Args:
        dst (str): The directory want to open
    """
    try:
        os.startfile(Path(dst))
    except Exception as err:
        print("Fail to reveal", err)


def is_subpath(child: str, parent: str, or_equal=False) -> bool:
    """Return True if child is a subpath of parent .

    Args:
        child (str): Child path
        parent (str): Parent path
        or_equal (bool, optional): [description]. Defaults to False.

    Returns:
        bool: Result.
    """
    parent = Path(parent).resolve()
    child = Path(child).resolve()
    is_subpath = parent in child.parents
    is_equal = parent == child
    if or_equal:
        return is_subpath or is_equal
    else:
        return is_subpath


def copy_to(src: str, dst: str):
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


def copy_to_clipboard(string: str):
    """Copy to clipboard

    Args:
        string (str): The string want to be copyed.
    """

    pyperclip.copy(string)


def rm_children(dir: str):
    dirpath = Path(dir).resolve()
    for child in dirpath.iterdir():
        if child.is_file():
            child.unlink()
        else:
            shutil.rmtree(child, ignore_errors=True)

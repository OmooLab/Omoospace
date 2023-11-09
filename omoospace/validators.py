from pathlib import Path
import re


def is_number(string):
    pattern = r'^-?\d+(?:\.\d+)?$'
    return bool(re.match(pattern, string))


def is_email(string):
    pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return bool(re.match(pattern, string))


def is_url(string):
    pattern = re.compile(
        r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    )
    return bool(re.match(pattern, string))


def is_version(string: str) -> bool:
    pattern = r'^v?\d+(\.\d+)+$|^v\d+$'
    return bool(re.match(pattern, string))


def is_autosave(string: str) -> bool:
    pattern = r'auto[-_\s]?save'
    return bool(re.match(pattern, string, re.IGNORECASE))


def is_entity(path: str) -> bool:
    path: Path = Path(path).resolve()
    if path.is_dir():
        is_subspace = Path(path, 'Subspace.yml').is_file()
        is_void = 'Void' in path.name.split("_")
        return is_subspace or is_void
    elif path.is_file():
        not_marker = 'Subspace.yml' not in path.name
        return not_marker
    else:
        return False

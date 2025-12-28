from pathlib import Path
import re


def is_number(string):
    pattern = r"^-?\d+(?:\.\d+)?$"
    return bool(re.match(pattern, string))


def is_email(string):
    pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
    return bool(re.match(pattern, string))


def is_url(string):
    pattern = re.compile(
        r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
    )
    return bool(re.match(pattern, string))


def is_version(string: str) -> bool:
    pattern = r"^v?\d+(\.\d+)+$|^v\d+$"
    return bool(re.match(pattern, string))


def is_autosave(string: str) -> bool:
    pattern = r"auto[-_\s]?save"
    return bool(re.match(pattern, string, re.IGNORECASE))


def is_buckup(string: str) -> bool:
    pattern = r"^bak\d*$|^backup$"
    return bool(re.match(pattern, string, re.IGNORECASE))


def is_recovered(string: str) -> bool:
    pattern = r"^recovered$"
    return bool(re.match(pattern, string, re.IGNORECASE))


def is_entity(path: str) -> bool:
    path = Path(path).resolve()
    # Check if any parent folder is named "Subspaces"
    if not any(p.name == "Subspaces" for p in path.parents):
        return False
    
    if path.is_dir():
        return True
    elif path.is_file():
        return "Subspace.yml" not in path.name
    else:
        return False

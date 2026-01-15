import fnmatch
from pathlib import Path
import re
from typing import List, Union


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
    # 空字符串直接返回False
    if not string:
        return False

    # 1. 处理纯预发布标签的情况（beta/stable/latest/pre-alpha等）
    pure_tag_pattern = r"^(alpha|beta|rc|stable|latest|pre-alpha)$"
    if re.match(pure_tag_pattern, string, re.IGNORECASE):
        return True

    # 2. 处理版本范围表达式（包含,分隔的多个版本条件）
    if "," in string:
        # 按,拆分成多个版本条件
        version_parts = string.split(",")
        # 每个子段都必须是合法的版本号（带范围符号或普通版本号）
        return all(is_version(part.strip()) for part in version_parts)

    # 3. 处理带版本范围符号的单版本（>=、<=、^、~ 开头）
    range_prefix = None
    range_prefix_match = re.match(r"^(>=|<=|\^|~)", string)
    if range_prefix_match:
        range_prefix = range_prefix_match.group(1)
        core_version = string[len(range_prefix) :]  # 提取范围符号后的核心版本号
    else:
        core_version = string  # 无范围符号，核心版本号就是原字符串

    # 4. 校验核心版本号的格式
    # 合法的核心版本号规则：
    # - 要么是 v+纯数字（如v4、v001）
    # - 要么是 包含至少一个小数点的数字（如4.2、0.1.0）
    # - 支持可选的预发布标签（如0.1.0-alpha）
    core_pattern = r"""
        ^                                           # 字符串开头
        (?:v\d+)                                    # 带v前缀的单数字（v4、v001）
        |                                           # 或
        (?:\d+(?:\.\d+)+)                           # 包含至少一个小数点的数字（4.2、0.1.0）
        (?:-(?:alpha|beta|rc|stable|latest|pre-alpha))?  # 可选的预发布标签
        $                                           # 字符串结尾
    """
    core_regex = re.compile(core_pattern, re.VERBOSE | re.IGNORECASE)

    return bool(core_regex.match(core_version))


def is_autosave(string: str) -> bool:
    pattern = r"auto[-_\s]?save"
    return bool(re.match(pattern, string, re.IGNORECASE))


def is_buckup(string: str) -> bool:
    pattern = r"^bak\d*$|^backup$"
    return bool(re.match(pattern, string, re.IGNORECASE))


def is_recovered(string: str) -> bool:
    pattern = r"^recovered$"
    return bool(re.match(pattern, string, re.IGNORECASE))


def is_ignore(path: str, ignore: Union[str, List[str]]) -> bool:
    """Check if a path should be ignored (gitignore style)

    Args:
        path: Path to check
        ignore: List of ignore patterns or a single pattern string

    Returns:
        bool: True if the path matches any ignore pattern, False otherwise
    """
    # Convert single string to list
    if isinstance(ignore, str):
        ignore = [ignore]

    # Normalize path separators to forward slashes
    path = path.replace("\\", "/")

    # Remove trailing slash unless it's the root directory
    if path != "/" and path.endswith("/"):
        path = path.rstrip("/")

    # Iterate through all ignore patterns
    for pattern in ignore:
        # Skip empty patterns
        if not pattern or pattern.strip() == "":
            continue

        # Normalize pattern separators
        pattern = pattern.replace("\\", "/")

        # Remove trailing slash from pattern unless it's the root directory
        if pattern != "/" and pattern.endswith("/"):
            pattern = pattern.rstrip("/")

        # Case 1: Exact match of the entire path
        if fnmatch.fnmatch(path, pattern):
            return True

        # Case 2: Pattern matches a directory in the path (e.g., "content" matches "content/file.txt")
        path_parts = path.split("/")
        for i in range(len(path_parts)):
            partial_path = "/".join(path_parts[: i + 1])
            if fnmatch.fnmatch(partial_path, pattern):
                return True

        # Case 3: Directory pattern (with /* suffix added)
        if fnmatch.fnmatch(path, f"{pattern}/*"):
            return True

    return False

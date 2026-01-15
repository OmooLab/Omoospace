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
    # 最终版正则：
    # 1. 支持 1.2.3 这类无前缀带小数点的版本号
    # 2. 支持 V001/v123（大小写前缀+纯数字）
    # 3. 纯数字123无效，预发布后缀/版本范围/通配符均有效
    pattern = r"""
        ^                           # 字符串开头
        (?:                         # 非捕获组：版本范围/通配符前缀（可选）
            [<>]=?|~|\^|,           # 匹配 >=/<=/>/</~/^/,
        )?                         
        (?:                         # 核心版本主体（核心分支，确保1.2.3能匹配）
            [vV]?\d+(?:\.\d+)+      # 情况1：无/有前缀+带小数点（如 1.2.3、V1.2.3、v0.2）
            |                       # 或
            [vV]\d+                 # 情况2：V/v前缀+纯数字（如 V001、v123）
            |                       # 或
            [<>]=?|~|\^[vV]?\d+     # 情况3：范围/通配符+纯数字（如 >7、~v4、^V8）
        )
        (?:                         # 可选后缀：预发布版本/通配符
            -                       # 分隔符-
            (?:\*|[a-zA-Z0-9-]+)    # 支持*通配符或字母数字-组合（如 alpha、rc1、123-beta）
        )?
        (?:                         # 可选：多版本范围（如 ,<7）
            ,
            (?:[<>]=?|~|\^|[vV]?)?  # 第二个版本的前缀（支持V/v）
            \d+(?:\.\d+)*           # 第二个版本号
            (?:-\*|[a-zA-Z0-9-]+)?  # 第二个版本的可选后缀
        )*                          # 允许多个逗号分隔
        $                           # 字符串结尾
    """
    return bool(re.match(pattern, string, re.VERBOSE))


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

import re
import os
import shutil
from pathlib import Path
from typing import Any, Generic, Iterable, Optional, TypeVar, Union


from pypinyin import lazy_pinyin
from ruamel.yaml import YAML
from omoospace.validators import (
    is_autosave,
    is_number,
    is_version,
    is_recovered,
    is_buckup,
)
from omoospace import pyperclip

yaml = YAML()
yaml.indent(sequence=4, offset=2)


NativePath = Path().__class__


class Opath(NativePath):
    """
    Custom Path class, inherit from system native Path class,
    keep all original features and add custom methods.
    """

    def reveal_in_explorer(self):
        """Open the directory in file exploarer"""
        try:
            os.startfile(self)
        except Exception as err:
            print("Fail to reveal", err)

    def is_under(self, b: Union[str, Path, "Opath"], or_equal=False) -> bool:
        """Return True if a is a subpath of b .

        Args:
            b (Union[str, Path]): Parent path
            or_equal (bool, optional): [description]. Defaults to False.

        Returns:
            bool: Result.
        """
        b = Path(b).resolve()
        a = self.resolve()
        is_under = b in a.parents
        is_equal = b == a

        return is_under or is_equal if or_equal else is_under

    def get_children(self, recursive: bool = True) -> list["Opath"]:
        """Get all paths in giving directory.

        Args:
            recursive (bool, optional): Whether recursive or not. Defaults to True.
        """
        search_path: Path = self.resolve()
        paths: list[Opath] = []
        if recursive:
            # FIXME: replace this with Path.walk (python 3.12)
            # https://docs.python.org/3/library/pathlib.html
            for root, dirs, files in os.walk(search_path):
                for path in [*dirs, *files]:
                    child = Opath(root, path).resolve()
                    paths.append(child)
        else:
            for child in search_path.iterdir():
                paths.append(child)
        return paths

    def copy_to(
        self, dir: Union[str, Path, "Opath"], overwrite: bool = False
    ) -> "Opath":
        """Copy file or directory to the given directory.

        Args:
            dir (Union[str, Path, Opath]): Destination directory.
        """

        if not self.exists():
            raise FileNotFoundError(f"{self} does not exist.")

        dir = Opath(dir).resolve()
        dst = dir / self.name

        if dst.exists():
            if not overwrite:
                raise FileExistsError(f"{dst} already exists.")

            if self.resolve() == dst.resolve():
                return self

        else:
            dir.mkdir(parents=True, exist_ok=True)

        if self.is_dir():
            return Opath(shutil.copytree(self.resolve(), dst, dirs_exist_ok=True))
        else:
            return Opath(shutil.copy(self.resolve(), dir))

    def move_to(
        self, dir: Union[str, Path, "Opath"], overwrite: bool = False
    ) -> "Opath":
        """Move the file or directory to the given directory.

        Args:
            dir (Union[str, Path, Opath]): Destination directory.
        """
        if not self.exists():
            raise FileNotFoundError(f"{self} does not exist.")

        dir = Opath(dir).resolve()
        dst = dir / self.name

        if dst.exists():
            if not overwrite:
                raise FileExistsError(f"{dst} already exists.")

            if self.resolve() == dst.resolve():
                return self

            if dst.is_dir():
                shutil.rmtree(dst, ignore_errors=True)
            else:
                dst.unlink()
        else:
            dir.mkdir(parents=True, exist_ok=True)

        if dst.exists():
            dst.unlink()
        return Opath(shutil.move(self.resolve(), dir))

    def remove_children(self):
        """Remove all children in the directory."""
        dirpath = self.resolve()

        for child in dirpath.iterdir():
            Opath(child).remove()

    def remove(self):
        """Remove all files and directories in the directory."""
        if self.is_file():
            self.unlink()
        elif self.is_dir():
            shutil.rmtree(self, ignore_errors=True)
        else:
            raise ValueError(f"{self} does not exist.")


AnyPath = Union[str, Path, Opath]


def normalize_name(name: str, chinese_to_pinyin: bool = False) -> str:
    def is_semantic(s: str):
        return not (
            is_number(s)
            or is_version(s)
            or is_autosave(s)
            or is_recovered(s)
            or is_buckup(s)
        )

    # Remove everything after the first "."
    name = name.split(".", 1)[0]

    result_parts = []
    for part in name.split("_"):
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

    normalized = "_".join(result_parts)

    if normalized == "":
        raise ValueError(f"{name} is not a valid name.")

    return normalized


def remove_duplicates(list, key):
    seen = set()
    new_list = []
    for d in list:
        if d[key] not in seen:
            seen.add(d[key])
            new_list.append(d)
    return new_list


def copy_to_clipboard(string: str):
    """Copy to clipboard

    Args:
        string (str): The string want to be copyed.
    """

    pyperclip.copy(string)


def make_path(
    *paths: list[Union[str, dict[str, str]]],
    under: AnyPath = ".",
    overwrite: bool = False,
):
    """Create paths.

    Args:
        paths (list[Union[str, dict[str, str]]]): The paths want to be created.
        under (AnyPath, optional): The parent directory. Defaults to ".".
    """
    maked_paths = []
    for p in paths:
        if isinstance(p, str):
            maked_path = Opath(under, p).resolve()
            if p.endswith("/"):
                maked_path.mkdir(parents=True, exist_ok=True)
            else:
                maked_path.parent.mkdir(parents=True, exist_ok=True)
                if maked_path.exists() and overwrite:
                    maked_path.remove()

                if not maked_path.exists():
                    maked_path.touch()

            maked_paths.append(maked_path)
            
        else:
            for path, content in p.items():
                maked_path = Opath(under, path).resolve()
                maked_path.parent.mkdir(parents=True, exist_ok=True)
                if maked_path.exists() and overwrite:
                    maked_path.remove()

                if not maked_path.exists():
                    maked_path.touch()
                    if content is None:
                        continue
                    with maked_path.open("w", encoding="utf-8") as f:
                        f.write(content)

                maked_paths.append(maked_path)

    return tuple(maked_paths) if len(maked_paths) > 1 else maked_paths[0]


# Generic type variable supporting primitive types and custom objects
T = TypeVar("T", str, int, float, bool, object)


class Oset(Generic[T], set):
    """
    Universal set implementation compatible with both primitive types (str/int/float/bool)
    and custom objects (enforcing uniqueness via a specified attribute).

    Key Features:
        - Primitive types: Behaves exactly like native Python set
        - Custom objects: Enforces uniqueness using specified attribute (default: "name")
        - Supports membership checks with both attribute values (str/int) and object instances
        - Supports equality comparison with native sets (e.g., Oset[Maker] == {"Alice", "Bob"})

    Attributes:
        key: Name of attribute used for uniqueness checks on custom objects (default: "name")
             Ignored for primitive type elements
    """

    def __init__(self, iterable: Iterable[T] = (), key: str = "name"):
        """
        Initialize Oset with automatic deduplication based on element type.

        Args:
            iterable: Iterable containing primitive values (str/int) or custom objects (default: empty)
            key: Attribute name for uniqueness validation on custom objects (default: "name")

        Raises:
            ValueError: If custom objects lack the specified key attribute
        """
        self.key = key
        unique_items = []
        seen_keys = set()

        for item in iterable:
            item_key = self._get_item_key(item)
            if item_key not in seen_keys:
                seen_keys.add(item_key)
                unique_items.append(item)

        super().__init__(unique_items)

    def _get_item_key(self, item: T) -> Union[str, int, float, bool]:
        """
        Get unique identity key for an element.

        For primitive types (str/int/float/bool): Returns the element itself
        For custom objects: Returns the value of the specified key attribute

        Args:
            item: Primitive value or custom object to get key for

        Returns:
            Union[str, int, float, bool]: Unique identity key

        Raises:
            ValueError: If custom object lacks the specified key attribute
        """
        if isinstance(item, (str, int, float, bool)):
            return item
        try:
            return getattr(item, self.key)
        except AttributeError:
            raise ValueError(f"Object {item} missing required attribute '{self.key}'")

    def __contains__(self, item: Any) -> bool:
        """
        Override membership operator ('in') with type-aware logic.

        Logic:
            1. Custom object collection: Check by attribute value (str/int) or object instance
            2. Primitive type collection: Maintain native set membership behavior

        Args:
            item: Attribute value (str/int) or object to check membership for

        Returns:
            bool: True if item exists in set, False otherwise
        """
        # Check if collection contains custom objects (not primitives)
        if self and not isinstance(next(iter(self)), (str, int, float, bool)):
            # Case 1: Check by attribute value (e.g., "Alice" for Maker object)
            if isinstance(item, (str, int, float, bool)):
                return any(self._get_item_key(obj) == item for obj in self)

            # Case 2: Check by object instance (compare key attributes)
            else:
                try:
                    item_key = self._get_item_key(item)
                    print(item_key)
                except ValueError:
                    return False
                return any(self._get_item_key(obj) == item_key for obj in self)
        # Primitive type collection - use native set behavior
        else:
            return super().__contains__(item)

    def __eq__(self, other: Any) -> bool:
        """
        Universal equality operator (==) for all Oset types (NO primitive exceptions).

        Compares key-based native sets for equality, enabling cross-type comparisons:
        - Oset[Maker] == {"Alice", "Bob"}
        - Oset[str] == {"Alice", "Bob"}
        - Oset[int] == {1, 2}

        Args:
            other: Object to compare with (native set, list, tuple, Oset, etc.)

        Returns:
            bool: True if key-based sets are equal, False otherwise
        """
        # Convert self to key-based native set (works for ALL Oset types)
        self_key_set = self.to_set()

        # Convert "other" to a native set (handle iterables/lists/tuples)
        if isinstance(other, (set, list, tuple, Oset)):
            # For Oset instances: use their to_set() method
            if isinstance(other, Oset):
                other_key_set = other.to_set()
            # For native iterables: convert directly to set
            else:
                other_key_set = set(other)
        # For non-iterable objects: return False immediately
        else:
            return False

        # Compare key-based sets (universal logic for all types)
        return self_key_set == other_key_set

    def add(self, item: T) -> None:
        """
        Add element to set with automatic deduplication.

        Args:
            item: Primitive value or custom object to add

        Raises:
            ValueError: If custom object lacks the specified key attribute
        """
        item_key = self._get_item_key(item)
        if item_key not in self:
            super().add(item)

    def update(self, *iterables: Iterable[T]) -> None:
        """
        Update set by adding multiple elements from one or more iterables.

        Maintains deduplication based on key attribute for custom objects.

        Args:
            iterables: One or more iterables containing primitives/objects

        Raises:
            ValueError: If custom objects lack the specified key attribute
        """
        for iterable in iterables:
            for item in iterable:
                self.add(item)

    def get(self, item: Any) -> Optional[T]:
        """
        Look up and return an element from the set.

        Supports lookup by:
            - Attribute value (str/int) for custom object collections
            - Exact value for primitive collections
            - Object instance for custom object collections

        Args:
            item: Attribute value (str/int) or object to find

        Returns:
            Optional[T]: Found element (primitive/object) or None if not found
        """
        # Custom object collection lookup
        if self and not isinstance(next(iter(self)), (str, int, float, bool)):
            if isinstance(item, (str, int, float, bool)):
                for obj in self:
                    if self._get_item_key(obj) == item:
                        return obj
            else:
                try:
                    item_key = self._get_item_key(item)
                except ValueError:
                    return None
                for obj in self:
                    if self._get_item_key(obj) == item_key:
                        return obj
        # Primitive collection lookup
        else:
            for obj in self:
                if obj == item:
                    return obj
        return None

    def remove(self, item: Any) -> None:
        """
        Remove element from set (raises KeyError if not found).

        Supports removal by attribute value (str/int) or object instance.

        Args:
            item: Attribute value (str/int) or object to remove

        Raises:
            KeyError: If element is not found in the set
        """
        target_item = self.get(item)
        if target_item is None:
            raise KeyError(item)
        super().remove(target_item)

    def discard(self, item: Any) -> None:
        """
        Remove element from set if present (no error if missing).

        Supports removal by attribute value (str/int) or object instance.

        Args:
            item: Attribute value (str/int) or object to remove
        """
        target_item = self.get(item)
        if target_item is not None:
            super().discard(target_item)

    def pop(self) -> T:
        """
        Remove and return an arbitrary element from the set.

        Returns:
            T: Removed element (primitive/object)

        Raises:
            KeyError: If set is empty
        """
        if not self:
            raise KeyError("pop from empty Oset")
        return super().pop()

    def clear(self) -> None:
        """Remove all elements from the set."""
        super().clear()

    def to_set(self) -> set[Union[str, int, float, bool]]:
        """
        Convert Oset to standard Python set.

        For custom object collections: Returns set of key attribute values
        For primitive collections: Returns identical native set

        Returns:
            set: Standard set containing primitive values or object key attributes
        """
        return {self._get_item_key(item) for item in self}

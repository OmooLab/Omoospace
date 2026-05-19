from typing import Any
import frontmatter
from omoospace.utils import Opath, yaml
from dataclasses import dataclass


class NodeData:
    def __init__(self, name: str, subspaces: list[Opath] = []):
        self.name = name
        self.subspaces = subspaces

    def __repr__(self):
        return self.name


class Profile:
    """Abstract base class for read and write profile"""

    def _read_profile(self):
        """Read profile data from Omoospace.yml or Omoospace.md file."""
        if self.profile_file is None:
            raise ValueError("profile file is None.")

        if not self.profile_file.exists():
            return {}

        if self.profile_file.suffix.lower() == ".md":
            # Handle Markdown file with YAML frontmatter
            try:
                post = frontmatter.load(self.profile_file)
                return dict(post) or {}
            except Exception:
                return {}
        else:
            # Handle YAML file
            with self.profile_file.open("r", encoding="utf-8") as file:
                return yaml.load(file) or {}

    def _write_profile(self, data):
        """Write profile data to Omoospace.yml or OMOOSPACE.md file."""
        if self.profile_file is None:
            raise ValueError("profile file is None.")

        self.profile_file.parent.mkdir(parents=True, exist_ok=True)

        if self.profile_file.suffix.lower() == ".md":
            # Write to Markdown file with YAML frontmatter
            post = frontmatter.Post("")
            post.metadata = data
            with self.profile_file.open("w", encoding="utf-8") as file:
                file.write(frontmatter.dumps(post))
        else:
            # Write to YAML file
            with self.profile_file.open("w", encoding="utf-8") as file:
                yaml.dump(data, file)

    @property
    def language(self) -> str:
        """str: Omoospace language."""
        parts = self.profile_file.stem.split(".")
        return parts[-1] if len(parts) > 1 else "en"

    def _key(self, key) -> str:
        return key

    def get(self, key: str) -> Any:
        """Get the latest data for this item from the profile file."""
        profile = self._read_profile()
        return profile.get(key)

    def set(self, key: str, value: Any):
        """Set the value for the given key in the profile file."""
        profile = self._read_profile()
        profile[key] = value
        self._write_profile(profile)


class ProfileItem:
    """Abstract class for profile items like Maker, Tool, and Work.

    This base class provides a unified way to access and update profile data, ensuring
    that attribute access always returns the latest data from the configuration file.
    """

    """The name used in the profile dictionary (e.g., "makers", "tools", "works")."""
    _dict_name: str
    _item_name: str

    def __init__(self, omoospace: "Omoospace", name: str) -> None:
        self._item_name = name
        self._omoospace = omoospace

        # init item with name if not find in profile
        item_dict = self._omoospace.get(self._dict_name) or {}
        if self._item_name not in item_dict:
            item_dict[self._item_name] = {}

        self._omoospace.set(self._dict_name, item_dict)

    def __repr__(self):
        return self.name

    def _key(self, key) -> str:
        return key

    @property
    def data(self):
        # e.g. makers
        item_dict = self._omoospace.get(self._dict_name)
        if item_dict is None:
            raise AttributeError(f"{self._dict_name} not found in profile.")

        # e.g. maker
        data = item_dict.get(self._item_name)
        if data is None:
            raise AttributeError(f"{self._item_name} not found in {self._dict_name}.")
        return data

    @data.setter
    def data(self, value: Any):
        """Update the profile with current data."""
        items = self._omoospace.get(self._dict_name) or {}

        items[self._item_name] = value

        self._omoospace.set(self._dict_name, items)

    def get(self, key: str) -> Any:
        """Get the latest data for this item from the profile file."""
        return self.data.get(key) if isinstance(self.data, dict) else None

    def set(self, key: str, value: Any):
        """Update the profile with current data."""
        data = self.data if isinstance(self.data, dict) else {}

        data[key] = value

        self.data = data

    def remove(self):
        """Remove this item from the profile."""
        item_dict = self._omoospace.get(self._dict_name)
        if item_dict is None:
            raise AttributeError(f"{self._dict_name} not found in profile.")

        if self._item_name in item_dict:
            del item_dict[self._item_name]
            self._omoospace.set(self._dict_name, item_dict)
        else:
            raise AttributeError(f"{self._item_name} not found in {self._dict_name}.")

    @property
    def name(self) -> str:
        """Get the name from the latest profile data."""
        return self._item_name

    @name.setter
    def name(self, value: str):
        item_dict = self._omoospace.get(self._dict_name)

        if self.name in item_dict:
            del item_dict[self.name]

        item_dict[value] = self.data
        self._omoospace.set(self._dict_name, item_dict)

        self._item_name = value

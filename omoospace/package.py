import os
from pathlib import Path
from zipfile import ZipFile


from omoospace.exceptions import NotFoundError
from omoospace.types import Item, PathLike
from omoospace.common import ProfileContainer, yaml
from omoospace.utils import is_subpath


class Package(ProfileContainer):
    """The class of omoospace package.

    A package class instance is always refer to a existed package directory, not dummy. 

    Usage:
    ```python
    pkg = Package('path/to/package')
    print(pkg.root_path)
    # >>> path/to/package
    ```
    
    Attributes:
        name (str): Package's name.
        description (str): Package's description.
        version (str): Package's version.
    """
    name: str
    description: str
    version: str

    def __init__(self, package_path: PathLike):
        """Initialize package .

        Args:
            package_path (PathLike): The package path.

        Raises:
            NotFoundError: No package detected.
        """
        package_path = Path(package_path).resolve()
        if (package_path.suffix == ".zip"):
            with ZipFile(package_path, 'r') as zip:
                try:
                    with zip.open('Package.yml') as file:
                        pass
                except:
                    raise NotFoundError("package", package_path)
        else:
            package_info_path = Path(package_path, 'Package.yml')
            if not package_info_path.exists():
                raise NotFoundError("package", package_path)

        self._root_path = package_path
        self._profile_path = Path(self.root_path, "Package.yml").resolve()

    @property
    def root_path(self) -> Path:
        """Path: Root path."""
        return self._root_path

    @property
    def profile_path(self) -> Path:
        """Path: Package.yml file path."""
        return self._profile_path

    def is_package_item(self, path: Path) -> bool:
        """Check if path is package item

        Args:
            path (Path): Input

        Returns:
            bool: result
        """
        exists = path.exists()
        in_package = is_subpath(path, self.root_path)
        not_profile_file = \
            'Omoospace.yml' != path.name \
            and 'Package.yml' != path.name \
            and 'Subspace.yml' not in path.name

        return exists and in_package and not_profile_file

    @property
    def items(self) -> list[Item]:
        """list[Item]: Package item list."""
        items: list[Item] = []
        for root, dirs, files in os.walk(self.root_path):
            for path in files:
                child = Path(root, path).resolve()
                if self.is_package_item(child):
                    items.append(child)
        return items

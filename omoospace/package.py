import os
from pathlib import Path
from zipfile import ZipFile


from omoospace.exceptions import NotFoundError
from omoospace.types import Item, PathLike
from omoospace.common import ProfileContainer, yaml
from omoospace.utils import is_subpath


class Package(ProfileContainer):
    """The class of omoospace package.

    A package class instance is always refer to a existed package directory, not in ideal. 

    Attributes:
        name (str): Package's name.
        description (str): Package's description.
        version (str): Package's version.
        creators (list[Creator]): Creator list.
        root_path (Path): Root path.
    """
    name: str
    description: str
    version: str

    def __init__(self, package_dir: PathLike):
        """Initialize package .

        Args:
            detect_dir (PathLike): [description]

        Raises:
            NotFoundError: [description]
            NotFoundError: [description]
        """
        package_path = Path(package_dir).resolve()
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

        self.root_path = package_path
        self.profile_path = Path(self.root_path, "Package.yml").resolve()

    def is_package_item(self, item: Item) -> bool:
        exists = item.exists()
        in_package = is_subpath(item, self.root_path)
        not_profile_file = \
            'Omoospace.yml' != item.name \
            and 'Package.yml' != item.name \
            and 'Subspace.yml' not in item.name

        return exists and in_package and not_profile_file

    @property
    def items(self) -> list[Item]:
        """list[Item]: The list of Item objects."""
        items: list[Item] = []
        for root, dirs, files in os.walk(self.root_path):
            for path in files:
                child = Path(root, path).resolve()
                if self.is_package_item(child):
                    items.append(child)
        return items

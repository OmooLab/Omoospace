import os
from pathlib import Path
from zipfile import ZipFile


from omoospace.exceptions import NotFoundError
from omoospace.types import Item, PathLike
from omoospace.common import console, yaml


class Package:
    """The class of omoospace package.

    A package class instance is always refer to a existed package directory, not in ideal. 

    Attributes:
        name (str): Package's name.
        description (str): Package's description.
        version (str): Package's version.
        creators (list[Creator]): Creator list.
        root_path (Path): Root path.
    """

    def __init__(self, detect_dir: PathLike):
        """Initialize package .

        Args:
            detect_dir (PathLike): [description]

        Raises:
            NotFoundError: [description]
            NotFoundError: [description]
        """
        package_path = Path(detect_dir).resolve()
        if (package_path.suffix == ".zip"):
            with ZipFile(package_path, 'r') as zip:
                try:
                    with zip.open('Package.yml') as file:
                        package_info = yaml.load(file)
                except:
                    raise NotFoundError("package", detect_dir)
        else:
            package_info_path = Path(package_path, 'Package.yml')
            if package_info_path.exists():
                with package_info_path.open('r', encoding='utf-8') as file:
                    package_info = yaml.load(file)
            else:
                raise NotFoundError("package", detect_dir)

        self.root_path = package_path
        self.name = package_info.get('name')
        self.description = package_info.get('description')
        self.version = package_info.get('version')
        self.creators = package_info.get('creators')

    # TODO: omoospace also has is_package_item. Keep one only.
    @staticmethod
    def is_package_item(path: Path) -> bool:
        not_marker = path.name != '.subspace'
        not_package_info = path.name != 'Package.yml'
        return not_marker and not_package_info

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

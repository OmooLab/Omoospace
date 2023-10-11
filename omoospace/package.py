import os
from pathlib import Path
import yaml
from zipfile import ZipFile


from omoospace.exceptions import NotFoundError
from omoospace.types import Item, PathLike


class Package:
    def __init__(self, dir: PathLike):
        package_path = Path(dir).resolve()
        if (package_path.suffix == ".zip"):
            with ZipFile(package_path, 'r') as zip:
                try:
                    with zip.open('Package.yml') as file:
                        package_info = yaml.safe_load(file)
                except:
                    raise NotFoundError("package", dir)
        else:
            package_info_path = Path(package_path, 'Package.yml')
            if package_info_path.exists():
                with package_info_path.open('r', encoding='utf-8') as file:
                    package_info = yaml.safe_load(file)
            else:
                raise NotFoundError("package", dir)

        self.root_path = package_path
        self.name = package_info.get('name')
        self.description = package_info.get('description')
        self.version = package_info.get('version')
        self.creators = package_info.get('creators')

    @staticmethod
    def is_item(path: Path) -> bool:
        not_marker = path.name != '.subspace'
        not_package_info = path.name != 'Package.yml'
        return not_marker and not_package_info

    @property
    def items(self):
        items: list[Item] = []
        for root, dirs, files in os.walk(self.root_path):
            for path in files:
                child = Path(root, path).resolve()
                if self.is_item(child):
                    items.append(child)

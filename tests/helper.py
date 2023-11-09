import pytest
from pathlib import Path
from omoospace.types import PathLike
from ruamel.yaml import YAML
yaml = YAML()


def factory_omoospace_file_paths(main_dir: str = "."):
    @pytest.fixture()
    def omoospace_file_paths(mini_omoos_path: Path, request):
        if not isinstance(request.param, list):
            raise TypeError
        files = request.param
        # create files

        file_paths = write_file(
            *[Path(file) for file in files],
            root_dir=Path(mini_omoos_path, main_dir)
        )

        file_paths = file_paths if isinstance(file_paths, tuple) else [file_paths]

        yield file_paths

        # delete all files
        # for file_path in file_paths:
        #     file_path.unlink(missing_ok=True)

    return omoospace_file_paths


def write_file_content(*files: list[(PathLike, str)], root_dir: PathLike = '.'):
    file_paths = []
    for file, content in files:
        file_path = Path(root_dir, file).resolve()
        file_paths.append(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with file_path.open('w') as file:
            profile = yaml.load(content)
            yaml.dump(profile, file)
    return tuple(file_paths) if len(file_paths) > 1 else file_paths[0]


def write_file(*files: list[PathLike], root_dir: PathLike = '.'):
    file_paths = []
    for file in files:
        file_path = Path(root_dir, file).resolve()
        file_paths.append(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with file_path.open('w') as file:
            pass
    return tuple(file_paths) if len(file_paths) > 1 else file_paths[0]

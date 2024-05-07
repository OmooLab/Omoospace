import shutil
from pathlib import Path


def copy_to_dir(source_path, dir_path, exist_ok=True):
    source = Path(source_path)
    target = Path(dir_path)

    # Check if the source exists
    if not source.exists():
        raise FileNotFoundError

    # Check if the target exists
    if not target.exists():
        target.mkdir(parents=True, exist_ok=True)

    target_path = target / source.name
    # If source is a file, copy it to the target directory
    if source.is_file():
        try:
            shutil.copy(source, target_path)
        except shutil.SameFileError:
            if exist_ok:
                pass
            else:
                raise shutil.SameFileError
    # If source is a directory, copy its contents to the target directory
    elif source.is_dir():
        shutil.copytree(source, target_path, dirs_exist_ok=exist_ok)

    if not target_path.exists():
        raise Exception

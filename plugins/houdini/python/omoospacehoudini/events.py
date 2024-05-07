import hou
import os
from pathlib import Path

from omoospace import (
    Omoospace,
    get_route_str,
    create_omoospace
)

BACKUP_NAMES = ["old", "Bak", "bak", ".bak", "Backup", "backup"]
HDA_PATHS = ["Contents/HDAs"]
HDA_EXTS = [".hda", ".otl"]


def resolve_mapped(path):
    """on windows path resolve will return UNC path."""

    path = Path(path).resolve()
    mapped_paths = []
    for drive in 'ZYXWVUTSRQPONMLKJIHGFEDCBA':
        root = Path('{}:/'.format(drive))
        try:
            mapped_paths.append(root / path.relative_to(root.resolve()))
        except (ValueError, OSError):
            pass

    return min(mapped_paths, key=lambda x: len(str(x)), default=path)


def read_env(path_format: str):
    try:
        file_path = Path(hou.hipFile.path()).resolve()
        omoos_path = Omoospace(file_path).root_path

        if path_format == "MNT":
            omoos_path = resolve_mapped(omoos_path)

        omoos_path_str = omoos_path.as_posix()
        route_str = get_route_str(file_path)
    except:
        omoos_path_str = get_voidspace().root_path.as_posix()
        route_str = "Void_Untitled"

    backup_dir_str = Path(omoos_path_str, "StagedData/Backup").as_posix()

    return omoos_path_str, route_str, backup_dir_str


def get_voidspace():
    try:
        voidspace = Omoospace(Path(Path.home(), "Void"))
    except:
        voidspace = create_omoospace(
            name="Void",
            root_dir=Path.home(),
            description="Default omoospace inited by houdini as default project.",
            reveal_in_explorer=False
        )
    return voidspace


def set_env(path_format: str = None):
    path_format = path_format or hou.getenv('PATH_FORMAT') or "UNC"
    omoos_path_str, route_str, backup_dir_str = read_env(path_format)

    if hou.getenv('JOB') != omoos_path_str:
        hou.hscript(f"setenv JOB = {omoos_path_str}")
        print(f"$JOB was changed to: {omoos_path_str}")

    if hou.getenv('ROUTE') != route_str:
        # hou.putenv not save to file. so use hscript "setenv"
        hou.hscript(f"setenv ROUTE = {route_str}")
        print(f"$ROUTE was changed to: {route_str}")

    hou.hscript(f"setenv HOUDINI_BACKUP_DIR = {backup_dir_str}")
    hou.hscript(f"setenv PATH_FORMAT = {path_format}")
    return omoos_path_str, route_str, backup_dir_str


def import_hda(project_path):
    if project_path:
        for hda_path in HDA_PATHS:
            for root, dirs, files in os.walk(Path(project_path, hda_path)):
                dirs[:] = [d for d in dirs if d not in BACKUP_NAMES]
                for file in files:
                    hda = Path(root, file)
                    if hda.suffix in HDA_EXTS:
                        hou.hda.installFile(hda.as_posix())


def on_hip_open():
    # when open a empty start project (untitled.hip) or no plugin configured .hip file.
    if hou.getenv('ROUTE') is None:
        omoos_path_str, route_str, backup_dir_str = read_env("UNC")

        # not use set_env() is because if we do so, in TOP open empty project, then open target .hip,
        # the target env cannot override untitle.hip env, Don't know why. so we have to set it softer,
        # using `hou.putenv("ROUTE", route_str)` not `hou.hscript(f"setenv ROUTE = {route_str}")`
        hou.putenv("JOB", omoos_path_str)
        hou.putenv("ROUTE", route_str)
        hou.putenv("HOUDINI_BACKUP_DIR", backup_dir_str)
    else:
        omoos_path_str = hou.getenv('JOB')
        route_str = hou.getenv('ROUTE')

    print(f"Current omoospace path $JOB: {omoos_path_str}")
    print(f"Current subspace route $ROUTE: {route_str}")

    # set lop render gallery source
    hou.parm("/stage/rendergallerysource").set(
        "$JOB/StagedData/Galleries/`$ROUTE`/Rendergallery.db")

    # import HDA from omoospace
    import_hda(omoos_path_str)


def on_hip_save(path_format: str = None):
    omoos_path_str, route_str, backup_dir_str = set_env(path_format)
    import_hda(omoos_path_str)

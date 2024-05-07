import shutil
from pathlib import Path
import bpy

try:
    from omoospace import Omoospace, create_omoospace, get_route_str
except:
    pass


def get_type(cls):
    return type(cls).__name__


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


def detect_omoospace_root():
    try:
        blend_path = Path(bpy.data.filepath).resolve()
        root_path = Omoospace(blend_path).root_path
        omoospace_root = str(root_path)
    except:
        try:
            voidspace = Omoospace(Path.home() / "Void")
        except:
            voidspace = create_omoospace(
                name="Void",
                root_dir=Path.home(),
                description="Default omoospace as default project.",
                reveal_in_explorer=False
            )
        omoospace_root = str(voidspace.root_path)

    return omoospace_root


def detect_subspace_route():
    try:
        blend_path = Path(bpy.data.filepath).resolve()
        root_path = Omoospace(blend_path).root_path
        subspace_route = get_route_str(blend_path)
    except:
        subspace_route = "Void_Untitled"

    return subspace_route


def set_omoospace_root(omoospace_root: str):
    if bpy.data.texts.get("omoospace") is None:
        bpy.data.texts.new("omoospace")
    env = bpy.data.texts["omoospace"]
    env["omoospace_root"] = omoospace_root


def get_omoospace_root():
    if bpy.data.texts.get("omoospace") is None:
        bpy.data.texts.new("omoospace")
    env = bpy.data.texts["omoospace"]
    return env.get("omoospace_root")


def set_subspace_route(subspace_route: str):
    if bpy.data.texts.get("omoospace") is None:
        bpy.data.texts.new("omoospace")
    env = bpy.data.texts["omoospace"]
    env["subspace_route"] = subspace_route


def get_subspace_route():
    if bpy.data.texts.get("omoospace") is None:
        bpy.data.texts.new("omoospace")
    env = bpy.data.texts["omoospace"]
    return env.get("subspace_route")


def get_parm_raw_path(parm: str):
    parm_paths = get_parm_paths()
    for parm_path in parm_paths:
        if parm_path["parm"] == parm:
            return parm_path["raw_path"]

    return None


def set_parm_raw_path(parm: str, raw_path: str, is_input=False):
    parm_paths = get_parm_paths()
    for parm_path in parm_paths:
        if parm_path["parm"] == parm:
            parm_path["raw_path"] = raw_path
            parm_path["is_input"] = is_input
            return

    parm_paths.append({
        "parm": parm,
        "raw_path": raw_path,
        "is_input": is_input
    })
    bpy.data.texts["omoospace"]['parm_paths'] = parm_paths


def get_parm_paths():
    if bpy.data.texts.get("omoospace") is None:
        bpy.data.texts.new("omoospace")
    env = bpy.data.texts["omoospace"]
    return env.get("parm_paths") or []


def eval_raw_path(raw_path: str) -> str:
    omoospace_root = get_omoospace_root()
    subspace_route = get_subspace_route()
    path_str = raw_path.replace("$OMOOSPACE", omoospace_root)
    path_str = path_str.replace("$SUBSPACE", subspace_route)
    return str(Path(path_str).resolve())

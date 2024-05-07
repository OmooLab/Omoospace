import bpy
from bpy.app.handlers import persistent
from pathlib import Path

from .utils import (eval_raw_path, detect_omoospace_root, detect_subspace_route, get_parm_paths,
                    get_subspace_route, get_omoospace_root, set_omoospace_root, set_parm_raw_path, set_subspace_route)
try:
    from omoospace import Omoospace
except:
    pass


def update_all_paths():
    omoospace_root = get_omoospace_root()
    subspace_route = get_subspace_route()
    for parm_path in get_parm_paths():
        is_input = parm_path.get("is_input")
        if is_input:
            continue

        parm = parm_path['parm']
        raw_path = parm_path['raw_path']

        path_str = raw_path.replace("$OMOOSPACE", omoospace_root)
        path_str = path_str.replace("$SUBSPACE", subspace_route)
        try:
            exec(f"{parm}=r'{str(Path(path_str).resolve())}'")
        except:
            print(f"Something went wrong, skip {parm}")


def update_env(omoospace_root: str, subspace_route: str):
    set_omoospace_root(omoospace_root)
    set_subspace_route(subspace_route)

    omoospace = Omoospace(omoospace_root)
    quick_dirs = bpy.context.window_manager.quick_dir_list.quick_dirs
    quick_dirs.clear()

    quick_dir = quick_dirs.add()
    quick_dir.label = "Contents"
    quick_dir.path = str(omoospace.contents_path)

    quick_dir = quick_dirs.add()
    quick_dir.label = "ExternalData"
    quick_dir.path = str(omoospace.externaldata_path)

    quick_dir = quick_dirs.add()
    quick_dir.label = "References"
    quick_dir.path = str(omoospace.references_path)

    quick_dir = quick_dirs.add()
    quick_dir.label = "SourceFiles"
    quick_dir.path = str(omoospace.sourcefiles_path)

    quick_dir = quick_dirs.add()
    quick_dir.label = "StagedData"
    quick_dir.path = str(omoospace.stageddata_path)


@persistent
def on_blend_open(dummy):
    omoospace_root = detect_omoospace_root()
    subspace_route = detect_subspace_route()
    old_omoospace_root = get_omoospace_root()
    old_subspace_route = get_subspace_route()

    update_env(omoospace_root, subspace_route)

    print(f"Current omoospace root: {omoospace_root}")
    print(f"Current subspace route: {subspace_route}")

    if old_subspace_route is None and subspace_route == "Void_Untitled":
        raw_path = str(Path("$OMOOSPACE") / "Contents" /
                       "Renders" / "$SUBSPACE" / "$SUBSPACE.####")
        parm = "bpy.data.scenes['Scene'].render.filepath"
        exec(f"{parm}=r'{eval_raw_path(raw_path)}'")
        set_parm_raw_path(parm, raw_path)

    if (old_omoospace_root != omoospace_root and old_omoospace_root)\
            or (old_subspace_route != subspace_route and old_subspace_route):
        update_all_paths()


@persistent
def on_blend_save(dummy):
    omoospace_root = detect_omoospace_root()
    subspace_route = detect_subspace_route()
    old_omoospace_root = get_omoospace_root()
    old_subspace_route = get_subspace_route()

    update_env(omoospace_root, subspace_route)

    if old_omoospace_root != omoospace_root and old_omoospace_root:
        print(f"Omoospace root was changed to: {omoospace_root}")

    if old_subspace_route != subspace_route and old_subspace_route:
        print(f"Subspace route was changed to: {subspace_route}")

    if (old_omoospace_root != omoospace_root and old_omoospace_root)\
            or (old_subspace_route != subspace_route and old_subspace_route):
        update_all_paths()


def register():
    bpy.app.handlers.load_post.append(on_blend_open)
    bpy.app.handlers.save_post.append(on_blend_save)


def unregister():
    bpy.app.handlers.load_post.remove(on_blend_open)
    bpy.app.handlers.save_post.remove(on_blend_save)

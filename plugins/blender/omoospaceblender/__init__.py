from .props import QuickDirList
from . import auto_load

import bpy


bl_info = {
    "name": "Omoospace",
    "author": "Ma Nan",
    "description": "",
    "blender": (4, 1, 0),
    "version": (0, 1, 0),
    "location": "Omoospace",
    "warning": "",
    "category": "System"
}

auto_load.init()


def register():
    auto_load.register()
    bpy.types.WindowManager.quick_dir_list = bpy.props.PointerProperty(
        type=QuickDirList)


def unregister():
    try:
        auto_load.unregister()
    except RuntimeError:
        pass

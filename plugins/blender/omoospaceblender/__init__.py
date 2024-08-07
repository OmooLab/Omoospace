from .props import OMOOSPACE_QuickDirList
from . import auto_load
from . import menus

import bpy


bl_info = {
    "name": "Omoospace",
    "author": "Ma Nan",
    "description": "",
    "blender": (4, 0, 0),
    "version": (0, 1, 1),
    "location": "Omoospace",
    "warning": "",
    "category": "System"
}

auto_load.init()


def register():
    auto_load.register()
    bpy.types.WindowManager.quick_dir_list = bpy.props.PointerProperty(
        type=OMOOSPACE_QuickDirList)
    menus.add()


def unregister():
    menus.remove()
    auto_load.unregister()

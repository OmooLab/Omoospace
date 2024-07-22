from .props import OMOOSPACE_QuickDirList
from . import auto_load
from . import menus

import bpy


auto_load.init()


def register():
    auto_load.register()
    bpy.types.WindowManager.quick_dir_list = bpy.props.PointerProperty(
        type=OMOOSPACE_QuickDirList)
    menus.add()


def unregister():
    menus.remove()
    auto_load.unregister()

import bpy


class OMOOSPACE_InputPath(bpy.types.PropertyGroup):
    do_manage: bpy.props.BoolProperty(default=True)   # type: ignore
    icon: bpy.props.StringProperty(default="None")   # type: ignore
    label: bpy.props.StringProperty()   # type: ignore
    parm: bpy.props.StringProperty()   # type: ignore
    orig_path: bpy.props.StringProperty(subtype="FILE_PATH")   # type: ignore
    raw_path: bpy.props.StringProperty(subtype="FILE_PATH")   # type: ignore
    
    category: bpy.props.StringProperty(default="Misc")  # type: ignore
    include_dir: bpy.props.BoolProperty(default=False)   # type: ignore


class OMOOSPACE_OutputPath(bpy.types.PropertyGroup):
    do_manage: bpy.props.BoolProperty(default=True)   # type: ignore
    icon: bpy.props.StringProperty(default="None")   # type: ignore
    label: bpy.props.StringProperty()   # type: ignore
    parm: bpy.props.StringProperty()   # type: ignore
    orig_path: bpy.props.StringProperty(subtype="FILE_PATH")   # type: ignore
    raw_path: bpy.props.StringProperty(subtype="FILE_PATH")   # type: ignore
    
    category: bpy.props.StringProperty(default="Misc")  # type: ignore
    name: bpy.props.StringProperty()   # type: ignore
    suffix: bpy.props.StringProperty()   # type: ignore
    is_dir: bpy.props.BoolProperty(default=False)   # type: ignore
    is_staged: bpy.props.BoolProperty(default=False)   # type: ignore


class OMOOSPACE_QuickDir(bpy.types.PropertyGroup):
    label: bpy.props.StringProperty()   # type: ignore
    path: bpy.props.StringProperty(subtype="DIR_PATH")   # type: ignore


def update_quick_dirs(self, context):
    quick_dir_list = bpy.context.window_manager.quick_dir_list
    quick_dirs = quick_dir_list.quick_dirs
    quick_dirs_active = quick_dir_list.quick_dirs_active
    
    if quick_dirs_active != -1:
        bpy.context.space_data.params.directory = \
            str(quick_dirs[quick_dirs_active].path).encode()

        quick_dir_list.quick_dirs_active = -1

class OMOOSPACE_QuickDirList(bpy.types.PropertyGroup):
    quick_dirs: bpy.props.CollectionProperty(type=OMOOSPACE_QuickDir)  # type: ignore
    quick_dirs_active: bpy.props.IntProperty(
        default=-1,
        name="Quick Directories",
        update=update_quick_dirs,
        options=set()
    )  # type: ignore

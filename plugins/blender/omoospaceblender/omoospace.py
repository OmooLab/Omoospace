import os
import bpy
from pathlib import Path

from .utils import get_omoospace_root, get_subspace_route
try:
    from omoospace import create_omoospace, format_name, exceptions, copy_to_clipboard
except:
    pass


class CreateOmoospace(bpy.types.Operator):
    bl_idname = "omoospace.create_omoospace"
    bl_label = "Create an Omoospace"
    bl_description = "Create an omoospace from current blender file"
    bl_options = {'UNDO'}

    omoospace_home: bpy.props.StringProperty(
        name="Home Directory",
        subtype="DIR_PATH",
        default=str(Path.home())
    )  # type: ignore

    omoospace_name: bpy.props.StringProperty(
        name="Omoospace Name"
    )  # type: ignore

    subspace_name: bpy.props.StringProperty(
        name="Subspace Name"
    )  # type: ignore

    def invoke(self, context, event):
        preferences = context.preferences.addons[__package__].preferences
        self.omoospace_home = preferences.omoospace_home
        context.window_manager.invoke_props_dialog(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):

        if not self.omoospace_name:
            self.report({"ERROR"}, "Invaild omoospace name.")
            return {'CANCELLED'}
        try:
            omoospace = create_omoospace(
                name=self.omoospace_name,
                root_dir=self.omoospace_home,
                reveal_in_explorer=False
            )
        except exceptions.ExistsError:
            self.report({"ERROR"}, "Omoospace already exists.")
            return {'CANCELLED'}

        subspace_name = self.subspace_name or self.omoospace_name
        blend_path = str(omoospace.sourcefiles_path /
                         f"{format_name(subspace_name)}.blend")
        bpy.ops.wm.save_as_mainfile(filepath=blend_path)
        return {'FINISHED'}


class OpenOmoospaceRoot(bpy.types.Operator):
    bl_idname = "omoospace.open_omoospace_root"
    bl_label = "Open Current Omoospace Root"
    bl_description = "Open the omoospace root directory that current blender file located in"
    bl_options = {'UNDO'}

    def execute(self, context):
        omoospace_root = get_omoospace_root()
        os.startfile(omoospace_root)
        self.report({"INFO"}, f"Successfully opened '{omoospace_root}'")
        return {'FINISHED'}


class CopySubspaceRoute(bpy.types.Operator):
    bl_idname = "omoospace.copy_subspace_route"
    bl_label = "Copy Current Subspace Route"
    bl_description = "Copy the subspace route of current blender file to clipboard"
    bl_options = {'UNDO'}

    def execute(self, context):
        subspace_route = get_subspace_route()
        copy_to_clipboard(subspace_route)
        self.report({"INFO"}, f"Successfully copyed '{subspace_route}'")
        return {'FINISHED'}

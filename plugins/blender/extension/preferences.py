import bpy
from pathlib import Path


class OmoospacePreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    omoospace_home: bpy.props.StringProperty(
        name="Home Directory",
        subtype="DIR_PATH",
        default=str(Path.home())
    )  # type: ignore

    def draw(self, context):
        layout = self.layout

        layout.label(text="Configuration")
        layout.prop(self, 'omoospace_home')

import bpy
from pathlib import Path

from .externalpackage import ExternalPackagePreferences

REQUIREMENTS_DIR = str(Path(__file__).parent)


class OmoospacePreferences(bpy.types.AddonPreferences, ExternalPackagePreferences):
    bl_idname = __package__

    omoospace_home: bpy.props.StringProperty(
        name="Home Directory",
        subtype="DIR_PATH",
        default=str(Path.home())
    )  # type: ignore

    def draw(self, context):
        layout = self.layout
        # ExternalPackagePreferences Config
        self.requirements_dir = REQUIREMENTS_DIR
        super().draw(context)

        layout.label(text="Configuration")
        layout.prop(self, 'omoospace_home')

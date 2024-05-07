import bpy
from .props import QuickDir


class OMOOSPACE_UL_QuickDirList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        directory: QuickDir = item

        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row(align=True)
            row.label(text=directory.label, icon='FILE_FOLDER')

        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.label(text=directory.label)

import bpy
from .utils import get_subspace_route, get_omoospace_root
from .manage_paths import MakePathAbsolute, MakePathRelative, ManageInputPaths, ManageOutputPaths
from .omoospace import CreateOmoospace, OpenOmoospaceRoot, CopySubspaceRoute
try:
    from .externalpackage import PackageInstaller
    from .preferences import REQUIREMENTS_DIR
except:
    pass


class OmoospaceMenu(bpy.types.Menu):
    bl_idname = "OMOOSPACE_MT_OMOOSPACE"
    bl_label = "Omoospace"

    def draw(self, context):
        omoospace_root = get_omoospace_root()
        subspace_route = get_subspace_route()

        layout = self.layout
        layout.operator(CreateOmoospace.bl_idname)
        layout.separator()
        layout.operator(OpenOmoospaceRoot.bl_idname,
                        text=f"Omoospace Root: {omoospace_root}")
        layout.operator(CopySubspaceRoute.bl_idname,
                        text=f"Subspace Route: {subspace_route}")
        layout.separator()
        layout.operator(ManageInputPaths.bl_idname)
        layout.operator(ManageOutputPaths.bl_idname)
        layout.separator()
        layout.operator(MakePathRelative.bl_idname)
        layout.operator(MakePathAbsolute.bl_idname)


def TOPBAR(self, context):
    layout = self.layout
    try:
        installer = PackageInstaller(requirements_dir=REQUIREMENTS_DIR)
        if installer.is_installed('omoospace'):
            layout.menu(OmoospaceMenu.bl_idname)
        else:
            layout.label(text="Omoospace (Disabled)")
    except:
        layout.menu(OmoospaceMenu.bl_idname)


def FILE_BROWSER(self, context):
    layout = self.layout
    quick_dir_list = bpy.context.window_manager.quick_dir_list

    layout.template_list(
        listtype_name="OMOOSPACE_UL_QuickDirList",
        list_id="quick_dirs",
        dataptr=quick_dir_list,
        propname="quick_dirs",
        active_dataptr=quick_dir_list,
        active_propname="quick_dirs_active",
        item_dyntip_propname="path",
        rows=5
    )


def add():
    bpy.types.TOPBAR_MT_editor_menus.prepend(TOPBAR)
    bpy.types.FILEBROWSER_PT_bookmarks_favorites.prepend(FILE_BROWSER)


def remove():
    bpy.types.TOPBAR_MT_editor_menus.remove(TOPBAR)
    bpy.types.FILEBROWSER_PT_bookmarks_favorites.remove(FILE_BROWSER)

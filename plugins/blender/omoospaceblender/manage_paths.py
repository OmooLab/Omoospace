import bpy
from pathlib import Path
from .utils import (copy_to_dir, eval_raw_path, get_omoospace_root,
                    get_parm_raw_path, get_subspace_route, get_type, set_parm_raw_path)
from .props import OMOOSPACE_InputPath, OMOOSPACE_OutputPath
try:
    from omoospace import format_name
except:
    pass

CATEGORY_ICON = {
    "Images": "IMAGE_DATA",
    "Volumes": "VOLUME_DATA",
    "Dynamics": "FORCE_WIND",
    "Libraries": "LIBRARY_DATA_DIRECT",
    "Misc": "FILE",
    "Renders": "OUTPUT",
    "Videos": "FILE_MOVIE",
    "GeometryNodes": "NODETREE"
}


def get_omoospace_path():
    return Path(get_omoospace_root()).resolve()


def resolve_blend_path(blend_path: str):
    return Path(bpy.path.abspath(blend_path)).resolve()


def is_in_omoospace(path: Path):
    root_path = get_omoospace_path()
    return root_path in path.parents


def is_in_contents(path: Path):
    root_path = get_omoospace_path() / "Contents"
    return root_path in path.parents


def is_in_stageddata(path: Path):
    root_path = get_omoospace_path() / "StagedData"
    return root_path in path.parents


def is_invaild_input_path(blend_path: str):
    return not is_in_omoospace(resolve_blend_path(blend_path))


def is_invaild_output_path(blend_path: str):
    subspace_route = get_subspace_route()
    path = resolve_blend_path(blend_path)
    return (not is_in_contents(path) and not is_in_stageddata(path)) \
        or subspace_route not in str(path)


def correct_input_path(input_path: Path, category="Misc", include_dir: bool = False):
    main_path = Path("$OMOOSPACE", "Contents") \
        if is_in_contents(input_path) else Path("$OMOOSPACE", "ExternalData")

    if include_dir:
        corrected_path = main_path / category / input_path.parent.name / input_path.name
    else:
        corrected_path = main_path / category / input_path.name

    return str(corrected_path)


def correct_output_path(is_staged=False, is_dir=False, category="Misc", name="", suffix=""):
    main_path = Path("$OMOOSPACE", "StagedData") \
        if is_staged else Path("$OMOOSPACE", "Contents")
    suffix.removeprefix(".")
    name = f"$SUBSPACE_{name}"if name else "$SUBSPACE"
    filename = f"{name}.{suffix}" if suffix else name
    if is_dir:
        corrected_path = main_path / category / name
    else:
        corrected_path = main_path / category / name / filename

    return str(corrected_path)


def collect_input_paths():
    input_path_dict = {}

    def is_sequence(blend_path: str):
        path = resolve_blend_path(blend_path)
        last = path.stem.split(".")[-1]
        return last.isnumeric() and len(last) >= 3

    for image in bpy.data.images:
        if image.filepath:
            parm = f"bpy.data.images['{image.name}'].filepath"
            input_path_dict[parm] = {
                "label": image.name,
                "orig_path": image.filepath,
                "category": "Images",
                "include_dir": is_sequence(image.filepath)
            }

    for volume in bpy.data.volumes:
        if volume.filepath:
            parm = f"bpy.data.volumes['{volume.name}'].filepath"
            input_path_dict[parm] = {
                "label": volume.name,
                "orig_path": volume.filepath,
                "category": "Volumes",
                "include_dir": is_sequence(volume.filepath)
            }

    for cache_file in bpy.data.cache_files:
        if cache_file.filepath:
            parm = f"bpy.data.cache_files['{cache_file.name}'].filepath"
            input_path_dict[parm] = {
                "label": cache_file.name,
                "orig_path": cache_file.filepath,
                "category": "Dynamics",
                "include_dir": is_sequence(cache_file.filepath)
            }

    for library in bpy.data.libraries:
        if library.filepath:
            parm = f"bpy.data.libraries['{library.name}'].filepath"
            input_path_dict[parm] = {
                "label": library.name,
                "orig_path": library.filepath,
                "category": "Libraries",
                "include_dir": False
            }

    return input_path_dict


def collect_output_paths():
    output_paths = {}
    for scene in bpy.data.scenes:
        parm = f"bpy.data.scenes['{scene.name}'].render.filepath"
        not_video = scene.render.image_settings.file_format not in [
            "AVI_JPEG", "AVI_RAW", "FFMPEG"]
        output_paths[parm] = {
            "label": f"{scene.name} Render",
            "orig_path": scene.render.filepath,
            "category": "Renders" if not_video else "Videos",
            "name": format_name(scene.name),
            "suffix": "####" if not_video else "",
            "is_dir": False,
            "is_staged": False
        }

        for obj in bpy.data.objects:
            for modifier in obj.modifiers:
                if get_type(modifier) == "NodesModifier" and hasattr(modifier, "bake_directory"):
                    parm = f"bpy.data.objects['{obj.name}'].modifiers['{modifier.name}'].bake_directory"
                    output_paths[parm] = {
                        "label": f"{obj.name} {modifier.name} Bake",
                        "orig_path": modifier.bake_directory,
                        "category": "GeometryNodes",
                        "name": format_name(obj.name),
                        "suffix": "",
                        "is_dir": True,
                        "is_staged": True
                    }

    return output_paths


class OMOOSPACE_UL_InputPathList(bpy.types.UIList):
    invaild_only: bpy.props.BoolProperty(
        name="Show Invaild Path Only",
        options=set(),
        default=False
    )  # type: ignore

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        path_item: OMOOSPACE_InputPath = item

        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.split(factor=0.02)
            row.prop(path_item, "do_manage", text="")
            row = row.split(factor=0.2)
            row.label(text=path_item.label, icon=path_item.icon)
            row = row.split(factor=0.15)
            row.prop(path_item, "category", text="")
            row = row.split(factor=0.15)
            row.prop(path_item, "include_dir", text="Include Dir", toggle=1)
            row = row.split(factor=1)
            if path_item.do_manage:
                corrected_raw_path: str = correct_input_path(resolve_blend_path(path_item.orig_path),
                                                             category=path_item.category,
                                                             include_dir=path_item.include_dir)
                row.label(text=corrected_raw_path)
            elif path_item.raw_path:
                row.label(text=path_item.raw_path)
            else:
                row.label(text=path_item.orig_path)

        elif self.layout_type == 'GRID':
            ...

    def draw_filter(self, context, layout):
        layout.prop(self, "invaild_only")

    def filter_items(self, context, data, propname):
        paths = getattr(data, propname)

        # Default return values.
        flt_flags = [self.bitflag_filter_item] * len(paths)

        for index, path_item in enumerate(paths):
            if self.invaild_only and not is_invaild_input_path(path_item.orig_path):
                flt_flags[index] &= ~self.bitflag_filter_item

        flt_neworder = bpy.types.UI_UL_list.sort_items_by_name(
            paths, "parm")

        return flt_flags, flt_neworder


def update_input_paths(self, context):
    input_paths_active = self.input_paths_active
    if input_paths_active != -1:
        self.input_paths_active = -1


class ManageInputPaths(bpy.types.Operator):
    bl_idname = "omoospace.manage_input_paths"
    bl_label = "Manage Input Paths"
    bl_description = "Manage all input paths in current file"
    bl_options = {'UNDO'}

    input_paths: bpy.props.CollectionProperty(
        type=OMOOSPACE_InputPath,
        options={"SKIP_SAVE"}
    )  # type: ignore

    input_paths_active: bpy.props.IntProperty(
        name="Input Paths",
        options=set(),
        default=-1,
        update=update_input_paths
    )  # type: ignore

    def invoke(self, context, event):

        for parm, item in collect_input_paths().items():
            path_item: OMOOSPACE_InputPath = self.input_paths.add()
            raw_path = get_parm_raw_path(parm)

            if raw_path and eval_raw_path(raw_path) == item["orig_path"]:
                path_item.raw_path = raw_path
                path_item.do_manage = False
            else:
                path_item.do_manage = is_invaild_input_path(item["orig_path"])
            path_item.label = item["label"]
            path_item.parm = parm
            path_item.orig_path = item["orig_path"]

            if item.get("category") is not None:
                path_item.category = item.get("category")
                path_item.icon = CATEGORY_ICON[item.get("category")]

            if item.get("include_dir") is not None:
                path_item.include_dir = item.get("include_dir")

        context.window_manager.invoke_props_dialog(self, width=800)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        input_paths: list[OMOOSPACE_InputPath] = self.input_paths

        def manage_path(path_item: OMOOSPACE_InputPath):
            # skip
            if not path_item.do_manage:
                return

            parm = path_item.parm
            source = resolve_blend_path(path_item.orig_path)
            corrected_raw: str = correct_input_path(source,
                                                    category=path_item.category,
                                                    include_dir=path_item.include_dir)
            corrected_blend_path: str = eval_raw_path(corrected_raw)
            target = Path(corrected_blend_path).resolve()

            # copy file if not the same path
            if source != target:
                try:
                    if "<UDIM>" in str(source):
                        udims = source.parent.glob(
                            source.name.replace("<UDIM>", "*"))
                        for udim in udims:
                            copy_to_dir(
                                udim.parent if path_item.include_dir else udim,
                                target.parent.parent if path_item.include_dir else target.parent,
                                exist_ok=True
                            )
                    else:
                        copy_to_dir(
                            source.parent if path_item.include_dir else source,
                            target.parent.parent if path_item.include_dir else target.parent,
                            exist_ok=True
                        )
                except Exception as e:
                    print(e)
                    if target.exists():
                        self.report(
                            {"WARNING"}, f"Fail to overwrite, manually delete {str(target)}, then try again.")
                    else:
                        self.report(
                            {"ERROR"}, f"Fail to copy, skip '{parm}'.")
                    return

            try:
                exec(f"{parm}=r'{corrected_blend_path}'")
                set_parm_raw_path(parm, corrected_raw, True)
                self.report(
                    {"INFO"}, f"{path_item.orig_path} -> {corrected_blend_path}")
            except:
                self.report(
                    {"ERROR"}, f"Fail to change path, skip '{parm}'.")

        for path_item in input_paths:
            manage_path(path_item)

        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        row = layout.split(factor=0.02)
        row.label(text="")
        row = row.split(factor=0.2)
        row.label(text="Label")
        row = row.split(factor=0.15)
        row.label(text="Category")
        row = row.split(factor=0.15)
        row.label(text="")
        row = row.split(factor=1)
        row.label(text="Preview")

        layout.template_list(
            listtype_name="OMOOSPACE_UL_InputPathList",
            list_id="input_paths",
            dataptr=self,
            propname="input_paths",
            active_dataptr=self,
            active_propname="input_paths_active",
            item_dyntip_propname="orig_path",
            rows=20
        )


class OMOOSPACE_UL_OutputPathList(bpy.types.UIList):

    invaild_only: bpy.props.BoolProperty(
        name="Show Invaild Path Only",
        options=set(),
        default=False
    )  # type: ignore

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        path_item: OMOOSPACE_OutputPath = item

        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.split(factor=0.02)
            row.prop(path_item, "do_manage", text="")
            row = row.split(factor=0.15)
            row.label(text=path_item.label, icon=path_item.icon)

            row = row.split(factor=0.06)
            row.prop(path_item, "is_staged", text="Staged", toggle=1)
            row = row.split(factor=0.04)
            row.prop(path_item, "is_dir", text="Dir", toggle=1)
            row = row.split(factor=0.1)
            row.prop(path_item, "category", text="")
            row = row.split(factor=0.1)
            row.prop(path_item, "name", text="")
            row = row.split(factor=0.1)
            row.prop(path_item, "suffix", text="")

            row = row.split(factor=1)
            if path_item.do_manage:
                corrected_path = correct_output_path(is_staged=path_item.is_staged,
                                                     is_dir=path_item.is_dir,
                                                     category=path_item.category,
                                                     name=path_item.name,
                                                     suffix=path_item.suffix)
                row.label(text=corrected_path)
            elif path_item.raw_path:
                row.label(text=path_item.raw_path)
            else:
                row.label(text=path_item.orig_path)

        elif self.layout_type == 'GRID':
            ...

    def draw_filter(self, context, layout):
        layout.prop(self, "invaild_only")

    def filter_items(self, context, data, propname):
        paths = getattr(data, propname)

        # Default return values.
        flt_flags = [self.bitflag_filter_item] * len(paths)

        for index, path_item in enumerate(paths):
            if self.invaild_only and not is_invaild_output_path(path_item.orig_path):
                flt_flags[index] &= ~self.bitflag_filter_item

        flt_neworder = bpy.types.UI_UL_list.sort_items_by_name(
            paths, "parm")

        return flt_flags, flt_neworder


def update_output_paths(self, context):
    output_paths_active = self.output_paths_active
    if output_paths_active != -1:
        self.output_paths_active = -1


class ManageOutputPaths(bpy.types.Operator):
    bl_idname = "omoospace.manage_output_paths"
    bl_label = "Manage Output Paths"
    bl_description = "Manage all output paths in current file"
    bl_options = {'UNDO'}

    output_paths: bpy.props.CollectionProperty(
        type=OMOOSPACE_OutputPath,
        options={"SKIP_SAVE"}
    )  # type: ignore

    output_paths_active: bpy.props.IntProperty(
        name="Output Paths",
        options=set(),
        default=-1,
        update=update_output_paths
    )  # type: ignore

    def invoke(self, context, event):
        for parm, item in collect_output_paths().items():
            path_item: OMOOSPACE_OutputPath = self.output_paths.add()
            raw_path = get_parm_raw_path(parm)

            if raw_path and eval_raw_path(raw_path) == item["orig_path"]:
                path_item.raw_path = raw_path
                path_item.do_manage = False
            else:
                path_item.do_manage = is_invaild_output_path(item["orig_path"])

            path_item.label = item["label"]
            path_item.parm = parm
            path_item.orig_path = item["orig_path"]

            if item.get("category") is not None:
                path_item.category = item.get("category")
                path_item.icon = CATEGORY_ICON[item.get("category")]

            if item.get("name") is not None:
                path_item.name = item.get("name")

            if item.get("suffix") is not None:
                path_item.suffix = item.get("suffix")

            if item.get("is_dir") is not None:
                path_item.is_dir = item.get("is_dir")

            if item.get("is_staged") is not None:
                path_item.is_staged = item.get("is_staged")

        context.window_manager.invoke_props_dialog(self, width=1000)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        output_paths: list[OMOOSPACE_OutputPath] = self.output_paths

        def manage_path(path_item: OMOOSPACE_OutputPath):
            # skip
            if not path_item.do_manage:
                return

            parm = path_item.parm
            corrected_raw: str = correct_output_path(is_staged=path_item.is_staged,
                                                     is_dir=path_item.is_dir,
                                                     category=path_item.category,
                                                     name=path_item.name,
                                                     suffix=path_item.suffix)

            corrected_blend_path: str = eval_raw_path(corrected_raw)

            try:
                exec(f"{parm}=r'{corrected_blend_path}'")
                set_parm_raw_path(parm, corrected_raw, path_item.is_staged)
                self.report(
                    {"INFO"}, f"{path_item.orig_path} -> {corrected_blend_path}")
            except:
                self.report(
                    {"ERROR"}, f"Fail to change path, skip '{parm}'.")

        for path_item in output_paths:
            manage_path(path_item)

        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        row = layout.split(factor=0.02)
        row.label(text="")
        row = row.split(factor=0.15)
        row.label(text="Label")
        row = row.split(factor=0.06)
        row.label(text="")
        row = row.split(factor=0.04)
        row.label(text="")
        row = row.split(factor=0.1)
        row.label(text="Category")
        row = row.split(factor=0.1)
        row.label(text="Name")
        row = row.split(factor=0.1)
        row.label(text="Suffix")
        row = row.split(factor=1)
        row.label(text="Preview")

        layout.template_list(
            listtype_name="OMOOSPACE_UL_OutputPathList",
            list_id="output_paths",
            dataptr=self,
            propname="output_paths",
            active_dataptr=self,
            active_propname="output_paths_active",
            item_dyntip_propname="orig_path",
            rows=20
        )


class MakePathRelative(bpy.types.Operator):
    bl_idname = "omoospace.make_path_relative"
    bl_label = "Make Path Relative"
    bl_description = "This will make sure all resouces will work if the whole omoospace directroy is moved"
    bl_options = {'UNDO'}

    def execute(self, context):
        all_paths = {}
        all_paths.update(collect_input_paths())
        all_paths.update(collect_output_paths())
        for parm, item in all_paths.items():
            path = resolve_blend_path(item["orig_path"])
            file_path = resolve_blend_path("//")
            try:
                relative_path = bpy.path.relpath(
                    str(path), start=str(file_path))
                if item['orig_path'] != relative_path:
                    exec(f"{parm}=r'{relative_path}'")
                    self.report(
                        {"INFO"}, f"{item['orig_path']} -> {relative_path}")
            except:
                self.report(
                    {"WARNING"}, f"{item['orig_path']} is not relative to this blender file, skiped.")

        return {'FINISHED'}


class MakePathAbsolute(bpy.types.Operator):
    bl_idname = "omoospace.make_path_absolute"
    bl_label = "Make Path Absolute"
    bl_description = "This will make sure all resouces will work if this file is moved"
    bl_options = {'UNDO'}

    def execute(self, context):
        all_paths = {}
        all_paths.update(collect_input_paths())
        all_paths.update(collect_output_paths())
        for parm, item in all_paths.items():
            absolute_path = str(resolve_blend_path(item["orig_path"]))
            if item['orig_path'] != absolute_path:
                exec(f"{parm}=r'{absolute_path}'")
                self.report(
                    {"INFO"}, f"{item['orig_path']} -> {absolute_path}")

        return {'FINISHED'}

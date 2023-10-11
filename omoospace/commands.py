import click
from pathlib import Path
import yaml
from InquirerPy import inquirer, get_style
from InquirerPy.validator import EmptyInputValidator
from InquirerPy.base import Choice
from prompt_toolkit.validation import ValidationError, Validator

from omoospace.directory import Structure
from omoospace.exceptions import InvalidError, NotFoundError, NotIncludeError
from omoospace.package import Package
from omoospace.types import PathLike
from omoospace.utils import format_name, is_subpath
from omoospace import console, ui
from omoospace.omoospace import Omoospace, OmoospaceTree

# TODO: more manage of templates
# TODO: docs


inquirer_style = get_style(
    {
        "questionmark": "#ffd700",
        "answermark": "#ffd700",
        "question": "",
        "answered_question": "",
        "pointer": "italic #ffd700",
        "input": "italic #ffd700",
        "answer": "italic #ffd700",
        "skipped": "#808080",
        "validator": "bold fg:#ffffff bg:red",
    },
    style_override=False
)


def option_omoospace():
    return click.option(
        "-os", "--omoospace",
        type=click.Path(),
        help="The root (or sub) directory of target Omoospace"
    )


class OmoospaceTemplate():
    def __init__(
        self,
        name: str,
        description: str,
        structure: Structure = None
    ) -> None:
        self.name = name
        self.description = description
        self.structure = structure or {}
        self.tree = OmoospaceTree(structure=structure)


class Setting():
    working_omoospace: str
    working_directory: str
    recent_omoospaces: list[str]
    omoospace_templates: list[OmoospaceTemplate]

    SETTING_PATH = "~/.omoospace/setting.yml"

    DEFAULT_SETTING = {
        "working_omoospace": None,
        "working_directory": None,
        "recent_omoospaces": None,
        "omoospace_templates": [
            {
                "name": "*Empty",
                "description": "No Subdirectories",
                "structure": None
            },
            {
                "name": "3D Asset",
                "description": "For 3D asset creation",
                "structure": {
                    "Contents": {
                        'Images': None,
                        'Materials': None,
                        'Models': None,
                        'Renders': None
                    },
                    "SourceFiles": {
                        '*AssetName': None,
                        'Void': None
                    }
                }
            },
            {
                "name": "CG Film",
                "description": "For short CG film producton",
                "structure": {
                    "Contents": {
                        'Audios': None,
                        'Dynamics': None,
                        'Images': None,
                        'Materials': None,
                        'Models': None,
                        'Renders': None,
                        'Videos': None,
                    },
                    "SourceFiles": {
                        '*FilmName': None,
                        'Void': None
                    }
                }
            }
        ],
        "process_templates": [
        ]
    }

    def __read_setting_yml(self):
        setting: dict = {}
        setting_yml = Path(self.SETTING_PATH).expanduser().resolve()
        if setting_yml.exists():
            with setting_yml.open('r', encoding='utf-8') as file:
                # aviod empty or invalid ifle
                setting = yaml.safe_load(file) or {}
        return setting

    def __write_setting_yml(self, setting):
        setting_yml = Path(self.SETTING_PATH).expanduser().resolve()
        with setting_yml.open('w', encoding='utf-8') as file:
            yaml.safe_dump(setting, file, sort_keys=False, allow_unicode=True)

    def __getattr__(self, key):
        if key not in self.DEFAULT_SETTING.keys():
            raise InvalidError(key, "key")
        setting = self.__read_setting_yml()

        if (key == "omoospace_templates"):
            omoospace_templates = setting.get("omoospace_templates") or []
            omoospace_templates.extend(
                self.DEFAULT_SETTING["omoospace_templates"])
            return [OmoospaceTemplate(
                name=template.get('name'),
                description=template.get('description'),
                structure=template.get('structure')
            ) for template in omoospace_templates]
        else:
            return setting.get(key) or self.DEFAULT_SETTING.get(key)

    def __setattr__(self, key, value):
        if key not in self.DEFAULT_SETTING.keys():
            raise InvalidError(key, "key")
        setting = self.__read_setting_yml()
        setting[key] = value
        self.__write_setting_yml(setting)


def choose_omoospace():
    recent_list = Setting().recent_omoospaces or []

    def is_valid(omoospace_dir):
        try:
            Omoospace(omoospace_dir)
            return True
        except:
            return False

    recent_list = list(filter(is_valid, recent_list))
    Setting().recent_omoospaces = recent_list
    recent_list.reverse()

    if (len(recent_list) > 0):
        omoospace_dir = inquirer.select(
            message="Choose one from recent",
            choices=recent_list,
            style=inquirer_style
        ).execute()
        return to_omoospace(omoospace_dir)
    else:
        raise NotFoundError("recent omoospace", "setting")


def to_omoospace(detect_path: str):
    omoospace = Omoospace(detect_path)
    recent_list = Setting().recent_omoospaces or []
    omoospace_dir = str(omoospace.root_path)
    # remove old record in settings
    try:
        recent_list.remove(omoospace_dir)
    except:
        pass
    recent_list.append(omoospace_dir)
    Setting().recent_omoospaces = recent_list
    Setting().working_omoospace = omoospace_dir
    console.print("Current working at 🛠️ [bright]%s (%s)." %
                  (omoospace.name, omoospace_dir))
    return omoospace


def get_omoospace(detect_path: str = None):
    detect_path = detect_path or "."
    try:
        omoospace = to_omoospace(detect_path)
    except:
        try:
            omoospace_dir = Setting().working_omoospace
            omoospace = to_omoospace(omoospace_dir)
        except Exception as err:
            console.print(err, style="warning")
            Setting().working_omoospace = None
            omoospace = choose_omoospace()
    return omoospace


def is_valid_working_dir(working_dir: PathLike):
    root_working_dir = get_root_working_dir()
    working_dir = working_dir or "."
    working_path = Path(working_dir).resolve()

    exists = working_path.is_dir()
    is_include = is_subpath(working_dir, root_working_dir, or_equal=True)
    return exists and is_include


def get_root_working_dir():
    omoospace_dir = Setting().working_omoospace
    if not omoospace_dir:
        raise NotFoundError("working omoospace", "setting")

    root_working_dir = str(Path(omoospace_dir, "SourceFiles").resolve())
    return root_working_dir


def get_working_dir():
    working_dir = Setting().working_directory
    if not is_valid_working_dir(working_dir):
        working_dir = get_root_working_dir()

    Setting().working_directory = working_dir
    return working_dir


def set_working_dir(working_dir: PathLike):
    working_dir = str(Path(working_dir).resolve())

    if not is_valid_working_dir(working_dir):
        raise InvalidError(working_dir, "working directory")

    Setting().working_directory = working_dir

# --------------------------------------------------------------------
#                                CREATE
# --------------------------------------------------------------------


@click.command('create', help="Create new omoospace.")
@click.option("-d", "--dst", default='.',
              type=click.Path(exists=True, file_okay=False))
def cli_create(dst: str):
    class OmoospaceNameValidator(Validator):
        def validate(self, document):
            # Check if is empty
            if not len(document.text) > 0:
                raise ValidationError(
                    message="Name cannot be empty.",
                    cursor_position=document.cursor_position,
                )

            omoospace_name = format_name(document.text)
            omoospace_path = Path(dst, omoospace_name).resolve()

            # Check if omoospace exists
            if (omoospace_path.exists()):
                raise ValidationError(
                    message="'%s' already exists in dstination directory, "
                    "change the name or the dstination." % omoospace_name,
                    cursor_position=document.cursor_position,
                )

    templates = Setting().omoospace_templates
    omoospace_structure = None
    choices = [Choice(
        name="%s (%s)" % (template.name, template.description),
        value=id
    ) for id, template in enumerate(templates)]

    template_id: int = inquirer.select(
        message="Choose a template",
        choices=choices,
        filter=lambda result: int(result),
        style=inquirer_style,
    ).execute()

    while True:
        template = templates[template_id]
        console.print(template.tree.render_tree())
        confirm_id: int = inquirer.select(
            message="Choose the same again to confirm",
            choices=choices,
            filter=lambda result: int(
                result) if result != choices[0] else None,
            default=template_id,
            long_instruction="Press Enter key to confirm",
            style=inquirer_style,
        ).execute()
        if confirm_id == template_id:
            break
        else:
            template_id = confirm_id

    omoospace_name: str = inquirer.text(
        message="Enter Omoospace name",
        validate=OmoospaceNameValidator(),
        style=inquirer_style
    ).execute()
    omoospace_path = Path(dst, format_name(omoospace_name)).resolve()

    description = inquirer.text(
        message="A brief of the Omoospace",
        default="An Omoospace for creation works",
        style=inquirer_style
    ).execute()

    omoospace_info = {
        "description": description
    }

    # Confirm information

    console.print(ui.Board(
        ui.Info("Name", "%s [dim](%s)[/dim]" %
                (omoospace_name, omoospace_path)),
        ui.Info("Description", description),
        ui.Info("Directory Tree", template.tree.render_tree()),
        title="Create Omoospace Form"
    ))

    print("")
    is_confirm = inquirer.confirm(
        message="Confirm",
        default=True,
        style=inquirer_style
    ).execute()
    if is_confirm:
        omoospace = Omoospace.create(
            create_dir=dst,
            name=omoospace_name,
            info=omoospace_info,
            structure=template.structure
        )
        to_omoospace(omoospace.root_path)
        console.print("Start create something! 🚀", style="cheer")

# --------------------------------------------------------------------
#                                PACKAGE
# --------------------------------------------------------------------


@click.command('export', help="Export new package.")
@option_omoospace()
@click.option(
    "-d", "--dst", type=click.Path(),
    help="The output path of Package"
)
def cli_export(omoospace, dst):
    omoospace = get_omoospace(omoospace)
    export_path = Path(dst).resolve() if dst \
        else Path(omoospace.root_path, 'StagedData', 'Packages').resolve()

    class PackageItemValidator(Validator):
        def validate(self, document):
            # Check if is empty
            pending_items = get_items(document.text)
            if len(pending_items) == 0:
                raise ValidationError(
                    message="Find no files or directories in %s" % document.text,
                    cursor_position=document.cursor_position,
                )

    def get_items(path_pattern: str):
        if not path_pattern:
            # inquirer will trigger filter even if is escaped. but path_pattern become None
            return []
        # FIXME: glob must be relative path, but inquirer need abs path for auto complete.
        # maybe can make a fake path auto completer to fix this
        path_pattern = path_pattern.removeprefix(str(omoospace.root_path))
        path_pattern = path_pattern.removeprefix("\\")
        path_pattern = path_pattern.removeprefix("/")
        if path_pattern == "":
            return []
        items = sorted(omoospace.root_path.glob(path_pattern))
        items = [item.resolve() for item in items]
        items = list(filter(omoospace.is_valid_item, items))
        return items

    def print_items(pending, checked):
        pending = [item.relative_to(omoospace.root_path) for item in pending]
        checked = [item.relative_to(omoospace.root_path) for item in checked]
        transfer = ui.Transfer(
            pending, checked, left_header="Pending", right_header="Checked")
        console.print(transfer)

    pending_items = []
    checked_items = []

    while True:
        if len(checked_items) > 0:
            print_items(pending_items, checked_items)
        pending_items = inquirer.filepath(
            message="Enter the item path or path pattern",
            long_instruction='Press Tab to summon auto completer.\n'
            'Press Enter to confirm the input.\n'
            'Press Esc to finish adding item (at least one checked item).',
            filter=get_items,
            validate=PackageItemValidator(),
            default=str(omoospace.root_path),
            keybindings={"skip": [{"key": "escape"}]},
            mandatory=len(checked_items) == 0,
            style=inquirer_style
        ).execute()
        if len(pending_items) == 0:
            break

        print_items(pending_items, checked_items)

        check_in = inquirer.confirm(
            message="Check if the items on left are wanted",
            default=True,
            style=inquirer_style
        ).execute()

        if check_in:
            checked_items.extend(pending_items)
            checked_items = list(set(checked_items))
        pending_items = []

    package_name = inquirer.text(
        message="Name this package",
        validate=EmptyInputValidator("Name cannot be empty"),
        default=omoospace.name,
        style=inquirer_style
    ).execute()

    package_description = inquirer.text(
        message="Enter a brief description of this package",
        default="An omoospace package for sharing",
        style=inquirer_style
    ).execute()
    package_version = inquirer.text(
        message="Enter the verison of this package",
        default="0.1.0",
        style=inquirer_style
    ).execute()

    package_info = {
        "description": package_description,
        "version": package_version
    }

    ui_items = ui.Table("Name", "Path")
    for item in checked_items:
        _abspath = str(Path(omoospace.root_path, item))
        _name = Path(_abspath).parts[-1]
        ui_items.add_row(_name, _abspath)

    package_path = Path(export_path, format_name(package_name)).resolve()
    console.print(ui.Board(
        ui.Info("Name", "%s [dim](%s)[/dim]" %
                (package_name, package_path)),
        ui.Info("Description", package_description),
        ui.Info("Version", package_version),
        ui.Info("Items", ui_items),
        title="Export Package Form"
    ))

    is_confirm = inquirer.confirm(
        message="Sure",
        default=True,
        style=inquirer_style
    ).execute()
    if is_confirm:
        omoospace.export_package(
            items=checked_items,
            export_dir=export_path,
            name=package_name,
            info=package_info
        )
        console.print("Successfully export! 📦", style="cheer")


@click.command('import', help="Import a package.")
@option_omoospace()
def cli_import(omoospace):
    omoospace = get_omoospace(omoospace)

    class ImportPackageValidator(Validator):
        def validate(self, document):
            # Check if is empty
            if not len(document.text) > 0:
                raise ValidationError(
                    message="Package path cannot be empty.",
                    cursor_position=document.cursor_position,
                )

            # Check if is package
            try:
                package = Package(document.text)
            except:
                raise ValidationError(
                    message="Package path is not a valid package.",
                    cursor_position=document.cursor_position,
                )

    import_dir = inquirer.filepath(
        message="Enter package file|dir path",
        validate=ImportPackageValidator(),
        long_instruction='Press Tab to summon auto completer. \n'
        'Press Enter to confirm.',
        style=inquirer_style
    ).execute()

    package = Package(import_dir)
    console.print(ui.Board(
        ui.Info("Name", "%s [dim](%s)[/dim]" %
                (package.name, import_dir)),
        ui.Info("Description", package.description),
        ui.Info("Version", package.version),
        ui.Info("Items", package.items),
        title="Import Package Form"
    ))

    is_confirm = inquirer.confirm(
        message="Confirm",
        default=True,
        style=inquirer_style
    ).execute()
    if is_confirm:
        omoospace.import_package(import_dir)
    console.print("Successfully import! 📦", style="cheer")

# --------------------------------------------------------------------
#                                TO
# --------------------------------------------------------------------


@click.command('to', help="Switch to another omoospace.")
@click.argument("omoospace", required=False, default='.',
                type=click.Path(exists=True, file_okay=False))
def cli_to(omoospace):
    try:
        omoospace = to_omoospace(omoospace)
    except Exception as err:
        console.print(err, style="warning")
        try:
            omoospace = choose_omoospace()
        except Exception as err:
            console.print(err, style="warning")


# --------------------------------------------------------------------
#                                ADD
# --------------------------------------------------------------------


@click.group('add', help="Add stuffs to omoospace.")
def cli_add():
    pass


def _add_subspace(omoospace):
    try:
        omoospace: Omoospace = get_omoospace(omoospace)
    except Exception as err:
        console.print(err, style="warning")

    class SubspaceParentDirValidator(Validator):
        def validate(self, document):
            # Check if is empty
            if not len(document.text) > 0:
                raise ValidationError(
                    message="Parent directory cannot be empty.",
                    cursor_position=document.cursor_position,
                )

            # Check if is valid directory
            path = Path(document.text)
            if not path.is_dir():
                raise ValidationError(
                    message="'%s' is invalid directory." % document.text,
                    cursor_position=document.cursor_position,
                )

            # Check if is in SourceFiles
            if not is_subpath(path, omoospace.sourcefiles_path, or_equal=True):
                raise ValidationError(
                    message="'%s' is out of SourceFiles." % document.text,
                    cursor_position=document.cursor_position,
                )

    parent_dir = inquirer.filepath(
        message="Enter subspace parent directory",
        only_directories=True,
        validate=SubspaceParentDirValidator(),
        long_instruction='Press Tab to summon auto completer. \n'
        'Press Enter to confirm.',
        default=get_working_dir(),
        style=inquirer_style
    ).execute()
    set_working_dir(parent_dir)

    subspace_name = inquirer.text(
        message="Enter subspace name",
        validate=EmptyInputValidator("Name cannot be empty."),
        style=inquirer_style
    ).execute()

    subspace_comment = inquirer.text(
        message="Enter a comment of this subspace (Optional)",
        style=inquirer_style
    ).execute()

    subspace_info = {
        "comments": subspace_comment or None
    }

    subspace_entity = Path(parent_dir, format_name(subspace_name)).resolve()
    subspace_tree = omoospace.get_subspace_tree(subspace_entity)
    console.print(ui.Board(
        ui.Info("Name", "%s [dim](%s)[/dim]" %
                (subspace_name, subspace_entity)),
        ui.Info("Comments", subspace_comment),
        ui.Info("Subspace Tree", subspace_tree.render_tree()),
        title="Add Subspace Form"
    ))

    is_confirm = inquirer.confirm(
        message="Confirm",
        default=True,
        style=inquirer_style
    ).execute()
    if is_confirm:
        omoospace.add_subspace(
            name=subspace_name,
            parent_dir=parent_dir,
            info=subspace_info
        )


@click.command('s')
@option_omoospace()
def cli_add_sub(omoospace):
    _add_subspace(omoospace)


@click.command('subspace')
@option_omoospace()
def cli_add_subspace(omoospace):
    _add_subspace(omoospace)


@click.command('p')
@option_omoospace()
def cli_add_process():
    pass


@click.command('process')
@option_omoospace()
def cli_add_process():
    pass


@click.command('w')
@option_omoospace()
def cli_add_work():
    pass


@click.command('work')
@option_omoospace()
def cli_add_work():
    pass


@click.command('c')
@option_omoospace()
def cli_add_creator():
    pass


@click.command('creator')
@option_omoospace()
def cli_add_creator():
    pass


@click.command('so')
@option_omoospace()
def cli_add_software():
    pass


@click.command('software')
@option_omoospace()
def cli_add_software():
    pass


cli_add.add_command(cli_add_subspace)
cli_add.add_command(cli_add_sub)
cli_add.add_command(cli_add_work)
cli_add.add_command(cli_add_creator)
cli_add.add_command(cli_add_software)

# --------------------------------------------------------------------
#                                SHOW
# --------------------------------------------------------------------


@click.command('show', help="Show summary")
@option_omoospace()
@click.option(
    "-d", "--dst",
    type=click.Path(),
    help="Destination directory of structure.html for Omoospace structure visualization"
)
def cli_show(omoospace, dst):
    omoospace = get_omoospace(omoospace)
    omoospace.show_summary(dst)


@click.group()
def cli():
    pass


cli.add_command(cli_add)
cli.add_command(cli_create)
cli.add_command(cli_show)
cli.add_command(cli_to)
cli.add_command(cli_export)
cli.add_command(cli_import)

if __name__ == "__main__":
    cli()

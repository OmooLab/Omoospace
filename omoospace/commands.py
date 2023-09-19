from typing import TypedDict
import click
from pathlib import Path
import yaml
from pathlib import Path
from glob import glob
from InquirerPy import inquirer, get_style
from InquirerPy.validator import EmptyInputValidator
from InquirerPy.base import Choice

from prompt_toolkit.validation import ValidationError, Validator
from omoospace.utils import format_name, is_subpath
from omoospace.ui import ui_info, console, ui_board, ui_table, ui_transfer
from omoospace.omoospace import Omoospace, OmoospaceStructure

# TODO: more manage of templates

# TODO: docs
# TODO: var name for omoospace package attr and ...
# TODO: separate in and out funtions and attrs


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


@click.group()
def cli():
    pass


SETTING_PATH = "~/.omoospace/setting.yml"


class Setting():
    current: str
    recent: str
    templates: dict[str, OmoospaceStructure]

    DEFAULT_SETTING = {
        "current": None,
        "recent": None,
        "templates": {
            "Asset": {
                "contents": {
                    'Images': None,
                    'Materials': None,
                    'Models': None,
                    'Renders': None
                },
                "sourcefiles": {
                    '*AssetName': None,
                    'Void': None
                }
            },
            "Film": {
                "contents": {
                    'Audios': None,
                    'Dynamics': None,
                    'Images': None,
                    'Materials': None,
                    'Models': None,
                    'Renders': None,
                    'Videos': None,
                },
                "sourcefiles": {
                    '*FilmName': None,
                    'Void': None
                }
            }
        }
    }

    def __read_setting_yml(self):
        setting: dict = {}
        setting_yml = Path(SETTING_PATH).expanduser().resolve()
        if setting_yml.exists():
            with setting_yml.open('r', encoding='utf-8') as file:
                # aviod empty or invalid ifle
                setting = yaml.safe_load(file) or {}
        return setting

    def __write_setting_yml(self, setting):
        setting_yml = Path(SETTING_PATH).expanduser().resolve()
        with setting_yml.open('w', encoding='utf-8') as file:
            yaml.safe_dump(setting, file, sort_keys=False)

    def __getattr__(self, key):
        if key not in self.DEFAULT_SETTING.keys():
            raise Exception("%s is invalid key in setting" % key)
        setting = self.__read_setting_yml()
        return setting.get(key) or self.DEFAULT_SETTING.get(key)

    def __setattr__(self, key, value):
        if key not in self.DEFAULT_SETTING.keys():
            raise Exception("%s is invalid key in setting" % key)
        setting = self.__read_setting_yml()
        setting[key] = value
        self.__write_setting_yml(setting)


def choose_omoospace():
    recent_list = Setting().recent or []

    def is_valid(root_dir):
        try:
            Omoospace(root_dir)
            return True
        except:
            return False

    recent_list = list(filter(is_valid, recent_list))
    Setting().recent = recent_list
    recent_list.reverse()

    if (len(recent_list) > 0):
        root_dir = inquirer.select(
            message="Choose one from recent",
            choices=recent_list,
            style=inquirer_style
        ).execute()
        return to_omoospace(root_dir)
    else:
        raise Exception("No recent omoospace in record")


def to_omoospace(detect_path: str):
    omoospace = Omoospace(detect_path)
    recent_list = Setting().recent or []
    root_dir = str(omoospace.root_path)
    # remove old record in settings
    try:
        recent_list.remove(root_dir)
    except:
        pass
    recent_list.append(root_dir)
    Setting().recent = recent_list
    Setting().current = root_dir
    console.print("Current working at 🛠️ [bright]%s (%s)." %
                  (omoospace.name, root_dir))
    return omoospace


def get_omoospace(detect_path: str = None):
    if detect_path:
        omoospace = Omoospace(detect_path)
    else:
        try:
            omoospace = to_omoospace(".")
        except:
            try:
                root_dir = Setting().current
                omoospace = to_omoospace(root_dir)
            except Exception as err:
                console.print(err, style="warning")
                Setting().current = None
                omoospace = choose_omoospace()
    return omoospace

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

    omoospace_name: str = inquirer.text(
        message="Enter Omoospace name",
        validate=OmoospaceNameValidator(),
        style=inquirer_style
    ).execute()
    omoospace_path = Path(dst, format_name(omoospace_name)).resolve()
    templates = Setting().templates

    template: str = inquirer.select(
        message="Choose a template",
        choices=["(Empty)", *templates.keys()],
        default="(Empty)",
        style=inquirer_style
    ).execute()
    omoospace_structure = templates.get(template)

    description = inquirer.text(
        message="A brief of the Omoospace",
        default="An Omoospace for creation works",
        style=inquirer_style
    ).execute()

    omoospace_info = {
        "description": description
    }

    # Confirm information
    # TODO: show folder tree
    console.print(ui_board(
        ui_info("Name", "%s [dim](%s)[/dim]" %
                (omoospace_name, omoospace_path)),
        ui_info("Description", description),
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
            structure=omoospace_structure
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

    def get_items(path_pattern: str):
        if not path_pattern:
            return []
        items = sorted(Path('.').glob(path_pattern))
        items = [item.resolve() for item in items]
        items = list(filter(omoospace.is_valid_item, items))
        return items

    class PackageItemValidator(Validator):
        def validate(self, document):
            # Check if is empty
            pending_items = get_items(document.text)
            if len(pending_items) == 0:
                raise ValidationError(
                    message="Find no files or directories in %s" % document.text,
                    cursor_position=document.cursor_position,
                )

    def print_items(pending, checked):
        pending = [item.relative_to(omoospace.root_path) for item in pending]
        checked = [item.relative_to(omoospace.root_path) for item in checked]
        transfer = ui_transfer(
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
            default=str(omoospace.root_path.relative_to(Path.cwd())),
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

    ui_items = ui_table("Name", "Path")
    for item in checked_items:
        _abspath = str(Path(omoospace.root_path, item))
        _name = Path(_abspath).parts[-1]
        ui_items.add_row(_name, _abspath)

    package_path = Path(export_path, format_name(package_name)).resolve()
    console.print(ui_board(
        ui_info("Name", "%s [dim](%s)[/dim]" %
                (package_name, package_path)),
        ui_info("Description", package_description),
        ui_info("Version", package_version),
        ui_info("Items", ui_items),
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
@click.argument("path")
@option_omoospace()
def cli_import(path, omoospace):
    omoospace = get_omoospace(omoospace)
    omoospace.import_package(path)
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


@click.command('subspace')
@option_omoospace()
def cli_add_subspace(omoospace):
    try:
        omoospace: Omoospace = get_omoospace(omoospace)
    except Exception as err:
        console.print(err, style="warning")

    class SubspaceDestinationValidator(Validator):
        def validate(self, document):
            # Check if is empty
            if not len(document.text) > 0:
                raise ValidationError(
                    message="Destination cannot be empty.",
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

    subspace_name = inquirer.text(
        message="Enter subspace name",
        validate=EmptyInputValidator("Name cannot be empty."),
        style=inquirer_style
    ).execute()
    subspace_name = format_name(subspace_name)

    parent_dir = inquirer.filepath(
        message="Enter subspace dstination directory",
        only_directories=True,
        validate=SubspaceDestinationValidator(),
        long_instruction='Press Tab to summon auto completer. \n'
        'Press Enter to confirm.',
        default=str(omoospace.sourcefiles_path.relative_to(Path.cwd())),
        style=inquirer_style
    ).execute()
    entity = Path(parent_dir, subspace_name).resolve()

    # TODO: better draw tree
    route = omoospace.get_route(entity)
    route = ["[dim](Root)[/dim]", *route]
    console.print("\nNew Subspace route will be:", style="bright")
    console.print(" > ".join(route))
    print("")

    is_confirm = inquirer.confirm(
        message="Confirm",
        default=True,
        style=inquirer_style
    ).execute()
    if is_confirm:
        subspace_dict = omoospace.add_subspace(subspace_name, parent_dir)

        # TODO: report new adding route


@click.command('process')
@option_omoospace()
def cli_add_process():
    pass


@click.command('work')
@option_omoospace()
def cli_add_work():
    pass


@click.command('creator')
@option_omoospace()
def cli_add_creator():
    pass


@click.command('software')
@option_omoospace()
def cli_add_software():
    pass


cli_add.add_command(cli_add_subspace)
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


cli.add_command(cli_add)
cli.add_command(cli_create)
cli.add_command(cli_show)
cli.add_command(cli_to)
cli.add_command(cli_export)
cli.add_command(cli_import)

if __name__ == "__main__":
    cli()

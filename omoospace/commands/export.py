import click
from pathlib import Path
from InquirerPy import inquirer
from InquirerPy.validator import EmptyInputValidator
from prompt_toolkit.validation import ValidationError, Validator
from omoospace.ui import Board, Info, Table, Transfer

from omoospace.utils import format_name
from omoospace.commands.common import collect_item_prompt, option_omoospace, get_omoospace, inquirer_style
from omoospace.common import console


@click.command('export', help="Export new package.")
@option_omoospace()
@click.option(
    "-d", "--dst", type=click.Path(),
    help="The output path of Package"
)
def cli_export(omoospace, dst):
    omoospace = get_omoospace(omoospace)

    package_items: list[Path] = collect_item_prompt(
        omoospace.root_path, omoospace.is_omoospace_item)

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

    ui_items = Table("Name", "Path")
    for item in package_items:
        _abspath = str(Path(omoospace.root_path, item))
        _name = Path(_abspath).parts[-1]
        ui_items.add_row(_name, _abspath)

    export_path = Path(dst).resolve() if dst \
        else Path(omoospace.root_path, 'StagedData', 'Packages').resolve()
    package_path = Path(export_path, format_name(package_name)).resolve()
    console.print(Board(
        Info("Name", "%s [dim](%s)[/dim]" %
             (package_name, package_path)),
        Info("Description", package_description),
        Info("Version", package_version),
        Info("Items", ui_items),
        title="Export Package Form"
    ))

    is_confirm = inquirer.confirm(
        message="Sure",
        default=True,
        style=inquirer_style
    ).execute()
    if is_confirm:
        omoospace.export_package(
            items=package_items,
            export_dir=export_path,
            name=package_name,
            info=package_info
        )
        console.print("Successfully export! 📦", style="cheer")

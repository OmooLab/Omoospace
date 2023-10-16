import click
from InquirerPy import inquirer
from prompt_toolkit.validation import ValidationError, Validator

from omoospace.package import Package
from omoospace.commands.common import option_omoospace, get_omoospace, inquirer_style
from omoospace.ui import Board, Info
from omoospace.common import console


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
    console.print(Board(
        Info("Name", "%s [dim](%s)[/dim]" %
             (package.name, import_dir)),
        Info("Description", package.description),
        Info("Version", package.version),
        Info("Items", package.items),
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

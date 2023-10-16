import click
from pathlib import Path
from InquirerPy import inquirer
from InquirerPy.base import Choice
from prompt_toolkit.validation import ValidationError, Validator
from omoospace.ui import Board, Info

from omoospace.utils import format_name
from omoospace.omoospace import Omoospace
from omoospace.commands.common import inquirer_style, to_omoospace
from omoospace.setting import OmoospaceTemplate, Setting
from omoospace.common import console


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
    template_choices = [
        Choice(name="*Empty",value=-1),
        *[Choice(
        name="%s (%s)" % (template.name, template.description),
        value=id
    ) for id, template in enumerate(templates)]
    ]

    template_id: int = inquirer.select(
        message="Choose a template",
        choices=template_choices,
        style=inquirer_style,
    ).execute()

    while True:
        if template_id >=0:
            template = templates[template_id]
        else:
            template = OmoospaceTemplate()
        console.print(template.tree.render_tree())
        confirm_id: int = inquirer.select(
            message="Choose the same again to confirm",
            choices=template_choices,
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

    console.print(Board(
        Info("Name", "%s [dim](%s)[/dim]" %
             (omoospace_name, omoospace_path)),
        Info("Description", description),
        Info("Directory Tree", template.tree.render_tree()),
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

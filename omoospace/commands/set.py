import click
from pathlib import Path
import validators
from InquirerPy import inquirer
from InquirerPy.validator import EmptyInputValidator
from InquirerPy.base import Choice
from prompt_toolkit.validation import ValidationError, Validator

from omoospace.directory import DirectoryTree
from omoospace.setting import Setting
from omoospace.subspace import SubspaceTree
from omoospace.types import Creator, Software, Work
from omoospace.ui import Board, CreatorProfile, Info, Transfer
from omoospace.utils import find_first, format_name, is_subpath
from omoospace.omoospace import Omoospace
from omoospace.commands.common import collect_item_prompt, get_omoospace, option_omoospace, get_working_dir, inquirer_style, set_working_dir
from omoospace.common import console

SET_SUBSPACE_HELP = "Add or update subspace directory."
SET_PROCESS_HELP = "Add or update process directory."
SET_CREATOR_HELP = "Add or update creator."
SET_SOFTWARE_HELP = "Add or update software."
SET_WORK_HELP = "Add or update work filepath."


def _set_subspace(omoospace):
    omoospace: Omoospace = get_omoospace(omoospace)

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
    subspace_dirname = format_name(subspace_name)

    subspace_comment = inquirer.text(
        message="Enter a comment of this subspace (Optional)",
        style=inquirer_style
    ).execute()

    subspace_info = {
        "name": subspace_name,
        "comments": subspace_comment or None
    }

    subspace_path = Path(parent_dir, subspace_dirname).resolve()
    subspace_tree = SubspaceTree(search_dir=parent_dir)
    subspace_tree.add_entity(subspace_path)
    # TODO: display new subspace with true name not dirname only.
    console.print(Board(
        Info("Name", "%s [dim](%s)[/dim]" %
             (subspace_name, subspace_path)),
        Info("Comments", subspace_comment),
        Info("Subspace Tree", subspace_tree.render_tree()),
        title="Set Subspace Form"
    ))

    is_confirm = inquirer.confirm(
        message="Confirm",
        default=True,
        style=inquirer_style
    ).execute()
    if is_confirm:
        omoospace.set_subspace(
            subspace=subspace_info,
            parent_dir=parent_dir,
        )


def _set_process(omoospace):
    omoospace: Omoospace = get_omoospace(omoospace)

    class ProcessParentDirValidator(Validator):
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
        message="Enter process parent directory",
        only_directories=True,
        validate=ProcessParentDirValidator(),
        long_instruction='Press Tab to summon auto completer. \n'
        'Press Enter to confirm.',
        default=get_working_dir(),
        style=inquirer_style
    ).execute()
    set_working_dir(parent_dir)

    templates = Setting().process_templates
    template_choices = [
        Choice(name="*Custom", value=-1),
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

    if template_id >= 0:
        while True:
            template = templates[template_id]
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
        process_structure = template.structure
    else:
        process_name = inquirer.text(
            message="Enter process name",
            validate=EmptyInputValidator("Name cannot be empty."),
            style=inquirer_style
        ).execute()
        process_structure = {format_name(process_name): None}

    directory_tree = DirectoryTree()
    directory_tree.root_path = omoospace.sourcefiles_path
    directory_tree.from_structure(process_structure, parent_dir)

    console.print(Board(
        Info("Directory Tree", directory_tree.render_tree()),
        title="Set Subspace Form"
    ))

    is_confirm = inquirer.confirm(
        message="Confirm",
        default=True,
        style=inquirer_style
    ).execute()
    if is_confirm:
        omoospace.set_process(
            process=process_structure,
            parent_dir=parent_dir,
        )


def _set_creator(omoospace):
    omoospace: Omoospace = get_omoospace(omoospace)

    class EmailValidator(Validator):

        def validate(self, document):
            # Allow empty
            if not validators.email(document.text):
                raise ValidationError(
                    message="Invaild email address.",
                    cursor_position=document.cursor_position,
                )

    class WebsiteValidator(Validator):

        def validate(self, document):
            # Allow empty
            if len(document.text) > 0 and not validators.url(document.text):
                raise ValidationError(
                    message="Invaild website address.",
                    cursor_position=document.cursor_position,
                )
    registered_creators = Setting().registered_creators
    creator_choices = [
        Choice(name="*Register", value=-1),
        *[Choice(
            name="%s (%s)" % (creator.get("name"), creator.get("email")),
            value=id
        ) for id, creator in enumerate(registered_creators)]
    ]

    creator_id = inquirer.fuzzy(
        message="Choose from registered creators",
        choices=creator_choices,
        style=inquirer_style
    ).execute()

    if creator_id >= 0:
        creator_info = registered_creators[creator_id]
    else:
        creator_email = inquirer.text(
            message="Enter creator email",
            validate=EmailValidator(),
            style=inquirer_style
        ).execute()
        creator_info = find_first(registered_creators, "email", creator_email)
        if not creator_info:
            creator_name = inquirer.text(
                message="Enter creator name",
                validate=EmptyInputValidator("Name cannot be empty."),
                style=inquirer_style
            ).execute()
            creator_website = inquirer.text(
                message="Enter creator website (Optional)",
                validate=WebsiteValidator(),
                long_instruction='Start with "http(s)://".',
                style=inquirer_style
            ).execute()
            creator_info: Creator = {
                "name": creator_name,
                "email": creator_email or None,
                "website": creator_website or None,
            }
            registered_creators.append(creator_info)
            Setting().registered_creators = registered_creators
        else:
            console.print(
                "Found creator with this email in regitered.", style="warning")

    console.print(CreatorProfile(creator_info))
    role_choices = Setting().role_choices
    creator_role = inquirer.fuzzy(
        message="Enter creator role in this omoospace (Optional)",
        choices=["*NotInclude", *role_choices],
        style=inquirer_style
    ).execute()
    if creator_role == "*NotInclude":
        creator_role = inquirer.text(
            message="Enter role name",
            validate=EmptyInputValidator("Name cannot be empty."),
            style=inquirer_style
        ).execute()

    creator_info["role"] = creator_role or None

    is_confirm = inquirer.confirm(
        message="Confirm",
        default=True,
        style=inquirer_style
    ).execute()
    if is_confirm:
        role_choices.append(creator_role)
        Setting().role_choices = role_choices
        omoospace.set_creator(creator_info)


def _set_software(omoospace):
    omoospace: Omoospace = get_omoospace(omoospace)
    software_choices = Setting().software_choices
    software_name = inquirer.fuzzy(
        message="Choose from presets",
        choices=["*NotInclude", *software_choices],
        style=inquirer_style
    ).execute()
    if software_name == "*NotInclude":
        software_name = inquirer.text(
            message="Enter software name",
            validate=EmptyInputValidator("Name cannot be empty."),
            style=inquirer_style
        ).execute()

    software_version = inquirer.text(
        message="Enter software version (Optional)",
        style=inquirer_style
    ).execute()

    software_info: Software = {
        "name": software_name,
        "version": software_version or None,
        "plugins": None,
    }
    console.print(software_info)
    is_confirm = inquirer.confirm(
        message="Confirm",
        default=True,
        style=inquirer_style
    ).execute()
    if is_confirm:
        software_choices.append(software_name)
        Setting().software_choices = software_choices
        omoospace.set_software(software_info)


def _set_work(omoospace):
    omoospace: Omoospace = get_omoospace(omoospace)
    work_paths: list[Path] = collect_item_prompt(omoospace.contents_path)

    work_name = inquirer.text(
        message="Enter work name (Optional)",
        style=inquirer_style
    ).execute()

    work_info = {
        "name": work_name,
        "paths": work_paths
    }
    console.print(work_paths)
    is_confirm = inquirer.confirm(
        message="Confirm",
        default=True,
        style=inquirer_style
    ).execute()
    if is_confirm:
        omoospace.set_work(work_info)


@click.group(
    'set',
    help="Add or update stuffs to omoospace.",
    invoke_without_command=True
)
@click.option(
    "-s", "--subspace",
    is_flag=True,
    help=SET_SUBSPACE_HELP
)
@click.option(
    "-p", "--process",
    is_flag=True,
    help=SET_PROCESS_HELP
)
@click.option(
    "-c", "--creator",
    is_flag=True,
    help=SET_CREATOR_HELP
)
@click.option(
    "-so", "--software",
    is_flag=True,
    help=SET_SOFTWARE_HELP
)
@click.option(
    "-w", "--work",
    is_flag=True,
    help=SET_WORK_HELP
)
@option_omoospace()
@click.pass_context
def cli_set(ctx, subspace, process, creator, software, work, omoospace):
    if not ctx.invoked_subcommand:
        if subspace:
            _set_subspace(omoospace)
        elif process:
            _set_process(omoospace)
        elif creator:
            _set_creator(omoospace)
        elif software:
            _set_software(omoospace)
        elif work:
            _set_work(omoospace)
        else:
            console.print("set something")


@click.command('subspace', help=SET_SUBSPACE_HELP)
@option_omoospace()
def cli_set_subspace(omoospace):
    _set_subspace(omoospace)


@click.command('process', help=SET_PROCESS_HELP)
@option_omoospace()
def cli_set_process(omoospace):
    _set_process(omoospace)


@click.command('creator', help=SET_CREATOR_HELP)
@option_omoospace()
def cli_set_creator(omoospace):
    _set_creator(omoospace)


@click.command('software', help=SET_SOFTWARE_HELP)
@option_omoospace()
def cli_set_software(omoospace):
    _set_software(omoospace)


@click.command('work', help=SET_WORK_HELP)
@option_omoospace()
def cli_set_work(omoospace):
    _set_work(omoospace)


cli_set.add_command(cli_set_subspace)
cli_set.add_command(cli_set_process)
cli_set.add_command(cli_set_creator)
cli_set.add_command(cli_set_software)
cli_set.add_command(cli_set_work)

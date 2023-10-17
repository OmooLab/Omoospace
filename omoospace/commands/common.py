import click
from pathlib import Path
from InquirerPy import inquirer, get_style
from prompt_toolkit.validation import ValidationError, Validator

from omoospace.ui import Transfer
from omoospace.exceptions import InvalidError, NotFoundError
from omoospace.setting import Setting
from omoospace.types import PathLike
from omoospace.utils import is_subpath
from omoospace.common import console
from omoospace.omoospace import Omoospace


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
        help="Set the working omoospace path."
    )


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
    console.print("Current working at 🛠️ [bright]%s (%s)[/bright]." %
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


def collect_item_prompt(root_dir: PathLike, item_filter=None):
    root_path = Path(root_dir).resolve()

    class ItemValidator(Validator):
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

        def remove_prefix(string, prefix):
            for i in range(len(prefix)):
                end_index = len(prefix) - i
                sub_prefix = prefix[:end_index]
                new_string = string.removeprefix(sub_prefix)
                if new_string != string:
                    return new_string
            return string
        path_pattern = remove_prefix(path_pattern, str(root_path))
        path_pattern = path_pattern.removeprefix("\\")
        path_pattern = path_pattern.removeprefix("/")
        if path_pattern == "":
            return []
        items = sorted(root_path.glob(path_pattern))
        items = [item.resolve() for item in items]
        if item_filter:
            items = list(filter(item_filter, items))
        return items

    def print_items(pending, checked):
        pending = [item.relative_to(root_path)
                   for item in pending]
        checked = [item.relative_to(root_path)
                   for item in checked]
        transfer = Transfer(
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
            validate=ItemValidator(),
            default=str(root_path),
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

    return checked_items

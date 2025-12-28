from pathlib import Path

from omoospace.directory import DirectoryTree, Structure
from omoospace.exceptions import InvalidError
from omoospace.types import Creator, OmoospaceStructure
from omoospace.omoospace import Omoospace, OmoospaceTree
from omoospace.common import console, yaml


class OmoospaceTemplate():
    def __init__(
        self,
        name: str = None,
        description: str = None,
        structure: OmoospaceStructure = None
    ) -> None:
        self.name = name
        self.description = description
        self.structure = structure or {}
        self.tree = OmoospaceTree(structure=structure)


class ProcessTemplate():
    def __init__(
        self,
        name: str,
        description: str,
        structure: Structure = None
    ) -> None:
        self.name = name
        self.description = description
        self.structure = structure or {}
        self.tree = DirectoryTree(structure=structure)


class Setting():
    working_omoospace: str
    working_directory: str
    recent_omoospaces: list[str]
    omoospace_templates: list[OmoospaceTemplate]
    process_templates: list[ProcessTemplate]
    registered_creators: list[Creator]
    software_choices: list[str]
    role_choices: list[str]

    SETTING_PATH = "~/.omoospace/setting.yml"

    DEFAULT_SETTING = {
        "working_omoospace": None,
        "working_directory": None,
        "recent_omoospaces": None,
        "omoospace_templates": [
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
            {
                "name": "Asset Creation",
                "description": "Asset Creation Process",
                "structure": {
                    "001-Modeling": None,
                    "002-Texturing": None,
                    "003-Shading": None
                }
            },
            {
                "name": "Film Production",
                "description": "Film Production Process",
                "structure": {
                    "001-PreProduction": None,
                    "002-Production": None,
                    "003-PostProduction": None
                }
            }
        ],
        "registered_creators": [],
        "role_choices": [
            "Owner",
            "Menber",
        ],
        "software_choices": [
            "Blender",
            "Cinema4D",
            "Zbrush"
        ]
    }

    def __read_setting_file(self):
        setting: dict = {}
        setting_filepath = Path(self.SETTING_PATH).expanduser().resolve()
        if setting_filepath.exists():
            with setting_filepath.open('r', encoding='utf-8') as file:
                # aviod empty or invalid ifle
                setting = yaml.load(file) or {}
        return setting

    def __write_setting_file(self, setting):
        setting_filepath = Path(self.SETTING_PATH).expanduser().resolve()
        with setting_filepath.open('w', encoding='utf-8') as file:
            yaml.dump(setting, file)

    def __getattr__(self, key):
        if key not in self.__annotations__.keys():
            raise InvalidError(key, "key")
        setting = self.__read_setting_file()
        if (key == "omoospace_templates"):
            omoospace_templates = setting.get("omoospace_templates") or []
            omoospace_templates.extend(
                self.DEFAULT_SETTING["omoospace_templates"])
            return [OmoospaceTemplate(
                name=template.get('name'),
                description=template.get('description'),
                structure=template.get('structure')
            ) for template in omoospace_templates]
        elif (key == "process_templates"):
            process_templates = setting.get("process_templates") or []
            process_templates.extend(
                self.DEFAULT_SETTING["process_templates"])
            return [ProcessTemplate(
                name=template.get('name'),
                description=template.get('description'),
                structure=template.get('structure')
            ) for template in process_templates]
        elif (key == "software_choices"):
            software_choices = setting.get("software_choices") or []
            software_choices += list(
                set(self.DEFAULT_SETTING["software_choices"])
                - set(software_choices))
            return software_choices
        elif (key == "role_choices"):
            role_choices = setting.get("role_choices") or []
            role_choices += list(
                set(self.DEFAULT_SETTING["role_choices"])
                - set(role_choices))
            return role_choices
        else:
            return setting.get(key) or self.DEFAULT_SETTING.get(key)

    def __setattr__(self, key, value):
        if key not in self.__annotations__.keys():
            raise InvalidError(key, "key")
        setting = self.__read_setting_file()
        if (key == "software_choices"):
            value = list(
                set(value)
                - set(self.DEFAULT_SETTING["software_choices"]))
        if (key == "role_choices"):
            value = list(
                set(value)
                - set(self.DEFAULT_SETTING["role_choices"]))
        setting[key] = value
        self.__write_setting_file(setting)


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

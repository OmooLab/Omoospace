from pathlib import Path
from ruamel.yaml import YAML
from abc import ABC, abstractmethod
from omoospace.utils import remove_duplicates

yaml = YAML()
yaml.indent(sequence=4, offset=2)


class AttributeDict(ABC):
    @abstractmethod
    def _get_data(self, name):
        return None

    @abstractmethod
    def _set_data(self, name, value):
        pass

    def __getattr__(self, name):
        if name in self.__annotations__.keys():
            return self._get_data(name)
        else:
            return object.__getattribute__(self, name)

    def __setattr__(self, name, value):
        if name in self.__annotations__.keys():
            self._set_data(name, value)
        else:
            object.__setattr__(self, name, value)


class ProfileItem(AttributeDict):
    _item_list_key = 'items'
    _item_id_key = 'id'

    def __init__(self, dict: dict, container: 'ProfileContainer') -> None:
        self._dict = dict
        self._container = container

    def _get_data(self, name):
        return self._dict.get(name)

    def _set_data(self, name, value):
        identify = self._dict[self._item_id_key]
        self._dict[name] = value
        self._container._set_profile_data(self, identify)


class ProfileItemList():
    def __init__(self, item_list: list[ProfileItem]) -> None:
        self._item_list = item_list

    def set(
        self,
        data: ProfileItem,
        identify: str = None
    ):
        _item_id_key = data._item_id_key
        identify = identify or getattr(data, _item_id_key)

        index = self.__get_matched_index(_item_id_key, identify)

        if index >= 0:
            self._item_list[index] = data
        else:
            self._item_list.append(data)

    def __get_matched_index(
        self,
        key: str,
        value: any
    ):
        index = -1
        for i, data in enumerate(self._item_list):
            if getattr(data, key) == value:
                index = i
                break

        return index

    def to_dict_list(self):
        return [data._dict for data in self._item_list]

    def find(
        self,
        key: str,
        value: any
    ):
        index = self.__get_matched_index(key, value)

        if index >= 0:
            return self._item_list[index]
        else:
            return None


class ProfileContainer(AttributeDict):
    profile_path: Path = Path()

    def _read_profile_file(self):
        with self.profile_path.open('r', encoding='utf-8') as file:
            # aviod empty or invalid ifle
            profile = yaml.load(file) or {}
        return profile

    def _write_profile_file(self, profile):
        with self.profile_path.open('w', encoding='utf-8') as file:
            yaml.dump(profile, file)

    def _get_data(self, name):
        profile = self._read_profile_file()
        return profile.get(name)

    def _get_item_list(self, data_class):
        item_list_key = data_class._item_list_key
        item_id_key = data_class._item_id_key

        profile = self._read_profile_file()
        item_list = profile.get(item_list_key) or []

        # remove data that is not dict
        item_list = [data for data in item_list
                     if isinstance(data, dict)]

        # remove data that key value is None
        item_list = [data for data in item_list
                     if data.get(item_id_key)]

        # remove duplicates in key
        item_list = remove_duplicates(item_list, item_id_key)

        # reassign modified data
        self._set_data(item_list_key, item_list)

        # wrap dict into class
        return [data_class(data, self) for data in item_list]

    def _set_data(self, name, value):
        profile = self._read_profile_file()
        profile[name] = value
        self._write_profile_file(profile)

    def _set_profile_data(self, data: ProfileItem, identify: str = None):
        item_list_key = data._item_list_key

        item_list = ProfileItemList(getattr(self, item_list_key))
        item_list.set(data, identify)
        self._set_data(item_list_key, item_list.to_dict_list())

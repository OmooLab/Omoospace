

import os
from pathlib import Path
from typing import TypedDict
from nutree import Tree, Node
from enum import Enum

from omoospace.exceptions import InvalidError, NotFoundError
from omoospace.types import Entity, PathLike, Route
from omoospace.common import yaml
from omoospace.utils import format_name
from omoospace.validators import is_entity


class SubspaceProfile(TypedDict):
    name: str
    description: str


class SubspaceType(Enum):
    DIRECTORY = "directory"
    FILE = "file"
    PHANTOM = "phantom"
    DUMMY = "dummy"


class SubspaceData():
    def __init__(self, node_name: str):
        self.node_name = node_name
        self.entities: list[Entity] = []

    def __repr__(self):
        return self.node_name


class Subspace():
    name: str
    description: str

    def __init__(self, node: Node):
        self._node = node

    def __repr__(self):
        return self.node_name

    def __read_profile_file(self) -> SubspaceProfile:
        if self.profile_path.is_file():
            with self.profile_path.open('r', encoding='utf-8') as file:
                # aviod empty or invalid file
                profile = yaml.load(file) or {}
            return profile
        else:
            return {}

    def __write_profile_file(self, profile: SubspaceProfile):
        with self.profile_path.open('w', encoding='utf-8') as file:
            yaml.dump(profile, file)

    def __getattr__(self, name):
        if name in SubspaceProfile.__annotations__.keys():
            if self.type == SubspaceType.DUMMY:
                return None
            else:
                profile = self.__read_profile_file()
                return profile.get(name)
        else:
            return object.__getattribute__(self, name)

    def __setattr__(self, name, value):
        if name in SubspaceProfile.__annotations__.keys():
            if self.type == SubspaceType.DUMMY:
                pass
            else:
                profile = self.__read_profile_file()
                profile[name] = value
                self.__write_profile_file(profile)
        else:
            object.__setattr__(self, name, value)

    @property
    def profile_path(self):
        if self.type == SubspaceType.DIRECTORY:
            return Path(self.root_path, 'Subspace.yml').resolve()
        elif self.type != SubspaceType.DUMMY:
            entity = self.entities[0]
            node = self
            while True:
                parent = node.parent
                if not parent:
                    dir_parent = None
                    break
                elif parent.type == SubspaceType.DIRECTORY:
                    dir_parent = parent
                    break
                node = parent
            sub_route = self.route[len(
                dir_parent.route):] if dir_parent else self.route
            profile_filename = '%s.Subspace.yml' % "_".join(sub_route)
            return Path(entity.parent, profile_filename).resolve()
        else:
            return None

    @property
    def type(self):
        if len(self.entities) != 0:
            if len(self.endpoint_entities) != 0:
                if self.root_path:
                    return SubspaceType.DIRECTORY
                else:
                    return SubspaceType.FILE
            else:
                return SubspaceType.PHANTOM
        else:
            return SubspaceType.DUMMY

    @property
    def endpoint_entities(self):
        phantom_entities = []
        for entity in self.entities:
            node_names = format_name(entity.stem).split("_")
            if self.node_name == node_names[-1]:
                phantom_entities.append(entity)
        return phantom_entities

    @property
    def root_path(self) -> Path:
        for entity in self.entities:
            if entity.is_dir():
                return entity
        return None

    @property
    def entities(self):
        entities = self._node.data.entities

        def is_vaild(entity: Entity):
            exists = entity.exists()
            return exists

        # real file/directory only. remove those not exists.
        entities = list(filter(is_vaild, entities))
        self._node.data.entities = entities

        return entities

    @property
    def node_name(self) -> str:
        return self._node.data.node_name

    @property
    def parent(self) -> "Subspace":
        node = self._node.parent
        return Subspace(node) if node else None

    @property
    def route(self) -> Route:
        path = self._node.path
        return path.split("/")[1:]

    @property
    def children(self) -> list["Subspace"]:
        nodes = self._node.children
        return [Subspace(node) for node in nodes]

    def add_entity(self, *entities: Entity):
        for entity in entities:
            if entity not in self.entities:
                self._node.data.entities.append(entity)

    def add(self, node_name: str) -> "Subspace":
        node = self._node.add(SubspaceData(node_name))
        return Subspace(node)


class SubspaceTree():
    """The class of subspace tree.

    An subspace tree instance is always refer to a existed SourceFiles directory, not in ideal. 

    """

    def __init__(
        self,
        path: PathLike = None
    ):
        """Initialize the subspace tree from the given directory.

        Args:
            search_dir (PathLike): [description]
        """
        self._tree = Tree()
        if path:
            path = Path(path).resolve()
            if path.is_dir():
                self.from_dir(path)
            elif path.is_file():
                self.from_entity(path)
            else:
                NotFoundError()

    def from_dir(
        self,
        search_dir: PathLike,
        recursive: bool = True
    ):
        """Set the subspace tree from the given directory.

        Args:
            search_dir (PathLike): [description]
            recursive (bool, optional): [description]. Defaults to True.
        """
        entities = get_entities(search_dir, recursive=recursive)
        for entity in entities:
            self.from_entity(entity)

    def get(self, route: Route) -> Subspace:
        node = self._tree.find(
            match=lambda node: node.path == "/" + "/".join(route)
        )
        return Subspace(node) if node else None

    def add(self, node_name: str) -> Subspace:
        node = self._tree.add(SubspaceData(node_name))
        return Subspace(node)

    def to_dict(self) -> dict:
        def mapper(node: Node, data: dict):
            data['data'] = Subspace(node)
            return data
        return self._tree.to_dict_list(mapper=mapper)

    def from_entity(self, entity_path: PathLike) -> Node:
        """Add subspace node to the tree based on entity.

        The entity path must be real, not in ideal.

        Args:
            entity (Entity): [description]

        Returns:
            Route: List of subspace name along the route.

        Raises:
            InvalidError: entity path is invalid.
        """
        route_entities = get_route_entities(entity_path)

        node = self
        for i in range(len(route_entities)):
            d = route_entities[i]
            route = [d.get('node_name') for d in route_entities[:i+1]]
            node_name = d.get('node_name')
            entities = d.get('entities')
            subspace = self.get(route)
            if not subspace:
                subspace = node.add(node_name)
            subspace.add_entity(*entities)
            node = subspace


def get_entities(
    search_dir: PathLike,
    recursive: bool = True
) -> list[Entity]:
    """Add subspace node to the tree based on entity.

    Args:
        entity (Entity): [description]
    """
    search_path: Path = Path(search_dir).resolve()
    entities: list[Entity] = []
    if recursive:
        # FIXME: replace this with Path.walk (python 3.12)
        # https://docs.python.org/3/library/pathlib.html
        for root, dirs, files in os.walk(search_path):
            for path in [*dirs, *files]:
                child = Path(root, path).resolve()
                if is_entity(child):
                    entities.append(child)
    else:
        for child in search_path.iterdir():
            if is_entity(child):
                entities.append(child)
    return entities


def get_route_entities(entity_path: PathLike) -> list:
    # Check if input entity is vaild.
    entity = Path(entity_path).resolve()
    if not is_entity(entity):
        InvalidError(entity, 'entity')

    # Get relpath parts. remove those directory that is not entity.
    entities = [entity]
    for parent in entity.parents:
        if is_entity(parent):
            entities.append(parent)
    entities.reverse()

    # Generate route.
    route_entities = []
    for entity in entities:
        route: Route = [d.get('node_name') for d in route_entities]

        # format namespace
        entity_name = format_name(entity.stem)

        # node names are the strings that splited by "_" from entity name.
        # e.g. `SQ010_SH0100.blend` has two namespace: `SQ010` and `SH0100`
        node_names: list[str] = entity_name.split('_')

        # clip matched route names as mush as possible.
        # e.g. route: ['SQ010'], enity name: `SQ010_SH0100.blend`
        # `SQ010` is the matched namespace, which will be cliped.
        for i in range(len(route)):
            route_suffix = '_'.join(route[i:])
            node_prefix = '_'.join(node_names[:len(route) - i])
            if route_suffix == node_prefix:
                node_names = node_names[len(route) - i:]
                break

        # append node_name to route with entity
        for node_name in node_names:
            route_entities.append({
                'node_name': node_name,
                'entities': [entity]
            })

        # Sometimes all namspaces are cliped. but still need to append entity
        if len(node_names) == 0:
            route_entities[-1].get('entities').append(entity)

    return route_entities


def get_route(entity_path: PathLike) -> Route:
    """Returns a route to a entity path.

    Args:
        entity_path (PathLike): [description]

    Returns:
        Route: The list of route name of subspace.
    """
    route_entities = get_route_entities(entity_path)
    route: Route = [d.get('node_name') for d in route_entities]
    return route


def get_route_str(entity_path: PathLike, *subsets: str) -> Route:
    route = get_route(entity_path)
    route.extend(subsets)
    return "_".join(route)

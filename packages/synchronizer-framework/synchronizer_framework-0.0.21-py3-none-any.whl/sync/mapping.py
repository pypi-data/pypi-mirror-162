from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Tuple, Set, Union, Dict


class Mode(Enum):
    LEFT_TO_RIGHT = auto()
    RIGHT_TO_LEFT = auto()


class DirtyMode(Enum):
    DO_NOT_OVERWRITE = auto()
    UPDATE = auto()
    IGNORE = auto()


class AttributeMap:
    def __init__(
            self,
            from_attribute: Union[str, Tuple[str, ...]],
            to_attribute: Union[str, Tuple[str, ...]],
            from_attribute_type_hint: Union[str, Tuple[str, ...]] = None,
            to_attribute_type_hint: Union[str, Tuple[str, ...]] = None,
    ):
        self.from_attribute = from_attribute
        self.to_attribute = to_attribute
        self.from_attribute_type_hint = from_attribute_type_hint
        self.to_attribute_type_hint = to_attribute_type_hint

    def swapped(self):
        return AttributeMap(
            self.to_attribute,
            self.from_attribute,
            self.to_attribute_type_hint,
            self.from_attribute_type_hint,
        )

    def __repr__(self):
        return f"AttributeMap({self.from_attribute}:{self.from_attribute_type_hint},{self.to_attribute}:{self.to_attribute_type_hint})"


@dataclass
class Mapping:
    modes: Set[Mode] = field(default_factory=set)
    entity_types: Tuple[type, type] = field(default_factory=set)
    keys: Set[AttributeMap] = field(default_factory=set)
    attributes: Set[AttributeMap] = field(default_factory=set)
    create: bool = True
    delete_orphaned_entities: bool = False
    dirty_mode: DirtyMode = field(default=DirtyMode.IGNORE)
    dirty_attribute_name: str = "pending_update"
    left_conditions: Dict[str, type] = field(default_factory=dict)
    right_conditions: Dict[str, type] = field(default_factory=dict)

    def swapped(self):
        if Mode.RIGHT_TO_LEFT not in self.modes:
            raise SwapUnsupported()

        return Mapping(
            self.modes,
            (self.entity_types[1], self.entity_types[0]),
            {key.swapped() for key in self.keys},
            {attribute.swapped() for attribute in self.attributes},
            self.create,
            self.delete_orphaned_entities,
            self.dirty_mode,
            self.dirty_attribute_name,
            left_conditions=self.right_conditions,
            right_conditions=self.left_conditions,
        )

    def from_paths(self):
        return {key.from_attribute for key in self.keys}.union(
            {attribute.from_attribute for attribute in self.attributes}
        )


class SwapUnsupported(Exception):
    pass

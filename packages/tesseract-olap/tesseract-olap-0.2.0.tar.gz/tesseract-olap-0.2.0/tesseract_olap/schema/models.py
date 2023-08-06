import logging
from dataclasses import dataclass, field
from typing import List, Mapping, Optional, Tuple, TypeVar, Union

import immutables as immu

from tesseract_olap.common.captions import get_localization

from .aggregators import Aggregator, Count
from .enums import DimensionType, MemberType

logger = logging.getLogger(__name__)

# Named types
Annotations = Mapping[str, Optional[str]]
CaptionSet = Mapping[str, str]
T = TypeVar("T")


@dataclass(eq=True, frozen=True)
class Schema:
    """Base Schema class."""

    name: str
    annotations: Annotations = field(default_factory=immu.Map)
    cube_map: Mapping[str, "Cube"] = field(default_factory=immu.Map)
    default_locale: str = "xx"
    # TODO: implement role permissions model
    shared_dimension_map: Mapping[str, "Dimension"] = field(default_factory=immu.Map)
    shared_table_map: Mapping[str, "InlineTable"] = field(default_factory=immu.Map)

    @classmethod
    def join(cls, *args: "Schema"):
        annotations = {}
        cube_map = {}
        shared_dimension_map = {}
        shared_table_map = {}

        for sch in args:
            annotations.update(sch.annotations)
            cube_map.update(sch.cube_map)
            shared_dimension_map.update(sch.shared_dimension_map)
            shared_table_map.update(sch.shared_table_map)

        return cls(
            name=next(item.name for item in args if item.name != ""),
            default_locale=next((item.default_locale for item in args), "xx"),
            annotations=annotations,
            cube_map=cube_map,
            shared_dimension_map=shared_dimension_map,
            shared_table_map=shared_table_map,
        )


# TODO: Consider to use a DataFrame directly here
@dataclass(eq=True, frozen=True)
class InlineTable:
    alias: str
    columns: Mapping[str, "InlineTableColumn"] = field(default_factory=immu.Map)
    rows: Tuple["InlineTableRow"] = field(default_factory=tuple)


@dataclass(eq=True, frozen=True)
class InlineTableColumn:
    name: str
    key_type: MemberType
    locale: Optional[str] = None


@dataclass(eq=True, frozen=True)
class InlineTableRow:
    values: immu.Map[str, str]


class Entity:
    name: str
    annotations: Annotations
    captions: CaptionSet

    def get_annotation(self, name: str) -> Optional[str]:
        """Retrieves an annotation for the entity.
        If the annotation is not defined, raises a :class:`KeyError`.
        """
        return self.annotations[name]

    def get_caption(self, locale: str = "xx") -> str:
        """Retrieves the caption of the entity for a certain locale.
        If the a caption hasn't been defined for said locale, will attempt to
        return the fallback caption, and if not defined either, will return the
        entity name.
        """
        caption = get_localization(self.captions, locale)
        return self.name if caption is None else caption

    def get_locale_available(self) -> List[str]:
        """Retrieves the list of locales for whose a caption has been defined in
        this entity.
        """
        return sorted(self.captions.keys())


@dataclass(eq=True, frozen=True)
class Cube(Entity):
    name: str
    table: "Table"
    annotations: Annotations = field(default_factory=immu.Map)
    captions: CaptionSet = field(default_factory=immu.Map)
    dimension_map: Mapping[str, Union["Dimension", "DimensionUsage"]] \
        = field(default_factory=immu.Map)
    measure_map: Mapping[str, "Measure"] = field(default_factory=immu.Map)


@dataclass(eq=True, frozen=True)
class Table:
    name: str
    primary_key: str = "id"
    schema: Optional[str] = None


@dataclass(eq=True, frozen=True)
class Dimension(Entity):
    name: str
    annotations: Annotations = field(default_factory=immu.Map)
    captions: CaptionSet = field(default_factory=immu.Map)
    dim_type: DimensionType = DimensionType.STANDARD
    foreign_key: Optional[str] = None
    hierarchy_map: Mapping[str, "Hierarchy"] = field(default_factory=immu.Map)

    @property
    def default_hierarchy(self):
        return next(item for item in self.hierarchy_map.values())


@dataclass(eq=True, frozen=True)
class Hierarchy(Entity):
    name: str
    primary_key: str
    table: Union["InlineTable", "Table", str, None]
    annotations: Annotations = field(default_factory=immu.Map)
    captions: CaptionSet = field(default_factory=immu.Map)
    default_member: Optional[str] = None
    level_map: Mapping[str, "Level"] = field(default_factory=immu.Map)


@dataclass(eq=True, frozen=True)
class Level(Entity):
    name: str
    depth: int
    key_column: str
    annotations: Annotations = field(default_factory=immu.Map)
    captions: CaptionSet = field(default_factory=immu.Map)
    name_column_map: CaptionSet = field(default_factory=immu.Map)
    key_type: MemberType = MemberType.STRING
    property_map: Mapping[str, "Property"] = field(default_factory=immu.Map)

    def get_name_column(self, locale: str = "xx") -> Optional[str]:
        return get_localization(self.name_column_map, locale)

    def get_locale_available(self) -> List[str]:
        return sorted(set(self.captions.keys()).union(self.name_column_map.keys()))


@dataclass(eq=True, frozen=True)
class Property(Entity):
    name: str
    annotations: Annotations = field(default_factory=immu.Map)
    captions: CaptionSet = field(default_factory=immu.Map)
    key_column_map: immu.Map[str, str] = field(default_factory=immu.Map)
    key_type: MemberType = MemberType.STRING

    def get_key_column(self, locale: str = "xx") -> str:
        return get_localization(self.key_column_map, locale, force=True)

    def get_locale_available(self) -> List[str]:
        return sorted(set(self.captions.keys()).union(self.key_column_map.keys()))


@dataclass(eq=True, frozen=True)
class Measure(Entity):
    name: str
    key_column: str
    aggregator: Aggregator = field(default_factory=Count)
    annotations: Annotations = field(default_factory=immu.Map)
    captions: CaptionSet = field(default_factory=immu.Map)
    submeasures: Mapping[str, "SubMeasure"] = field(default_factory=immu.Map)


@dataclass(eq=True, frozen=True)
class SubMeasure(Entity):
    name: str
    aggregator: Aggregator = field(default_factory=Count)
    captions: CaptionSet = field(default_factory=immu.Map)


class Usage(Entity):
    """Defines a base class for Usage entities, so the type checker can enforce
    a bound class as a parameter.
    """
    source: str


@dataclass(eq=True, frozen=True)
class DimensionUsage(Usage):
    """Defines an usage of a :class:`Schema`-level :class:`SharedDimension`
    inside a :class:`Cube`.
    """
    name: str
    source: str
    foreign_key: str
    annotations: Annotations = field(default_factory=immu.Map)
    captions: CaptionSet = field(default_factory=immu.Map)
    hierarchy_map: Mapping[str, "HierarchyUsage"] = field(default_factory=immu.Map)


@dataclass(eq=True, frozen=True)
class HierarchyUsage(Usage):
    """Defines an usage of a :class:`Hierarchy` from a inside of a
    :class:`SharedDimension`, in a :class:`DimensionUsage`.
    """
    name: str
    source: str
    annotations: Annotations = field(default_factory=immu.Map)
    captions: CaptionSet = field(default_factory=immu.Map)
    level_map: Mapping[str, "LevelUsage"] = field(default_factory=immu.Map)


@dataclass(eq=True, frozen=True)
class LevelUsage(Usage):
    """Defines an usage of a :class:`Level` from a inside of a
    :class:`SharedDimension`, in a :class:`HierarchyUsage`.
    """
    name: str
    source: str
    annotations: Annotations = field(default_factory=immu.Map)
    captions: CaptionSet = field(default_factory=immu.Map)
    property_map: Mapping[str, "PropertyUsage"] = field(default_factory=immu.Map)


@dataclass(eq=True, frozen=True)
class PropertyUsage(Usage):
    """Defines an usage of a :class:`Property` from a inside of a
    :class:`SharedDimension`, in a :class:`LevelUsage`.
    """
    name: str
    source: str
    annotations: Annotations = field(default_factory=immu.Map)
    captions: CaptionSet = field(default_factory=immu.Map)

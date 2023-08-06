"""Query-related data-handling models module.

This module contains data structs used to carry and compose objects used during
a Query. The elements are agnostic to the type of backend used, and its primary
purpose is organize and easily obtain the data needed for later steps.
"""

from collections import defaultdict
from dataclasses import dataclass, field
from typing import (Any, Dict, List, Mapping, Optional, Sequence, Set, Tuple,
                    Union)

import immutables as immu

from tesseract_olap.schema import (CubeTraverser, DimensionTraverser,
                                   HierarchyTraverser, LevelTraverser,
                                   SchemaTraverser)

from .enums import LogicOperator, RestrictionScale
from .exceptions import InvalidEntityName
from .models import (HierarchyField, LevelField, MeasureField,
                     PaginationIntent, SortingIntent)
from .requests import DataRequest, MembersRequest


@dataclass(eq=False, order=False)
class DataQuery:
    """Internal DataQuery class.

    Contains all the schema-hydrated elements corresponding to a
    :class:`DataRequest`, but also joining properties related to the same
    columnar entities.
    """

    cube: "CubeTraverser"
    locale: str
    fields_qualitative: Tuple["HierarchyField", ...] = field(default_factory=tuple)
    fields_quantitative: Tuple["MeasureField", ...] = field(default_factory=tuple)
    options: Mapping[str, bool] = field(default_factory=dict)
    pagination: "PaginationIntent" = field(default_factory=PaginationIntent)
    parents: Union[bool, Set[str]] = False
    sorting: Optional["SortingIntent"] = None

    @classmethod
    def from_request(cls, schema: "SchemaTraverser", request: "DataRequest"):
        """Generates a new :class:`Query` instance from the parameters defined
        in a :class:`DataRequest` object.

        If any of the parameters can't be found on the Schema, raises a derivate
        of the :class:`InvalidQuery` error.
        """
        cube = schema.get_cube(request.cube)

        return cls(
            cube=cube,
            fields_qualitative=_get_data_hierarfields(cube, request),
            fields_quantitative=_get_data_measurefields(cube, request),
            locale=schema.default_locale \
                   if request.locale is None else \
                   request.locale,
            options=request.options,
            pagination=request.pagination,
            parents=request.parents,
            sorting=request.sorting,
        )

    def get_sources(self) -> Sequence[Dict[str, Any]]:
        """Returns a sequence containing the sources for each measure in the Query.

        Only measures with a properly declared source will appear in this dict.
        """
        source = {
            "name": self.cube.name,
            "measures": [item.name for item in self.fields_quantitative if item.is_measure],
            "annotations": self.cube.annotations,
        }
        return (source,)


@dataclass(eq=False, order=False)
class MembersQuery:
    """Internal MembersQuery class."""

    cube: "CubeTraverser"
    hiefield: "HierarchyField"
    locale: str
    pagination: "PaginationIntent" = field(default_factory=PaginationIntent)
    search: Optional[str] = None

    @classmethod
    def from_request(cls, schema: "SchemaTraverser", request: "MembersRequest"):
        """Generates a new :class:`MembersQuery` instance from a user-provided
        :class:`MembersRequest` instance.
        """
        cube = schema.get_cube(request.cube)

        return cls(
            cube=cube,
            hiefield=_get_members_hierarfield(cube, request),
            locale=schema.default_locale \
                   if request.locale is None else \
                   request.locale,
            pagination=request.pagination,
            search=request.search,
        )


def _get_data_hierarfields(cube: "CubeTraverser", req: "DataRequest"):
    """Regroups query parameters related to a Level, to simplify later usage."""
    # we need a map with all possible levels, including the cube's shared dimensions
    level_map = immu.Map((level.name, (dimension, hierarchy, level))
                         for dimension in cube.dimensions
                         for hierarchy in dimension.hierarchies
                         for level in hierarchy.levels)

    drilldown_set = req.drilldowns
    property_set = req.properties
    caption_set = req.captions
    with_parents = req.parents

    involved_levels = req.drilldowns.copy()
    involved_levels.update(item.level for item in req.cuts.values())

    time_level = None
    time_restr = req.time_restriction
    if time_restr is not None:
        granularity = time_restr.level
        time_level = (
            cube.get_time_level(granularity.value)
            if isinstance(granularity, RestrictionScale) else
            cube.get_time_level(granularity)
        )
        involved_levels.add(time_level.name)

    dimension_store: Mapping[DimensionTraverser, HierarchyTraverser] = {}
    hierarchy_store: Mapping[HierarchyTraverser, List[LevelTraverser]] = defaultdict(list)

    for name in involved_levels:
        dimension, hierarchy, level = level_map[name]
        if dimension_store.get(dimension, hierarchy) != hierarchy:
            raise ValueError("Multiple Hierarchies from the same Dimension are being requested. Only a single Hierarchy can be used at a time for a query.")
        dimension_store[dimension] = hierarchy
        hierarchy_store[hierarchy].append(level)

    def _compose_field(level: "LevelTraverser", is_drilldown: bool) -> "LevelField":
        """Capsules the logic to fill a LevelField instance with data from both
        a Drilldown and a Cut.
        """
        kwargs = {
            "is_drilldown": is_drilldown,
            "properties": frozenset(prop
                                    for prop in level.properties
                                    if prop.name in property_set),
            "caption": next((capt
                            for capt in level.properties
                            if capt.name in caption_set), None),
            "time_restriction": time_restr if time_level == level else None,
        }

        cut = req.cuts.get(level.name)
        if cut is not None:
            kwargs["members_exclude"] = set(cut.exclude_members)
            kwargs["members_include"] = set(cut.include_members)

        return LevelField(level=level, **kwargs)

    def _resolve_fields(hierarchy: "HierarchyTraverser"):
        """Calculates the levels involved in the request, depending on the
        with_parent parameter.
        """
        involved_levels = hierarchy_store[hierarchy]
        fields: List[LevelField] = []

        parent_flag = False
        # iterations will be done in reverse to use a flag for parents
        for level in reversed(tuple(hierarchy.levels)):
            # if includes_parents, and a deeper level is drilldown,
            # or if it's explicitly a drilldown
            is_drilldown = parent_flag or level.name in drilldown_set
            # is_field means the level needs to be SELECTed
            # to be used as a foreign key for a drilldown or a cut
            is_field = is_drilldown or level in involved_levels
            if is_field:
                fields.append(_compose_field(level, is_drilldown))
            # if level is marked in parents, raise flag
            parent_flag = parent_flag or (
                with_parents is True or
                (with_parents is not False and level.name in with_parents)
            )

        fields.reverse()
        return tuple(fields)

    return tuple(
        HierarchyField(dimension, hierarchy, columns=_resolve_fields(hierarchy))
        for dimension, hierarchy in (
            sorted(dimension_store.items(), key=lambda item: item[0].name)
        )
    )


def _get_data_measurefields(cube: "CubeTraverser", req: "DataRequest"):
    """Regroups query parameters related to a Measure, to simplify contextual use.
    """
    measure_set = req.measures

    involved_measures = req.measures.copy()
    involved_measures.update(item.field for item in req.filters.values())

    def _compose_field(measure_name: str) -> "MeasureField":
        measure = cube.get_measure(measure_name)
        kwargs = {
            "is_measure": measure_name in measure_set,
            "constraint1": None,
        }

        fltr = req.filters.get(measure_name)
        if fltr is None:
            pass
        elif len(fltr.condition) == 2: # is NumericConstraint
            kwargs["constraint1"] = fltr.condition
        elif len(fltr.condition) == 3: # is (NumConstr, LogicOp, NumConstr)
            kwargs["constraint1"] = fltr.condition[0]
            kwargs["joint"] = LogicOperator.from_str(fltr.condition[1])
            kwargs["constraint2"] = fltr.condition[2]

        return MeasureField(measure, **kwargs)

    return tuple(_compose_field(measure) for measure in involved_measures)


def _get_members_hierarfield(cube: "CubeTraverser", req: "MembersRequest"):
    """Regroups query parameters related to a Level, to simplify later usage."""
    level_name = req.level
    with_parents = req.options.get("parents", False)

    try:
        dimension, hierarchy, level = next((dimension, hierarchy, level)
                                           for dimension in cube.dimensions
                                           for hierarchy in dimension.hierarchies
                                           for level in hierarchy.levels
                                           if level.name == level_name)
    except StopIteration:
        raise InvalidEntityName("Level", level_name) from None

    if with_parents:
        levels = tuple(hierarchy.levels)
        last_index = levels.index(level)
        fields = tuple(LevelField(level) for level in levels[0:last_index])
    else:
        fields = LevelField(level),

    return HierarchyField(dimension, hierarchy, columns=fields)

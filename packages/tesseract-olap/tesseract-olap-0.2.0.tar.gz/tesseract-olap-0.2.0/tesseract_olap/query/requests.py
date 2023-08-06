"""Requests module.

Contains structs to build a :class:`DataRequest` instance: an object to describe
the parameters needed for the query using only entity names and relationships.
"""

import collections.abc
from dataclasses import dataclass, field
from itertools import chain
from typing import Mapping, Optional, Sequence, Set, Tuple, Union

from typing_extensions import Literal, TypedDict

from .models import (CutIntent, FilterCondition, FilterIntent,
                     PaginationIntent, SortingIntent, TimeRestriction)


class DataRequestOptionalParams(TypedDict, total=False):
    """Defines the optional parameters in the DataRequestParams interface.

    Is a separate class is due to the implementation of the
    [Totality](https://www.python.org/dev/peps/pep-0589/#totality) in the
    :class:`TypedDict` class.

    This will give a better hint to the type checker when the user makes use of
    this interface.
    """
    captions: Sequence[str]
    cuts_exclude: Mapping[str, Sequence[Union[str, int]]]
    cuts_include: Mapping[str, Sequence[Union[str, int]]]
    filters: Mapping[str, FilterCondition]
    locale: str
    pagination: Tuple[int, int]
    parents: Union[bool, Sequence[str], Set[str]]
    properties: Sequence[str]
    sorting: Tuple[str, Literal["asc", "desc"]]
    time: str


class DataRequestParams(DataRequestOptionalParams, total=True):
    """DataRequestParams interface.

    Determines the expected params in a :class:`dict`, to use when creating a
    new :class:`DataRequest` object via the :func:`DataRequest.new` class method.
    """
    drilldowns: Sequence[str]
    measures: Sequence[str]


@dataclass(eq=False, order=False)
class DataRequest:
    """Represents the intent for a Data Query made by the user.

    All its properties are defined by strings of the names of the components
    from the schema.
    None of these parameters are verified during construction, so it's possible
    the query results in to be invalid. The only purpose of this structure is
    containing and passing this query intent.

    During a request, a :class:`Query` instance is constructed with objects from
    a schema, using parameters from this instance.
    """

    cube: str
    drilldowns: Set[str]
    measures: Set[str]
    captions: Set[str] = field(default_factory=set)
    cuts: Mapping[str, "CutIntent"] = field(default_factory=dict)
    filters: Mapping[str, "FilterIntent"] = field(default_factory=dict)
    locale: Optional[str] = None
    options: Mapping[str, bool] = field(default_factory=dict)
    pagination: "PaginationIntent" = field(default_factory=PaginationIntent)
    parents: Union[bool, Set[str]] = False
    properties: Set[str] = field(default_factory=set)
    sorting: Optional["SortingIntent"] = None
    time_restriction: Optional["TimeRestriction"] = None

    @classmethod
    def new(cls, cube: str, request: DataRequestParams):
        """Creates a new :class:`DataRequest` instance from a set of parameters
        defined in a dict.

        This should be the preferred method by final users, as it doesn't
        require the use of internal dataclasses and the setup of internal
        structures and unique conditions.
        """

        cuts_include = request.get("cuts_include", {})
        cuts_exclude = request.get("cuts_exclude", {})
        filters = request.get("filters", {})

        kwargs = {
            "locale": request.get("locale"),
            "cuts": {
                item: CutIntent.new(level=item,
                                    incl=cuts_include.get(item, []),
                                    excl=cuts_exclude.get(item, []))
                for item in frozenset(
                    chain(cuts_include.keys(), cuts_exclude.keys())
                )
            },
            "filters": {
                item: FilterIntent(item, constraint)
                for item, constraint in filters.items()
            },
            "captions": set(request.get("captions", [])),
            "properties": set(request.get("properties", [])),
            "options": {},
        }

        item = request.get("pagination", (0, 0))
        if isinstance(item, str):
            kwargs["pagination"] = PaginationIntent.from_str(item)
        elif isinstance(item, collections.abc.Sequence):
            kwargs["pagination"] = PaginationIntent(*item)

        item = request.get("parents", False)
        if isinstance(item, (set, bool)):
            kwargs["parents"] = item
        elif isinstance(item, collections.abc.Sequence):
            kwargs["parents"] = set(item)

        item = request.get("sorting")
        if isinstance(item, str):
            kwargs["sorting"] = SortingIntent.from_str(item)
        elif isinstance(item, collections.abc.Sequence):
            kwargs["sorting"] = SortingIntent.new(*item)

        # TODO: maybe these should be checked against Iterable/__getindex__?

        item = request.get("time")
        if isinstance(item, str):
            kwargs["time_restriction"] = TimeRestriction.from_str(item)

        return cls(cube=cube,
                   drilldowns=set(request["drilldowns"]),
                   measures=set(request["measures"]),
                   **kwargs)


class MembersRequestOptionalParams(TypedDict, total=False):
    """Defines the optional parameters in the MembersRequestParams interface.

    Is a separate class is due to the implementation of the
    [Totality](https://www.python.org/dev/peps/pep-0589/#totality) in the
    :class:`TypedDict` class.

    This will give a better hint to the type checker when the user makes use of
    this interface.
    """
    locale: str
    pagination: Tuple[int, int]
    search: str


class MembersRequestParams(MembersRequestOptionalParams, total=True):
    """MembersRequestParams interface.

    Determines the expected params in a :class:`dict`, to use when creating a
    new :class:`MembersRequest` object via the :func:`MembersRequest.new` class
    method.
    """
    level: str


@dataclass(eq=False, order=False)
class MembersRequest:
    """Represents the intent for a Level Metadata Query made by the user.

    Parameters are constructed with primitives that describe the entities being
    requested.

    It is suggested to use the :func:`MembersRequest.new` method to create a new
    instance of this class, instead of calling a new instance directly.
    """

    cube: str
    level: str
    locale: Optional[str] = None
    options: Mapping[str, bool] = field(default_factory=dict)
    pagination: "PaginationIntent" = field(default_factory=PaginationIntent)
    search: Optional[str] = None

    @classmethod
    def new(cls, cube: str, request: MembersRequestParams):
        """Creates a new :class:`MembersRequest` instance from a set of parameters
        defined in a dict.

        This should be the preferred method by final users, as it doesn't
        require the use of internal dataclasses and the setup of internal
        structures and unique conditions.
        """

        item = request.get("pagination", (0, 0))
        pagination = PaginationIntent(*item)

        return cls(
            cube=cube,
            level=request["level"],
            locale=request.get("locale"),
            options={
                "parents": request.get("parents", False),
                "children": request.get("children", False),
            },
            pagination=pagination,
            search=request.get("search"),
        )

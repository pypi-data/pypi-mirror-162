from typing import Dict, List, Optional, Tuple, Union

from fastapi import Depends, Query, Request
from typing_extensions import Literal

from tesseract_olap.query import (DataRequest, DataRequestParams,
                                  MembersRequest, MembersRequestParams)


def query_cuts_include(request: Request):
    """FastAPI Dependency to parse including cut parameters.

    Parses all URL Search Params whose key is capitalized, as cut definitions.
    Values are members' IDs, separated by commas.
    """
    return {key: value.split(",")
            for key, value in request.query_params.items()
            if key[0].isupper()}


def query_cuts_exclude(exclude: str = ""):
    """FastAPI Dependency to parse excluding cut parameters.

    The value is composed by multiple cut definitions separated by semicolons:
        `{value}` := `{cut_def};{cut_def...}`
    Where a single cut definition is composed by the Level name, colon, and the
    list of keys separated by commas:
        `{cut_def}` := `{name}:{key},{key...}`
        `{name}` : `str`, the name of the Level to apply the cut
        `{key}` : `str | int`, the members' ID values
    """
    return {key: value.split(",")
            for key, value in (
                item.split(":")[:2]
                for item in exclude.split(";")
                if item != ""
            )}


def query_pagination(limit: Optional[str] = None):
    """FastAPI Dependency to parse pagination parameters.

    The shape of the parameter is composed by one integer, or two integers
    separated by a comma:
        `{value}` := `{limit}` | `{limit},{offset}`
    Where:
        `{limit}` : `int`, defines the max amount of items in the response data
        `{offset}` : `int`, defines the index of the first item in the full list
                     where the list in the response data will start
    """
    return None if limit is None else tuple(int(i) for i in limit.split(",")[:2])


def query_parents(parents: str = ""):
    """FastAPI Dependency to parse parent drilldown call parameters.

    The shape for the value is:
        `{value}` := `{truthy}` | `{falsey}` | `{name},{name...}`
    Where:
        `{truthy}` : `Literal["1", "true", "on", "yes"]`, retrieves parents for
        all drilldowns in the request
        `{falsey}` : `Literal["", "0", "false", "off", "no"]`, deactivates
        parents for all drilldowns in the request (default)
        `{name}` : `str`, the name of the specific drilldown(s) to get parents for.
    """
    if parents.lower() in ("", "0", "false", "off", "no"):
        return False
    if parents.lower() in ("1", "true", "on", "yes"):
        return True
    return parents.split(",")


def query_sorting(sort: Optional[str] = None):
    """FastAPI Dependency to parse sorting parameters.

    The shape for the value is:
        `{value}` := `{field}` | `{field}.{order}`
    Where:
        `{field}` : `str`, defines the field to use: a Measure or Property
        `{order}` : `Literal["asc", "desc"]`, defines the order to use

    The field will be resolved to a Measure first, then a Property.
    When `{order}` is not set, `"asc"` will be used.
    """
    if sort is None:
        return None
    params = sort.split(".")
    order = (params[1] if len(params) > 1 else "asc").lower()
    return params[0], order if order in ("asc", "desc") else "asc"


def dataquery_params(
    cube_name: str = Query(..., alias="cube"),
    drilldowns: str = Query(...),
    measures: str = Query(...),
    properties: Optional[str] = None,
    cuts_include: Dict[str, List[str]] = Depends(query_cuts_include),
    cuts_exclude: Dict[str, List[str]] = Depends(query_cuts_exclude),
    locale: Optional[str] = None,
    limit: Optional[Tuple[int, int]] = Depends(query_pagination),
    sorting: Optional[Tuple[str, Literal["asc", "desc"]]] = Depends(query_sorting),
    time: Optional[str] = None,
    parents: Union[bool, List[str]] = Depends(query_parents),
):
    """FastAPI Dependency to parse parameters into a DataRequest object.
    """
    params: DataRequestParams = {
        "drilldowns": [item.strip() for item in drilldowns.split(",")],
        "measures": [item.strip() for item in measures.split(",")],
        "parents": parents,
        "cuts_include": cuts_include,
        "cuts_exclude": cuts_exclude,
    }

    if locale is not None:
        params["locale"] = locale

    if properties is not None:
        params["properties"] = properties.split(",")

    if time is not None:
        params["time"] = time

    if limit is not None:
        params["pagination"] = limit

    if sorting is not None:
        params["sorting"] = sorting

    return DataRequest.new(cube_name, params)


def membersquery_params(
    cube_name: str = Query(..., alias="cube"),
    level: str = Query(...),
    locale: Optional[str] = None,
    search: str = "",
    limit: Optional[Tuple[int, int]] = Depends(query_pagination),
):
    """FastAPI Dependency to parse parameters into a MembersRequest object.
    """
    params: MembersRequestParams = {
        "level": level,
    }

    if locale is not None:
        params["locale"] = locale

    if limit is not None:
        params["pagination"] = limit

    if search != "":
        params["search"] = search

    return MembersRequest.new(cube_name, params)

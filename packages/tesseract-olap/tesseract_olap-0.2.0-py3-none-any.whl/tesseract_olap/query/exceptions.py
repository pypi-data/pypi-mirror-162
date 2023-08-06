"""Query exceptions module.

The errors in this module refer to problems during the retrieval of data from
the backend, but happening at the core side of the code.
"""

from typing import Optional

from tesseract_olap.common import BaseError


class QueryError(BaseError):
    """Base class for exceptions in this module."""


class InvalidQuery(QueryError):
    """This error occurs when a query is misconstructed.

    Can be raised before or after a request is made against a data server.
    """


class InvalidParameter(InvalidQuery):
    """This error occurs when a parameter in the query is incorrectly set before
    any data validation happens. This includes parameters with the wrong type.

    As this is entirely an user issue, should be informed to the user, but not
    necessarily to the administrator.
    """

    def __init__(self, param: str, detail: Optional[str]) -> None:
        super().__init__(
            f"Query parameter '{param}' set incorrectly" +\
            ("" if detail is None else f": {detail}")
        )


class InvalidEntityName(InvalidQuery):
    """This error occurs when a query asks for an object missing in the schema.
    """

    def __init__(self, node: str, name: str) -> None:
        super().__init__(
            f"Failed attempt to get a {node} object with name '{name}': "
            f"Entity doesn't exist"
        )


class TimeDimensionUnavailable(InvalidQuery):
    """This error occurs when a query asks for a time restriction, but the Cube
    doesn't contain a Dimension whose type is "time".

    On an information level this should be informed to the user, and in a debug
    level should be reported to the administrator to check if there's a issue
    with the schema.
    """

    def __init__(self, cube_name: str) -> None:
        super().__init__(
            f"Cube '{cube_name}' doesn't contain a declared time dimension."
        )


class TimeScaleUnavailable(InvalidQuery):
    """This error occurs when a query asks for a specific time granularity which
    is not configured in the levels of any hierarchy in the selected dimension.
    """

    def __init__(self, cube_name: str, scale: str) -> None:
        super().__init__(
            f"Cube '{cube_name}' dimensions' don't contain a level matching the"
            f" {scale} granularity"
        )


class EmptyResult(QueryError):
    """This exception occurs when a query against a server returns an empty
    dataset.

    This might want to be caught and reported to the administrator.
    """


class InvalidFormat(QueryError):
    """This error occurs when a format used to retrieve data is not supported by
    the upstream server.

    Should be raised before the target url to contact with the upstream server
    is built.
    """

    def __init__(self, extension: str) -> None:
        super().__init__(
            f"Format '{extension}' is not supported by the server."
        )

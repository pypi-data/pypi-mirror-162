"""Backend exceptions module.

The errors in this module refer to problems during the retrieval of data from
the backend, but happening at the backend plugin side of the code.
These should be extended/raised from inside the Backend module.
"""

from tesseract_olap.common import BaseError


class BackendError(BaseError):
    """Base class for exceptions in this module."""


class BackendNotReadyError(BackendError):
    """This error happens when there's a connection attempt done against a
    backend which is still not ready for connections.

    The user shoud check the use of the `Backend.connect()` method, and avoid
    race conditions.
    """
    def __init__(self) -> None:
        super().__init__("The configured Backend isn't ready yet.")


class UpstreamInternalError(BackendError):
    """This error occurs when a remote server returns a valid response, but the
    contents give details about an internal server error.

    This must be caught and reported to the administrator.
    """


class InvalidAggregatorError(BackendError):
    """This error occurs when a Measure was configured with an Aggregator
    function unsupported by the current backend.

    This must be reported to the administrator, but also should stop the process.
    """

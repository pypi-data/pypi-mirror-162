class BaseError(Exception):
    """Base class for exceptions in this library."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message

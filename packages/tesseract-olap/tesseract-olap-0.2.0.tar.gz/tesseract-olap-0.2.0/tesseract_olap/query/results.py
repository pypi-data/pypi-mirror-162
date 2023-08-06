"""Result structs module

This module contains wrapper classes for the resulting data of queries obtained
for structs in the requests module.
"""

from dataclasses import dataclass
from typing import Any, Dict, Iterable, Sequence

from tesseract_olap.query.exceptions import EmptyResult

from .requests import DataRequest, MembersRequest


@dataclass(eq=False, frozen=True, order=False)
class DataResult:
    """Container class for results to :class:`DataRequest`."""
    data: Iterable[Dict[str, Any]]
    sources: Sequence[Dict[str, Any]]
    query: DataRequest

    def raise_if_empty(self):
        """Raises an :class:`EmptyResult` exception if the contained data has no
        elements.
        """
        if next(iter(self.data), None) is None:
            raise EmptyResult(self)


@dataclass(eq=False, frozen=True, order=False)
class MembersResult:
    """Container class for results to :class:`MembersRequest`."""
    data: Iterable[Dict[str, Any]]
    query: MembersRequest

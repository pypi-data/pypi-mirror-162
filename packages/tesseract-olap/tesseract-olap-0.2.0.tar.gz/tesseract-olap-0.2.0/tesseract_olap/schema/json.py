from functools import lru_cache
from pathlib import Path
from typing import Callable, Dict, TextIO, TypeVar, Union

import httpx
import orjson

from . import models


class JSONSchema(models.Schema):
    @classmethod
    def parse(cls, root: dict):

        cubes_mapper = _mapper_factory("cubes", "name", JSONCube.parse)
        dimensions_mapper = _mapper_factory("dimensions", "name", JSONDimension.parse)
        tables_mapper = _mapper_factory("inline_tables", "name", JSONInlineTable.parse)

        return cls(
            name=root["name"],
            annotations=root.get("annotations", {}),
            cubes=cubes_mapper(root),
            shared_dimensions=dimensions_mapper(root),
            shared_tables=tables_mapper(root),
            default_role=root.get("default_role"),
            default_locale=root.get("default_locale", "xx"),
        )


class JSONCube(models.Cube):
    @classmethod
    def parse(cls, root: dict):
        return cls(
            name
        )


class JSONDimension(models.Dimension):
    @classmethod
    def parse(cls, root: dict):
        return cls(
            name
        )


class JSONInlineTable(models.InlineTable):
    @classmethod
    def parse(cls, root: dict):
        return cls(
            name
        )


T = TypeVar('T')


@lru_cache(10)
def _mapper_factory(
    parent_obj: str,
    property_name: str,
    reducer: Callable[[dict], T],
) -> Callable[[dict], Dict[str, T]]:
    """
    """
    def mapper_func(root: dict) -> Dict[str, T]:
        return {
            item[property_name]: reducer(item)
            for item in root.get(parent_obj, [])
        }

    return mapper_func


def _parse_pathlib_path(path: Path) -> JSONSchema:
    pass


async def parse_json_schema(source: Union[str, Path, TextIO]) -> JSONSchema:
    if isinstance(source, str):
        # Check if argument is a URL and fetch the file
        if source.lstrip().startswith("http"):
            with httpx.AsyncClient() as client:
                response = await client.get(source)
                response.raise_for_status()

            root = orjson.loads(response.content)

        # Check if argument is a file path and load the file
        elif source.rstrip().endswith(".json"):
            path = Path(source).resolve()
            if not path.exists():
                raise FileNotFoundError("JSON schema: Path '{}' does not exist".format(path))

            if path.is_file():
                with path.open("rb") as f:
                    root = orjson.loads(f.read())
            else:
                # TODO: enable traversing all JSON files in a directory
                raise IsADirectoryError("JSON schema: Path must point to a single file")

        # Check if argument is a raw XML string
        elif source.lstrip().startswith("{"):
            root = orjson.loads(source)

        else:
            raise ValueError("JSON schema: Source can't be recognized")

    # if argument is not a string, attempt to use it like a file-like object
    else:
        with source as f:
            root = orjson.loads(f.read())

    return JSONSchema.parse(root)

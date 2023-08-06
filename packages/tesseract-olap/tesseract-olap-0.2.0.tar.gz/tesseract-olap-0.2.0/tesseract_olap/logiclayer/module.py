"""Tesseract Module for LogicLayer

This module contains an implementation of the :class:`LogicLayerModule` class,
for use with a :class:`LogicLayer` instance.
"""

import dataclasses
from pathlib import Path
from typing import Optional, Union

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse, FileResponse
import logiclayer as ll

from tesseract_olap import __version__ as tesseract_version
from tesseract_olap.backend.exceptions import BackendError
from tesseract_olap.query import DataRequest, MembersRequest
from tesseract_olap.query.exceptions import QueryError
from tesseract_olap.server import OlapServer

from .dependencies import dataquery_params, membersquery_params


class TesseractModule(ll.LogicLayerModule):
    """Tesseract OLAP server module for LogicLayer.

    It must be initialized with a :class:`logiclayer.OlapServer` instance, but
    can also be created directly with the schema path and the connection string
    using the helper method `TesseractModule.new(connection, schema)`.
    """

    server: OlapServer

    def __init__(self, server: OlapServer):
        super().__init__()
        self.server = server

    @classmethod
    def new(cls, connection: str, schema: Union[str, Path]):
        """Creates a new :class:`TesseractModule` instance from the strings with
        the path to the schema file (or the schema content itself), and with the
        connection string to the backend.
        """
        server = OlapServer(connection, schema)
        return cls(server)

    @ll.healthcheck
    def healthcheck(self):
        return self.server.ping()

    @ll.on_startup
    async def event_startup(self):
        await self.server.connect()

    @ll.on_shutdown
    async def event_shutdown(self):
        await self.server.disconnect()

    @ll.route("GET", "/")
    async def status(self):
        """Pings the backend configured in the tesseract server."""
        beat = await self.server.ping()
        return {
            "status": "ok" if beat else "error",
            "software": "tesseract-olap[python]",
            "version": tesseract_version,
        }

    @ll.route("GET", "/cubes")
    def public_schema(self, locale: Optional[str] = None):
        return self.server.schema.get_public_schema(locale=locale)

    @ll.route("GET", "/cubes/{cube_name}")
    def public_schema_cube(self, cube_name: str, locale: Optional[str] = None):
        locale = self.server.schema.default_locale if locale is None else locale
        cube = self.server.schema.get_cube(cube_name)
        return cube.get_public_schema(locale=locale)

    @ll.route(["HEAD", "GET"], "/data", response_class=RedirectResponse)
    def query_data_default(self, request: Request):
        return f"{request.url.path}.jsonrecords?{request.url.query}"

    @ll.route(["HEAD", "GET"], "/members", response_class=RedirectResponse)
    def query_members_default(self, request: Request):
        return f"{request.url.path}.jsonrecords?{request.url.query}"

    @ll.route("GET", "/data.{filetype}")
    async def query_data(
        self,
        filetype: str = "jsonrecords",
        query: DataRequest = Depends(dataquery_params),
    ):
        try:
            result = await self.server.get_data(query)
        except QueryError as exc:
            raise HTTPException(status_code=400, detail=exc.message) from None
        except BackendError as exc:
            raise HTTPException(status_code=500, detail=exc.message) from None
        return {
            "format": filetype,
            "data": result.data,
            "sources": result.sources,
        }

    @ll.route("GET", "/members.{filetype}")
    async def query_members(
        self,
        filetype: str = "jsonrecords",
        query: MembersRequest = Depends(membersquery_params),
    ):
        try:
            result = await self.server.get_members(query)
        except QueryError as exc:
            raise HTTPException(status_code=400, detail=exc.message) from None
        except BackendError as exc:
            raise HTTPException(status_code=500, detail=exc.message) from None
        return {
            "format": filetype,
            "data": result.data,
        }

    @ll.route("GET", "/debug/schema", debug=True)
    def debug_schema(self):
        return dataclasses.asdict(self.server.raw_schema)

    @ll.route("GET", "/debug/reload_server", debug=True)
    async def debug_reconnect(self):
        await self.server.disconnect()
        await self.server.connect()

    @ll.route("GET", "/debug/download_logs", debug=True)
    def debug_logs_download(self, filename: str):
        filename = Path(filename).name
        if not filename.endswith(".log"):
            raise HTTPException(401, "File not allowed")
        filepath = Path.cwd().joinpath(filename).resolve()
        return FileResponse(filepath, media_type="text/plain", filename=filename)

    @ll.route("GET", "/debug/clear_logs", debug=True)
    def debug_logs_clear(self, filename: str):
        filename = Path(filename).name
        if not filename.endswith(".log"):
            raise HTTPException(401, "File not allowed")
        filepath = Path.cwd().joinpath(filename).resolve()
        with filepath.open("w", encoding="utf-8") as fileio:
            fileio.write("")
        return

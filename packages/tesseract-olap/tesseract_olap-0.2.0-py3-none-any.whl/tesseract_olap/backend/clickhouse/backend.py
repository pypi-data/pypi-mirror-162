import logging
from typing import Optional

import asynch
import asynch.cursors
import asynch.errors
import asynch.pool

from tesseract_olap.backend import Backend
from tesseract_olap.backend.exceptions import (BackendNotReadyError,
                                               UpstreamInternalError)
from tesseract_olap.query import DataQuery, MembersQuery
from tesseract_olap.schema import Schema

from .sqlbuild import dataquery_sql, membersquery_sql

logger = logging.getLogger("tesseract_olap.backend.clickhouse")


class ClickhouseBackend(Backend):
    """Clickhouse Backend class

    This is the main implementation for Clickhouse of the core :class:`Backend`
    class.

    Must be initialized with a connection string with the parameters for the
    Clickhouse database. Then must be connected before used to execute queries,
    and must be closed after finishing use.
    """

    _pool: Optional[asynch.pool.Pool]

    def __init__(self, connection_string: str) -> None:
        self.connection_string = connection_string
        self._pool = None

    def __repr__(self) -> str:
        return f"ClickhouseBackend('{self.connection_string}')"

    async def connect(self, pool_size: int = 10, **kwargs):
        pool = await asynch.create_pool(size=pool_size,
                                        dsn=self.connection_string,
                                        **kwargs)
        self._pool = pool

    def close(self):
        self.get_pool().close()

    async def wait_closed(self):
        await self.get_pool().wait_closed()
        self._pool = None

    def get_pool(self) -> asynch.pool.Pool:
        """Obtains the internal Pool instance, if the backend has connected.
        Otherwise, raises a :class:`BackendNotReadyError`."""
        pool = self._pool
        if pool is None:
            raise BackendNotReadyError()
        return pool

    async def get_data(self, query: "DataQuery", **kwargs):
        """Retrieves the dataset for the request made by the :class:`DataQuery`
        instance, from the database.
        """
        logger.debug("DataQuery [%r]", query)
        pool = self.get_pool()

        async with pool.acquire() as conn:
            async with conn.cursor(cursor=asynch.cursors.DictCursor) as cursor:
                # cursor.set_stream_results(True, 100)
                # cursor.set_query_id(str(uuid.uuid4()))
                chquery, chargs = dataquery_sql(query)
                try:
                    await cursor.execute(query=chquery.get_sql(), args=chargs)
                    response = cursor.fetchall()
                except asynch.errors.ClickHouseException as exc:
                    logger.debug("ClickHouse exception", exc_info=exc, extra={
                        "type": "DataQuery",
                        "query": query,
                        "sql_query": chquery.get_sql(),
                        "sql_args": chargs,
                    })
                    raise UpstreamInternalError(exc.message) from None

        return response

    async def get_members(self, query: "MembersQuery", **kwargs):
        """Retrieves the members for the request made by the :class:`MembersQuery`
        instance, from the database.
        """
        logger.debug("MembersQuery [%r]", query)
        pool = self.get_pool()

        async with pool.acquire() as conn:
            async with conn.cursor(cursor=asynch.cursors.DictCursor) as cursor:
                chquery, chargs = membersquery_sql(query)
                try:
                    await cursor.execute(query=chquery.get_sql(), args=chargs)
                    response = cursor.fetchall()
                except asynch.errors.ClickHouseException as exc:
                    logger.debug("ClickHouse exception", exc_info=exc, extra={
                        "type": "MembersQuery",
                        "query": query,
                        "sql_query": chquery.get_sql(),
                        "sql_args": chargs,
                    })
                    raise UpstreamInternalError(exc.message) from None

        return response

    async def ping(self) -> bool:
        """Sends a ping signal to the database using a connection.

        If the server doesn't return "Pong", raises an error.
        This method accesses a private object's method to send the ping, so keep
        an eye on future version changes.
        """
        pool = self.get_pool()
        async with pool.acquire() as conn:
            ping = await conn._connection.ping()
        return ping

    async def validate_schema(self, schema: "Schema") -> None:
        """Checks all the tables and columns referenced in the schema exist in
        the backend.
        """
        # logger.debug("Schema %s", schema)
        # TODO: implement
        for cube in schema.cube_map.values():
            pass
        return None

# -*- coding: UTF-8 -*-

from decimal import Decimal
from sqlite3 import (
    Connection,
    Cursor,
    connect,
    PARSE_COLNAMES,
    PARSE_DECLTYPES,
    Error,
    Row,
    register_adapter,
    register_converter,
)
from typing import Iterable

from .utils import ensure_folder, to_bytes, to_decimal
from ..logging import get_logger, Logger

log: Logger = get_logger(name="sqlite.logger", handler="nostream")

# Registering adapters:
register_adapter(Decimal, to_bytes)

# Registering converters:
register_converter("DECIMAL", to_decimal)


class SQLite(object):
    """SQLite engine."""

    @staticmethod
    def set_logger(instance: Logger):
        global log

        if instance is not None:
            log = instance

    def __init__(self, database: str, detect_types: int = PARSE_COLNAMES | PARSE_DECLTYPES, **kwargs):

        _ensure_folder: bool = kwargs.pop("ensure_folder", False)
        if (_ensure_folder is True) and (database != ":memory:"):
            ensure_folder(database)

        self.set_logger(
            instance=kwargs.pop("logger", None)
        )

        log.debug("Acquiring a new connection with the SQLite database...")
        try:
            self.connection: Connection = connect(database, detect_types=detect_types, **kwargs)
        except Error as sql_error:
            log.error("Failed to connect with the SQLite database!", exception=sql_error)
            raise
        else:
            log.debug("Acquired a new connection with the SQLite database.")
            self.connection.row_factory = Row

    def query(self, sql: str, *args, **kwargs):
        """

        Execute SQL query statement `sql`.
        Bind values to the statement using placeholders that map to the
        sequence `args`.

        If error occurs database will roll back the last transaction(s) else
        it will commit the changes.

        **Keyword arguments:**
            ``arraysize``:
                The cursor’s `arraysize` which determines the number
                of rows to be fetched.

        :param sql: SQL command.
        :param args: Parameter substitution to avoid using Python’s string
            operations.
        :param kwargs: Additional keyword arguments.
        :return: All (remaining) rows of a query result as a list.
            Return an empty list if no rows are available.
            Note that the `arraysize` attribute can affect the performance of
            this operation.
        """
        log.debug(sql)
        cursor: Cursor = self.connection.cursor()

        if "arraysize" in kwargs:
            cursor.arraysize = kwargs.pop("arraysize")

        try:
            results: Cursor = cursor.execute(sql, args)
        except Error as sql_error:
            log.error("Failed to execute the last SQLite query!", exception=sql_error)
            raise
        else:
            # for row in results.fetchall():
            #     yield dict(zip(row.keys(), tuple(row)))
            return results.fetchall()
        finally:
            cursor.close()

    def execute(self, sql: str, *args):
        """
        Execute SQL statement `sql`.
        Bind values to the statement using placeholders that map to the
        sequence `args`. If error occurs database will rollback the
        last transaction(s) else it will commit the changes.

        :param sql: SQL command.
        :param args: Parameter substitution to avoid using Python’s string
            operations.
        """

        log.debug(sql)
        try:
            with self.connection:
                self.connection.execute(sql, args)
        except Error as sql_error:
            log.error("Last sqlite transaction(s) failed!", exception=sql_error)

    def execute_many(self, sql: str, data: Iterable[Iterable]):
        """
        Execute parameterized SQL statement `sql` against all parameter sequences
        or mappings found in the sequence `args`. It is also possible to
        use an iterator yielding parameters instead of a sequence. Uses the
        same implicit transaction handling as :func:`execute()`. If error occurs
        database will :func:`rollback()` the last transaction(s) else it will commit the changes.

        :param sql: SQL command.
        :param data: Parameter substitution to avoid using Python’s string operations.
        """

        log.debug(sql)
        try:
            with self.connection:
                self.connection.executemany(sql, data)
        except Error as sql_error:
            log.error("Last sqlite transaction(s) failed!", exception=sql_error)

    def execute_script(self, sql_script: str):
        """
        Execute the SQL statements in `sql_script`.
        If there is a pending transaction, an implicit COMMIT statement is
        executed first. No other implicit transaction control is performed;
        any transaction control must be added to sql_script.

        If error occurs database will rollback the last transaction(s) else it
        will commit the changes.

        :param sql_script: SQL script.
        """

        log.debug(sql_script)
        try:
            with self.connection:
                self.connection.executescript(sql_script)
        except Error as sql_error:
            log.error("Last sqlite transaction(s) failed!", exception=sql_error)

    def close(self):
        """Close the connection with the sqlite database file and release the resources."""
        log.debug("Closing the connection with the SQLite database...")
        try:
            self.connection.close()
        except Error as sql_error:
            log.warning("Failed to close connection with the SQLite database!", exception=sql_error)
        else:
            log.debug("Connection with SQLite database terminated.")
        finally:
            del self.connection

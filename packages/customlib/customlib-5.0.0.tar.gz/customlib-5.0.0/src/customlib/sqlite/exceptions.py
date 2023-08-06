# -*- coding: UTF-8 -*-

class DatabaseError(Exception):
    """All exception classes inherit from this class."""


class SQLiteIndexError(DatabaseError):
    """Exception raised for index related errors."""


class MissingColumnsError(DatabaseError):
    """Exception raised for missing columns."""


class MissingEngineError(DatabaseError):
    """Exception class raised for missing SQL engine."""


class ArgumentError(DatabaseError):
    """Exception class raised for argument related errors."""

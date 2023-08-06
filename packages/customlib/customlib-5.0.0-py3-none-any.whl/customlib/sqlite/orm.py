# -*- coding: UTF-8 -*-

from __future__ import annotations

from typing import Generator, NewType

from .dialect import DDL, DML, DQL, Comparison
from .engine import SQLite
from .exceptions import SQLiteIndexError, MissingColumnsError
from .utils import single_quote, as_namedtuple

# distinct types:
Tables = NewType("Tables", as_namedtuple)
Columns = NewType("Columns", as_namedtuple)
Indexes = NewType("Indexes", as_namedtuple)


class BaseModel(object):
    """Base ORM model."""

    def __init__(self, name: str):
        self.name = name

    @property
    def typename(self):
        return self.__class__.__name__.lower()

    @property
    def parent(self) -> BaseModel:
        return getattr(self, "_parent", None)

    @parent.setter
    def parent(self, value: BaseModel):
        setattr(self, "_parent", value)


class Model(BaseModel):
    """ORM model."""

    def _add_child(self, item: Model):
        if item.parent is None:
            item.parent = self


class CollectionModel(Model):
    """ORM collection model."""

    def _map_collection(self, target: str, *args, **kwargs) -> dict:
        return {key: value for key, value in self._filter(target, *args, **kwargs)}

    def _filter(self, target: str, *args, **kwargs) -> Generator:
        target: str = target.lower()  # force lowercase
        items: tuple = args + tuple(kwargs.values())

        for item in items:
            if item.typename == target:
                self._add_child(item)
                yield item.name, item


class Schema(Model, DDL):
    """SQLite schema ORM model."""

    def __init__(self, name: str = "main", **kwargs):
        super(Schema, self).__init__(name=name)

        self.engine = kwargs.pop("engine", None)
        self._tables = dict()

    @property
    def tables(self) -> Tables:
        return as_namedtuple("Tables", **self._tables)

    def add_table(self, table: Table):
        self._add_child(table)
        self._tables.update({table.name: table})

    def __repr__(self):
        typename: str = self.typename.title()
        fields: tuple = (
            f"name='{self.name}'",
            f"engine='{self.engine}'",
            f"tables={self.tables}",
        )
        return f"{typename}({', '.join(fields)})"


class Table(CollectionModel, DDL, DML, DQL):
    """SQLite table ORM model."""

    def __init__(self, name: str, schema: Schema, *args, **kwargs):
        super(Table, self).__init__(name=name)

        self.schema = schema
        self.temp: bool = kwargs.pop("temp", False)
        self._columns: dict = self._map_collection("column", *args, **kwargs)

        if len(self._columns) == 0:
            raise MissingColumnsError(f"Cannot create a table '{self.name}' without any column!")

        # TODO: store indexes into schema as well
        #  to avoid duplicate index names...
        self._indexes: dict = self._idx_collection(*args, **kwargs)

        self._resolve_constraints(self._columns)
        self.schema.add_table(table=self)

    @property
    def engine(self) -> SQLite:
        return self.schema.engine

    @engine.setter
    def engine(self, value: SQLite):
        self.schema.engine = value

    @property
    def columns(self) -> Columns:
        return as_namedtuple("Columns", **self._columns)

    @property
    def indexes(self) -> Indexes:
        return as_namedtuple("Indexes", **self._indexes)

    # why not?
    c = columns
    i = indexes

    def _resolve_constraints(self, columns: dict):
        autoincrement: Column = self._find_autoincrement(columns)

        if autoincrement is not None:

            for key, value in columns.items():
                if value is autoincrement:
                    continue
                else:
                    value.autoincrement = value.primary = False

    @staticmethod
    def _find_autoincrement(columns: dict) -> Column:
        for key, value in columns.items():
            if value.autoincrement is True:
                return value

    def _idx_collection(self, *args, **kwargs) -> dict:
        _mapped_indexes: dict = self._map_indexes(**self._columns)
        _idx_collection: dict = self._map_collection("index", *args, **kwargs)

        for name, index in _idx_collection.items():

            if name in _mapped_indexes:
                raise SQLiteIndexError(f"An index with this name '{name}' already exists!")

            for column in index.columns:

                if column.name not in self._columns:
                    raise SQLiteIndexError(
                        f"{self.typename.title()} '{self.name}' has no such column '{column.name}'!"
                    )

                if column.type.upper() == "DUMMY":
                    column = self._columns.get(column.name)
                    index.update_columns(column)

            if index.table is not None:
                table_name = index.table.name if isinstance(index.table, Table) else index.table

                if table_name != self.name:
                    raise SQLiteIndexError(f"Wrong table name '{table_name}' for this index '{index.name}'!")
            else:
                index.table = index.parent or self

        _mapped_indexes.update(**_idx_collection)
        return _mapped_indexes

    def _map_indexes(self, **kwargs) -> dict:
        return {
            item.name: item
            for item in self._filter_indexes(**kwargs)
        }

    def _filter_indexes(self, **kwargs) -> Generator:
        for key, value in kwargs.items():

            if value.index is True:
                index = Index(
                    self._idx_name(key, value.unique),
                    value,
                    table=self,
                    unique=value.unique,

                )
                self._add_child(index)
                yield index

    def _idx_name(self, basename: str, unique: bool) -> str:
        if unique is True:
            return f"ux_{basename}_{self.name}"
        return f"ix_{basename}_{self.name}"

    def __repr__(self):
        typename: str = self.typename.title()
        fields: tuple = (
            f"name='{self.name}'",
            f"schema='{self.schema.name}'",
            f"columns={self.columns}",
            f"indexes={self.indexes}"
        )
        return f"{typename}({', '.join(fields)})"


class Column(BaseModel):
    """SQLite column ORM model."""

    def __init__(self, name: str, type: str, **kwargs):
        super(Column, self).__init__(name=name)

        self.type: str = type
        self.null: bool = kwargs.pop("null", True)
        self.primary: bool = kwargs.pop("primary", False)
        self.autoincrement: bool = kwargs.pop("autoincrement", False)
        self.foreign: bool = kwargs.pop("foreign", False)
        self.references: Column = kwargs.pop("references", None)
        self.unique: bool = kwargs.pop("unique", False)
        self.index: bool = kwargs.pop("index", False)

        self._rezolve_constraints()

    def __call__(self, alias: str):
        self.alias = alias
        return self

    def __eq__(self, other):
        return Comparison(name=self.name, operator="==", value=other)

    def __ne__(self, other):
        return Comparison(name=self.name, operator="!=", value=other)

    def __le__(self, other):
        return Comparison(name=self.name, operator="<=", value=other)

    def __ge__(self, other):
        return Comparison(name=self.name, operator=">=", value=other)

    def __lt__(self, other):
        return Comparison(name=self.name, operator="<", value=other)

    def __gt__(self, other):
        return Comparison(name=self.name, operator=">", value=other)

    def is_null(self):
        return Comparison(name=self.name, operator="IS", value="NULL")

    def is_not_null(self):
        return Comparison(name=self.name, operator="IS NOT", value="NULL")

    def like(self, value: str):
        return Comparison(name=self.name, operator="LIKE", value=value)

    def _rezolve_constraints(self):

        if self.foreign is True:
            self.primary = self.autoincrement = False

        if self.autoincrement is True:
            self.primary = True

    def __repr__(self) -> str:
        typename: str = self.typename.title()
        fields: tuple = tuple(
            f"{key}={single_quote(value)}"
            for key, value in self.__dict__.items()
            if (key.startswith("_") is False)
        )
        return f"{typename}({', '.join(fields)})"


class Index(CollectionModel, DDL):
    """SQLite `INDEX` ORM model."""

    def __init__(self, name: str, *args, **kwargs):
        super(Index, self).__init__(name=name)

        self.table: Table = kwargs.pop("table", None)
        self.unique = kwargs.pop("unique", False)
        self._columns: dict = self._map_collection("column", *args, **kwargs)

        if len(self._columns) == 0:
            raise MissingColumnsError(f"Cannot create an index '{self.name}' without any column!")

    @property
    def columns(self) -> Columns:
        return as_namedtuple("Columns", **self._columns)

    @property
    def engine(self) -> SQLite:
        return self.table.engine

    @engine.setter
    def engine(self, value: SQLite):
        self.table.engine = value

    def update_columns(self, column: Column):
        self._columns.update({column.name: column})

    def _filter(self, target: str, *args, **kwargs) -> Generator:
        """Filter and return only objects with targeted typename."""
        target: str = target.lower()
        items: tuple = args + tuple(kwargs.values())

        for item in items:

            if hasattr(item, "typename"):
                if item.typename == target:
                    yield item.name, item

            elif isinstance(item, str):
                yield item, Column(name=item, type="DUMMY")

    def __repr__(self):
        typename: str = self.typename.title()
        fields: tuple = (
            f"name='{self.name}'",
            f"table='{self.table.name}'",
            f"columns={tuple(column.name for column in self.columns)}",
            f"unique={self.unique}",
        )
        return f"{typename}({', '.join(fields)})"

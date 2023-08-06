# -*- coding: UTF-8 -*-

from __future__ import annotations

from dataclasses import dataclass, asdict, field
from string import Template
from typing import Any, Generator

from .constants import PLACEHOLDERS, TABLE, INDEX, COLUMN
from .engine import SQLite
from .exceptions import ArgumentError, MissingEngineError
from .utils import clean_string


class DDL(object):

    def create(self, if_not_exists: bool = False):
        syntax = Create(model=self)
        return syntax(if_not_exists)

    def drop(self, if_exists: bool = False):
        syntax = Drop(model=self)
        return syntax(if_exists)


class DML(object):

    def insert(self, *args, **kwargs):
        syntax = Insert(model=self)
        return syntax(*args, **kwargs)

    def update(self, *args, **kwargs):
        syntax = Update(model=self)
        return syntax(*args, **kwargs)

    def delete(self, *args, **kwargs):
        syntax = Delete(model=self)
        return syntax(*args, **kwargs)


class DQL(object):

    def select(self, *args):
        syntax = Select(model=self)
        return syntax(*args)


class Syntax(object):

    @staticmethod
    def _clean(value: str) -> str:
        for item in PLACEHOLDERS:
            if item in value:
                value = clean_string(item, value)
        return value

    def __init__(self, model: Any):
        self._model = model

    @property
    def statement(self) -> str:
        return getattr(self, "_statement", None)

    @statement.setter
    def statement(self, value: str):
        setattr(self, "_statement", value)

    @property
    def params(self) -> tuple:
        return getattr(self, "_params", tuple())

    @params.setter
    def params(self, value: tuple):
        setattr(self, "_params", value)

    def execute(self):
        engine: SQLite = self._get_engine()

        if self.statement is not None:

            if self._model.typename == "schema":
                engine.execute_script(self.statement)
            else:
                engine.execute(f"{self.statement};", *self.params)

    def query(self, **kwargs):
        """
        Perform a `SELECT` command execution wit `kwargs` if any.

        **Keyword arguments:**
            ``arraysize``:
                The cursor’s `arraysize` which determines the number
                of rows to be fetched.

        :param kwargs: Additional keyword arguments.
        """
        engine: SQLite = self._get_engine()

        if self.statement is not None:
            query: list = engine.query(f"{self.statement};", *self.params, **kwargs)
            return [dict(zip(row.keys(), tuple(row))) for row in query]

    def _get_engine(self) -> SQLite:
        if self._model.engine is None:
            raise MissingEngineError(
                f"{self._model.typename.title()}(name='{self._model.name}') is not bound to an Engine or Connection!"
            )
        return self._model.engine

    def _build(self, template: Template, **kwargs) -> str:
        stmt = template.safe_substitute(**kwargs)
        return self._clean(stmt)

    def _resolve_parameters(self, *args, **kwargs) -> dict:
        columns = [column.name for column in self._model.columns]

        if 0 < len(args) <= len(columns):
            kwargs, params = {columns[idx]: arg for idx, arg in enumerate(args)}, kwargs.copy()
            keys = set(kwargs).intersection(set(params))

            if len(keys) > 0:
                duplicates = ", ".join([f'"{key}"' for key in keys])
                raise ArgumentError(f"Columns({duplicates}) already passed through positional only args!")

            kwargs.update(params)

        if 0 <= len(kwargs) <= len(columns):
            for key, value in kwargs.items():

                if key not in columns:
                    raise ArgumentError(f"Column(name='{key}') not in Table(name='{self._model.name}')!")
            else:
                return kwargs
        else:
            raise ArgumentError(f"Failed to resolve the parameters for Table(name='{self._model.name}')!")

    def _resolve_tuples(self, *args):
        columns = [column.name for column in self._model.columns]
        if 0 < len(args):
            for arg in args:
                if arg.name not in columns:
                    raise ArgumentError(f"Column(name='{arg.name}') not in Table(name='{self._model.name}')!")
            else:
                return [f'"{arg.name}" {arg.operator} ?' for arg in args]
        else:
            raise ArgumentError(f"Failed to resolve the parameters for Table(name='{self._model.name}')!")

    def __repr__(self):
        if self.statement is not None:
            return f"{self.statement};"
        return super(Syntax, self).__repr__()


class Create(Syntax):

    def __call__(self, if_not_exists: bool = False):
        _make = getattr(self, f"_{self._model.typename}")
        self.statement = _make(if_not_exists)
        return self

    def _schema(self, if_not_exists: bool) -> str:
        return "\n".join(
            [
                f"{sql_cmd};"
                for sql_cmd in self._create_commands(if_not_exists)
            ]
        )

    def _table(self, if_not_exists: bool) -> str:
        """Construct a sqlite `CREATE` table statement."""
        fields = dict(
            name=self._model.name,
            columns=", ".join(self._get_columns()),
        )

        if self._model.temp is True:
            fields.update(temp="TEMP")

        if if_not_exists is True:
            fields.update(if_not_exists="IF NOT EXISTS")

        constraints = self._get_constraints()
        if constraints is not None:
            fields.update(
                constraints=", ".join(constraints),
            )

        return self._build(TABLE.CREATE, **fields)

    def _index(self, if_not_exists: bool) -> str:
        """Construct a sqlite `CREATE` index statement."""

        fields = dict(
            name=self._model.name,
            table=self._model.table.name,
            columns=", ".join(
                [
                    f'"{column.name}"'
                    for column in self._model.columns
                ]
            ),
        )

        if self._model.unique is True:
            fields.update(unique="UNIQUE")

        if if_not_exists is True:
            fields.update(if_not_exists="IF NOT EXISTS")

        return self._build(INDEX.CREATE, **fields)

    def _create_commands(self, if_not_exists: bool) -> Generator:

        for table in self._model.tables:
            yield table.create(if_not_exists).statement

            if table.indexes is not None:
                for index in table.indexes:
                    yield index.create(if_not_exists).statement

    def _get_columns(self) -> list[str]:
        return [
            self._column_clause(column)
            for column in self._model.columns
        ]

    def _column_clause(self, value) -> str:
        """SQLite column clause."""
        fields = dict(
            name=value.name,
            type=value.type,
        )

        if value.null is False:
            fields.update(null="NOT NULL")

        if value.unique is True:
            fields.update(unique="UNIQUE")

        return self._build(TABLE.COLUMN, **fields)

    def _get_constraints(self) -> list[str]:
        """Return a list of constraint clauses for this table."""
        primary: str = self._get_primary()
        foreign: list[str] = self._get_foreign()
        constraints = list()

        if primary is not None:
            constraints.append(primary)

        if len(foreign) > 0:
            constraints += foreign

        if len(constraints) > 0:
            return constraints

    def _get_primary(self) -> str:
        """Construct & return the `PRIMARY KEY` clause."""

        for column in self._model.columns:
            if column.autoincrement is True:
                return self._autoincrement(column)

        else:
            columns: list[str] = [
                f'"{column.name}"'
                for column in self._model.columns
                if column.primary is True
            ]

            if len(columns) > 0:
                return self._primary(columns)

    def _autoincrement(self, column) -> str:
        """SQLite `PRIMARY KEY` with autoincrement clause."""
        fields = dict(
            name=column.name,
            autoincrement="AUTOINCREMENT",
        )
        return self._build(TABLE.AUTOINCREMENT, **fields)

    def _primary(self, columns: list) -> str:
        """SQLite `PRIMARY KEY` clause."""
        fields = dict(
            columns=", ".join(columns)
        )
        return self._build(TABLE.PRIMARY, **fields)

    def _get_foreign(self) -> list[str]:
        return [
            self._foreign(column)
            for column in self._model.columns
            if column.foreign is True
        ]

    def _foreign(self, column) -> str:
        """SQLite foreign column clause."""
        fields = dict(
            name=column.name,
            table=column.references.parent.name,
            column=column.references.name,
        )
        return self._build(TABLE.FOREIGN, **fields)


class Drop(Syntax):

    def __call__(self, if_exists: bool = False):
        _make_statement = getattr(self, f"_{self._model.typename}")
        self.statement = _make_statement(if_exists)
        return self

    def _schema(self, if_exists: bool) -> str:
        return "\n".join(
            [
                f"{sql_cmd};"
                for sql_cmd in self._drop_commands(if_exists)
            ]
        )

    def _table(self, if_exists: bool) -> str:
        """Construct a `DROP` sqlite table statement."""

        fields = dict(
            name=self._model.name
        )

        if if_exists is True:
            fields.update(if_exists="IF EXISTS")

        return self._build(TABLE.DROP, **fields)

    def _index(self, if_exists: bool) -> str:
        """Construct a `DROP` sqlite index statement."""

        fields = dict(
            name=self._model.name
        )

        if if_exists is True:
            fields.update(if_exists="IF EXISTS")

        return self._build(INDEX.DROP, **fields)

    def _drop_commands(self, if_exists: bool) -> Generator:

        for table in self._model.tables:

            if table.indexes is not None:
                for index in table.indexes:
                    yield index.drop(if_exists).statement

            yield table.drop(if_exists).statement


class Insert(Syntax):
    """INSERT INTO "${table}" (${columns}) VALUES (${values})"""

    def __call__(self, *args, **kwargs):
        kwargs = self._resolve_parameters(*args, **kwargs)

        fields = {
            "table": self._model.name,
        }

        self.params = tuple(kwargs.values())

        fields.update(
            columns=", ".join([f'"{key}"' for key in kwargs.keys()]),
            values=", ".join("?" * len(kwargs)),
        )

        self.statement = self._build(TABLE.INSERT, **fields)
        return self


class Update(Syntax):

    def __call__(self, *args, **kwargs):
        kwargs = self._resolve_parameters(*args, **kwargs)

        self._fields = dict(
            table=self._model.name,
        )

        cols = [f'"{key}" = ?' for key in kwargs.keys()]
        self._fields.update(
            set=f"SET {', '.join(cols)}",
        )

        self.params = tuple(kwargs.values())
        self.statement = self._build(TABLE.UPDATE, **self._fields)

        return Where(
            model=self._model,
            params=self.params,
            fields=self._fields,
            template=TABLE.UPDATE,
        )


class Delete(Syntax):

    def __call__(self, *args, **kwargs):
        self._fields = dict(
            table=self._model.name,
        )
        self.statement = self._build(TABLE.DELETE, **self._fields)
        return Where(
            model=self._model,
            params=self.params,
            fields=self._fields,
            template=TABLE.DELETE,
        )


class Select(Syntax):

    def __call__(self, *args):
        columns = [column.name for column in self._model.columns]
        _fields = list()

        if len(args) == 0:
            _fields.append("*")

        for arg in args:

            if isinstance(arg, str) is True:

                if arg in columns:
                    _fields.append(f'"{arg}"')

                elif " as " in arg.lower():
                    values = arg.split(" ")

                    if (len(values) == 3) and (values[0] in columns) and (values[1].lower() == "as"):
                        alias = f"'{values[-1]}'"
                        _fields.append(f'"{values[0]}" {values[1].upper()} {alias}')

                # We're stopping here...
                # If you plan on using just strings then,
                # there's no point in using ORMs anymore... right?

            elif hasattr(arg, "typename") is True:

                if arg.typename == "column":
                    if hasattr(arg, "alias"):
                        alias = f"'{arg.alias}'"
                        _fields.append(f'"{arg.name}" AS {alias}')
                    else:
                        _fields.append(f'"{arg.name}"')

                elif "function" in arg.typename:
                    _fields.append(arg.statement)
            else:
                raise ArgumentError("Bad parameter passed!")

        self._fields = dict(
            columns=", ".join(_fields),
            table=self._model.name,
        )

        self.statement = self._build(TABLE.SELECT, **self._fields)

        return Where(
            model=self._model,
            params=self.params,
            fields=self._fields,
            template=TABLE.SELECT,
            statement=self.statement,
        )


class Where(Syntax):

    def __init__(self, model: Any, **kwargs):
        super(Where, self).__init__(model)

        self.statement = kwargs.pop("statement", None)
        self.params = kwargs.pop("params", tuple())
        self._fields = kwargs.pop("fields", dict())
        self._template = kwargs.pop("template")

    def where(self, *args):
        expressions = self._resolve_tuples(*args)
        self._fields.update(
            where=f"WHERE {' AND '.join(expressions)}"
        )
        self.params += tuple(arg.value for arg in args)
        self.statement = self._build(self._template, **self._fields)

        return LogicalOperator(
            model=self._model,
            params=self.params,
            fields=self._fields,
            template=self._template,
            statement=self.statement,
        )


class LogicalOperator(Syntax):

    def __init__(self, model: Any, **kwargs):
        super(LogicalOperator, self).__init__(model)

        self.statement = kwargs.pop("statement", None)
        self.params = kwargs.pop("params", tuple())
        self._fields = kwargs.pop("fields", dict())
        self._template = kwargs.pop("template")

    def __and__(self, *args):
        expressions = self._resolve_tuples(*args)

        self._fields.update(
            where=f"{self._fields.get('where')} AND {' AND '.join(expressions)}"
        )

        self.params += tuple(arg.value for arg in args)
        self.statement = self._build(self._template, **self._fields)
        return self

    def __or__(self, *args):
        expressions = self._resolve_tuples(*args)

        self._fields.update(
            where=f"{self._fields.get('where')} OR {' AND '.join(expressions)}"
        )

        self.params += tuple(arg.value for arg in args)
        self.statement = self._build(self._template, **self._fields)
        return self


@dataclass
class Comparison(object):

    name: str
    operator: str
    value: Any

    def __post_init__(self):
        _fields: dict = asdict(self)
        _fields.update(
            value=self._quote(_fields.get("value"))
        )
        self.statement: str = self._build(COLUMN.COMPARISON, **_fields)

    @staticmethod
    def _quote(value: Any):
        if (isinstance(value, str) is True) and (value not in ["NULL", "NOT NULL"]):
            value = f"'{value}'"
        return value

    @staticmethod
    def _clean(value: str) -> str:
        for item in PLACEHOLDERS:
            if item in value:
                value = clean_string(item, value)
        return value

    def _build(self, template: Template, **kwargs) -> str:
        stmt = template.safe_substitute(**kwargs)
        return self._clean(stmt)

    def __repr__(self):
        return self.statement


@dataclass
class Aggregate(object):
    """
    SQLite base aggregate function statement constructor.

    Example:
        table.select(MAX(table.c.column))

        Will result in: `SELECT MAX("{column-name}") FROM "{table-name}"`
    """

    model: Any
    alias: str = field(default=None)

    def __post_init__(self):
        if "function" in self.model.typename:
            self.statement = f'{self._split_typename()}({self.model.statement})'
        else:
            self.statement = f'{self._split_typename()}("{self.model.name}")'

        if self.alias is not None:
            self.statement = f"{self.statement} AS '{self.alias}'"

    @property
    def typename(self) -> str:
        name: str = self.__class__.__name__.lower()
        return f"function.{name}" if name != "function" else "function"

    def _split_typename(self) -> str:
        typename: str = self.typename.split(".")[-1]
        return typename.upper()

    def __repr__(self):
        return self.statement


@dataclass
class AVG(Aggregate):
    """
    AVG("{column}")
    """

    def __repr__(self):
        return self.statement


@dataclass
class COUNT(Aggregate):
    """
    COUNT("{column}")
    """

    def __repr__(self):
        return self.statement


@dataclass
class MAX(Aggregate):
    """
    MAX("{column}")
    """

    def __repr__(self):
        return self.statement


@dataclass
class MIN(Aggregate):
    """
    MIN("{column}")
    """

    def __repr__(self):
        return self.statement


@dataclass
class SUM(Aggregate):
    """
    SUM("{column}")
    """

    def __repr__(self):
        return self.statement


@dataclass
class TOTAL(Aggregate):
    """
    TOTAL("{column}")
    """

    def __repr__(self):
        return self.statement


@dataclass
class DISTINCT(Aggregate):
    """
    DISTINCT("{column}")
    """

    def __repr__(self):
        return self.statement


@dataclass
class ALL(Aggregate):
    """
    ALL("{column}")
    """

    def __repr__(self):
        return self.statement


@dataclass
class GROUP_CONCAT(Aggregate):
    """
    GROUP_CONCAT("{column}", ",")
    """

    sep: str = field(default=",")

    def __post_init__(self):
        self.statement = f'{self._split_typename()}("{self.model.name}", "{self.sep}")'

        if self.alias is not None:
            self.statement = f"{self.statement} AS '{self.alias}'"

    def __repr__(self):
        return self.statement


@dataclass
class Function(Aggregate):
    """
    SQLite core function statement constructor.

    Example:
        table.select(LOWER(table.c.column))

    Will result in: `SELECT LOWER("{column-name}") FROM "{table-name}";`
    """


@dataclass
class LOWER(Function):
    """
    LOWER("{column}")
    """

    def __repr__(self):
        return self.statement


@dataclass
class UPPER(Function):
    """
    UPPER("{column}")
    """

    def __repr__(self):
        return self.statement

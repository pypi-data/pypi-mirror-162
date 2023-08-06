# -*- coding: UTF-8 -*-

from os.path import realpath
from string import Template

from .utils import find_in_file


class TABLE:
    CREATE: Template = Template('CREATE ${temp} TABLE ${if_not_exists} "${name}" (${columns}, ${constraints})')
    DROP: Template = Template('DROP TABLE ${if_exists} "${name}"')

    SELECT: Template = Template(
        'SELECT ${columns} FROM "${table}" ${where} ${group_by} ${order_by} ${limit}'
    )
    INSERT: Template = Template('INSERT INTO "${table}" (${columns}) VALUES (${values})')
    UPDATE: Template = Template('UPDATE "${table}" ${set} ${where}')
    DELETE: Template = Template('DELETE FROM "${table}" ${where}')

    WHERE: Template = Template('WHERE ${clause}')
    COLUMN: Template = Template('"${name}" ${type} ${null} ${unique}')
    FOREIGN: Template = Template('FOREIGN KEY ("${name}") REFERENCES "${table}" ("${column}")')
    PRIMARY: Template = Template('PRIMARY KEY (${columns})')
    AUTOINCREMENT: Template = Template('PRIMARY KEY ("${name}" ${autoincrement})')


class COLUMN:
    COMPARISON: Template = Template('"${name}" ${operator} ${value}')


class INDEX:
    CREATE: Template = Template('CREATE ${unique} INDEX ${if_not_exists} "${name}" ON "${table}" (${columns}) ${where}')
    DROP: Template = Template('DROP INDEX ${if_exists} "${name}"')


# gathering a set of placeholders (ex: `${name}`) for statement cleaning
PLACEHOLDERS = set(
    find_in_file(realpath(__file__), "placeholder", r"\$\{\w+\}")
)

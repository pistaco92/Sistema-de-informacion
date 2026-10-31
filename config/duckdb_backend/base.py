"""
Backend de base de datos de Django para DuckDB.
Permite usar los modelos y el ORM de Django directamente sobre un archivo .duckdb.
"""

import re
from collections.abc import Mapping
from decimal import Decimal
from itertools import tee

import duckdb
from django.db.backends.base.schema import BaseDatabaseSchemaEditor
from django.db.backends.sqlite3.base import DatabaseWrapper as SQLiteDatabaseWrapper
from django.db.backends.sqlite3.client import DatabaseClient
from django.db.backends.sqlite3.creation import DatabaseCreation
from django.db.backends.sqlite3.features import DatabaseFeatures as SQLiteDatabaseFeatures
from django.db.backends.sqlite3.introspection import (
    DatabaseIntrospection as SQLiteDatabaseIntrospection,
    TableInfo,
)
from django.db.backends.sqlite3.operations import (
    DatabaseOperations as SQLiteDatabaseOperations,
)
from django.utils.asyncio import async_unsafe
from django.utils.regex_helper import _lazy_re_compile

FORMAT_QMARK_REGEX = _lazy_re_compile(r"(?<!%)%s")
AUTOINCREMENT_REGEX = re.compile(
    r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?(?:"([^"]+)"|(\w+))\s*\(\s*(?:"([^"]+)"|(\w+))\s+(?:integer|bigint|smallint)\s+NOT\s+NULL\s+PRIMARY\s+KEY\s+AUTOINCREMENT',
    re.IGNORECASE,
)


SISIFO_TABLES = {
    "categories",
    "suppliers",
    "products",
    "composition",
    "users",
    "ratings",
    "deliveries",
    "purchases",
}


class DuckDBCursorWrapper:
    """Envuelve el cursor nativo de DuckDB para adaptar placeholders (%s -> ?) y DDL."""

    def __init__(self, cursor):
        self._cursor = cursor
        self.lastrowid = None

    def _transform_ddl(self, query):
        # Eliminar cláusulas DEFERRABLE no soportadas por DuckDB
        if "DEFERRABLE" in query.upper():
            query = re.sub(
                r"\s+DEFERRABLE\s+INITIALLY\s+(?:DEFERRED|IMMEDIATE)",
                "",
                query,
                flags=re.IGNORECASE,
            )

        # Hacer CREATE TABLE idempotente (IF NOT EXISTS) para convivir con init.sql del contenedor DuckDB
        query = re.sub(
            r"^\s*CREATE\s+TABLE\s+(?!IF\s+NOT\s+EXISTS\b)",
            "CREATE TABLE IF NOT EXISTS ",
            query,
            flags=re.IGNORECASE,
        )

        # Emular AUTOINCREMENT de Django mediante secuencias nativas de DuckDB
        match = AUTOINCREMENT_REGEX.search(query)
        if match:
            table_name = match.group(1) or match.group(2)
            col_name = match.group(3) or match.group(4)
            seq_name = f"seq_{table_name}_{col_name}"
            self._cursor.execute(f'CREATE SEQUENCE IF NOT EXISTS "{seq_name}" START 1')
            query = re.sub(
                r"\bAUTOINCREMENT\b",
                f"DEFAULT nextval('\"{seq_name}\"')",
                query,
                count=1,
                flags=re.IGNORECASE,
            )
            if table_name.lower() not in SISIFO_TABLES:
                query = re.sub(
                    r'\s+REFERENCES\s+"[^"]+"\s*\("[^"]+"\)',
                    "",
                    query,
                    flags=re.IGNORECASE,
                )
        return query

    def convert_query(self, query, *, param_names=None):
        if param_names is None:
            return FORMAT_QMARK_REGEX.sub("?", query).replace("%%", "%")
        return query % {name: f"${name}" for name in param_names}

    def execute(self, query, params=None):
        query = self._transform_ddl(query)
        idx_match = re.match(
            r'^\s*CREATE\s+(?:UNIQUE\s+)?INDEX\s+.*?\bON\s+(?:"([^"]+)"|(\w+))',
            query,
            re.IGNORECASE,
        )
        if idx_match:
            idx_table = (idx_match.group(1) or idx_match.group(2)).lower()
            if idx_table not in SISIFO_TABLES:
                return self._cursor

        if params is None or len(params) == 0:
            return self._cursor.execute(query)
        param_names = list(params) if isinstance(params, Mapping) else None
        query = self.convert_query(query, param_names=param_names)
        if not isinstance(params, (list, tuple, Mapping)):
            params = tuple(params)
        return self._cursor.execute(query, params)

    def executemany(self, query, param_list):
        query = self._transform_ddl(query)
        peekable, param_list = tee(iter(param_list))
        first = next(peekable, None)
        if first is None:
            return self._cursor
        param_names = list(first) if isinstance(first, Mapping) else None
        query = self.convert_query(query, param_names=param_names)
        return self._cursor.executemany(query, list(param_list))

    def fetchone(self):
        return self._cursor.fetchone()

    def fetchmany(self, size=1):
        return self._cursor.fetchmany(size)

    def fetchall(self):
        return self._cursor.fetchall()

    def close(self):
        pass

    @property
    def description(self):
        return self._cursor.description

    @property
    def rowcount(self):
        return getattr(self._cursor, "rowcount", -1)

    def __iter__(self):
        return iter(self._cursor)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __getattr__(self, name):
        return getattr(self._cursor, name)


class DatabaseFeatures(SQLiteDatabaseFeatures):
    minimum_database_version = (1, 0)
    can_create_inline_fk = True
    can_defer_constraint_checks = False
    can_rollback_ddl = False
    uses_savepoints = False
    can_release_savepoints = False
    can_return_columns_from_insert = True
    can_return_rows_from_bulk_insert = True
    supports_default_keyword_in_insert = True
    supports_transactions = True
    atomic_transactions = False
    supports_json_field = True


class DatabaseOperations(SQLiteDatabaseOperations):
    def pk_default_value(self):
        return "DEFAULT"

    def last_executed_query(self, cursor, sql, params):
        if params:
            return f"{sql} /* params={params!r} */"
        return sql

    def force_group_by(self):
        return []


class DatabaseIntrospection(SQLiteDatabaseIntrospection):
    def get_table_list(self, cursor):
        cursor.execute(
            """
            SELECT table_name, table_type
            FROM information_schema.tables
            WHERE table_schema = 'main'
            ORDER BY table_name
            """
        )
        return [
            TableInfo(row[0], "v" if "VIEW" in row[1].upper() else "t")
            for row in cursor.fetchall()
        ]

    def get_primary_key_columns(self, cursor, table_name):
        cursor.execute(f"PRAGMA table_info({self.connection.ops.quote_name(table_name)})")
        return [row[1] for row in cursor.fetchall() if row[5]]

    def get_constraints(self, cursor, table_name):
        return {}


class DatabaseSchemaEditor(BaseDatabaseSchemaEditor):
    sql_delete_table = "DROP TABLE %(table)s"
    sql_create_fk = None
    sql_create_inline_fk = "REFERENCES %(to_table)s (%(to_column)s)"
    sql_create_column_inline_fk = sql_create_inline_fk
    sql_delete_column = "ALTER TABLE %(table)s DROP COLUMN %(column)s"
    sql_create_unique = "CREATE UNIQUE INDEX IF NOT EXISTS %(name)s ON %(table)s (%(columns)s)"
    sql_delete_unique = "DROP INDEX IF EXISTS %(name)s"

    def quote_value(self, value):
        if isinstance(value, bool):
            return "TRUE" if value else "FALSE"
        if isinstance(value, (Decimal, float, int)):
            return str(value)
        if isinstance(value, str):
            return "'%s'" % value.replace("'", "''")
        if value is None:
            return "NULL"
        return str(value)

    def prepare_default(self, value):
        return self.quote_value(value)


class DatabaseWrapper(SQLiteDatabaseWrapper):
    vendor = "duckdb"
    display_name = "DuckDB"

    Database = duckdb
    SchemaEditorClass = DatabaseSchemaEditor
    client_class = DatabaseClient
    creation_class = DatabaseCreation
    features_class = DatabaseFeatures
    introspection_class = DatabaseIntrospection
    ops_class = DatabaseOperations

    data_types = {
        **SQLiteDatabaseWrapper.data_types,
        "CharField": "varchar",
        "DateTimeField": "timestamp",
        "PositiveBigIntegerField": "bigint",
        "PositiveIntegerField": "integer",
        "PositiveSmallIntegerField": "smallint",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._in_duckdb_tx = False

    def get_connection_params(self):
        settings_dict = self.settings_dict
        return {
            "database": str(settings_dict["NAME"]),
            "read_only": settings_dict.get("OPTIONS", {}).get("read_only", False),
        }

    def get_database_version(self):
        parts = duckdb.__version__.split(".")
        return tuple(int(p) for p in parts[:3] if p.isdigit())

    @async_unsafe
    def get_new_connection(self, conn_params):
        self._in_duckdb_tx = False
        return duckdb.connect(**conn_params)

    def create_cursor(self, name=None):
        return DuckDBCursorWrapper(self.connection)

    def _set_autocommit(self, autocommit):
        if autocommit and self._in_duckdb_tx:
            try:
                self.connection.execute("COMMIT")
            except Exception:
                pass
            self._in_duckdb_tx = False
        elif not autocommit and not self._in_duckdb_tx:
            self.connection.execute("BEGIN TRANSACTION")
            self._in_duckdb_tx = True

    def _start_transaction_under_autocommit(self):
        if not self._in_duckdb_tx:
            self.connection.execute("BEGIN TRANSACTION")
            self._in_duckdb_tx = True

    def _commit(self):
        if self.connection is not None and self._in_duckdb_tx:
            with self.wrap_database_errors:
                self.connection.execute("COMMIT")
            self._in_duckdb_tx = False

    def _rollback(self):
        if self.connection is not None and self._in_duckdb_tx:
            with self.wrap_database_errors:
                self.connection.execute("ROLLBACK")
            self._in_duckdb_tx = False

    def disable_constraint_checking(self):
        return True

    def enable_constraint_checking(self):
        pass

    def check_constraints(self, table_names=None):
        pass

    def _savepoint_allowed(self):
        return False

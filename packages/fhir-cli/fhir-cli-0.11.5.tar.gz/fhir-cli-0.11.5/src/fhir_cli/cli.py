import os
import shutil
from typing import Iterator

import fire
from colorama import Fore, deinit, init
from psycopg2 import ProgrammingError, connect, sql
from psycopg2.extras import RealDictCursor
from requests import HTTPError

from fhir_cli import (
    DBT_META_TABLE,
    DBT_SCHEMA,
    FHIR_COLUMN_NAME,
    FHIR_DBT_SCHEMA,
    PACKAGE_PATH,
    POSTGRES_DB,
    POSTGRES_HOST,
    POSTGRES_PASSWORD,
    POSTGRES_PORT,
    POSTGRES_USER,
    log,
)
from fhir_cli.admin import Admin
from fhir_cli.dbt import Dbt
from fhir_cli.fhir_resource import FhirResource, FhirValidationError
from utils.compact import dict_compact
from utils.dotty import dotty_dict
from utils.number_print import number_print

CURSOR_ITERSIZE = 20


def get_fhir_resources_from_model(
    cursor, model: str, offset: int = 0, limit: int = 100
) -> Iterator[dict]:
    """get_fhir_resources_from_model looks for a fhir model file and retrieves the Fhir resources

    This function uses a named cursor fetching at most CURSOR_ITERSIZE rows
    at each network roundtrip during iteration on the cursor
    https://www.psycopg.org/docs/cursor.html#cursor.itersize

    Args:
        cursor: a database connection cursor
        model (str): a Fhir model name
        offset (:obj:`int`, optional): an offset for the executed query. Defaults to 0.
        limit (:obj:`int`, optional): a limit for the executed query. Defaults to 100.
    """
    select_fhir_stmt = sql.SQL(
        "SELECT {fhir_column_name} FROM {fhir_model} LIMIT %s OFFSET %s"
    ).format(
        fhir_column_name=sql.Identifier(FHIR_COLUMN_NAME),
        fhir_model=sql.Identifier(model),
    )
    cursor.execute(select_fhir_stmt, (limit, offset))
    for row in cursor:
        yield dotty_dict(dict_compact(row[FHIR_COLUMN_NAME]))


class Cli:
    """a cli to manage your DbtOnFhir project"""

    def __init__(self):
        self.dbt = Dbt()
        self.admin = Admin()

    @staticmethod
    def init(omop=False):
        """Generate a new project

        Args:
            omop (:obj:`bool`, optional): include OMOP DBT models
        """

        shutil.copytree(
            os.path.join(PACKAGE_PATH, "starter"),
            ".",
            ignore=shutil.ignore_patterns("*omop") if not omop else None,
            dirs_exist_ok=True,
        )

    @staticmethod
    def add_omop_models():
        """Add OMOP DBT models"""

        shutil.copytree(os.path.join(PACKAGE_PATH, "starter", "schemas/omop"), "./schemas/omop")

    @staticmethod
    def link(database: str, schema: str, include: tuple[str] = None, exclude: tuple[str] = None):
        """Create a foreign schema from a schema of the source database

        This command uses a foreign data wrapper to access data
        stored in an external server. The module opens a connection and extracts
        a database schema. Subsequently a user can import the data to the local
        database by creating a table or a materialized view selecting from a
        foreign table of a given schema.

        Args:
            database (str): the source database
            schema (str): the source schema
            include (:obj:`tuple` of :obj:`str`, optional): comma separated table names to import
            only foreign tables matching one of the given table names. Other tables existing in
            the foreign schema will be ignored.
            exclude (:obj:`tuple` of :obj:`str`, optional): comma separated table names to exclude
            specified  foreign tables from the import. All tables existing in the foreign
            schema will be imported except the ones listed here.
        """

        if include and exclude:
            log.error("include and exclude options are mutually exclusive")
            return

        conn = connect(
            host=POSTGRES_HOST,
            dbname=POSTGRES_DB,
            port=POSTGRES_PORT,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
        )

        try:
            with conn:
                with conn.cursor() as curs:
                    db_type_stmt = sql.SQL("SELECT db_type FROM {dbt_meta_table}").format(
                        dbt_meta_table=sql.Identifier(DBT_SCHEMA, DBT_META_TABLE)
                    )
                    curs.execute(db_type_stmt)
                    db_type = curs.fetchone()
        except Exception as e:
            conn.close()
            log.error(e)
            return

        schema_stmt = sql.SQL("CREATE SCHEMA IF NOT EXISTS {target_schema}").format(
            target_schema=sql.Identifier(f"{database}_{schema}")
        )

        constraints = sql.SQL("")
        if include:
            included_tables = list(map(lambda table: sql.Identifier(table), include))
            constraints = sql.SQL("LIMIT TO ({included_tables})").format(
                included_tables=sql.SQL(", ").join(included_tables)
            )
        elif exclude:
            excluded_tables = list(map(lambda table: sql.Identifier(table), exclude))
            constraints = sql.SQL("EXCEPT ({excluded_tables})").format(
                excluded_tables=sql.SQL(", ").join(excluded_tables)
            )

        # increase the number of rows prefetched from the oracle db to improve perf.
        # see https://github.com/laurenz/oracle_fdw#foreign-table-options
        options = sql.SQL("OPTIONS (prefetch '10240')") if db_type == "oracle" else sql.SQL("")

        import_stmt = sql.SQL(
            "IMPORT FOREIGN SCHEMA {source_schema} "
            "{constraints} "
            "FROM SERVER {server} INTO {target_schema} "
            "{options}"
        ).format(
            source_schema=sql.Identifier(schema),
            target_schema=sql.Identifier(f"{database}_{schema}"),
            constraints=constraints,
            server=sql.Identifier(f"source_server_{database}"),
            options=options,
        )

        try:
            with conn:
                with conn.cursor() as curs:
                    curs.execute(schema_stmt)
                    curs.execute(import_stmt)
        except Exception as e:
            log.error(e)
        finally:
            conn.close()

    @staticmethod
    def validate(model: str, offset: int = 0, limit: int = 100):
        """Extract a fhir model row and validates the Fhir resource
        against a Fhir server

        Args:
            model (str): should be a valid DBT Fhir model name such as `observation_heartrate`
            offset (:obj:`int`, optional): set an offset to the query. Defaults to 0.
            limit (:obj:`int`, optional): a limit for the executed query. Defaults to 100.
        """
        conn = connect(
            host=POSTGRES_HOST,
            dbname=POSTGRES_DB,
            port=POSTGRES_PORT,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            cursor_factory=RealDictCursor,
            options=f"-c search_path={FHIR_DBT_SCHEMA}",
        )
        cursor = conn.cursor(name="curname")
        try:
            # Function in order to filter ANSI escape sequences on Windows
            # see https://pypi.org/project/colorama/
            init(autoreset=True)
            with conn:
                with cursor:
                    cursor.itersize = CURSOR_ITERSIZE
                    for resource in get_fhir_resources_from_model(cursor, model, offset, limit):
                        fhir = FhirResource(resource)
                        number_print(repr(fhir))
                        try:
                            fhir.validate()
                            # The message will be printed in GREEN, hence the weird sequence
                            # at the beginning and at the end
                            log.info(f"{Fore.GREEN}✅ FHIR resource is valid")
                        except FhirValidationError as e:
                            # Same as above
                            log.error(f"{Fore.RED}❌ FHIR resource is not valid\n{e}")
                        input("Press [Return] for the next result or [Ctrl+c] to quit")
        except (ProgrammingError, HTTPError) as e:
            log.error(e)
        except KeyboardInterrupt:
            pass
        finally:
            conn.close()
            # Stop using Colorama
            # see https://pypi.org/project/colorama/
            deinit()


def run():
    cli = Cli()
    fire.Fire(cli)


if __name__ == "__main__":
    run()

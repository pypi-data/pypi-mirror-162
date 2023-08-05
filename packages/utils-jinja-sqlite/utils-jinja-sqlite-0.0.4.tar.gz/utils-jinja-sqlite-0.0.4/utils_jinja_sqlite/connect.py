import os
import sqlite3
from contextlib import closing
from pathlib import Path
from sqlite3 import Connection, OperationalError
from typing import Iterator

# import aiosqlite
from dotenv import find_dotenv, load_dotenv
from jinja2 import Environment, PackageLoader, select_autoescape
from rich import print

load_dotenv(find_dotenv())


def setup_connection() -> Connection:
    """Gets proper database connection depending on env variables. `local_var` implies a location starting from the Path().home(); `volume_var` implies a Dockerfile."""
    if folder := os.getenv("LOCAL_PATH"):
        conn = sqlite3.connect(Path().home() / folder)
        conn.row_factory = sqlite3.Row
        return conn
    elif volume := os.getenv("DB_FILE"):
        conn = sqlite3.connect(volume)
        conn.row_factory = sqlite3.Row
        return conn
    raise Exception("Not connected to volume nor local file.")


def setup_env(name: str):
    return Environment(
        loader=PackageLoader(name), autoescape=select_autoescape()
    )


def yielded_rows(sql_stmt: str) -> Iterator[dict]:
    """Convert sqlite3 row objects into dictionaries."""
    with closing(setup_connection()) as conn:  # db needs to be open
        with closing(conn.cursor()) as cursor:
            try:
                if cur := cursor.execute(sql_stmt):
                    if rows := cur.fetchall():
                        for row in rows:
                            yield {k: row[k] for k in row.keys()}
            except OperationalError as e:
                raise Exception(f"Could not fetch rows, {e=}")


def get_rows(sql_stmt: str, show_sql: bool = False) -> Iterator[dict]:
    """Source sql statement from Jinja templates."""
    if show_sql:
        print(sql_stmt)
    yield from yielded_rows(sql_stmt)


def get_row(sql_stmt, show_sql: bool = False) -> dict:
    """Get the first dict from all rows that match statement and parameters;
    this is the first row of `get_rows()`, if it exists."""
    try:
        return next(get_rows(sql_stmt, show_sql))
    except StopIteration:
        raise Exception(f"Could not get row via {sql_stmt=}")

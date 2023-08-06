import os
import sqlite3 as sq
from typing import Iterator

import aiosqlite
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

URL = os.getenv("DB_FILE", "test.db")


def get_row(stmt: str) -> dict | None:
    db = sq.connect(URL)
    db.row_factory = sq.Row
    cursor = db.execute(stmt)
    item = cursor.fetchone()
    cursor.close()
    db.close()
    return {k: item[k] for k in item.keys()} if item else None


async def a_row(stmt: str) -> dict | None:
    db = await aiosqlite.connect(URL)
    db.row_factory = aiosqlite.Row
    cursor = await db.execute(stmt)
    item = await cursor.fetchone()
    await cursor.close()
    await db.close()
    return {k: item[k] for k in item.keys()} if item else None


def get_rows(stmt: str) -> Iterator[dict]:
    db = sq.connect(URL)
    db.row_factory = sq.Row
    cursor = db.execute(stmt)
    items = cursor.fetchall()
    cursor.close()
    db.close()
    return ({k: item[k] for k in item.keys()} for item in items)


async def a_rows(stmt: str) -> Iterator[dict]:
    db = await aiosqlite.connect(URL)
    db.row_factory = aiosqlite.Row
    cursor = await db.execute(stmt)
    items = await cursor.fetchall()
    await cursor.close()
    await db.close()
    return ({k: item[k] for k in item.keys()} for item in items)

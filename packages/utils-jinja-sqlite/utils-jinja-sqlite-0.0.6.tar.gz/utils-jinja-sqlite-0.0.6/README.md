# Utils for Jinja & sqlite

Must setup an .env pointing to a database file `DB_FILE`; otherwise, will default to `test.db`.

## Setup Jinja Environment to fetch via .sql file

Assumes a basic Jinja environment has been setup:

```python
from jinja2 import Environment
assert isinstance(env, Environment)
```

### Sync

Query the environment using `sqlite3`,*viz*:

```python
from utils_jinja_sqlite import get_rows, get_row
# base
params = dict(a="'hello world'")
sql_stmt = env.get_template("test.sql").render(params)

# get all
rows = get_rows(sql_stmt=sql_stmt)
type(rows) # generator

# get one
row = get_row(sql_stmt=sql_stmt) # gets only the first row
type(row) # dict
```

### Async

Query the environment using a `aiosqlite3`,*viz*:

```python
from utils_jinja_sqlite import get_rows, get_row
import asyncio
# base
params = dict(a="'hello world'")
sql_stmt = env.get_template("test.sql").render(params)

# get all
rows = a_rows(sql_stmt=sql_stmt)
type(rows) # co-routine
rows_result = asyncio.run(rows)
type(rows_result) # generator

# get one
row = a_row(sql_stmt=sql_stmt)
type(row) # co-routine
row_result = asyncio.run(row)
type(row_result) # dict

```

Note that this will not work:

```python
for first_stmt_row in get_rows(sql_stmt=sql_stmt1):
    for second_stmt_row in get_rows(sql_stmt=sql_stmt2):
        ... # the first sql_stmt has not yet terminated
```

## SQL string literal binder funcs

Instead of quoting a string literal can use a helper function

```python
from utils_jinja_sqlite import quote_sql_string
params = dict(a=quote_sql_string(hello world))
```

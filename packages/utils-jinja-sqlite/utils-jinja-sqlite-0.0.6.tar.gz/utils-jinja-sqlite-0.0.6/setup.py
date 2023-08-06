# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['utils_jinja_sqlite']

package_data = \
{'': ['*']}

install_requires = \
['Jinja2>=3.1.2,<4.0.0',
 'aiosqlite>=0.17.0,<0.18.0',
 'python-dotenv>=0.19,<0.20',
 'rich>=12.2,<13.0',
 'sqlparse>=0.4.2,<0.5.0']

setup_kwargs = {
    'name': 'utils-jinja-sqlite',
    'version': '0.0.6',
    'description': 'Common helper utility functions used when connecting to sqlite databases and binding SQL values from python variables.',
    'long_description': '# Utils for Jinja & sqlite\n\nMust setup an .env pointing to a database file `DB_FILE`; otherwise, will default to `test.db`.\n\n## Setup Jinja Environment to fetch via .sql file\n\nAssumes a basic Jinja environment has been setup:\n\n```python\nfrom jinja2 import Environment\nassert isinstance(env, Environment)\n```\n\n### Sync\n\nQuery the environment using `sqlite3`,*viz*:\n\n```python\nfrom utils_jinja_sqlite import get_rows, get_row\n# base\nparams = dict(a="\'hello world\'")\nsql_stmt = env.get_template("test.sql").render(params)\n\n# get all\nrows = get_rows(sql_stmt=sql_stmt)\ntype(rows) # generator\n\n# get one\nrow = get_row(sql_stmt=sql_stmt) # gets only the first row\ntype(row) # dict\n```\n\n### Async\n\nQuery the environment using a `aiosqlite3`,*viz*:\n\n```python\nfrom utils_jinja_sqlite import get_rows, get_row\nimport asyncio\n# base\nparams = dict(a="\'hello world\'")\nsql_stmt = env.get_template("test.sql").render(params)\n\n# get all\nrows = a_rows(sql_stmt=sql_stmt)\ntype(rows) # co-routine\nrows_result = asyncio.run(rows)\ntype(rows_result) # generator\n\n# get one\nrow = a_row(sql_stmt=sql_stmt)\ntype(row) # co-routine\nrow_result = asyncio.run(row)\ntype(row_result) # dict\n\n```\n\nNote that this will not work:\n\n```python\nfor first_stmt_row in get_rows(sql_stmt=sql_stmt1):\n    for second_stmt_row in get_rows(sql_stmt=sql_stmt2):\n        ... # the first sql_stmt has not yet terminated\n```\n\n## SQL string literal binder funcs\n\nInstead of quoting a string literal can use a helper function\n\n```python\nfrom utils_jinja_sqlite import quote_sql_string\nparams = dict(a=quote_sql_string(hello world))\n```\n',
    'author': 'Marcelino G. Veloso III',
    'author_email': 'mars@veloso.one',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)

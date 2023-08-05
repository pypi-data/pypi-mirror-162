# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['utils_jinja_sqlite']

package_data = \
{'': ['*']}

install_requires = \
['Jinja2>=3.1.2,<4.0.0', 'python-dotenv>=0.19,<0.20', 'rich>=12.2,<13.0']

setup_kwargs = {
    'name': 'utils-jinja-sqlite',
    'version': '0.0.4',
    'description': 'Common helper utility functions used when connecting to sqlite databases and binding SQL values from python variables.',
    'long_description': '# Utils for Jinja & sqlite\n\nMust setup an .env pointing to the database folder, e.g.:\n\n`LOCAL_PATH="code/corpus-db/ph.db"`\n\nThis will enable creating a connection via `setup_connection()`:\n\n```python\nfrom utils_jinja_sqlite import setup_connection\nconn = setup_connection()\n```\n\n## Setup Jinja Environment to fetch via .sql file\n\nCreate a basic Jinja environment with `setup_env()`:\n\n```python\nfrom utils_jinja_sqlite import setup_env, get_rows, get_row\nenv = setup_env("corpus_db") # will utilize templates found in corpus_db\nparams = dict(a="\'hello world\'")\nsql_stmt = env.get_template("test.sql").render(params)\nget_rows(sql_stmt=sql_stmt) # will open a connection, yield results of the query\nget_row(sql_stmt=sql_stmt) # gets only the first row\n```\n\nNote that this will not work:\n\n```python\nfor first_stmt_row in get_rows(sql_stmt=sql_stmt1):\n    for second_stmt_row in get_rows(sql_stmt=sql_stmt2):\n        ... # the first sql_stmt has not yet terminated\n```\n\n## SQL string literal binder funcs\n\nInstead of quoting a string literal can use a helper function\n\n```python\nfrom utils_jinja_sqlite import quote_sql_string\nparams = dict(a=quote_sql_string(hello world))\n```\n\n## Cleaner syntax\n\nsqlparse is not included but the following can be used as a template for debugging statements:\n\n```python\nimport sqlparse\nfrom jinja2 import Environment\nfrom rich.syntax import Syntax\n\n\ndef format_sql(sql_stmt: str) -> Syntax:\n    """Helper debug function to display the SQL properly; often used in Jupyter\n    notebooks."""\n    parsed = sqlparse.format(\n        sql_stmt,\n        comma_first=True,\n        reindent=True,\n        wrap_after=60,\n    )\n    return Syntax(code=parsed, lexer="sql")\n\n\ndef nb_stmt(env: Environment, path: str, params={}):\n    """Display Jinja-configured and SQLParse-prettified query statement via\n    Rich in Jupyter notebooks."""\n    return format_sql(env.get_template(path).render(params))\n\n```\n',
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

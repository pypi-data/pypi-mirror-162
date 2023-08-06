import sqlparse
from jinja2 import Environment
from rich.syntax import Syntax


def format_sql(sql_stmt: str) -> Syntax:
    """Helper debug function to display the SQL properly; often used in Jupyter
    notebooks."""
    parsed = sqlparse.format(
        sql_stmt,
        comma_first=True,
        reindent=True,
        wrap_after=60,
    )
    return Syntax(code=parsed, lexer="sql")


def nb_stmt(env: Environment, path: str, params={}):
    """Display Jinja-configured and SQLParse-prettified query statement via
    Rich in Jupyter notebooks."""
    return format_sql(env.get_template(path).render(params))

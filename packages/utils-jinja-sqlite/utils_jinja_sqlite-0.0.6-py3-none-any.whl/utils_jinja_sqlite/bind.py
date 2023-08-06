import re


def clean_fts_search_term(value) -> str:
    """Thin wrapper around  the `quote_sql_string()` and the `custom_escape_fts()`"""
    return quote_sql_string(custom_escape_fts(value))


def quote_sql_string(value: str):
    """See https://towardsdatascience.com/a-simple-approach-to-templated-sql-
    queries-in-python-adc4f0dc511 If `value` is a string type, escapes single
    quotes in the string and returns the string enclosed in single quotes."""
    new_value = str(value)
    new_value = new_value.replace("'", "''")
    return "'{}'".format(new_value)


_escape_fts_re = re.compile(r'\s+|(".*?")')

_quoted_operators_fts_re = re.compile(
    r"""
    ^
    (
        "AND"|
        "OR"|
        "NOT"|
        "\(+"| # handles (((
        "\)+" # handles )))
    )
    $
    """,
    re.X,
)


def custom_escape_fts(query: str):
    """Modifies datasette's escape-fts here: https://github.com/simonw/datasett
    e/blob/8e18c7943181f228ce5ebcea48deb59ce50bee1f/datasette/utils/__init__.py
    .

    #L818-L829.
    """

    if query.count('"') % 2:
        query += '"'
    bits = _escape_fts_re.split(query)
    bits = [b for b in bits if b and b != '""']
    quoted_bits = [
        '"{}"'.format(bit) if not bit.startswith('"') else bit for bit in bits
    ]
    # this part ensures that any bit that matches a boolean / operator for FTS operations is reverted back
    for idx, qb in enumerate(quoted_bits):
        if _quoted_operators_fts_re.fullmatch(qb):
            quoted_bits[idx] = qb.strip('"')  # remove quotes
    return " ".join(quoted_bits)


def sql_strings_translator(data: dict):
    """SQL statements may contain variables which, if not populated, will be considered NULL. Pairing this with the OR pattern can render the expression as `True`, e.g.

    SELECT column_a
    FROM tbl_name_test
    WHERE (:x is NULL OR column_a = :x) -- if :x is not supplied, the result set will be all column_a's from tbl_name_test since the where clause is rendered `True`

    This can be paired with other parameters, like so:

    SELECT column_a, column_b
    FROM tbl_name_test
    WHERE (:x is NULL OR column_a = :x)  -- if :x is NULL (or not supplied) but :y is supplied then the WHERE clause becomes operative only with respect to the second SQL expression.
    AND (:y is NULL OR column_b = :y)

    In order for :x to be considered null from Python's perspective, it needs to be removed from possible parameters, e.g. if a Python variable evalutes to an empty strings or None, remove it from parameters.

    Otherwise the SQL statement will resolve as follows:

    SELECT column_a
    FROM tbl_name_test
    WHERE (None is NULL OR column_a = None)  -- None is not a valid keyword in SQLite

    SQL will translate bind parameters without values as NULL, see https://www.sqlite.org/c3ref/bind_blob.html, speaking of :VVV

    > "The third argument is the value to bind to the parameter. If the third parameter to sqlite3_bind_text() or sqlite3_bind_text16() or sqlite3_bind_blob() is a NULL pointer then the fourth parameter is ignored and the end result is the same as sqlite3_bind_null()."

    In addition, each value is first converted into a python string and eventually quoted to be useful as a SQL string literal.
    """
    return {
        k: f"{quote_sql_string(stripped_v)}"
        for k, v in data.items()
        if v  # only include in the new dictionary if this exists
        and (new_v := str(v))  # converts values 1.1.1.2 into '1.1.1.2'
        and (stripped_v := new_v.strip())  #  empty strings "" are excluded
    }

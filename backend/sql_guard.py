import sqlglot
from sqlglot import expressions as exp


class SqlGuardError(Exception):
    pass


def guard_sql(sql: str, max_rows: int = 1000) -> str:
    """Validate SQL is a single read-only SELECT; inject LIMIT on raw-row queries.

    Raises SqlGuardError on anything that could mutate or is unsafe.
    Returns the (possibly LIMIT-augmented) SQL string.
    """
    try:
        statements = sqlglot.parse(sql, read="duckdb")
    except Exception as e:  # noqa: BLE001
        raise SqlGuardError(f"could not parse SQL: {e}") from e

    statements = [s for s in statements if s is not None]
    if len(statements) != 1:
        raise SqlGuardError("only a single statement is allowed")

    stmt = statements[0]
    if not isinstance(stmt, (exp.Select, exp.With, exp.Union)):
        raise SqlGuardError(f"only SELECT queries are allowed, got {type(stmt).__name__}")

    forbidden = (
        exp.Insert, exp.Update, exp.Delete, exp.Drop, exp.Create,
        exp.Alter, exp.Command, exp.Copy, exp.Attach,
    )
    for node in stmt.walk():
        if isinstance(node, forbidden):
            raise SqlGuardError(f"forbidden operation: {type(node).__name__}")

    # Inject LIMIT only on a top-level SELECT that has no aggregation/group by.
    select = stmt if isinstance(stmt, exp.Select) else stmt.find(exp.Select)
    has_group = select.args.get("group") is not None if select else False
    has_agg = bool(select.find(exp.AggFunc)) if select else False
    has_limit = select.args.get("limit") is not None if select else False
    if select is not None and not has_group and not has_agg and not has_limit:
        select.set("limit", exp.Limit(expression=exp.Literal.number(max_rows)))

    return stmt.sql(dialect="duckdb")

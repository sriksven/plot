import pytest
from backend.sql_guard import guard_sql, SqlGuardError


def test_allows_select():
    out = guard_sql("SELECT county_location, COUNT(*) FROM collisions GROUP BY 1")
    assert out.lower().startswith("select")


def test_allows_with_cte():
    out = guard_sql("WITH t AS (SELECT 1 AS x) SELECT * FROM t")
    assert "select" in out.lower()


@pytest.mark.parametrize("sql", [
    "DELETE FROM collisions",
    "UPDATE collisions SET x=1",
    "INSERT INTO collisions VALUES (1)",
    "DROP TABLE collisions",
    "ALTER TABLE collisions ADD COLUMN x INT",
    "CREATE TABLE t (x INT)",
    "ATTACH 'evil.db' AS e",
    "COPY collisions TO 'x.csv'",
    "PRAGMA database_list",
])
def test_rejects_mutations_and_ddl(sql):
    with pytest.raises(SqlGuardError):
        guard_sql(sql)


def test_rejects_multiple_statements():
    with pytest.raises(SqlGuardError):
        guard_sql("SELECT 1; SELECT 2")


def test_injects_limit_on_raw_rows():
    out = guard_sql("SELECT * FROM collisions", max_rows=500)
    assert "limit 500" in out.lower()


def test_does_not_inject_limit_on_aggregate():
    out = guard_sql("SELECT county_location, COUNT(*) FROM collisions GROUP BY 1")
    assert "limit" not in out.lower()


def test_does_not_double_limit():
    out = guard_sql("SELECT * FROM collisions LIMIT 10", max_rows=500)
    assert out.lower().count("limit") == 1

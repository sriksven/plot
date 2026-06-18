from backend import db


def test_run_query_returns_columns_and_rows():
    result = db.run_query(
        "SELECT county_location AS county, COUNT(*) AS n "
        "FROM collisions GROUP BY 1 ORDER BY n DESC LIMIT 1"
    )
    assert result.columns == ["county", "n"]
    assert result.rows[0][0] == "los angeles"
    assert result.rows[0][1] == 2851925
    assert result.query_ms >= 0


def test_views_registered_for_all_tables():
    for t in ["collisions", "parties", "victims", "case_ids"]:
        r = db.run_query(f"SELECT COUNT(*) AS n FROM {t}")
        assert r.rows[0][0] > 0

from backend import pipeline, llm


def test_answer_question_happy_path(monkeypatch):
    def fake_generate(question):
        return llm.SqlGen(
            sql="SELECT county_location AS county, COUNT(*) AS n "
                "FROM collisions GROUP BY 1 ORDER BY n DESC LIMIT 3",
            chart_type="bar", restatement="top counties",
            usage=llm.Usage(100, 20, 120),
        )

    monkeypatch.setattr(pipeline.llm, "generate_sql", fake_generate)
    result = pipeline.answer_question("which county has most collisions?")
    assert result.sql.lower().startswith("select")
    assert result.columns == ["county", "n"]
    assert result.rows[0][0] == "los angeles"
    assert result.chart_spec["type"] == "bar"
    assert result.error is None


def test_llm_exception_returns_error_not_raises(monkeypatch):
    def boom(question):
        raise RuntimeError("401 Incorrect API key provided")

    monkeypatch.setattr(pipeline.llm, "generate_sql", boom)
    result = pipeline.answer_question("anything")
    # must not raise; must surface a clean error so the UI never hangs
    assert result.error is not None
    assert "401" in result.error
    assert result.rows == []


def test_regenerates_once_on_bad_sql(monkeypatch):
    calls = {"n": 0}

    def fake_generate(question):
        calls["n"] += 1
        if calls["n"] == 1:
            return llm.SqlGen("DELETE FROM collisions", "none", "x",
                              llm.Usage(10, 5, 15))
        return llm.SqlGen("SELECT COUNT(*) AS n FROM collisions", "none", "x",
                          llm.Usage(10, 5, 15))

    monkeypatch.setattr(pipeline.llm, "generate_sql", fake_generate)
    result = pipeline.answer_question("count crashes")
    assert calls["n"] == 2
    assert result.regenerated is True
    assert result.error is None

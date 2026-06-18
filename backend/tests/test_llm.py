from backend import llm


class FakeMessage:
    def __init__(self, content):
        self.content = content


class FakeChoice:
    def __init__(self, content):
        self.message = FakeMessage(content)


class FakeUsage:
    prompt_tokens = 100
    completion_tokens = 20
    total_tokens = 120


class FakeResp:
    def __init__(self, content):
        self.choices = [FakeChoice(content)]
        self.usage = FakeUsage()


def test_generate_sql_parses_json(monkeypatch):
    payload = (
        '{"sql": "SELECT county_location, COUNT(*) AS n FROM collisions '
        'GROUP BY 1 ORDER BY n DESC LIMIT 5", "chart_type": "bar", '
        '"restatement": "Top counties by collisions"}'
    )

    def fake_create(**kwargs):
        return FakeResp(payload)

    monkeypatch.setattr(llm, "_chat_create", fake_create)
    out = llm.generate_sql("which county has the most collisions?")
    assert out.sql.lower().startswith("select")
    assert out.chart_type == "bar"
    assert out.usage.total_tokens == 120

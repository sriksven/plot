import pytest
from fastapi.testclient import TestClient
from backend import main, pipeline, llm


@pytest.fixture(autouse=True)
def _no_metrics_writes(monkeypatch):
    """Endpoint tests must not pollute the real metrics log."""
    monkeypatch.setattr(main.metrics, "record", lambda *a, **k: None)


def _fake_result():
    return pipeline.AnswerResult(
        question="q", restatement="top counties",
        sql="SELECT county_location AS county, COUNT(*) AS n FROM collisions GROUP BY 1 LIMIT 3",
        columns=["county", "n"], rows=[["los angeles", 2851925]],
        chart_spec={"type": "bar", "x": ["los angeles"], "y": [2851925],
                    "x_label": "county", "y_label": "n"},
        chart_type="bar", regenerated=False,
        usage=llm.Usage(100, 20, 120), query_ms=15.0, error=None,
    )


def test_chat_endpoint(monkeypatch):
    monkeypatch.setattr(main.pipeline, "answer_question", lambda q: _fake_result())
    client = TestClient(main.app)
    r = client.post("/chat", json={"question": "which county has most collisions?"})
    assert r.status_code == 200
    body = r.json()
    assert body["sql"].lower().startswith("select")
    assert body["columns"] == ["county", "n"]
    assert body["chart_spec"]["type"] == "bar"


def test_stream_endpoint_emits_events(monkeypatch):
    monkeypatch.setattr(main.pipeline, "answer_question", lambda q: _fake_result())
    monkeypatch.setattr(main.llm, "stream_summary",
                        lambda q, c, r: iter(["Los ", "Angeles ", "leads."]))
    client = TestClient(main.app)
    with client.stream("POST", "/chat/stream",
                       json={"question": "q"}) as resp:
        text = "".join(resp.iter_text())
    assert "event: sql" in text
    assert "event: rows" in text
    assert "event: answer" in text
    assert "event: done" in text

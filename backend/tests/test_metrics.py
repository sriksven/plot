import json
from backend import metrics


def test_record_appends_jsonl(tmp_path):
    rec = metrics.RequestMetrics(
        ts="2026-06-18T10:00:00", question="q", sql="SELECT 1",
        sql_valid=True, regenerated=False, model="gpt-4o",
        prompt_tokens=100, completion_tokens=20, total_tokens=120,
        llm_sql_ms=800, query_ms=30, llm_summary_ms=600, total_ms=1500,
        row_count=5, chart_type="bar", error=None,
    )
    metrics.record(rec, metrics_dir=str(tmp_path))
    files = list(tmp_path.glob("logs/requests-*.jsonl"))
    assert len(files) == 1
    line = json.loads(files[0].read_text().strip())
    assert line["question"] == "q"
    assert line["est_cost_usd"] > 0
    assert line["total_tokens"] == 120

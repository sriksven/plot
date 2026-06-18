import json
import importlib.util


def _load_report():
    spec = importlib.util.spec_from_file_location("report", "metrics/report.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_report_aggregates(tmp_path):
    logs = tmp_path / "logs"
    logs.mkdir()
    rows = [
        {"ts": "2026-06-18T10:00:00", "question": "q1", "sql": "SELECT 1", "sql_valid": True,
         "regenerated": False, "model": "gpt-4o", "prompt_tokens": 100, "completion_tokens": 20,
         "total_tokens": 120, "est_cost_usd": 0.0005, "llm_sql_ms": 800, "query_ms": 30,
         "llm_summary_ms": 600, "total_ms": 1500, "row_count": 5, "chart_type": "bar", "error": None},
        {"ts": "2026-06-18T10:01:00", "question": "q2", "sql": "SELECT 2", "sql_valid": True,
         "regenerated": True, "model": "gpt-4o", "prompt_tokens": 200, "completion_tokens": 40,
         "total_tokens": 240, "est_cost_usd": 0.0009, "llm_sql_ms": 900, "query_ms": 50,
         "llm_summary_ms": 700, "total_ms": 1800, "row_count": 3, "chart_type": "line", "error": None},
    ]
    (logs / "requests-2026-06-18.jsonl").write_text(
        "\n".join(json.dumps(r) for r in rows) + "\n")
    report = _load_report()
    md = report.build_report(str(tmp_path))
    assert "Requests: 2" in md
    assert "gpt-4o" in md
    assert "$0.0014" in md or "0.0014" in md  # total cost


def test_report_handles_empty(tmp_path):
    (tmp_path / "logs").mkdir()
    report = _load_report()
    md = report.build_report(str(tmp_path))
    assert "Requests: 0" in md

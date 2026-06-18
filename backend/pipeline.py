from dataclasses import dataclass
from typing import Optional
from backend import llm, db
from backend.sql_guard import guard_sql, SqlGuardError
from backend.chart import build_chart_spec
from backend.config import load_settings

_settings = load_settings()


@dataclass
class AnswerResult:
    question: str
    restatement: str
    sql: str
    columns: list
    rows: list
    chart_spec: dict
    chart_type: str
    regenerated: bool
    usage: llm.Usage
    query_ms: float
    error: Optional[str]


def answer_question(question: str) -> AnswerResult:
    regenerated = False
    last_error = None
    last_sql = ""
    total_usage = llm.Usage(0, 0, 0)
    prompt = question

    for attempt in range(2):
        try:
            gen = llm.generate_sql(prompt)
            total_usage = llm.Usage(
                total_usage.prompt_tokens + gen.usage.prompt_tokens,
                total_usage.completion_tokens + gen.usage.completion_tokens,
                total_usage.total_tokens + gen.usage.total_tokens,
            )
            last_sql = gen.sql
            safe_sql = guard_sql(gen.sql, max_rows=_settings.max_raw_rows)
            qr = db.run_query(safe_sql)
            chart_spec = build_chart_spec(gen.chart_type, qr.columns, qr.rows)
            return AnswerResult(
                question=question, restatement=gen.restatement, sql=safe_sql,
                columns=qr.columns, rows=qr.rows, chart_spec=chart_spec,
                chart_type=chart_spec["type"], regenerated=regenerated,
                usage=total_usage, query_ms=qr.query_ms, error=None,
            )
        except Exception as e:  # noqa: BLE001 — any failure (LLM auth, SQL, exec)
            last_error = str(e)
            if attempt == 0:
                regenerated = True
                prompt = f"{question}\n\nPrevious SQL failed: {last_error}. Fix it."

    return AnswerResult(
        question=question, restatement=question, sql=last_sql, columns=[], rows=[],
        chart_spec={"type": "none"}, chart_type="none", regenerated=regenerated,
        usage=total_usage, query_ms=0.0, error=last_error,
    )

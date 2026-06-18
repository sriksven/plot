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
    gen = llm.generate_sql(question)
    total_usage = gen.usage

    for attempt in range(2):
        try:
            safe_sql = guard_sql(gen.sql, max_rows=_settings.max_raw_rows)
            qr = db.run_query(safe_sql)
            chart_spec = build_chart_spec(gen.chart_type, qr.columns, qr.rows)
            return AnswerResult(
                question=question, restatement=gen.restatement, sql=safe_sql,
                columns=qr.columns, rows=qr.rows, chart_spec=chart_spec,
                chart_type=chart_spec["type"], regenerated=regenerated,
                usage=total_usage, query_ms=qr.query_ms, error=None,
            )
        except (SqlGuardError, Exception) as e:  # noqa: BLE001
            last_error = str(e)
            if attempt == 0:
                regenerated = True
                gen = llm.generate_sql(
                    f"{question}\n\nPrevious SQL failed: {last_error}. Fix it."
                )
                total_usage = llm.Usage(
                    total_usage.prompt_tokens + gen.usage.prompt_tokens,
                    total_usage.completion_tokens + gen.usage.completion_tokens,
                    total_usage.total_tokens + gen.usage.total_tokens,
                )

    return AnswerResult(
        question=question, restatement=question, sql=gen.sql, columns=[], rows=[],
        chart_spec={"type": "none"}, chart_type="none", regenerated=regenerated,
        usage=total_usage, query_ms=0.0, error=last_error,
    )

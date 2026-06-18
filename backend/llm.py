import json
from dataclasses import dataclass
from openai import OpenAI
from backend.config import load_settings
from backend.data_dictionary import build_schema_prompt

_settings = load_settings()
_client = None


def _client_instance():
    global _client
    if _client is None:
        _client = OpenAI(api_key=_settings.openai_api_key)
    return _client


def _chat_create(**kwargs):
    """Indirection point so tests can monkeypatch the OpenAI call."""
    return _client_instance().chat.completions.create(**kwargs)


@dataclass
class Usage:
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


@dataclass
class SqlGen:
    sql: str
    chart_type: str
    restatement: str
    usage: Usage


_SYS = build_schema_prompt() + """

Return ONLY a JSON object with keys:
  "sql": a single DuckDB SELECT query answering the question,
  "chart_type": one of "bar","line","pie","none",
  "restatement": a one-sentence restatement of the question.
No markdown, no code fences.
"""


def generate_sql(question: str) -> SqlGen:
    resp = _chat_create(
        model=_settings.model,
        messages=[
            {"role": "system", "content": _SYS},
            {"role": "user", "content": question},
        ],
        temperature=0,
        response_format={"type": "json_object"},
    )
    data = json.loads(resp.choices[0].message.content)
    u = resp.usage
    return SqlGen(
        sql=data["sql"],
        chart_type=data.get("chart_type", "bar"),
        restatement=data.get("restatement", question),
        usage=Usage(u.prompt_tokens, u.completion_tokens, u.total_tokens),
    )


def stream_summary(question: str, columns: list, rows: list):
    """Yield prose summary tokens for the result. Used by the SSE endpoint."""
    preview = {"columns": columns, "rows": rows[:50]}
    stream = _chat_create(
        model=_settings.model,
        messages=[
            {"role": "system", "content":
             "You explain SQL query results about California traffic collisions "
             "in 1-3 concise sentences. State the key number(s). Note caveats only "
             "if important (e.g. counts reflect popularity, not risk)."},
            {"role": "user", "content":
             f"Question: {question}\nResult: {json.dumps(preview)}"},
        ],
        temperature=0.2,
        stream=True,
    )
    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta

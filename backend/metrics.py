import os
import json
from dataclasses import dataclass, asdict
from typing import Optional
from backend.config import load_settings

_settings = load_settings()


@dataclass
class RequestMetrics:
    ts: str
    question: str
    sql: str
    sql_valid: bool
    regenerated: bool
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    llm_sql_ms: float
    query_ms: float
    llm_summary_ms: float
    total_ms: float
    row_count: int
    chart_type: str
    error: Optional[str]


def _date_from_ts(ts: str) -> str:
    return ts.split("T")[0] if "T" in ts else ts[:10]


def record(rec: RequestMetrics, metrics_dir: str = None) -> None:
    metrics_dir = metrics_dir or _settings.metrics_dir
    logs_dir = os.path.join(metrics_dir, "logs")
    os.makedirs(logs_dir, exist_ok=True)
    row = asdict(rec)
    row["est_cost_usd"] = round(
        rec.prompt_tokens / 1000 * _settings.price_prompt_per_1k
        + rec.completion_tokens / 1000 * _settings.price_completion_per_1k,
        6,
    )
    path = os.path.join(logs_dir, f"requests-{_date_from_ts(rec.ts)}.jsonl")
    with open(path, "a") as f:
        f.write(json.dumps(row) + "\n")

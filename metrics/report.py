"""Aggregate metrics/logs/*.jsonl into metrics/REPORT.md."""
import os
import sys
import glob
import json
import statistics


def _percentile(values, p):
    if not values:
        return 0
    s = sorted(values)
    k = int(round((p / 100) * (len(s) - 1)))
    return s[k]


def _load(metrics_dir):
    rows = []
    for path in glob.glob(os.path.join(metrics_dir, "logs", "requests-*.jsonl")):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line:
                    rows.append(json.loads(line))
    return rows


def build_report(metrics_dir: str) -> str:
    rows = _load(metrics_dir)
    n = len(rows)
    if n == 0:
        return "# SWITRS Chatbot — Metrics Report\n\nRequests: 0\n"
    success = sum(1 for r in rows if not r.get("error"))
    regen = sum(1 for r in rows if r.get("regenerated"))
    cost = sum(r.get("est_cost_usd", 0) for r in rows)
    tok = sum(r.get("total_tokens", 0) for r in rows)
    models = sorted({r.get("model", "?") for r in rows})

    def col(name):
        return [r.get(name, 0) for r in rows]

    lines = [
        "# SWITRS Chatbot — Metrics Report",
        "",
        f"Requests: {n}   Success: {100*success/n:.1f}%   "
        f"Regenerated: {100*regen/n:.1f}%",
        f"Model(s): {', '.join(models)}",
        f"LLM tokens: {tok:,}   Total cost: ${cost:.4f}   "
        f"Avg cost/request: ${cost/n:.4f}",
        "",
        "Latency (ms)      p50      p95",
    ]
    for metric in ["llm_sql_ms", "query_ms", "llm_summary_ms", "total_ms"]:
        vals = col(metric)
        lines.append(f"  {metric:<14}{_percentile(vals,50):>6.0f}   "
                     f"{_percentile(vals,95):>6.0f}")
    avg_rows = statistics.mean(col("row_count"))
    errors = [r.get("error") for r in rows if r.get("error")]
    lines += ["", f"Query health: avg {avg_rows:.0f} rows   errors: {len(errors)}"]
    slow = sorted(rows, key=lambda r: r.get("query_ms", 0), reverse=True)[:10]
    lines += ["", "Slowest queries (ms):"]
    for r in slow:
        lines.append(f"  {r.get('query_ms',0):>6.0f}  {r.get('question','')[:60]}")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    metrics_dir = sys.argv[1] if len(sys.argv) > 1 else "metrics"
    md = build_report(metrics_dir)
    out = os.path.join(metrics_dir, "REPORT.md")
    with open(out, "w") as f:
        f.write(md)
    print(md)
    print(f"\nWritten to {out}")

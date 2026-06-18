import json
import time
import asyncio
from datetime import datetime, timezone
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from backend import pipeline, llm, metrics

app = FastAPI(title="SWITRS Chatbot")
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
)


class ChatRequest(BaseModel):
    question: str


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def _record(result, total_ms, llm_summary_ms=0.0):
    metrics.record(metrics.RequestMetrics(
        ts=_utcnow(), question=result.question, sql=result.sql,
        sql_valid=result.error is None, regenerated=result.regenerated,
        model=llm._settings.model,
        prompt_tokens=result.usage.prompt_tokens,
        completion_tokens=result.usage.completion_tokens,
        total_tokens=result.usage.total_tokens,
        llm_sql_ms=max(total_ms - result.query_ms - llm_summary_ms, 0),
        query_ms=result.query_ms, llm_summary_ms=llm_summary_ms,
        total_ms=total_ms, row_count=len(result.rows),
        chart_type=result.chart_type, error=result.error,
    ))


@app.post("/chat")
async def chat(req: ChatRequest):
    start = time.time()
    result = await asyncio.to_thread(pipeline.answer_question, req.question)
    total_ms = (time.time() - start) * 1000
    _record(result, total_ms)
    return {
        "question": result.question, "restatement": result.restatement,
        "sql": result.sql, "columns": result.columns, "rows": result.rows,
        "chart_spec": result.chart_spec, "error": result.error,
    }


def _sse(event: str, data) -> str:
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


@app.post("/chat/stream")
async def chat_stream(req: ChatRequest):
    async def gen():
        start = time.time()
        yield _sse("status", {"stage": "thinking"})
        result = await asyncio.to_thread(pipeline.answer_question, req.question)
        yield _sse("sql", {"sql": result.sql, "restatement": result.restatement})
        if result.error:
            yield _sse("error", {"message": result.error})
            _record(result, (time.time() - start) * 1000)
            yield _sse("done", {})
            return
        yield _sse("status", {"stage": "querying"})
        yield _sse("rows", {"columns": result.columns, "rows": result.rows,
                            "chart_spec": result.chart_spec})
        s_start = time.time()
        for token in llm.stream_summary(result.question, result.columns, result.rows):
            yield _sse("answer", {"token": token})
        llm_summary_ms = (time.time() - s_start) * 1000
        _record(result, (time.time() - start) * 1000, llm_summary_ms)
        yield _sse("done", {})

    return StreamingResponse(gen(), media_type="text/event-stream")

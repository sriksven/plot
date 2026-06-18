# SWITRS Collision Chatbot ("plot")

A natural-language chatbot over California traffic collision data (SWITRS, 2001–2021,
9.4M crashes). Ask a question; it generates SQL (**shown as proof**), runs it on a fast
DuckDB/Parquet engine, and returns a **chart**, a **result table**, and a
**streaming prose answer**.

## How it works
```
question → GPT-4o (grounded by a data dictionary) → SQL
        → read-only guard (SELECT-only, LIMIT-injected)
        → DuckDB over Parquet (20–75ms) → rows
        → chart + streaming summary
```
Streamed over Server-Sent Events so the UI shows each stage as it's ready — SQL first,
then table + chart, then the answer typing in.

## Setup
```bash
cp .env.example .env                              # add your OPENAI_API_KEY
python3 -m pip install -r backend/requirements.txt
python3 scripts/convert_to_parquet.py             # one-time, ~65s (9.3GB → 523MB)
python3 -m uvicorn backend.main:app --port 8000   # backend
cd frontend && npm install && npm run dev         # frontend (separate terminal)
```
Full steps: `docs/06-running-locally.md`.

## Stack
Python · FastAPI · DuckDB · sqlglot · OpenAI (gpt-4o) · React · Vite · Plotly

## Tests
```bash
python3 -m pytest backend/tests/ -v   # 31 tests; golden tests need a live API key
```

## Metrics
Every request logs tokens, cost, and per-stage latency to `metrics/logs/` (gitignored).
```bash
python3 metrics/report.py             # → metrics/REPORT.md
```

## Safety
- DuckDB opens Parquet **read-only**; the SQL guard rejects all mutations/DDL.
- Secrets live in `.env` (gitignored). `.env.example` holds placeholders only.

Detailed build docs are in `docs/` (gitignored per project convention).

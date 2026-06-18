import time
from dataclasses import dataclass
import duckdb
from backend.config import load_settings

_settings = load_settings()
_con = None


@dataclass
class QueryResult:
    columns: list
    rows: list
    query_ms: float


def _connection():
    """Lazily create a DuckDB connection with a view per parquet table."""
    global _con
    if _con is None:
        con = duckdb.connect()
        for t in ["collisions", "parties", "victims", "case_ids"]:
            con.execute(
                f"CREATE VIEW {t} AS "
                f"SELECT * FROM read_parquet('{_settings.data_dir}/{t}.parquet')"
            )
        _con = con
    return _con


def run_query(sql: str) -> QueryResult:
    con = _connection()
    start = time.time()
    cur = con.execute(sql)
    rows = cur.fetchall()
    columns = [d[0] for d in cur.description]
    return QueryResult(columns=columns, rows=rows, query_ms=(time.time() - start) * 1000)

"""One-time ETL: convert switrs.sqlite tables to compressed Parquet.

Idempotent: overwrites existing parquet. Safe to re-run.
"""
import os
import sys
import time
import duckdb

TABLES = ["collisions", "parties", "victims", "case_ids"]


def convert(sqlite_path: str = "switrs.sqlite", out_dir: str = "data") -> None:
    os.makedirs(out_dir, exist_ok=True)
    con = duckdb.connect()
    con.execute("INSTALL sqlite; LOAD sqlite;")
    con.execute(f"ATTACH '{sqlite_path}' AS s (TYPE sqlite, READ_ONLY);")
    for t in TABLES:
        out = os.path.join(out_dir, f"{t}.parquet")
        start = time.time()
        con.execute(
            f"COPY (SELECT * FROM s.{t}) TO '{out}' "
            f"(FORMAT parquet, COMPRESSION zstd);"
        )
        n = con.execute(f"SELECT COUNT(*) FROM '{out}'").fetchone()[0]
        print(f"{t}: {n:,} rows -> {out} ({time.time() - start:.1f}s)")
    con.close()


if __name__ == "__main__":
    convert(*sys.argv[1:])

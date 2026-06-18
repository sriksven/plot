import os
import duckdb

EXPECTED = {
    "collisions": 9424334,
    "parties": 18669166,
    "victims": 9639334,
    "case_ids": 9424334,
}


def test_parquet_files_exist_with_correct_counts():
    con = duckdb.connect()
    for table, expected in EXPECTED.items():
        path = f"data/{table}.parquet"
        assert os.path.exists(path), f"missing {path}"
        n = con.execute(f"SELECT COUNT(*) FROM '{path}'").fetchone()[0]
        assert n == expected, f"{table}: {n} != {expected}"

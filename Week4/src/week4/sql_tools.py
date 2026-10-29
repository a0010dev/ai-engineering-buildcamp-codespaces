import urllib.request
from pathlib import Path

import duckdb

DATA_URL = "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-01.parquet"
DATA_DIR = Path(__file__).resolve().parents[2]
PARQUET_FILE = DATA_DIR / "yellow_tripdata_2024-01.parquet"

con = duckdb.connect(str(DATA_DIR / "taxi.db"))


def setup_database():
    """Download the parquet file and load it into DuckDB."""
    if not PARQUET_FILE.exists():
        print(f"Downloading {DATA_URL}...")
        urllib.request.urlretrieve(DATA_URL, PARQUET_FILE)

    con.execute("""
        CREATE TABLE IF NOT EXISTS trips AS
        SELECT * FROM read_parquet(?)
    """, [str(PARQUET_FILE)])
    count = con.execute("SELECT COUNT(*) FROM trips").fetchone()[0]
    print(f"Loaded {count} rows")
    return count


class SQLTools:
    def __init__(self, connection: duckdb.DuckDBPyConnection = con):
        self.con = connection

    def get_schema(self) -> str:
        """Return all column names and types in the trips table."""
        columns = self.con.execute("DESCRIBE trips").fetchall()
        return "\n".join(f"{column[0]}: {column[1]}" for column in columns)

    def run_sql(self, query: str) -> str:
        """Execute SQL and return column headers and up to 50 data rows as text."""
        result = self.con.execute(query)
        headers = [column[0] for column in result.description]
        rows = result.fetchmany(50)
        lines = ["\t".join(headers)]
        lines.extend(
            "\t".join("NULL" if value is None else str(value) for value in row)
            for row in rows
        )
        lines.append(f"Rows returned: {len(rows)} (maximum 50)")
        return "\n".join(lines)

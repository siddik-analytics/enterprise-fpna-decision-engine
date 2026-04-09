import duckdb

from src.config import DUCKDB_PATH, SQL_VIEWS_DIR


# Open DuckDB connection
def get_connection():
    return duckdb.connect(str(DUCKDB_PATH))


# Read SQL file contents
def read_sql_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


# Execute SQL view creation script
def build_views() -> None:
    conn = get_connection()

    sql_text = read_sql_file(SQL_VIEWS_DIR / "create_views.sql")
    conn.execute(sql_text)

    conn.close()
    print("SQL views created successfully.")


if __name__ == "__main__":
    build_views()
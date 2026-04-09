import duckdb
import pandas as pd

from src.config import DUCKDB_PATH, PROCESSED_DIR, RAW_DIR


# Open DuckDB connection
def get_connection():
    return duckdb.connect(str(DUCKDB_PATH))


# Load a CSV file into a DuckDB table
def load_csv_to_table(conn, file_path: str, table_name: str) -> None:
    query = f"""
    CREATE OR REPLACE TABLE {table_name} AS
    SELECT * FROM read_csv_auto('{file_path}', HEADER=TRUE);
    """
    conn.execute(query)
    print(f"Loaded table: {table_name}")


# Load all key raw and processed datasets
def load_all_tables() -> None:
    conn = get_connection()

    # Raw tables
    load_csv_to_table(conn, str(RAW_DIR / "revenue_actuals.csv"), "revenue_actuals")
    load_csv_to_table(conn, str(RAW_DIR / "revenue_budget.csv"), "revenue_budget")
    load_csv_to_table(conn, str(RAW_DIR / "opex_actuals.csv"), "opex_actuals")
    load_csv_to_table(conn, str(RAW_DIR / "opex_budget.csv"), "opex_budget")
    load_csv_to_table(conn, str(RAW_DIR / "headcount_actuals.csv"), "headcount_actuals")
    load_csv_to_table(conn, str(RAW_DIR / "headcount_budget.csv"), "headcount_budget")
    load_csv_to_table(conn, str(RAW_DIR / "working_capital_actuals.csv"), "working_capital_actuals")
    load_csv_to_table(conn, str(RAW_DIR / "working_capital_budget.csv"), "working_capital_budget")

    # Processed tables
    load_csv_to_table(conn, str(PROCESSED_DIR / "monthly_revenue_summary.csv"), "monthly_revenue_summary")
    load_csv_to_table(conn, str(PROCESSED_DIR / "monthly_opex_summary.csv"), "monthly_opex_summary")
    load_csv_to_table(conn, str(PROCESSED_DIR / "monthly_headcount_summary.csv"), "monthly_headcount_summary")
    load_csv_to_table(conn, str(PROCESSED_DIR / "monthly_working_capital_summary.csv"), "monthly_working_capital_summary")
    load_csv_to_table(conn, str(PROCESSED_DIR / "monthly_pnl_dataset.csv"), "monthly_pnl_dataset")

    conn.close()
    print("All tables loaded into DuckDB.")


if __name__ == "__main__":
    load_all_tables()
import duckdb
import pandas as pd

from src.config import DUCKDB_PATH, OUTPUT_DIR


REPORT_DIR = OUTPUT_DIR / "reports"
REPORT_DIR.mkdir(parents=True, exist_ok=True)


# Open DuckDB connection
def get_connection():
    return duckdb.connect(str(DUCKDB_PATH))


# Save query result to CSV
def export_query(conn, query: str, filename: str) -> None:
    df = conn.execute(query).df()
    df.to_csv(REPORT_DIR / filename, index=False)
    print(f"Exported: {filename}")


# Run management-style SQL reporting queries
def run_reporting_queries() -> None:
    conn = get_connection()

    # Consolidated monthly EBITDA summary
    export_query(
        conn,
        """
        SELECT
            period,
            entity,
            SUM(actual_revenue) AS actual_revenue,
            SUM(budget_revenue) AS budget_revenue,
            SUM(revenue_variance) AS revenue_variance,
            SUM(actual_ebitda) AS actual_ebitda,
            SUM(budget_ebitda) AS budget_ebitda,
            SUM(ebitda_variance) AS ebitda_variance
        FROM vw_monthly_pnl
        GROUP BY period, entity
        ORDER BY period, entity;
        """,
        "entity_monthly_ebitda_summary.csv",
    )

    # Region margin performance
    export_query(
        conn,
        """
        SELECT
            period,
            entity,
            region,
            SUM(actual_revenue) AS actual_revenue,
            SUM(actual_gross_profit) AS actual_gross_profit,
            ROUND(SUM(actual_gross_profit) / NULLIF(SUM(actual_revenue), 0), 4) AS gross_margin_pct,
            SUM(actual_ebitda) AS actual_ebitda,
            ROUND(SUM(actual_ebitda) / NULLIF(SUM(actual_revenue), 0), 4) AS ebitda_margin_pct
        FROM vw_monthly_pnl
        GROUP BY period, entity, region
        ORDER BY period, entity, region;
        """,
        "region_margin_performance.csv",
    )

    # Department overspend analysis
    export_query(
        conn,
        """
        SELECT
            period,
            entity,
            region,
            department,
            actual_total_opex,
            budget_total_opex,
            total_opex_variance
        FROM vw_department_opex
        WHERE total_opex_variance > 0
        ORDER BY total_opex_variance DESC;
        """,
        "department_overspend_analysis.csv",
    )

    # Headcount variance analysis
    export_query(
        conn,
        """
        SELECT
            period,
            entity,
            region,
            department,
            actual_ending_headcount,
            budget_ending_headcount,
            headcount_variance,
            actual_payroll_cost,
            budget_payroll_cost,
            payroll_variance
        FROM vw_headcount
        ORDER BY period, entity, region, department;
        """,
        "headcount_variance_analysis.csv",
    )

    # Working capital snapshot
    export_query(
        conn,
        """
        SELECT
            period,
            entity,
            actual_accounts_receivable,
            budget_accounts_receivable,
            ar_variance,
            actual_accounts_payable,
            budget_accounts_payable,
            ap_variance,
            actual_inventory,
            budget_inventory,
            inventory_variance,
            actual_operating_cash_proxy,
            budget_operating_cash_proxy,
            cash_proxy_variance
        FROM vw_working_capital
        ORDER BY period, entity;
        """,
        "working_capital_snapshot.csv",
    )

    conn.close()
    print("All SQL reporting queries completed.")


if __name__ == "__main__":
    run_reporting_queries()
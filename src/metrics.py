import pandas as pd

from src.config import PROCESSED_DIR, OUTPUT_DIR


REPORT_DIR = OUTPUT_DIR / "reports"
REPORT_DIR.mkdir(parents=True, exist_ok=True)


# Load processed P&L data
def load_pnl_data() -> pd.DataFrame:
    df = pd.read_csv(PROCESSED_DIR / "monthly_pnl_dataset.csv")
    df["month_start"] = pd.to_datetime(df["month_start"])
    return df


# Build consolidated KPI table by month
def build_monthly_kpi_table(df: pd.DataFrame) -> pd.DataFrame:
    kpi = (
        df.groupby(["month_start", "period"], as_index=False)[
            [
                "actual_revenue",
                "budget_revenue",
                "revenue_variance",
                "actual_gross_profit",
                "budget_gross_profit",
                "gross_profit_variance",
                "actual_total_opex",
                "budget_total_opex",
                "total_opex_variance",
                "actual_ebitda",
                "budget_ebitda",
                "ebitda_variance",
            ]
        ]
        .sum()
        .sort_values("month_start")
    )

    # Add margin metrics
    kpi["actual_gross_margin_pct"] = (
        kpi["actual_gross_profit"] / kpi["actual_revenue"]
    ).round(4)
    kpi["budget_gross_margin_pct"] = (
        kpi["budget_gross_profit"] / kpi["budget_revenue"]
    ).round(4)

    kpi["actual_ebitda_margin_pct"] = (
        kpi["actual_ebitda"] / kpi["actual_revenue"]
    ).round(4)
    kpi["budget_ebitda_margin_pct"] = (
        kpi["budget_ebitda"] / kpi["budget_revenue"]
    ).round(4)

    # Add prior month comparisons
    kpi["prior_month_revenue"] = kpi["actual_revenue"].shift(1)
    kpi["prior_month_ebitda"] = kpi["actual_ebitda"].shift(1)

    kpi["mom_revenue_growth_pct"] = (
        (kpi["actual_revenue"] / kpi["prior_month_revenue"]) - 1
    ).round(4)

    kpi["mom_ebitda_growth_pct"] = (
        (kpi["actual_ebitda"] / kpi["prior_month_ebitda"]) - 1
    ).round(4)

    # Add rolling averages
    kpi["revenue_roll_3"] = kpi["actual_revenue"].rolling(3, min_periods=1).mean().round(2)
    kpi["ebitda_roll_3"] = kpi["actual_ebitda"].rolling(3, min_periods=1).mean().round(2)

    return kpi.round(2)


# Build entity KPI summary
def build_entity_kpi_table(df: pd.DataFrame) -> pd.DataFrame:
    entity_kpi = (
        df.groupby(["entity"], as_index=False)[
            [
                "actual_revenue",
                "budget_revenue",
                "revenue_variance",
                "actual_gross_profit",
                "actual_total_opex",
                "actual_ebitda",
                "budget_ebitda",
                "ebitda_variance",
            ]
        ]
        .sum()
    )

    # Add margin metrics
    entity_kpi["gross_margin_pct"] = (
        entity_kpi["actual_gross_profit"] / entity_kpi["actual_revenue"]
    ).round(4)
    entity_kpi["ebitda_margin_pct"] = (
        entity_kpi["actual_ebitda"] / entity_kpi["actual_revenue"]
    ).round(4)

    return entity_kpi.round(2)


# Build regional KPI summary
def build_region_kpi_table(df: pd.DataFrame) -> pd.DataFrame:
    region_kpi = (
        df.groupby(["entity", "region"], as_index=False)[
            [
                "actual_revenue",
                "budget_revenue",
                "revenue_variance",
                "actual_gross_profit",
                "actual_total_opex",
                "actual_ebitda",
                "budget_ebitda",
                "ebitda_variance",
            ]
        ]
        .sum()
    )

    # Add margin metrics
    region_kpi["gross_margin_pct"] = (
        region_kpi["actual_gross_profit"] / region_kpi["actual_revenue"]
    ).round(4)
    region_kpi["ebitda_margin_pct"] = (
        region_kpi["actual_ebitda"] / region_kpi["actual_revenue"]
    ).round(4)

    return region_kpi.round(2)


# Run KPI pipeline
def run_metrics_pipeline() -> None:
    df = load_pnl_data()

    monthly_kpi = build_monthly_kpi_table(df)
    entity_kpi = build_entity_kpi_table(df)
    region_kpi = build_region_kpi_table(df)

    monthly_kpi.to_csv(PROCESSED_DIR / "monthly_kpi_table.csv", index=False)
    entity_kpi.to_csv(PROCESSED_DIR / "entity_kpi_table.csv", index=False)
    region_kpi.to_csv(PROCESSED_DIR / "region_kpi_table.csv", index=False)

    monthly_kpi.to_csv(REPORT_DIR / "monthly_kpi_table.csv", index=False)
    entity_kpi.to_csv(REPORT_DIR / "entity_kpi_table.csv", index=False)
    region_kpi.to_csv(REPORT_DIR / "region_kpi_table.csv", index=False)

    print("KPI tables created.")


if __name__ == "__main__":
    run_metrics_pipeline()
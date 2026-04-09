import numpy as np
import pandas as pd

from src.config import (
    START_DATE,
    PERIODS,
    FREQ,
    ENTITIES,
    REGIONS,
    DEPARTMENTS,
    PRODUCTS,
    CUSTOMER_SEGMENTS,
    ENTITY_REVENUE_MULTIPLIER,
    REGION_REVENUE_MULTIPLIER,
    PRODUCT_PRICE,
    PRODUCT_COST_RATIO,
    SEGMENT_VOLUME_MULTIPLIER,
    DEPARTMENT_OPEX_BASE,
    DEPARTMENT_HEADCOUNT_BASE,
    RAW_DIR,
    MASTER_DATA_DIR,
)

RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)


def month_end_label(dt: pd.Timestamp) -> str:
    return dt.strftime("%Y-%m")


def generate_date_dimension() -> pd.DataFrame:
    dates = pd.date_range(start=START_DATE, periods=PERIODS, freq=FREQ)
    df = pd.DataFrame({"month_start": dates})
    df["month"] = df["month_start"].dt.month
    df["year"] = df["month_start"].dt.year
    df["quarter"] = "Q" + df["month_start"].dt.quarter.astype(str)
    df["month_name"] = df["month_start"].dt.strftime("%b")
    df["period"] = df["month_start"].apply(month_end_label)
    df["month_index"] = np.arange(1, len(df) + 1)
    return df


def generate_master_data():
    dim_entity = pd.DataFrame({"entity": ENTITIES})
    dim_region = pd.DataFrame({"region": REGIONS})
    dim_department = pd.DataFrame({"department": DEPARTMENTS})
    dim_product = pd.DataFrame({"product": PRODUCTS})
    dim_segment = pd.DataFrame({"customer_segment": CUSTOMER_SEGMENTS})

    dim_entity.to_csv(MASTER_DATA_DIR / "dim_entity.csv", index=False)
    dim_region.to_csv(MASTER_DATA_DIR / "dim_region.csv", index=False)
    dim_department.to_csv(MASTER_DATA_DIR / "dim_department.csv", index=False)
    dim_product.to_csv(MASTER_DATA_DIR / "dim_product.csv", index=False)
    dim_segment.to_csv(MASTER_DATA_DIR / "dim_customer_segment.csv", index=False)

    print("Master data exported.")


def build_revenue_driver_table(date_dim: pd.DataFrame) -> pd.DataFrame:
    rows = []

    seasonality_map = {
        1: 0.94,
        2: 0.96,
        3: 0.98,
        4: 1.00,
        5: 1.02,
        6: 1.03,
        7: 1.01,
        8: 1.00,
        9: 1.04,
        10: 1.06,
        11: 1.09,
        12: 1.14,
    }

    for _, drow in date_dim.iterrows():
        month_start = drow["month_start"]
        month_num = drow["month"]
        month_index = drow["month_index"]

        trend_factor = 1 + (month_index - 1) * 0.008
        seasonality = seasonality_map[month_num]

        for entity in ENTITIES:
            for region in REGIONS:
                for product in PRODUCTS:
                    for segment in CUSTOMER_SEGMENTS:
                        base_volume = 900
                        volume_noise = np.random.normal(1.0, 0.08)
                        price_noise = np.random.normal(1.0, 0.03)

                        units = (
                            base_volume
                            * ENTITY_REVENUE_MULTIPLIER[entity]
                            * REGION_REVENUE_MULTIPLIER[region]
                            * SEGMENT_VOLUME_MULTIPLIER[segment]
                            * trend_factor
                            * seasonality
                            * volume_noise
                        )

                        unit_price = PRODUCT_PRICE[product] * price_noise
                        revenue = units * unit_price
                        cogs = revenue * PRODUCT_COST_RATIO[product] * np.random.normal(1.0, 0.03)

                        rows.append(
                            {
                                "month_start": month_start,
                                "period": month_end_label(month_start),
                                "entity": entity,
                                "region": region,
                                "product": product,
                                "customer_segment": segment,
                                "units": round(units, 2),
                                "unit_price": round(unit_price, 2),
                                "revenue": round(revenue, 2),
                                "cogs": round(cogs, 2),
                                "gross_profit": round(revenue - cogs, 2),
                            }
                        )

    return pd.DataFrame(rows)


def build_opex_table(date_dim: pd.DataFrame) -> pd.DataFrame:
    rows = []

    for _, drow in date_dim.iterrows():
        month_start = drow["month_start"]
        month_index = drow["month_index"]

        inflation_factor = 1 + (month_index - 1) * 0.003

        for entity in ENTITIES:
            for department in DEPARTMENTS:
                for region in REGIONS:
                    base_cost = DEPARTMENT_OPEX_BASE[department]
                    entity_factor = ENTITY_REVENUE_MULTIPLIER[entity]
                    region_factor = REGION_REVENUE_MULTIPLIER[region]

                    salary_cost = (
                        base_cost
                        * 0.62
                        * inflation_factor
                        * entity_factor
                        * region_factor
                        * np.random.normal(1.0, 0.05)
                    )

                    non_salary_cost = (
                        base_cost
                        * 0.38
                        * inflation_factor
                        * entity_factor
                        * region_factor
                        * np.random.normal(1.0, 0.08)
                    )

                    rows.append(
                        {
                            "month_start": month_start,
                            "period": month_end_label(month_start),
                            "entity": entity,
                            "region": region,
                            "department": department,
                            "salary_opex": round(salary_cost, 2),
                            "non_salary_opex": round(non_salary_cost, 2),
                            "total_opex": round(salary_cost + non_salary_cost, 2),
                        }
                    )

    return pd.DataFrame(rows)


def build_headcount_table(date_dim: pd.DataFrame) -> pd.DataFrame:
    rows = []

    for _, drow in date_dim.iterrows():
        month_start = drow["month_start"]
        month_index = drow["month_index"]

        for entity in ENTITIES:
            for department in DEPARTMENTS:
                for region in REGIONS:
                    base_hc = DEPARTMENT_HEADCOUNT_BASE[department]
                    growth = 1 + (month_index - 1) * 0.0025
                    entity_factor = ENTITY_REVENUE_MULTIPLIER[entity]
                    region_factor = REGION_REVENUE_MULTIPLIER[region]

                    ending_hc = (
                        base_hc
                        * growth
                        * entity_factor
                        * region_factor
                        * np.random.normal(1.0, 0.04)
                    )

                    ending_hc = max(1, int(round(ending_hc)))
                    avg_salary = np.random.normal(7200, 900)

                    rows.append(
                        {
                            "month_start": month_start,
                            "period": month_end_label(month_start),
                            "entity": entity,
                            "region": region,
                            "department": department,
                            "ending_headcount": ending_hc,
                            "avg_monthly_salary": round(avg_salary, 2),
                            "payroll_cost": round(ending_hc * avg_salary, 2),
                        }
                    )

    return pd.DataFrame(rows)


def build_working_capital_table(revenue_df: pd.DataFrame, opex_df: pd.DataFrame) -> pd.DataFrame:
    rev_group = (
        revenue_df.groupby(["month_start", "period", "entity"], as_index=False)[["revenue", "cogs"]]
        .sum()
    )

    opex_group = (
        opex_df.groupby(["month_start", "period", "entity"], as_index=False)[["total_opex"]]
        .sum()
    )

    df = rev_group.merge(opex_group, on=["month_start", "period", "entity"], how="left")

    df["ar_days"] = np.random.randint(38, 56, size=len(df))
    df["ap_days"] = np.random.randint(22, 40, size=len(df))
    df["inventory_days"] = np.random.randint(45, 70, size=len(df))

    df["accounts_receivable"] = (df["revenue"] / 30.0) * df["ar_days"]
    df["accounts_payable"] = ((df["cogs"] + 0.20 * df["total_opex"]) / 30.0) * df["ap_days"]
    df["inventory"] = (df["cogs"] / 30.0) * df["inventory_days"]

    df["operating_cash_proxy"] = (
        df["revenue"]
        - df["cogs"]
        - df["total_opex"]
        - (df["accounts_receivable"] * 0.015)
        + (df["accounts_payable"] * 0.010)
        - (df["inventory"] * 0.008)
    )

    return df.round(2)


def build_budget_from_actuals(actuals_df: pd.DataFrame, value_columns: list[str], growth_rate: float = 0.06) -> pd.DataFrame:
    budget_df = actuals_df.copy()

    noise = np.random.normal(1.0 + growth_rate, 0.03, size=(len(budget_df), len(value_columns)))
    noise_df = pd.DataFrame(noise, columns=value_columns, index=budget_df.index)

    for col in value_columns:
        budget_df[col] = (budget_df[col] * noise_df[col]).round(2)

    budget_df["scenario"] = "Budget"
    return budget_df


def main():
    print("Generating date dimension...")
    date_dim = generate_date_dimension()
    date_dim.to_csv(MASTER_DATA_DIR / "dim_date.csv", index=False)

    print("Generating master data...")
    generate_master_data()

    print("Generating revenue actuals...")
    revenue_actuals = build_revenue_driver_table(date_dim)
    revenue_actuals["scenario"] = "Actual"

    print("Generating opex actuals...")
    opex_actuals = build_opex_table(date_dim)
    opex_actuals["scenario"] = "Actual"

    print("Generating headcount actuals...")
    headcount_actuals = build_headcount_table(date_dim)
    headcount_actuals["scenario"] = "Actual"

    print("Generating working capital actuals...")
    wc_actuals = build_working_capital_table(revenue_actuals, opex_actuals)
    wc_actuals["scenario"] = "Actual"

    print("Generating budgets...")
    revenue_budget = build_budget_from_actuals(
        revenue_actuals,
        ["units", "unit_price", "revenue", "cogs", "gross_profit"],
        growth_rate=0.05,
    )

    opex_budget = build_budget_from_actuals(
        opex_actuals,
        ["salary_opex", "non_salary_opex", "total_opex"],
        growth_rate=0.04,
    )

    headcount_budget = build_budget_from_actuals(
        headcount_actuals,
        ["ending_headcount", "avg_monthly_salary", "payroll_cost"],
        growth_rate=0.03,
    )

    wc_budget = build_budget_from_actuals(
        wc_actuals,
        [
            "revenue",
            "cogs",
            "total_opex",
            "ar_days",
            "ap_days",
            "inventory_days",
            "accounts_receivable",
            "accounts_payable",
            "inventory",
            "operating_cash_proxy",
        ],
        growth_rate=0.03,
    )

    print("Exporting CSV files...")
    revenue_actuals.to_csv(RAW_DIR / "revenue_actuals.csv", index=False)
    revenue_budget.to_csv(RAW_DIR / "revenue_budget.csv", index=False)

    opex_actuals.to_csv(RAW_DIR / "opex_actuals.csv", index=False)
    opex_budget.to_csv(RAW_DIR / "opex_budget.csv", index=False)

    headcount_actuals.to_csv(RAW_DIR / "headcount_actuals.csv", index=False)
    headcount_budget.to_csv(RAW_DIR / "headcount_budget.csv", index=False)

    wc_actuals.to_csv(RAW_DIR / "working_capital_actuals.csv", index=False)
    wc_budget.to_csv(RAW_DIR / "working_capital_budget.csv", index=False)

    print("Done. Files created in data/raw and data/master_data.")


if __name__ == "__main__":
    main()
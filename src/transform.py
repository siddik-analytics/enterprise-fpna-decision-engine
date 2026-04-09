"""
Transform Layer

This module converts raw finance datasets into reporting-ready tables
used for FP&A analysis, dashboards, and forecasting.

Outputs:
- Monthly revenue summary (Actual vs Budget)
- Monthly opex summary
- Monthly headcount summary
- Working capital summary
- Consolidated P&L dataset
"""

import pandas as pd

from src.config import RAW_DIR, PROCESSED_DIR


# ---------------------------------------------------------
# Helper functions
# ---------------------------------------------------------

def load_csv(filename: str) -> pd.DataFrame:
    """
    Load CSV file from RAW directory

    Parameters
    ----------
    filename : str
        File name inside data/raw

    Returns
    -------
    DataFrame
    """
    return pd.read_csv(RAW_DIR / filename)


def save_csv(df: pd.DataFrame, filename: str) -> None:
    """
    Save processed dataframe to processed directory
    """
    df.to_csv(PROCESSED_DIR / filename, index=False)


# ---------------------------------------------------------
# Revenue Summary
# ---------------------------------------------------------

def build_monthly_revenue_summary() -> pd.DataFrame:
    """
    Build monthly revenue summary:
    - Actual vs Budget
    - Variance
    - Gross margin %
    """

    # Load datasets
    actuals = load_csv("revenue_actuals.csv")
    budget = load_csv("revenue_budget.csv")

    # Reporting grain
    group_cols = ["month_start", "period", "entity", "region"]

    # Aggregate actuals
    actuals_sum = (
        actuals.groupby(group_cols, as_index=False)[["revenue", "cogs", "gross_profit"]]
        .sum()
        .rename(
            columns={
                "revenue": "actual_revenue",
                "cogs": "actual_cogs",
                "gross_profit": "actual_gross_profit",
            }
        )
    )

    # Aggregate budget
    budget_sum = (
        budget.groupby(group_cols, as_index=False)[["revenue", "cogs", "gross_profit"]]
        .sum()
        .rename(
            columns={
                "revenue": "budget_revenue",
                "cogs": "budget_cogs",
                "gross_profit": "budget_gross_profit",
            }
        )
    )

    # Merge actuals and budget
    df = actuals_sum.merge(budget_sum, on=group_cols, how="left")

    # Variance calculations
    df["revenue_variance"] = df["actual_revenue"] - df["budget_revenue"]
    df["cogs_variance"] = df["actual_cogs"] - df["budget_cogs"]
    df["gross_profit_variance"] = df["actual_gross_profit"] - df["budget_gross_profit"]

    # Margin %
    df["gross_margin_pct_actual"] = (
        df["actual_gross_profit"] / df["actual_revenue"]
    ).round(4)

    df["gross_margin_pct_budget"] = (
        df["budget_gross_profit"] / df["budget_revenue"]
    ).round(4)

    df["gross_margin_pct_variance"] = (
        df["gross_margin_pct_actual"] - df["gross_margin_pct_budget"]
    )

    return df.round(2)


# ---------------------------------------------------------
# OPEX Summary
# ---------------------------------------------------------

def build_monthly_opex_summary() -> pd.DataFrame:
    """
    Build departmental OPEX summary:
    - salary vs non-salary
    - actual vs budget
    - variance
    """

    actuals = load_csv("opex_actuals.csv")
    budget = load_csv("opex_budget.csv")

    group_cols = ["month_start", "period", "entity", "region", "department"]

    # Aggregate actuals
    actuals_sum = (
        actuals.groupby(group_cols, as_index=False)[
            ["salary_opex", "non_salary_opex", "total_opex"]
        ]
        .sum()
        .rename(
            columns={
                "salary_opex": "actual_salary_opex",
                "non_salary_opex": "actual_non_salary_opex",
                "total_opex": "actual_total_opex",
            }
        )
    )

    # Aggregate budget
    budget_sum = (
        budget.groupby(group_cols, as_index=False)[
            ["salary_opex", "non_salary_opex", "total_opex"]
        ]
        .sum()
        .rename(
            columns={
                "salary_opex": "budget_salary_opex",
                "non_salary_opex": "budget_non_salary_opex",
                "total_opex": "budget_total_opex",
            }
        )
    )

    # Merge
    df = actuals_sum.merge(budget_sum, on=group_cols, how="left")

    # Variance
    df["salary_opex_variance"] = (
        df["actual_salary_opex"] - df["budget_salary_opex"]
    )

    df["non_salary_opex_variance"] = (
        df["actual_non_salary_opex"] - df["budget_non_salary_opex"]
    )

    df["total_opex_variance"] = (
        df["actual_total_opex"] - df["budget_total_opex"]
    )

    return df.round(2)


# ---------------------------------------------------------
# Headcount Summary
# ---------------------------------------------------------

def build_monthly_headcount_summary() -> pd.DataFrame:
    """
    Build headcount reporting dataset:
    - headcount
    - payroll cost
    - variance vs budget
    """

    actuals = load_csv("headcount_actuals.csv")
    budget = load_csv("headcount_budget.csv")

    group_cols = ["month_start", "period", "entity", "region", "department"]

    actuals_sum = (
        actuals.groupby(group_cols, as_index=False)[
            ["ending_headcount", "payroll_cost"]
        ]
        .sum()
        .rename(
            columns={
                "ending_headcount": "actual_ending_headcount",
                "payroll_cost": "actual_payroll_cost",
            }
        )
    )

    budget_sum = (
        budget.groupby(group_cols, as_index=False)[
            ["ending_headcount", "payroll_cost"]
        ]
        .sum()
        .rename(
            columns={
                "ending_headcount": "budget_ending_headcount",
                "payroll_cost": "budget_payroll_cost",
            }
        )
    )

    df = actuals_sum.merge(budget_sum, on=group_cols, how="left")

    # Variance
    df["headcount_variance"] = (
        df["actual_ending_headcount"] - df["budget_ending_headcount"]
    )

    df["payroll_variance"] = (
        df["actual_payroll_cost"] - df["budget_payroll_cost"]
    )

    return df.round(2)


# ---------------------------------------------------------
# Working Capital Summary
# ---------------------------------------------------------

def build_monthly_working_capital_summary() -> pd.DataFrame:
    """
    Build working capital reporting:
    - AR / AP / Inventory
    - cash proxy
    - variance vs budget
    """

    actuals = load_csv("working_capital_actuals.csv")
    budget = load_csv("working_capital_budget.csv")

    group_cols = ["month_start", "period", "entity"]

    # Rename actual columns
    actuals_sum = actuals.rename(
        columns={
            "accounts_receivable": "actual_accounts_receivable",
            "accounts_payable": "actual_accounts_payable",
            "inventory": "actual_inventory",
            "operating_cash_proxy": "actual_operating_cash_proxy",
            "ar_days": "actual_ar_days",
            "ap_days": "actual_ap_days",
            "inventory_days": "actual_inventory_days",
        }
    )

    # Rename budget columns
    budget_sum = budget.rename(
        columns={
            "accounts_receivable": "budget_accounts_receivable",
            "accounts_payable": "budget_accounts_payable",
            "inventory": "budget_inventory",
            "operating_cash_proxy": "budget_operating_cash_proxy",
            "ar_days": "budget_ar_days",
            "ap_days": "budget_ap_days",
            "inventory_days": "budget_inventory_days",
        }
    )

    keep_actual_cols = group_cols + [
        "actual_accounts_receivable",
        "actual_accounts_payable",
        "actual_inventory",
        "actual_operating_cash_proxy",
        "actual_ar_days",
        "actual_ap_days",
        "actual_inventory_days",
    ]

    keep_budget_cols = group_cols + [
        "budget_accounts_receivable",
        "budget_accounts_payable",
        "budget_inventory",
        "budget_operating_cash_proxy",
        "budget_ar_days",
        "budget_ap_days",
        "budget_inventory_days",
    ]

    df = actuals_sum[keep_actual_cols].merge(
        budget_sum[keep_budget_cols],
        on=group_cols,
        how="left",
    )

    # Variance
    df["ar_variance"] = (
        df["actual_accounts_receivable"] - df["budget_accounts_receivable"]
    )

    df["ap_variance"] = (
        df["actual_accounts_payable"] - df["budget_accounts_payable"]
    )

    df["inventory_variance"] = (
        df["actual_inventory"] - df["budget_inventory"]
    )

    df["cash_proxy_variance"] = (
        df["actual_operating_cash_proxy"] - df["budget_operating_cash_proxy"]
    )

    return df.round(2)


# ---------------------------------------------------------
# P&L Dataset
# ---------------------------------------------------------

def build_pnl_dataset() -> pd.DataFrame:
    """
    Build consolidated P&L:
    Revenue
    Gross Profit
    OPEX
    EBITDA
    Margin %
    """

    revenue = build_monthly_revenue_summary()
    opex = build_monthly_opex_summary()

    # Aggregate OPEX to match revenue grain
    opex_grouped = (
        opex.groupby(
            ["month_start", "period", "entity", "region"],
            as_index=False
        )[
            ["actual_total_opex", "budget_total_opex", "total_opex_variance"]
        ]
        .sum()
    )

    # Merge revenue + opex
    pnl = revenue.merge(
        opex_grouped,
        on=["month_start", "period", "entity", "region"],
        how="left",
    )

    # EBITDA
    pnl["actual_ebitda"] = (
        pnl["actual_gross_profit"] - pnl["actual_total_opex"]
    )

    pnl["budget_ebitda"] = (
        pnl["budget_gross_profit"] - pnl["budget_total_opex"]
    )

    pnl["ebitda_variance"] = (
        pnl["actual_ebitda"] - pnl["budget_ebitda"]
    )

    # EBITDA margin
    pnl["ebitda_margin_actual"] = (
        pnl["actual_ebitda"] / pnl["actual_revenue"]
    ).round(4)

    pnl["ebitda_margin_budget"] = (
        pnl["budget_ebitda"] / pnl["budget_revenue"]
    ).round(4)

    pnl["ebitda_margin_variance"] = (
        pnl["ebitda_margin_actual"] - pnl["ebitda_margin_budget"]
    )

    return pnl.round(2)


# ---------------------------------------------------------
# Run All Transforms
# ---------------------------------------------------------

def run_all_transforms() -> None:
    """
    Run full transformation pipeline and save outputs
    """

    revenue_summary = build_monthly_revenue_summary()
    opex_summary = build_monthly_opex_summary()
    headcount_summary = build_monthly_headcount_summary()
    wc_summary = build_monthly_working_capital_summary()
    pnl_dataset = build_pnl_dataset()

    save_csv(revenue_summary, "monthly_revenue_summary.csv")
    save_csv(opex_summary, "monthly_opex_summary.csv")
    save_csv(headcount_summary, "monthly_headcount_summary.csv")
    save_csv(wc_summary, "monthly_working_capital_summary.csv")
    save_csv(pnl_dataset, "monthly_pnl_dataset.csv")

    print("All processed datasets created in data/processed/")


if __name__ == "__main__":
    run_all_transforms()
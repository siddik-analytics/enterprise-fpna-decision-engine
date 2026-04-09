"""
Purpose:
--------
Data quality validation layer for the FP&A pipeline.

This module performs:
- Missing value checks
- Duplicate record checks
- Negative value checks
- Financial integrity checks (gross profit)
- Validation logging to output/logs/
"""

import pandas as pd

from src.config import RAW_DIR, OUTPUT_DIR


# -----------------------------------------------------------------------------
# Create logging directory for validation outputs
# -----------------------------------------------------------------------------
LOG_DIR = OUTPUT_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)


# -----------------------------------------------------------------------------
# GENERIC VALIDATION FUNCTIONS
# -----------------------------------------------------------------------------


def check_missing_values(df: pd.DataFrame, dataset_name: str) -> pd.DataFrame:
    """
    Identify missing/null values by column.

    Returns:
        DataFrame listing columns with missing counts
    """
    result = df.isnull().sum().reset_index()
    result.columns = ["column_name", "missing_count"]
    result["dataset"] = dataset_name

    return result[result["missing_count"] > 0]


def check_duplicates(
    df: pd.DataFrame,
    subset_cols: list[str],
    dataset_name: str
) -> pd.DataFrame:
    """
    Identify duplicate records based on business key.

    Parameters:
        subset_cols: columns defining uniqueness
    """
    dupes = df[df.duplicated(subset=subset_cols, keep=False)].copy()

    if not dupes.empty:
        dupes["dataset"] = dataset_name

    return dupes


def check_negative_values(
    df: pd.DataFrame,
    numeric_cols: list[str],
    dataset_name: str
) -> pd.DataFrame:
    """
    Identify negative values in numeric columns.

    Useful for:
    - revenue
    - headcount
    - payroll
    - working capital balances
    """
    issue_frames = []

    for col in numeric_cols:
        bad = df[df[col] < 0].copy()

        if not bad.empty:
            bad["issue_column"] = col
            bad["dataset"] = dataset_name
            issue_frames.append(bad)

    if issue_frames:
        return pd.concat(issue_frames, ignore_index=True)

    return pd.DataFrame()


# -----------------------------------------------------------------------------
# FINANCIAL LOGIC VALIDATION
# -----------------------------------------------------------------------------


def check_gross_profit_integrity(
    df: pd.DataFrame,
    tolerance: float = 1.0
) -> pd.DataFrame:
    """
    Validate:
        gross_profit = revenue - cogs

    Flags records where difference exceeds tolerance.
    """
    calc_gp = (df["revenue"] - df["cogs"]).round(2)
    diff = (df["gross_profit"] - calc_gp).abs()

    issues = df[diff > tolerance].copy()

    if not issues.empty:
        issues["calculated_gross_profit"] = calc_gp.loc[issues.index]
        issues["difference"] = diff.loc[issues.index]
        issues["dataset"] = "revenue_actuals"

    return issues


# -----------------------------------------------------------------------------
# EXPORT LOGGING
# -----------------------------------------------------------------------------


def export_issue_file(df: pd.DataFrame, filename: str) -> None:
    """
    Export validation results.

    If no issues found → write placeholder file.
    """
    output_path = LOG_DIR / filename

    if df.empty:
        pd.DataFrame({"status": ["no_issues_found"]}).to_csv(
            output_path,
            index=False
        )
    else:
        df.to_csv(output_path, index=False)


# -----------------------------------------------------------------------------
# DATASET-SPECIFIC VALIDATIONS
# -----------------------------------------------------------------------------


def validate_revenue() -> None:
    """
    Validate revenue dataset:
    - Missing values
    - Duplicate rows
    - Negative values
    - Gross profit integrity
    """
    df = pd.read_csv(RAW_DIR / "revenue_actuals.csv")

    missing = check_missing_values(df, "revenue_actuals")

    duplicates = check_duplicates(
        df,
        ["month_start", "entity", "region", "product", "customer_segment", "scenario"],
        "revenue_actuals",
    )

    negatives = check_negative_values(
        df,
        ["units", "unit_price", "revenue", "cogs", "gross_profit"],
        "revenue_actuals",
    )

    gp_issues = check_gross_profit_integrity(df)

    export_issue_file(missing, "revenue_missing.csv")
    export_issue_file(duplicates, "revenue_duplicates.csv")
    export_issue_file(negatives, "revenue_negatives.csv")
    export_issue_file(gp_issues, "revenue_gp_integrity.csv")


def validate_opex() -> None:
    """
    Validate operating expense dataset.
    """
    df = pd.read_csv(RAW_DIR / "opex_actuals.csv")

    missing = check_missing_values(df, "opex_actuals")

    duplicates = check_duplicates(
        df,
        ["month_start", "entity", "region", "department", "scenario"],
        "opex_actuals",
    )

    negatives = check_negative_values(
        df,
        ["salary_opex", "non_salary_opex", "total_opex"],
        "opex_actuals",
    )

    export_issue_file(missing, "opex_missing.csv")
    export_issue_file(duplicates, "opex_duplicates.csv")
    export_issue_file(negatives, "opex_negatives.csv")


def validate_headcount() -> None:
    """
    Validate headcount dataset.
    """
    df = pd.read_csv(RAW_DIR / "headcount_actuals.csv")

    missing = check_missing_values(df, "headcount_actuals")

    duplicates = check_duplicates(
        df,
        ["month_start", "entity", "region", "department", "scenario"],
        "headcount_actuals",
    )

    negatives = check_negative_values(
        df,
        ["ending_headcount", "avg_monthly_salary", "payroll_cost"],
        "headcount_actuals",
    )

    export_issue_file(missing, "headcount_missing.csv")
    export_issue_file(duplicates, "headcount_duplicates.csv")
    export_issue_file(negatives, "headcount_negatives.csv")


def validate_working_capital() -> None:
    """
    Validate working capital dataset.
    """
    df = pd.read_csv(RAW_DIR / "working_capital_actuals.csv")

    missing = check_missing_values(df, "working_capital_actuals")

    duplicates = check_duplicates(
        df,
        ["month_start", "entity", "scenario"],
        "working_capital_actuals",
    )

    negatives = check_negative_values(
        df,
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
        ],
        "working_capital_actuals",
    )

    export_issue_file(missing, "working_capital_missing.csv")
    export_issue_file(duplicates, "working_capital_duplicates.csv")
    export_issue_file(negatives, "working_capital_negatives.csv")


# -----------------------------------------------------------------------------
# MASTER VALIDATION RUNNER
# -----------------------------------------------------------------------------


def run_all_validations() -> None:
    """
    Run all dataset validations.
    """
    validate_revenue()
    validate_opex()
    validate_headcount()
    validate_working_capital()

    print("All validations completed. Check output/logs/")


if __name__ == "__main__":
    run_all_validations()
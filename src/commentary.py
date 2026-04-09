import pandas as pd

from src.config import PROCESSED_DIR, OUTPUT_DIR


REPORT_DIR = OUTPUT_DIR / "reports"
REPORT_DIR.mkdir(parents=True, exist_ok=True)


# Load processed files
def load_inputs():
    pnl = pd.read_csv(PROCESSED_DIR / "monthly_pnl_dataset.csv")
    opex = pd.read_csv(PROCESSED_DIR / "monthly_opex_summary.csv")
    forecast_summary = pd.read_csv(PROCESSED_DIR / "forecast_scenario_summary.csv")

    pnl["month_start"] = pd.to_datetime(pnl["month_start"])
    return pnl, opex, forecast_summary


# Convert variance into direction text
def get_variance_label(value: float, positive_good: bool = True) -> str:
    # Interpret favorable or unfavorable movement
    if positive_good:
        return "favorable" if value >= 0 else "unfavorable"
    return "favorable" if value <= 0 else "unfavorable"


# Build top entity commentary for latest month
def build_latest_month_commentary(pnl: pd.DataFrame) -> pd.DataFrame:
    latest_month = pnl["month_start"].max()

    latest = pnl[pnl["month_start"] == latest_month].copy()

    summary = (
        latest.groupby(["entity"], as_index=False)[
            [
                "actual_revenue",
                "budget_revenue",
                "revenue_variance",
                "actual_ebitda",
                "budget_ebitda",
                "ebitda_variance",
            ]
        ]
        .sum()
    )

    comments = []

    for _, row in summary.iterrows():
        # Revenue variance text
        revenue_label = get_variance_label(row["revenue_variance"], positive_good=True)

        # EBITDA variance text
        ebitda_label = get_variance_label(row["ebitda_variance"], positive_good=True)

        text = (
            f"{row['entity']} delivered revenue of {row['actual_revenue']:,.0f} "
            f"vs budget of {row['budget_revenue']:,.0f}, a {revenue_label} variance "
            f"of {row['revenue_variance']:,.0f}. EBITDA came in at {row['actual_ebitda']:,.0f} "
            f"vs budget of {row['budget_ebitda']:,.0f}, resulting in a {ebitda_label} "
            f"variance of {row['ebitda_variance']:,.0f}."
        )

        comments.append(
            {
                "period": latest_month.strftime("%Y-%m"),
                "entity": row["entity"],
                "commentary": text,
            }
        )

    return pd.DataFrame(comments)


# Build department overspend commentary
def build_department_commentary(opex: pd.DataFrame) -> pd.DataFrame:
    opex["month_start"] = pd.to_datetime(opex["month_start"])
    latest_month = opex["month_start"].max()

    latest = opex[opex["month_start"] == latest_month].copy()

    dept_summary = (
        latest.groupby(["entity", "department"], as_index=False)[
            ["actual_total_opex", "budget_total_opex", "total_opex_variance"]
        ]
        .sum()
        .sort_values("total_opex_variance", ascending=False)
    )

    comments = []

    for _, row in dept_summary.iterrows():
        label = get_variance_label(row["total_opex_variance"], positive_good=False)

        text = (
            f"{row['entity']} - {row['department']} recorded opex of "
            f"{row['actual_total_opex']:,.0f} vs budget of {row['budget_total_opex']:,.0f}, "
            f"representing a {label} variance of {row['total_opex_variance']:,.0f}."
        )

        comments.append(
            {
                "period": latest_month.strftime("%Y-%m"),
                "entity": row["entity"],
                "department": row["department"],
                "commentary": text,
            }
        )

    return pd.DataFrame(comments)


# Build scenario commentary
def build_scenario_commentary(forecast_summary: pd.DataFrame) -> pd.DataFrame:
    comments = []

    for _, row in forecast_summary.iterrows():
        # Add margin for narrative context
        margin_pct = row["ebitda_margin"] * 100

        text = (
            f"Under the {row['forecast_version']} scenario, {row['entity']} is forecast to deliver "
            f"revenue of {row['forecast_revenue']:,.0f} and EBITDA of {row['forecast_ebitda']:,.0f}, "
            f"implying an EBITDA margin of {margin_pct:.1f}%."
        )

        comments.append(
            {
                "forecast_version": row["forecast_version"],
                "entity": row["entity"],
                "commentary": text,
            }
        )

    return pd.DataFrame(comments)


# Run commentary pipeline
def run_commentary_pipeline() -> None:
    pnl, opex, forecast_summary = load_inputs()

    latest_month_commentary = build_latest_month_commentary(pnl)
    department_commentary = build_department_commentary(opex)
    scenario_commentary = build_scenario_commentary(forecast_summary)

    latest_month_commentary.to_csv(REPORT_DIR / "latest_month_commentary.csv", index=False)
    department_commentary.to_csv(REPORT_DIR / "department_commentary.csv", index=False)
    scenario_commentary.to_csv(REPORT_DIR / "scenario_commentary.csv", index=False)

    print("Commentary files created.")


if __name__ == "__main__":
    run_commentary_pipeline()
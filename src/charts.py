import pandas as pd
import matplotlib.pyplot as plt

from src.config import PROCESSED_DIR, OUTPUT_DIR


CHART_DIR = OUTPUT_DIR / "charts"
CHART_DIR.mkdir(parents=True, exist_ok=True)


# Load KPI table
def load_kpi_table() -> pd.DataFrame:
    df = pd.read_csv(PROCESSED_DIR / "monthly_kpi_table.csv")
    df["month_start"] = pd.to_datetime(df["month_start"])
    return df


# Save a revenue trend chart
def plot_revenue_vs_budget(df: pd.DataFrame) -> None:
    plt.figure(figsize=(12, 6))

    # Plot actual and budget revenue
    plt.plot(df["month_start"], df["actual_revenue"], label="Actual Revenue")
    plt.plot(df["month_start"], df["budget_revenue"], label="Budget Revenue")

    # Add chart labels
    plt.title("Actual vs Budget Revenue")
    plt.xlabel("Month")
    plt.ylabel("Revenue")
    plt.legend()
    plt.tight_layout()

    plt.savefig(CHART_DIR / "revenue_vs_budget.png", dpi=150)
    plt.close()


# Save an EBITDA trend chart
def plot_ebitda_vs_budget(df: pd.DataFrame) -> None:
    plt.figure(figsize=(12, 6))

    # Plot actual and budget EBITDA
    plt.plot(df["month_start"], df["actual_ebitda"], label="Actual EBITDA")
    plt.plot(df["month_start"], df["budget_ebitda"], label="Budget EBITDA")

    # Add chart labels
    plt.title("Actual vs Budget EBITDA")
    plt.xlabel("Month")
    plt.ylabel("EBITDA")
    plt.legend()
    plt.tight_layout()

    plt.savefig(CHART_DIR / "ebitda_vs_budget.png", dpi=150)
    plt.close()


# Save a revenue variance bar chart
def plot_revenue_variance(df: pd.DataFrame) -> None:
    plt.figure(figsize=(12, 6))

    # Plot monthly revenue variance
    plt.bar(df["period"], df["revenue_variance"])

    # Add chart labels
    plt.title("Monthly Revenue Variance")
    plt.xlabel("Period")
    plt.ylabel("Revenue Variance")
    plt.xticks(rotation=45)
    plt.tight_layout()

    plt.savefig(CHART_DIR / "revenue_variance.png", dpi=150)
    plt.close()


# Save an EBITDA margin trend chart
def plot_ebitda_margin(df: pd.DataFrame) -> None:
    plt.figure(figsize=(12, 6))

    # Plot margin trend
    plt.plot(
        df["month_start"],
        df["actual_ebitda_margin_pct"] * 100,
        label="Actual EBITDA Margin %",
    )
    plt.plot(
        df["month_start"],
        df["budget_ebitda_margin_pct"] * 100,
        label="Budget EBITDA Margin %",
    )

    # Add chart labels
    plt.title("EBITDA Margin Trend")
    plt.xlabel("Month")
    plt.ylabel("Margin %")
    plt.legend()
    plt.tight_layout()

    plt.savefig(CHART_DIR / "ebitda_margin_trend.png", dpi=150)
    plt.close()


# Run chart pipeline
def run_chart_pipeline() -> None:
    df = load_kpi_table()

    plot_revenue_vs_budget(df)
    plot_ebitda_vs_budget(df)
    plot_revenue_variance(df)
    plot_ebitda_margin(df)

    print("Charts created.")


if __name__ == "__main__":
    run_chart_pipeline()
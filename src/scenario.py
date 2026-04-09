import pandas as pd

from src.config import PROCESSED_DIR


# Load base forecast output
def load_base_forecast() -> pd.DataFrame:
    df = pd.read_csv(PROCESSED_DIR / "rolling_12m_forecast.csv")
    df["month_start"] = pd.to_datetime(df["month_start"])
    return df


# Apply a generic scenario to the forecast
def apply_scenario(
    df: pd.DataFrame,
    scenario_name: str,
    revenue_multiplier: float = 1.0,
    gross_profit_multiplier: float = 1.0,
    opex_multiplier: float = 1.0,
) -> pd.DataFrame:
    out = df.copy()

    # Adjust financial lines
    out["forecast_revenue"] = (out["forecast_revenue"] * revenue_multiplier).round(2)
    out["forecast_gross_profit"] = (out["forecast_gross_profit"] * gross_profit_multiplier).round(2)
    out["forecast_total_opex"] = (out["forecast_total_opex"] * opex_multiplier).round(2)

    # Recalculate EBITDA
    out["forecast_ebitda"] = (out["forecast_gross_profit"] - out["forecast_total_opex"]).round(2)
    out["forecast_version"] = scenario_name

    return out


# Build all business scenarios
def build_scenarios(df: pd.DataFrame) -> pd.DataFrame:
    scenarios = []

    # Base case
    scenarios.append(apply_scenario(df, "Base Case"))

    # Upside: stronger revenue and slightly better margin
    scenarios.append(
        apply_scenario(
            df,
            "Upside Case",
            revenue_multiplier=1.06,
            gross_profit_multiplier=1.08,
            opex_multiplier=1.01,
        )
    )

    # Downside: weaker revenue and lower GP
    scenarios.append(
        apply_scenario(
            df,
            "Downside Case",
            revenue_multiplier=0.93,
            gross_profit_multiplier=0.89,
            opex_multiplier=1.02,
        )
    )

    # Hiring freeze: opex reduction only
    scenarios.append(
        apply_scenario(
            df,
            "Hiring Freeze",
            revenue_multiplier=1.00,
            gross_profit_multiplier=1.00,
            opex_multiplier=0.96,
        )
    )

    # Pricing uplift: better revenue and margin
    scenarios.append(
        apply_scenario(
            df,
            "Pricing Uplift",
            revenue_multiplier=1.04,
            gross_profit_multiplier=1.07,
            opex_multiplier=1.00,
        )
    )

    # Demand shock: lower revenue and some cost pressure
    scenarios.append(
        apply_scenario(
            df,
            "Demand Shock",
            revenue_multiplier=0.90,
            gross_profit_multiplier=0.86,
            opex_multiplier=1.01,
        )
    )

    combined = pd.concat(scenarios, ignore_index=True)
    return combined


# Create summary table for scenario comparison
def build_scenario_summary(df: pd.DataFrame) -> pd.DataFrame:
    summary = (
        df.groupby(["forecast_version", "entity"], as_index=False)[
            ["forecast_revenue", "forecast_gross_profit", "forecast_total_opex", "forecast_ebitda"]
        ]
        .sum()
    )

    summary["ebitda_margin"] = (
        summary["forecast_ebitda"] / summary["forecast_revenue"]
    ).round(4)

    return summary.round(2)


# Run scenario pipeline
def run_scenario_pipeline() -> None:
    base_forecast = load_base_forecast()
    scenarios = build_scenarios(base_forecast)
    summary = build_scenario_summary(scenarios)

    scenarios.to_csv(PROCESSED_DIR / "forecast_scenarios.csv", index=False)
    summary.to_csv(PROCESSED_DIR / "forecast_scenario_summary.csv", index=False)

    print("Scenario outputs created.")


if __name__ == "__main__":
    run_scenario_pipeline()
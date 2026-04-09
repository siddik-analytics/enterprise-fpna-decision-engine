import pandas as pd

from src.config import PROCESSED_DIR, OUTPUT_DIR


REPORT_DIR = OUTPUT_DIR / "reports"
REPORT_DIR.mkdir(parents=True, exist_ok=True)


# Export executive summary files
def export_forecast_reports() -> None:
    forecast = pd.read_csv(PROCESSED_DIR / "rolling_12m_forecast.csv")
    scenarios = pd.read_csv(PROCESSED_DIR / "forecast_scenario_summary.csv")

    # Entity forecast summary
    entity_forecast = (
        forecast.groupby(["forecast_version", "entity"], as_index=False)[
            ["forecast_revenue", "forecast_gross_profit", "forecast_total_opex", "forecast_ebitda"]
        ]
        .sum()
    )
    entity_forecast.to_csv(REPORT_DIR / "forecast_entity_summary.csv", index=False)

    # Monthly consolidated forecast
    monthly_forecast = (
        forecast.groupby(["period"], as_index=False)[
            ["forecast_revenue", "forecast_gross_profit", "forecast_total_opex", "forecast_ebitda"]
        ]
        .sum()
    )
    monthly_forecast.to_csv(REPORT_DIR / "forecast_monthly_consolidated.csv", index=False)

    # Scenario comparison summary
    scenarios.to_csv(REPORT_DIR / "forecast_scenario_comparison.csv", index=False)

    print("Forecast reporting exports created.")


if __name__ == "__main__":
    export_forecast_reports()
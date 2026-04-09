import pandas as pd
import numpy as np

from src.config import PROCESSED_DIR


# Load processed P&L dataset
def load_pnl_data() -> pd.DataFrame:
    df = pd.read_csv(PROCESSED_DIR / "monthly_pnl_dataset.csv")
    df["month_start"] = pd.to_datetime(df["month_start"])
    return df


# Build entity-region monthly summary for forecasting
def prepare_forecast_base(df: pd.DataFrame) -> pd.DataFrame:
    summary = (
        df.groupby(["month_start", "period", "entity", "region"], as_index=False)[
            [
                "actual_revenue",
                "actual_gross_profit",
                "actual_total_opex",
                "actual_ebitda",
            ]
        ]
        .sum()
        .sort_values(["entity", "region", "month_start"])
    )

    return summary


# Add lag and rolling features
def add_forecast_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    for metric in ["actual_revenue", "actual_gross_profit", "actual_total_opex", "actual_ebitda"]:
        # Prior month value
        df[f"{metric}_lag_1"] = df.groupby(["entity", "region"])[metric].shift(1)

        # 3-month rolling average
        df[f"{metric}_roll_3"] = (
            df.groupby(["entity", "region"])[metric]
            .transform(lambda s: s.shift(1).rolling(3, min_periods=1).mean())
        )

        # 6-month rolling average
        df[f"{metric}_roll_6"] = (
            df.groupby(["entity", "region"])[metric]
            .transform(lambda s: s.shift(1).rolling(6, min_periods=1).mean())
        )

    return df


# Build forecast for next 12 months using recent trend
def build_rolling_forecast(df: pd.DataFrame, forecast_months: int = 12) -> pd.DataFrame:
    latest_month = df["month_start"].max()
    entities_regions = df[["entity", "region"]].drop_duplicates()

    forecast_rows = []

    for _, combo in entities_regions.iterrows():
        entity = combo["entity"]
        region = combo["region"]

        hist = (
            df[(df["entity"] == entity) & (df["region"] == region)]
            .sort_values("month_start")
            .copy()
        )

        recent = hist.tail(6)

        # Simple trend assumptions
        revenue_growth = recent["actual_revenue"].pct_change().mean()
        gp_growth = recent["actual_gross_profit"].pct_change().mean()
        opex_growth = recent["actual_total_opex"].pct_change().mean()

        # Clean unstable rates
        revenue_growth = 0.01 if pd.isna(revenue_growth) else np.clip(revenue_growth, -0.05, 0.06)
        gp_growth = 0.01 if pd.isna(gp_growth) else np.clip(gp_growth, -0.05, 0.06)
        opex_growth = 0.008 if pd.isna(opex_growth) else np.clip(opex_growth, -0.04, 0.05)

        last_revenue = hist["actual_revenue"].iloc[-1]
        last_gp = hist["actual_gross_profit"].iloc[-1]
        last_opex = hist["actual_total_opex"].iloc[-1]

        for i in range(1, forecast_months + 1):
            # Advance one month
            forecast_month = latest_month + pd.DateOffset(months=i)

            # Apply compounding trend
            forecast_revenue = last_revenue * ((1 + revenue_growth) ** i)
            forecast_gp = last_gp * ((1 + gp_growth) ** i)
            forecast_opex = last_opex * ((1 + opex_growth) ** i)
            forecast_ebitda = forecast_gp - forecast_opex

            forecast_rows.append(
                {
                    "month_start": forecast_month,
                    "period": forecast_month.strftime("%Y-%m"),
                    "entity": entity,
                    "region": region,
                    "forecast_revenue": round(forecast_revenue, 2),
                    "forecast_gross_profit": round(forecast_gp, 2),
                    "forecast_total_opex": round(forecast_opex, 2),
                    "forecast_ebitda": round(forecast_ebitda, 2),
                    "assumed_revenue_growth": round(revenue_growth, 4),
                    "assumed_gp_growth": round(gp_growth, 4),
                    "assumed_opex_growth": round(opex_growth, 4),
                    "forecast_version": "Base Forecast",
                }
            )

    return pd.DataFrame(forecast_rows)


# Export forecast output
def run_forecast_pipeline() -> pd.DataFrame:
    df = load_pnl_data()
    base = prepare_forecast_base(df)
    featured = add_forecast_features(base)
    forecast_df = build_rolling_forecast(featured)

    forecast_df.to_csv(PROCESSED_DIR / "rolling_12m_forecast.csv", index=False)
    print("Rolling 12-month forecast created.")

    return forecast_df


if __name__ == "__main__":
    run_forecast_pipeline()
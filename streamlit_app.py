import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path


# -----------------------------
# Page config
# -----------------------------
st.set_page_config(
    page_title="Enterprise FP&A Dashboard",
    page_icon="📊",
    layout="wide",
)


# -----------------------------
# Premium dark theme CSS
# -----------------------------
st.markdown(
    """
    <style>
    .stApp {
        background-color: #0b0f17;
        color: #e5e7eb;
    }

    section[data-testid="stSidebar"] {
        background-color: #0f172a;
        border-right: 1px solid #1f2937;
    }

    h1, h2, h3 {
        color: #f9fafb;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }

    .stTabs [data-baseweb="tab"] {
        color: #9ca3af;
    }

    .stTabs [aria-selected="true"] {
        color: white !important;
    }

    [data-testid="stMetric"] {
        background: linear-gradient(180deg, #111827, #0b1220);
        border: 1px solid #1f2937;
        padding: 12px;
        border-radius: 14px;
    }

    div[data-testid="stDataFrame"] {
        border: 1px solid #1f2937;
        border-radius: 12px;
        overflow: hidden;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# -----------------------------
# Paths
# -----------------------------
BASE_DIR = Path(__file__).resolve().parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"
REPORT_DIR = BASE_DIR / "output" / "reports"


# -----------------------------
# Premium colors
# -----------------------------
COLORS = {
    "actual": "#3b82f6",
    "budget": "#64748b",
    "forecast": "#14b8a6",
    "ebitda": "#f97316",
    "gross_profit": "#a855f7",
    "favorable": "#22c55e",
    "unfavorable": "#ef4444",
    "neutral": "#9ca3af",
    "accent": "#f59e0b",
}


# -----------------------------
# Helpers
# -----------------------------
def format_money(value: float) -> str:
    # Format money in millions
    return f"${value / 1_000_000:.2f}M"


def format_pct(value: float) -> str:
    # Format percentage
    return f"{value:.1f}%"


def safe_read_csv(path: Path) -> pd.DataFrame:
    # Read CSV with friendly error
    if not path.exists():
        raise FileNotFoundError(f"Missing file: {path}")
    return pd.read_csv(path)


@st.cache_data
def load_data():
    # Load processed files
    monthly_kpi = safe_read_csv(PROCESSED_DIR / "monthly_kpi_table.csv")
    entity_kpi = safe_read_csv(PROCESSED_DIR / "entity_kpi_table.csv")
    region_kpi = safe_read_csv(PROCESSED_DIR / "region_kpi_table.csv")
    pnl = safe_read_csv(PROCESSED_DIR / "monthly_pnl_dataset.csv")
    forecast = safe_read_csv(PROCESSED_DIR / "rolling_12m_forecast.csv")
    scenarios = safe_read_csv(PROCESSED_DIR / "forecast_scenarios.csv")
    scenario_summary = safe_read_csv(PROCESSED_DIR / "forecast_scenario_summary.csv")
    opex = safe_read_csv(PROCESSED_DIR / "monthly_opex_summary.csv")

    # Load commentary files if available
    commentary_latest = safe_read_csv(REPORT_DIR / "latest_month_commentary.csv")
    commentary_dept = safe_read_csv(REPORT_DIR / "department_commentary.csv")
    commentary_scenario = safe_read_csv(REPORT_DIR / "scenario_commentary.csv")

    # Convert dates
    monthly_kpi["month_start"] = pd.to_datetime(monthly_kpi["month_start"])
    pnl["month_start"] = pd.to_datetime(pnl["month_start"])
    forecast["month_start"] = pd.to_datetime(forecast["month_start"])
    scenarios["month_start"] = pd.to_datetime(scenarios["month_start"])
    opex["month_start"] = pd.to_datetime(opex["month_start"])

    return {
        "monthly_kpi": monthly_kpi,
        "entity_kpi": entity_kpi,
        "region_kpi": region_kpi,
        "pnl": pnl,
        "forecast": forecast,
        "scenarios": scenarios,
        "scenario_summary": scenario_summary,
        "opex": opex,
        "commentary_latest": commentary_latest,
        "commentary_dept": commentary_dept,
        "commentary_scenario": commentary_scenario,
    }


def style_dark_axes(ax, title: str) -> None:
    # Style axes for dark theme
    ax.set_title(title, loc="left", color="white", pad=12)
    ax.set_facecolor("#0b0f17")
    ax.grid(axis="y", linestyle="--", alpha=0.20, color="#94a3b8")
    ax.tick_params(colors="white")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#334155")
    ax.spines["bottom"].set_color("#334155")
    ax.yaxis.label.set_color("white")
    ax.xaxis.label.set_color("white")


def build_filtered_pnl(pnl: pd.DataFrame, entities: list[str], regions: list[str]) -> pd.DataFrame:
    # Apply entity and region filters
    df = pnl.copy()

    if entities:
        df = df[df["entity"].isin(entities)]

    if regions:
        df = df[df["region"].isin(regions)]

    return df


def build_kpi_summary(df: pd.DataFrame) -> dict[str, float]:
    # Build KPI summary for filtered data
    revenue = df["actual_revenue"].sum()
    budget_revenue = df["budget_revenue"].sum()
    revenue_variance = df["revenue_variance"].sum()
    ebitda = df["actual_ebitda"].sum()
    budget_ebitda = df["budget_ebitda"].sum()
    ebitda_variance = df["ebitda_variance"].sum()
    margin = (ebitda / revenue * 100) if revenue else 0

    return {
        "revenue": revenue,
        "budget_revenue": budget_revenue,
        "revenue_variance": revenue_variance,
        "ebitda": ebitda,
        "budget_ebitda": budget_ebitda,
        "ebitda_variance": ebitda_variance,
        "margin": margin,
    }


def show_top_kpi_cards(summary: dict[str, float]) -> None:
    # Render top KPI cards
    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Revenue", format_money(summary["revenue"]))
    c2.metric("Revenue Variance", format_money(summary["revenue_variance"]))
    c3.metric("EBITDA", format_money(summary["ebitda"]))
    c4.metric("EBITDA Margin", format_pct(summary["margin"]))


def show_sidebar_kpis(summary: dict[str, float]) -> None:
    # Render sidebar KPI snapshot
    st.sidebar.markdown("### KPI Snapshot")
    st.sidebar.metric("Revenue", format_money(summary["revenue"]))
    st.sidebar.metric("EBITDA", format_money(summary["ebitda"]))
    st.sidebar.metric("Margin", format_pct(summary["margin"]))


def plot_revenue_vs_budget(df: pd.DataFrame):
    # Plot revenue vs budget over time
    monthly = (
        df.groupby(["month_start", "period"], as_index=False)[["actual_revenue", "budget_revenue"]]
        .sum()
        .sort_values("month_start")
    )

    fig, ax = plt.subplots(figsize=(10, 4.5))
    fig.patch.set_facecolor("#0b0f17")

    ax.plot(monthly["month_start"], monthly["actual_revenue"], color=COLORS["actual"], label="Actual")
    ax.plot(monthly["month_start"], monthly["budget_revenue"], color=COLORS["budget"], label="Budget")
    ax.fill_between(monthly["month_start"], monthly["actual_revenue"], monthly["budget_revenue"], alpha=0.15, color=COLORS["actual"])

    style_dark_axes(ax, "Revenue vs Budget")
    ax.legend(frameon=False, labelcolor="white")

    return fig


def plot_ebitda_vs_budget(df: pd.DataFrame):
    # Plot EBITDA vs budget over time
    monthly = (
        df.groupby(["month_start", "period"], as_index=False)[["actual_ebitda", "budget_ebitda"]]
        .sum()
        .sort_values("month_start")
    )

    fig, ax = plt.subplots(figsize=(10, 4.5))
    fig.patch.set_facecolor("#0b0f17")

    ax.plot(monthly["month_start"], monthly["actual_ebitda"], color=COLORS["ebitda"], label="Actual")
    ax.plot(monthly["month_start"], monthly["budget_ebitda"], color=COLORS["budget"], label="Budget")
    ax.fill_between(monthly["month_start"], monthly["actual_ebitda"], monthly["budget_ebitda"], alpha=0.15, color=COLORS["ebitda"])

    style_dark_axes(ax, "EBITDA vs Budget")
    ax.legend(frameon=False, labelcolor="white")

    return fig


def plot_entity_ebitda(df: pd.DataFrame):
    # Plot EBITDA by entity
    entity = (
        df.groupby("entity", as_index=False)["actual_ebitda"]
        .sum()
        .sort_values("actual_ebitda", ascending=False)
    )

    palette = ["#3b82f6", "#14b8a6", "#f97316", "#a855f7", "#22c55e"]

    fig, ax = plt.subplots(figsize=(8, 4.5))
    fig.patch.set_facecolor("#0b0f17")

    ax.bar(entity["entity"], entity["actual_ebitda"], color=palette[: len(entity)])

    style_dark_axes(ax, "EBITDA by Entity")
    return fig


def plot_region_margin(df: pd.DataFrame):
    # Plot EBITDA margin by entity and region
    region = (
        df.groupby(["entity", "region"], as_index=False)[["actual_revenue", "actual_ebitda"]]
        .sum()
    )

    region["ebitda_margin_pct"] = np.where(
        region["actual_revenue"] != 0,
        region["actual_ebitda"] / region["actual_revenue"] * 100,
        0,
    )
    region["label"] = region["entity"] + " - " + region["region"]
    region = region.sort_values("ebitda_margin_pct")

    fig, ax = plt.subplots(figsize=(9, 5.5))
    fig.patch.set_facecolor("#0b0f17")

    ax.barh(region["label"], region["ebitda_margin_pct"], color=COLORS["gross_profit"])

    style_dark_axes(ax, "EBITDA Margin by Entity / Region")
    return fig


def plot_department_opex_variance(opex: pd.DataFrame, entities: list[str], regions: list[str]):
    # Plot latest month department opex variance
    df = opex.copy()

    if entities:
        df = df[df["entity"].isin(entities)]

    if regions:
        df = df[df["region"].isin(regions)]

    latest_month = df["month_start"].max()
    latest = df[df["month_start"] == latest_month].copy()

    dept = (
        latest.groupby("department", as_index=False)["total_opex_variance"]
        .sum()
        .sort_values("total_opex_variance", ascending=False)
    )

    colors = [COLORS["unfavorable"] if x > 0 else COLORS["favorable"] for x in dept["total_opex_variance"]]

    fig, ax = plt.subplots(figsize=(8.5, 4.5))
    fig.patch.set_facecolor("#0b0f17")

    ax.bar(dept["department"], dept["total_opex_variance"], color=colors)
    ax.axhline(0, color=COLORS["neutral"], linewidth=1)

    style_dark_axes(ax, "Department Opex Variance")
    return fig


def get_selected_scenario_summary(scenario_summary: pd.DataFrame, scenario_name: str) -> pd.DataFrame:
    # Return selected scenario summary rows
    return scenario_summary[scenario_summary["forecast_version"] == scenario_name].copy()


def plot_scenario_overview(scenario_summary: pd.DataFrame):
    # Plot all scenario EBITDA comparison
    total = (
        scenario_summary.groupby("forecast_version", as_index=False)["forecast_ebitda"]
        .sum()
        .sort_values("forecast_ebitda", ascending=False)
    )

    colors = ["#3b82f6", "#14b8a6", "#f97316", "#a855f7", "#ef4444", "#22c55e"][: len(total)]

    fig, ax = plt.subplots(figsize=(10, 4.5))
    fig.patch.set_facecolor("#0b0f17")

    ax.bar(total["forecast_version"], total["forecast_ebitda"], color=colors)

    style_dark_axes(ax, "Scenario EBITDA Comparison")
    ax.tick_params(axis="x", rotation=20)

    return fig


def plot_forecast_vs_selected_scenario(forecast: pd.DataFrame, scenarios: pd.DataFrame, scenario_name: str):
    # Compare base forecast with selected scenario
    base_monthly = (
        forecast.groupby("month_start", as_index=False)["forecast_ebitda"]
        .sum()
        .sort_values("month_start")
    )

    selected_monthly = (
        scenarios[scenarios["forecast_version"] == scenario_name]
        .groupby("month_start", as_index=False)["forecast_ebitda"]
        .sum()
        .sort_values("month_start")
    )

    fig, ax = plt.subplots(figsize=(10, 4.5))
    fig.patch.set_facecolor("#0b0f17")

    ax.plot(
        base_monthly["month_start"],
        base_monthly["forecast_ebitda"],
        color=COLORS["forecast"],
        label="Base Forecast",
    )

    ax.plot(
        selected_monthly["month_start"],
        selected_monthly["forecast_ebitda"],
        color=COLORS["accent"],
        linestyle="--",
        label=scenario_name,
    )

    style_dark_axes(ax, "Base Forecast vs Selected Scenario")
    ax.legend(frameon=False, labelcolor="white")

    return fig


def show_commentary_table(df: pd.DataFrame, title: str) -> None:
    # Show commentary dataframe
    st.subheader(title)
    st.dataframe(df, width="stretch", hide_index=True)


# -----------------------------
# App
# -----------------------------
st.title("Enterprise FP&A Dashboard")
st.caption("Interactive reporting, forecasting, scenario planning, and executive finance insights.")

try:
    data = load_data()
except Exception as e:
    st.error(f"Unable to load dashboard data. Run `python main.py` first. Details: {e}")
    st.stop()

monthly_kpi = data["monthly_kpi"]
entity_kpi = data["entity_kpi"]
region_kpi = data["region_kpi"]
pnl = data["pnl"]
forecast = data["forecast"]
scenarios = data["scenarios"]
scenario_summary = data["scenario_summary"]
opex = data["opex"]
commentary_latest = data["commentary_latest"]
commentary_dept = data["commentary_dept"]
commentary_scenario = data["commentary_scenario"]


# -----------------------------
# Sidebar filters
# -----------------------------
st.sidebar.header("Filters")

entity_options = sorted(pnl["entity"].dropna().unique().tolist())
region_options = sorted(pnl["region"].dropna().unique().tolist())
scenario_options = sorted(scenarios["forecast_version"].dropna().unique().tolist())

selected_entities = st.sidebar.multiselect(
    "Entity",
    entity_options,
    default=entity_options,
)

selected_regions = st.sidebar.multiselect(
    "Region",
    region_options,
    default=region_options,
)

selected_scenario = st.sidebar.selectbox(
    "Scenario",
    scenario_options,
    index=0,
)


# -----------------------------
# Filtered data and KPIs
# -----------------------------
filtered_pnl = build_filtered_pnl(pnl, selected_entities, selected_regions)
summary = build_kpi_summary(filtered_pnl)

show_sidebar_kpis(summary)
show_top_kpi_cards(summary)


# -----------------------------
# Tabs
# -----------------------------
summary_tab, forecast_tab, commentary_tab, data_tab = st.tabs(
    ["Executive Summary", "Forecast & Scenarios", "Commentary", "Data Explorer"]
)

with summary_tab:
    # First row
    col1, col2 = st.columns(2)

    with col1:
        st.pyplot(plot_revenue_vs_budget(filtered_pnl), clear_figure=True)

    with col2:
        st.pyplot(plot_ebitda_vs_budget(filtered_pnl), clear_figure=True)

    # Second row
    col3, col4 = st.columns(2)

    with col3:
        st.pyplot(plot_entity_ebitda(filtered_pnl), clear_figure=True)

    with col4:
        st.pyplot(plot_region_margin(filtered_pnl), clear_figure=True)

    # Opex variance chart
    st.pyplot(
        plot_department_opex_variance(opex, selected_entities, selected_regions),
        clear_figure=True,
    )

with forecast_tab:
    # Selected scenario summary
    selected_summary = get_selected_scenario_summary(scenario_summary, selected_scenario)

    st.subheader(f"Selected Scenario: {selected_scenario}")

    total_revenue = selected_summary["forecast_revenue"].sum()
    total_ebitda = selected_summary["forecast_ebitda"].sum()
    total_margin = (total_ebitda / total_revenue * 100) if total_revenue else 0

    c1, c2, c3 = st.columns(3)
    c1.metric("Scenario Revenue", format_money(total_revenue))
    c2.metric("Scenario EBITDA", format_money(total_ebitda))
    c3.metric("Scenario EBITDA Margin", format_pct(total_margin))

    # Scenario comparison chart
    st.pyplot(
        plot_forecast_vs_selected_scenario(forecast, scenarios, selected_scenario),
        clear_figure=True,
    )

    # Selected scenario detail
    st.subheader("Selected Scenario Detail")
    st.dataframe(selected_summary, width="stretch", hide_index=True)

    # Overview chart and table
    st.subheader("All Scenario Comparison")
    st.pyplot(plot_scenario_overview(scenario_summary), clear_figure=True)
    st.dataframe(scenario_summary, width="stretch", hide_index=True)

with commentary_tab:
    show_commentary_table(commentary_latest, "Latest Month Commentary")
    show_commentary_table(commentary_dept, "Department Commentary")
    show_commentary_table(commentary_scenario, "Scenario Commentary")

with data_tab:
    dataset_name = st.selectbox(
        "Choose dataset",
        [
            "monthly_kpi",
            "entity_kpi",
            "region_kpi",
            "monthly_pnl_dataset",
            "rolling_12m_forecast",
            "forecast_scenarios",
            "forecast_scenario_summary",
        ],
    )

    dataset_map = {
        "monthly_kpi": monthly_kpi,
        "entity_kpi": entity_kpi,
        "region_kpi": region_kpi,
        "monthly_pnl_dataset": pnl,
        "rolling_12m_forecast": forecast,
        "forecast_scenarios": scenarios,
        "forecast_scenario_summary": scenario_summary,
    }

    st.dataframe(dataset_map[dataset_name], width="stretch", hide_index=True)


# -----------------------------
# Footer
# -----------------------------
st.markdown("---")
st.caption("Run `python main.py` first, then launch with `streamlit run streamlit_app.py`.")
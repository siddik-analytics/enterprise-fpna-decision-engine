import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FuncFormatter

from src.config import PROCESSED_DIR, OUTPUT_DIR


# Create output folder
CHART_DIR = OUTPUT_DIR / "charts"
CHART_DIR.mkdir(parents=True, exist_ok=True)


# -----------------------------
# Global chart style
# -----------------------------
plt.rcParams["figure.figsize"] = (12, 6)
plt.rcParams["axes.spines.top"] = False
plt.rcParams["axes.spines.right"] = False
plt.rcParams["axes.titleweight"] = "bold"
plt.rcParams["axes.titlesize"] = 16
plt.rcParams["axes.labelsize"] = 11
plt.rcParams["xtick.labelsize"] = 9
plt.rcParams["ytick.labelsize"] = 9
plt.rcParams["legend.frameon"] = False
plt.rcParams["lines.linewidth"] = 2.4


# -----------------------------
# Finance color palette
# -----------------------------
COLORS = {
    # Core finance series
    "actual": "#1D4ED8",        # deep blue
    "budget": "#64748B",        # slate
    "forecast": "#0F766E",      # teal
    "gross_profit": "#7C3AED",  # purple
    "ebitda": "#EA580C",        # orange
    "opex": "#DC2626",          # red
    "revenue": "#2563EB",       # bright blue

    # Variance semantics
    "favorable": "#16A34A",     # green
    "unfavorable": "#DC2626",   # red
    "neutral": "#94A3B8",       # light slate

    # Support colors
    "highlight": "#0EA5E9",     # cyan
    "accent": "#F59E0B",        # amber
    "fill_blue": "#DBEAFE",
    "fill_teal": "#CCFBF1",
    "fill_orange": "#FED7AA",
    "fill_purple": "#E9D5FF",
}


# Format values in millions
def format_millions(x, pos):
    return f"${x / 1_000_000:.1f}M"


# Format values in percent
def format_percent(x, pos):
    return f"{x:.1f}%"


# Apply common axis styling
def style_axis(ax, title: str, subtitle: str = "", percent_axis: bool = False) -> None:
    # Set chart title
    ax.set_title(title, loc="left", pad=18)

    # Add subtitle
    if subtitle:
        ax.text(
            0.0,
            1.02,
            subtitle,
            transform=ax.transAxes,
            fontsize=10,
            alpha=0.75,
            va="bottom",
        )

    # Add soft grid
    ax.grid(axis="y", linestyle="--", alpha=0.20)

    # Format y-axis
    if percent_axis:
        ax.yaxis.set_major_formatter(FuncFormatter(format_percent))
    else:
        ax.yaxis.set_major_formatter(FuncFormatter(format_millions))

    # Soften visible spines
    ax.spines["left"].set_alpha(0.25)
    ax.spines["bottom"].set_alpha(0.25)


# Add labels above bars
def add_bar_labels(ax, bars, percent: bool = False) -> None:
    for bar in bars:
        value = bar.get_height()

        # Skip missing values
        if pd.isna(value):
            continue

        # Format label text
        label = f"{value:.1f}%" if percent else f"${value / 1_000_000:.1f}M"

        # Position label
        ax.annotate(
            label,
            xy=(bar.get_x() + bar.get_width() / 2, value),
            xytext=(0, 4 if value >= 0 else -14),
            textcoords="offset points",
            ha="center",
            fontsize=8,
            alpha=0.9,
        )


# Add end label to line chart
def add_line_end_label(ax, x, y, prefix: str = "", percent: bool = False) -> None:
    if len(y) == 0:
        return

    # Get last point
    last_x = x.iloc[-1]
    last_y = y.iloc[-1]

    # Format label text
    label = f"{last_y:.1f}%" if percent else f"${last_y / 1_000_000:.1f}M"

    # Add annotation
    ax.annotate(
        f"{prefix}{label}",
        xy=(last_x, last_y),
        xytext=(8, 0),
        textcoords="offset points",
        va="center",
        fontsize=9,
        alpha=0.9,
    )


# Pick favorable or unfavorable colors
def get_variance_colors(values) -> list[str]:
    return [
        COLORS["favorable"] if v >= 0 else COLORS["unfavorable"]
        for v in values
    ]


# Pick favorable or unfavorable colors for opex
def get_opex_variance_colors(values) -> list[str]:
    return [
        COLORS["unfavorable"] if v > 0 else COLORS["favorable"]
        for v in values
    ]


# Pick distinct colors for many categories
def get_distinct_colors(n: int) -> list[str]:
    palette = [
        "#1D4ED8",  # blue
        "#0F766E",  # teal
        "#7C3AED",  # purple
        "#EA580C",  # orange
        "#DC2626",  # red
        "#16A34A",  # green
        "#0891B2",  # cyan
        "#CA8A04",  # gold
        "#BE185D",  # magenta
        "#4338CA",  # indigo
        "#0369A1",  # sky
        "#4D7C0F",  # lime
    ]
    return [palette[i % len(palette)] for i in range(n)]


# Load all required datasets
def load_data():
    # Load KPI data
    monthly_kpi = pd.read_csv(PROCESSED_DIR / "monthly_kpi_table.csv")
    monthly_kpi["month_start"] = pd.to_datetime(monthly_kpi["month_start"])

    # Load entity KPI data
    entity_kpi = pd.read_csv(PROCESSED_DIR / "entity_kpi_table.csv")

    # Load region KPI data
    region_kpi = pd.read_csv(PROCESSED_DIR / "region_kpi_table.csv")

    # Load P&L data
    pnl = pd.read_csv(PROCESSED_DIR / "monthly_pnl_dataset.csv")
    pnl["month_start"] = pd.to_datetime(pnl["month_start"])

    # Load opex data
    opex = pd.read_csv(PROCESSED_DIR / "monthly_opex_summary.csv")
    opex["month_start"] = pd.to_datetime(opex["month_start"])

    # Load scenario summary
    scenarios = pd.read_csv(PROCESSED_DIR / "forecast_scenario_summary.csv")

    # Load rolling forecast
    forecast = pd.read_csv(PROCESSED_DIR / "rolling_12m_forecast.csv")
    forecast["month_start"] = pd.to_datetime(forecast["month_start"])

    return monthly_kpi, entity_kpi, region_kpi, pnl, opex, scenarios, forecast


# Plot revenue vs budget
def plot_revenue_vs_budget(df: pd.DataFrame) -> None:
    fig, ax = plt.subplots()

    # Plot actual and budget lines
    ax.plot(
        df["month_start"],
        df["actual_revenue"],
        label="Actual Revenue",
        color=COLORS["actual"],
    )
    ax.plot(
        df["month_start"],
        df["budget_revenue"],
        label="Budget Revenue",
        color=COLORS["budget"],
        alpha=0.95,
    )

    # Add variance shading
    ax.fill_between(
        df["month_start"],
        df["actual_revenue"],
        df["budget_revenue"],
        color=COLORS["fill_blue"],
        alpha=0.35,
    )

    # Style chart
    style_axis(ax, "Revenue vs Budget", "Monthly actual revenue compared with plan.")

    # Add end labels
    add_line_end_label(ax, df["month_start"], df["actual_revenue"], "Actual: ")
    add_line_end_label(ax, df["month_start"], df["budget_revenue"], "Budget: ")

    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.legend()
    fig.tight_layout()
    fig.savefig(CHART_DIR / "revenue_vs_budget.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


# Plot EBITDA vs budget
def plot_ebitda_vs_budget(df: pd.DataFrame) -> None:
    fig, ax = plt.subplots()

    # Plot actual and budget lines
    ax.plot(
        df["month_start"],
        df["actual_ebitda"],
        label="Actual EBITDA",
        color=COLORS["ebitda"],
    )
    ax.plot(
        df["month_start"],
        df["budget_ebitda"],
        label="Budget EBITDA",
        color=COLORS["budget"],
        alpha=0.95,
    )

    # Add variance shading
    ax.fill_between(
        df["month_start"],
        df["actual_ebitda"],
        df["budget_ebitda"],
        color=COLORS["fill_orange"],
        alpha=0.35,
    )

    # Style chart
    style_axis(ax, "EBITDA vs Budget", "Tracking profitability against plan.")

    # Add end labels
    add_line_end_label(ax, df["month_start"], df["actual_ebitda"], "Actual: ")
    add_line_end_label(ax, df["month_start"], df["budget_ebitda"], "Budget: ")

    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.legend()
    fig.tight_layout()
    fig.savefig(CHART_DIR / "ebitda_vs_budget.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


# Plot EBITDA margin trend
def plot_ebitda_margin(df: pd.DataFrame) -> None:
    fig, ax = plt.subplots()

    # Convert margins to percent
    actual_margin = df["actual_ebitda_margin_pct"] * 100
    budget_margin = df["budget_ebitda_margin_pct"] * 100

    # Plot actual and budget margin
    ax.plot(
        df["month_start"],
        actual_margin,
        label="Actual Margin %",
        color=COLORS["ebitda"],
    )
    ax.plot(
        df["month_start"],
        budget_margin,
        label="Budget Margin %",
        color=COLORS["budget"],
        alpha=0.95,
    )

    # Add area fill
    ax.fill_between(
        df["month_start"],
        actual_margin,
        color=COLORS["fill_orange"],
        alpha=0.25,
    )

    # Style chart
    style_axis(ax, "EBITDA Margin Trend", "Margin trend over time.", percent_axis=True)

    # Add end labels
    add_line_end_label(ax, df["month_start"], actual_margin, "Actual: ", percent=True)
    add_line_end_label(ax, df["month_start"], budget_margin, "Budget: ", percent=True)

    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.legend()
    fig.tight_layout()
    fig.savefig(CHART_DIR / "ebitda_margin_trend.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


# Plot entity revenue vs EBITDA
def plot_entity_revenue_ebitda(entity_kpi: pd.DataFrame) -> None:
    df = entity_kpi.sort_values("actual_revenue", ascending=False).copy()
    x = np.arange(len(df))
    width = 0.38

    fig, ax = plt.subplots()

    # Plot grouped bars
    bars1 = ax.bar(
        x - width / 2,
        df["actual_revenue"],
        width=width,
        label="Revenue",
        color=COLORS["revenue"],
    )
    bars2 = ax.bar(
        x + width / 2,
        df["actual_ebitda"],
        width=width,
        label="EBITDA",
        color=COLORS["ebitda"],
    )

    # Style chart
    style_axis(ax, "Entity Revenue vs EBITDA", "Compares scale and profitability by entity.")

    # Add bar labels
    add_bar_labels(ax, bars1)
    add_bar_labels(ax, bars2)

    ax.set_xticks(x)
    ax.set_xticklabels(df["entity"])
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.legend()
    fig.tight_layout()
    fig.savefig(CHART_DIR / "entity_revenue_vs_ebitda.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


# Plot region EBITDA margin comparison
def plot_region_margin_comparison(region_kpi: pd.DataFrame) -> None:
    df = region_kpi.copy()
    df["ebitda_margin_pct"] = df["ebitda_margin_pct"] * 100
    df["entity_region"] = df["entity"] + " - " + df["region"]
    df = df.sort_values("ebitda_margin_pct", ascending=True)

    # Use distinct colors per category
    colors = get_distinct_colors(len(df))

    fig, ax = plt.subplots(figsize=(13, 7))

    # Plot horizontal bars
    ax.barh(
        df["entity_region"],
        df["ebitda_margin_pct"],
        color=colors,
        alpha=0.95,
    )

    # Add average line
    avg_margin = df["ebitda_margin_pct"].mean()
    ax.axvline(
        avg_margin,
        linestyle="--",
        linewidth=1.2,
        alpha=0.5,
        color=COLORS["neutral"],
    )
    ax.text(avg_margin, len(df) - 0.5, f" Avg {avg_margin:.1f}%", fontsize=9, alpha=0.8)

    # Style chart
    style_axis(
        ax,
        "EBITDA Margin by Entity and Region",
        "Highlights stronger and weaker operating areas.",
        percent_axis=True,
    )

    # Add labels at end of bars
    for i, value in enumerate(df["ebitda_margin_pct"]):
        ax.text(value, i, f" {value:.1f}%", va="center", fontsize=8)

    ax.set_xlabel("")
    ax.set_ylabel("")
    fig.tight_layout()
    fig.savefig(CHART_DIR / "region_ebitda_margin_comparison.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


# Plot revenue waterfall bridge
def plot_latest_month_revenue_bridge(monthly_kpi: pd.DataFrame) -> None:
    latest = monthly_kpi.sort_values("month_start").iloc[-1]

    # Build bridge values
    budget_value = latest["budget_revenue"]
    variance_value = latest["revenue_variance"]
    actual_value = latest["actual_revenue"]

    labels = ["Budget", "Variance", "Actual"]
    values = [budget_value, variance_value, actual_value]
    bottoms = [0, budget_value, 0]

    # Pick semantic colors
    variance_color = COLORS["favorable"] if variance_value >= 0 else COLORS["unfavorable"]
    bar_colors = [COLORS["budget"], variance_color, COLORS["actual"]]

    fig, ax = plt.subplots(figsize=(10, 6))

    # Plot waterfall bars
    for i in range(len(labels)):
        ax.bar(labels[i], values[i], bottom=bottoms[i], color=bar_colors[i], alpha=0.92)

    # Add guide lines
    ax.plot([0, 1], [budget_value, budget_value], linestyle="--", alpha=0.35, color=COLORS["neutral"])
    ax.plot([1, 2], [actual_value, actual_value], linestyle="--", alpha=0.35, color=COLORS["neutral"])

    # Style chart
    style_axis(ax, f"Revenue Bridge — {latest['period']}", "Movement from budget to actual revenue.")

    ax.set_xlabel("")
    ax.set_ylabel("")
    fig.tight_layout()
    fig.savefig(CHART_DIR / "latest_month_revenue_bridge.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


# Plot EBITDA waterfall bridge
def plot_latest_month_ebitda_bridge(monthly_kpi: pd.DataFrame) -> None:
    latest = monthly_kpi.sort_values("month_start").iloc[-1]

    # Build bridge values
    gross_profit = latest["actual_gross_profit"]
    opex = latest["actual_total_opex"]
    ebitda = latest["actual_ebitda"]

    labels = ["Gross Profit", "Opex", "EBITDA"]
    values = [gross_profit, -opex, ebitda]
    bottoms = [0, gross_profit, 0]
    bar_colors = [COLORS["gross_profit"], COLORS["opex"], COLORS["ebitda"]]

    fig, ax = plt.subplots(figsize=(10, 6))

    # Plot bars
    for i in range(len(labels)):
        ax.bar(labels[i], values[i], bottom=bottoms[i], color=bar_colors[i], alpha=0.92)

    # Add zero line
    ax.axhline(0, linewidth=1.0, alpha=0.25, color=COLORS["neutral"])

    # Style chart
    style_axis(ax, f"EBITDA Bridge — {latest['period']}", "Bridge from gross profit to EBITDA.")

    ax.set_xlabel("")
    ax.set_ylabel("")
    fig.tight_layout()
    fig.savefig(CHART_DIR / "latest_month_ebitda_bridge.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


# Plot department overspend Pareto
def plot_department_pareto(opex: pd.DataFrame) -> None:
    latest_month = opex["month_start"].max()
    latest = opex[opex["month_start"] == latest_month].copy()

    # Aggregate department variances
    df = (
        latest.groupby("department", as_index=False)["total_opex_variance"]
        .sum()
        .sort_values("total_opex_variance", ascending=False)
    )

    # Keep positive overspends only
    df = df[df["total_opex_variance"] > 0].copy()

    if df.empty:
        return

    # Calculate cumulative contribution
    df["cum_pct"] = df["total_opex_variance"].cumsum() / df["total_opex_variance"].sum() * 100

    fig, ax1 = plt.subplots(figsize=(12, 6))
    ax2 = ax1.twinx()

    # Plot overspend bars
    bars = ax1.bar(
        df["department"],
        df["total_opex_variance"],
        color=COLORS["unfavorable"],
        alpha=0.9,
    )

    # Plot cumulative line
    ax2.plot(
        df["department"],
        df["cum_pct"],
        marker="o",
        linewidth=2,
        color=COLORS["forecast"],
    )

    # Style primary axis
    style_axis(
        ax1,
        f"Department Overspend Pareto — {latest_month.strftime('%Y-%m')}",
        "Shows which departments drive most of the overspend.",
    )

    # Style secondary axis
    ax2.set_ylim(0, 110)
    ax2.yaxis.set_major_formatter(FuncFormatter(format_percent))
    ax2.spines["top"].set_visible(False)

    # Add labels
    add_bar_labels(ax1, bars)

    ax1.set_xlabel("")
    ax1.set_ylabel("")
    ax2.set_ylabel("Cumulative %")
    plt.xticks(rotation=25, ha="right")

    fig.tight_layout()
    fig.savefig(CHART_DIR / "department_overspend_pareto.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


# Plot scenario EBITDA comparison
def plot_scenario_ebitda_comparison(scenarios: pd.DataFrame) -> None:
    summary = (
        scenarios.groupby("forecast_version", as_index=False)["forecast_ebitda"]
        .sum()
        .sort_values("forecast_ebitda", ascending=False)
    )

    # Use distinct colors per scenario
    colors = get_distinct_colors(len(summary))

    fig, ax = plt.subplots(figsize=(12, 6))

    # Plot bars
    bars = ax.bar(
        summary["forecast_version"],
        summary["forecast_ebitda"],
        color=colors,
        alpha=0.95,
    )

    # Style chart
    style_axis(ax, "Scenario Comparison — Forecast EBITDA", "Profitability by forecast scenario.")

    # Add labels
    add_bar_labels(ax, bars)

    ax.set_xlabel("")
    ax.set_ylabel("")
    plt.xticks(rotation=25, ha="right")
    fig.tight_layout()
    fig.savefig(CHART_DIR / "scenario_ebitda_comparison.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


# Plot scenario bubble chart
def plot_scenario_bubble(scenarios: pd.DataFrame) -> None:
    summary = (
        scenarios.groupby("forecast_version", as_index=False)[
            ["forecast_revenue", "forecast_ebitda", "forecast_gross_profit"]
        ]
        .sum()
    )

    # Scale bubble size by gross profit
    bubble_size = summary["forecast_gross_profit"] / summary["forecast_gross_profit"].max() * 2000
    bubble_colors = get_distinct_colors(len(summary))

    fig, ax = plt.subplots(figsize=(11, 7))

    # Plot bubbles
    ax.scatter(
        summary["forecast_revenue"],
        summary["forecast_ebitda"],
        s=bubble_size,
        c=bubble_colors,
        alpha=0.55,
    )

    # Add scenario labels
    for _, row in summary.iterrows():
        ax.annotate(
            row["forecast_version"],
            (row["forecast_revenue"], row["forecast_ebitda"]),
            xytext=(5, 5),
            textcoords="offset points",
            fontsize=9,
        )

    # Style chart
    style_axis(ax, "Scenario Bubble Chart", "Bubble size represents forecast gross profit.")

    ax.set_xlabel("Forecast Revenue")
    ax.set_ylabel("Forecast EBITDA")
    fig.tight_layout()
    fig.savefig(CHART_DIR / "scenario_bubble_chart.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


# Plot actuals plus rolling forecast
def plot_actuals_and_forecast(monthly_kpi: pd.DataFrame, forecast: pd.DataFrame) -> None:
    # Prepare actuals
    actuals = monthly_kpi[["month_start", "actual_revenue"]].copy()

    # Prepare forecast summary
    forecast_sum = (
        forecast.groupby("month_start", as_index=False)[["forecast_revenue"]]
        .sum()
        .sort_values("month_start")
    )

    fig, ax = plt.subplots(figsize=(13, 6))

    # Plot actual revenue
    ax.plot(
        actuals["month_start"],
        actuals["actual_revenue"],
        label="Actual Revenue",
        color=COLORS["actual"],
    )

    # Plot forecast revenue
    ax.plot(
        forecast_sum["month_start"],
        forecast_sum["forecast_revenue"],
        linestyle="--",
        label="Forecast Revenue",
        color=COLORS["forecast"],
    )

    # Style chart
    style_axis(
        ax,
        "Actuals + Rolling Forecast",
        "Historical actual revenue with forward forecast continuation.",
    )

    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.legend()
    fig.tight_layout()
    fig.savefig(CHART_DIR / "actuals_plus_forecast.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


# Plot executive KPI scorecard
def plot_executive_scorecard(monthly_kpi: pd.DataFrame) -> None:
    latest = monthly_kpi.sort_values("month_start").iloc[-1]

    # Build scorecard values
    cards = [
        ("Revenue", latest["actual_revenue"], COLORS["revenue"]),
        ("Revenue Var", latest["revenue_variance"], COLORS["favorable"] if latest["revenue_variance"] >= 0 else COLORS["unfavorable"]),
        ("Gross Profit", latest["actual_gross_profit"], COLORS["gross_profit"]),
        ("EBITDA", latest["actual_ebitda"], COLORS["ebitda"]),
        ("EBITDA Var", latest["ebitda_variance"], COLORS["favorable"] if latest["ebitda_variance"] >= 0 else COLORS["unfavorable"]),
        ("EBITDA Margin %", latest["actual_ebitda_margin_pct"] * 100, COLORS["highlight"]),
    ]

    fig, axes = plt.subplots(2, 3, figsize=(14, 7))
    axes = axes.flatten()

    for ax, (title, value, color) in zip(axes, cards):
        # Remove ticks for scorecard style
        ax.set_xticks([])
        ax.set_yticks([])

        # Show a subtle border
        for spine in ax.spines.values():
            spine.set_visible(True)
            spine.set_alpha(0.15)

        # Format metric value
        if "%" in title:
            value_text = f"{value:.1f}%"
        else:
            value_text = f"${value / 1_000_000:.1f}M"

        # Add title and value
        ax.text(0.05, 0.75, title, transform=ax.transAxes, fontsize=11, alpha=0.75)
        ax.text(0.05, 0.40, value_text, transform=ax.transAxes, fontsize=22, weight="bold", color=color)

    # Add page title
    fig.suptitle(
        f"Executive KPI Scorecard — {latest['period']}",
        x=0.06,
        ha="left",
        fontsize=18,
        weight="bold",
    )
    fig.tight_layout(rect=[0, 0, 1, 0.94])
    fig.savefig(CHART_DIR / "executive_kpi_scorecard.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


# Plot executive finance dashboard
def plot_executive_dashboard(
    monthly_kpi: pd.DataFrame,
    entity_kpi: pd.DataFrame,
    scenarios: pd.DataFrame,
) -> None:
    latest = monthly_kpi.sort_values("month_start").iloc[-1]

    # Aggregate scenario EBITDA
    scenario_summary = (
        scenarios.groupby("forecast_version", as_index=False)["forecast_ebitda"]
        .sum()
        .sort_values("forecast_ebitda", ascending=False)
    )

    # Sort entity EBITDA
    entity_summary = entity_kpi.sort_values("actual_ebitda", ascending=False)

    # Create dashboard canvas
    fig = plt.figure(figsize=(16, 10))

    # Create layout
    ax1 = plt.subplot2grid((2, 2), (0, 0))
    ax2 = plt.subplot2grid((2, 2), (0, 1))
    ax3 = plt.subplot2grid((2, 2), (1, 0))
    ax4 = plt.subplot2grid((2, 2), (1, 1))

    # Revenue trend
    ax1.plot(monthly_kpi["month_start"], monthly_kpi["actual_revenue"], label="Actual", color=COLORS["actual"])
    ax1.plot(monthly_kpi["month_start"], monthly_kpi["budget_revenue"], label="Budget", color=COLORS["budget"], alpha=0.85)
    style_axis(ax1, "Revenue Trend", "Actual vs budget.")
    ax1.legend()

    # EBITDA trend
    ax2.plot(monthly_kpi["month_start"], monthly_kpi["actual_ebitda"], label="Actual", color=COLORS["ebitda"])
    ax2.plot(monthly_kpi["month_start"], monthly_kpi["budget_ebitda"], label="Budget", color=COLORS["budget"], alpha=0.85)
    style_axis(ax2, "EBITDA Trend", "Profitability vs plan.")
    ax2.legend()

    # Entity EBITDA bars
    entity_colors = get_distinct_colors(len(entity_summary))
    bars = ax3.bar(entity_summary["entity"], entity_summary["actual_ebitda"], color=entity_colors, alpha=0.95)
    style_axis(ax3, "Entity EBITDA", "Current contribution by entity.")
    add_bar_labels(ax3, bars)

    # Scenario EBITDA bars
    scenario_colors = get_distinct_colors(len(scenario_summary))
    bars2 = ax4.bar(
        scenario_summary["forecast_version"],
        scenario_summary["forecast_ebitda"],
        color=scenario_colors,
        alpha=0.95,
    )
    style_axis(ax4, "Scenario EBITDA", "Forecast profitability across cases.")
    add_bar_labels(ax4, bars2)
    ax4.tick_params(axis="x", rotation=25)

    # Add dashboard title
    fig.suptitle(
        f"Executive Finance Dashboard — {latest['period']}",
        x=0.06,
        ha="left",
        fontsize=20,
        weight="bold",
    )
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(CHART_DIR / "executive_finance_dashboard.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


# Run all charts
def run_chart_pipeline() -> None:
    monthly_kpi, entity_kpi, region_kpi, pnl, opex, scenarios, forecast = load_data()

    # Core charts
    plot_revenue_vs_budget(monthly_kpi)
    plot_ebitda_vs_budget(monthly_kpi)
    plot_ebitda_margin(monthly_kpi)
    plot_entity_revenue_ebitda(entity_kpi)
    plot_region_margin_comparison(region_kpi)

    # Premium charts
    plot_latest_month_revenue_bridge(monthly_kpi)
    plot_latest_month_ebitda_bridge(monthly_kpi)
    plot_department_pareto(opex)
    plot_scenario_ebitda_comparison(scenarios)
    plot_scenario_bubble(scenarios)
    plot_actuals_and_forecast(monthly_kpi, forecast)
    plot_executive_scorecard(monthly_kpi)
    plot_executive_dashboard(monthly_kpi, entity_kpi, scenarios)

    print("Premium executive charts created.")


if __name__ == "__main__":
    run_chart_pipeline()
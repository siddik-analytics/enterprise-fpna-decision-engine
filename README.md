# Enterprise FP&A Decision Engine

An end-to-end FP&A analytics project that simulates a real-world corporate finance environment using Python, SQL, DuckDB, forecasting, scenario modeling, automated commentary, and executive dashboards.

This project demonstrates how a modern FP&A function can automate reporting, forecasting, and decision support using scalable data workflows.

---

# Overview

Finance teams often spend significant time manually preparing:

- Monthly reporting packs  
- Budget vs actual variance analysis  
- Rolling forecasts  
- Scenario planning  
- Department spend reviews  
- KPI dashboards  
- Executive commentary  

This project converts that process into a fully automated pipeline.

It generates synthetic multi-entity finance data, validates it, builds reporting tables, creates forecasts and scenarios, and produces executive-ready dashboards and visuals.

---

# What This Project Does

## Finance Data Simulation
- Generates 36 months of finance data  
- Multi-entity and multi-region structure  
- Revenue, COGS, Opex, Headcount, Working Capital  
- Budget vs Actual layers  

## FP&A Reporting
- Monthly P&L dataset  
- Revenue analysis  
- Gross margin tracking  
- Opex breakdown  
- EBITDA analysis  
- Entity and region performance  

## Forecasting & Planning
- Rolling 12-month forecast  
- Trend-based forecasting logic  
- Scenario comparison (upside/downside)  
- Profitability impact modeling  

## Executive Decision Support
- KPI scorecards  
- Executive dashboards  
- Revenue and EBITDA bridges  
- Variance commentary  
- Scenario visuals  
- Department overspend analysis  

---

# Business Questions Answered

This project helps answer practical FP&A questions:

- Which entity is driving EBITDA performance?
- Where are we missing budget?
- Which departments are overspending?
- How does forecast change under different scenarios?
- What drives margin expansion?
- How can reporting be automated?

---

# Tech Stack

- Python  
- Pandas  
- NumPy  
- Matplotlib  
- DuckDB  
- SQL  
- Git / GitHub  

---

# Project Structure

```
enterprise-fpna-decision-engine/
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── master_data/
│
├── output/
│   ├── charts/
│   ├── reports/
│   └── logs/
│
├── screenshots/
│
├── sql/
│
├── src/
│   ├── generate_data.py
│   ├── validate.py
│   ├── transform.py
│   ├── forecast.py
│   ├── scenario.py
│   ├── metrics.py
│   ├── commentary.py
│   ├── charts.py
│
├── main.py
├── requirements.txt
└── README.md
```

---

# End-to-End Pipeline

```
Synthetic Data
     ↓
Validation
     ↓
Transformation
     ↓
SQL Reporting Layer
     ↓
Rolling Forecast
     ↓
Scenario Modeling
     ↓
KPI Tables
     ↓
Executive Visuals
```

---

# Key Outputs

## Reporting
- Monthly P&L  
- Revenue summary  
- Opex summary  
- Headcount summary  
- Working capital metrics  

## Forecasting
- Rolling 12-month forecast  
- Scenario comparison  
- Forecast entity summary  

## Executive Outputs
- KPI scorecard  
- Executive dashboard  
- Revenue vs budget chart  
- EBITDA vs budget chart  
- Revenue bridge  
- EBITDA bridge  
- Scenario bubble chart  
- Department overspend Pareto  

---

# Example Visuals

## Executive Finance Dashboard
![Executive Finance Dashboard](output\charts/executive_finance_dashboard.png)

## Executive KPI Scorecard
![Executive KPI Scorecard](output\charts/executive_kpi_scorecard.png)

## Revenue vs Budget
![Revenue vs Budget](output\charts/revenue_vs_budget.png)

## Revenue Bridge
![Revenue Bridge](output\charts/latest_month_revenue_bridge.png)

## Scenario Bubble Chart
![Scenario Bubble Chart](output\charts/scenario_bubble_chart.png)

## Department Overspend Pareto
![Department Overspend Pareto](output\charts/department_overspend_pareto.png)

---

# How to Run

## Install dependencies

```
pip install -r requirements.txt
```

## Run full pipeline

```
python main.py
```

Outputs will be generated in:

```
output/
```

---

# Example Deliverables

After running the pipeline, the project produces:

- Processed finance datasets  
- Forecast outputs  
- Scenario comparisons  
- KPI tables  
- Executive dashboards  
- Management charts  
- Commentary files  

---

# Author

Md Siddik, ACCA  
Senior Financial Analyst / FP&A  
Vancouver, Canada
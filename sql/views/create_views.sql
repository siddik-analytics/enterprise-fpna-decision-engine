-- Consolidated monthly P&L by entity and region
CREATE OR REPLACE VIEW vw_monthly_pnl AS
SELECT
    month_start,
    period,
    entity,
    region,
    actual_revenue,
    budget_revenue,
    revenue_variance,
    actual_gross_profit,
    budget_gross_profit,
    gross_profit_variance,
    actual_total_opex,
    budget_total_opex,
    total_opex_variance,
    actual_ebitda,
    budget_ebitda,
    ebitda_variance,
    gross_margin_pct_actual,
    gross_margin_pct_budget,
    ebitda_margin_actual,
    ebitda_margin_budget
FROM monthly_pnl_dataset;

-- Department opex view
CREATE OR REPLACE VIEW vw_department_opex AS
SELECT
    month_start,
    period,
    entity,
    region,
    department,
    actual_salary_opex,
    budget_salary_opex,
    salary_opex_variance,
    actual_non_salary_opex,
    budget_non_salary_opex,
    non_salary_opex_variance,
    actual_total_opex,
    budget_total_opex,
    total_opex_variance
FROM monthly_opex_summary;

-- Headcount summary view
CREATE OR REPLACE VIEW vw_headcount AS
SELECT
    month_start,
    period,
    entity,
    region,
    department,
    actual_ending_headcount,
    budget_ending_headcount,
    headcount_variance,
    actual_payroll_cost,
    budget_payroll_cost,
    payroll_variance
FROM monthly_headcount_summary;

-- Working capital summary view
CREATE OR REPLACE VIEW vw_working_capital AS
SELECT
    month_start,
    period,
    entity,
    actual_accounts_receivable,
    budget_accounts_receivable,
    ar_variance,
    actual_accounts_payable,
    budget_accounts_payable,
    ap_variance,
    actual_inventory,
    budget_inventory,
    inventory_variance,
    actual_operating_cash_proxy,
    budget_operating_cash_proxy,
    cash_proxy_variance
FROM monthly_working_capital_summary;
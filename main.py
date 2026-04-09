from src.generate_data import main as generate_data_main
from src.validate import run_all_validations
from src.transform import run_all_transforms
from src.load_to_duckdb import load_all_tables
from src.build_views import build_views
from src.query_reporting import run_reporting_queries
from src.forecast import run_forecast_pipeline
from src.scenario import run_scenario_pipeline
from src.export import export_forecast_reports


# Run the full FP&A pipeline
def run_pipeline() -> None:
    print("STEP 1: Generating synthetic data...")
    generate_data_main()

    print("STEP 2: Running validation checks...")
    run_all_validations()

    print("STEP 3: Building processed reporting tables...")
    run_all_transforms()

    print("STEP 4: Loading tables into DuckDB...")
    load_all_tables()

    print("STEP 5: Building SQL views...")
    build_views()

    print("STEP 6: Running management reporting queries...")
    run_reporting_queries()

    print("STEP 7: Building rolling forecast...")
    run_forecast_pipeline()

    print("STEP 8: Building scenarios...")
    run_scenario_pipeline()

    print("STEP 9: Exporting forecast reports...")
    export_forecast_reports()

    print("Pipeline completed successfully.")


if __name__ == "__main__":
    run_pipeline()
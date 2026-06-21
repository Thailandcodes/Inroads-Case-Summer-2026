import importlib
import subprocess
import sys
from datetime import datetime

from helpers import (
    setup_folders,
    load_all_data,
    get_sex_data,
    get_race_data,
    get_cause_data,
    get_age_cause_data,
    load_social_data,
    get_social_data,
    save_csv,
    package_project
)

from graphs import (
    graph_heatmaps_by_source_and_county,
    graph_combined_pie_dashboards,
    graph_social_determinants,
    graph_race_social_breakdowns,
    graph_age_cause_sunbursts
)

from analyze_aetna_ma_enrollment import run_aetna_analysis
from market_dashboards import run_market_dashboards
from forecast import run_forecast
from report import generate_metrics_report


REQUIRED_PACKAGES = [
    "pandas",
    "openpyxl",
    "matplotlib",
    "plotly",
    "seaborn",
    "tabulate",
    "weasyprint"
]


def install_requirements():
    missing = []

    for package in REQUIRED_PACKAGES:
        try:
            importlib.import_module(package)
        except ImportError:
            missing.append(package)

    if not missing:
        print("All required packages already installed.\n")
        return

    print("Installing missing packages...\n")

    subprocess.check_call([
        sys.executable,
        "-m",
        "pip",
        "install",
        *missing
    ])

    print("Installation complete.\n")


def checkpoint(step, total, message):
    now = datetime.now().strftime("%H:%M:%S")
    print(f"[{now}] [{step}/{total}] {message}")


def main():
    checkpoint(1, 14, "Checking required packages...")
    install_requirements()

    checkpoint(2, 14, "Creating output folders...")
    setup_folders(clear_outputs=True)

    checkpoint(3, 14, "Loading mortality datasets...")
    data = load_all_data()
    print(f"Loaded {len(data):,} records.\n")

    checkpoint(4, 14, "Preparing analysis datasets...")
    sex_data = get_sex_data(data)
    race_data = get_race_data(data)
    cause_data = get_cause_data(data)
    age_cause_data = get_age_cause_data(data)

    checkpoint(5, 14, "Saving cleaned datasets...")
    save_csv(sex_data, "Sex Data")
    save_csv(race_data, "Race Data")
    save_csv(cause_data, "Cause Data")
    save_csv(age_cause_data, "Age Cause Data")

    checkpoint(6, 14, "Generating mortality dashboards...")
    graph_heatmaps_by_source_and_county(cause_data)
    graph_combined_pie_dashboards(
        sex_data,
        race_data,
        cause_data
    )

    checkpoint(7, 14, "Generating interactive disease and age sunbursts...")
    graph_age_cause_sunbursts(age_cause_data)

    checkpoint(8, 14, "Loading social determinant datasets...")
    social_raw = load_social_data()
    social_data = get_social_data(social_raw)
    save_csv(social_data, "Social Determinants Data")

    checkpoint(9, 14, "Generating education and SES visualizations...")
    graph_social_determinants(social_data)
    graph_race_social_breakdowns(social_data)

    checkpoint(10, 14, "Running Aetna enrollment analysis...")
    aetna_summary = run_aetna_analysis()

    checkpoint(11, 14, "Running age 65+ market opportunity analysis...")
    market_summary = run_market_dashboards()

    checkpoint(12, 14, "Generating CVS forecast...")
    forecast_summary = run_forecast()

    checkpoint(13, 14, "Generating HTML, PDF, and Markdown reports...")
    generate_metrics_report(
        sex_data=sex_data,
        race_data=race_data,
        cause_data=cause_data,
        social_data=social_data,
        aetna_summary=aetna_summary,
        market_summary=market_summary,
        forecast_summary=forecast_summary
    )

    checkpoint(14, 14, "Packaging final project...")
    package_project()

    print("\n" + "=" * 60)
    print("ATLANTA HEALTH EDA COMPLETED SUCCESSFULLY")
    print("=" * 60)
    print("Outputs created:")
    print("  • outputs/png/")
    print("  • outputs/html/")
    print("  • outputs/csv/")
    print("  • outputs/report/")
    print("  • AtlantaHealthEDA.zip")
    print("=" * 60)


if __name__ == "__main__":
    main()

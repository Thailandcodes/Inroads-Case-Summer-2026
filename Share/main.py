from helpers import (
    setup_folders,
    load_all_data,
    get_sex_data,
    get_race_data,
    get_cause_data,
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
    graph_social_sunbursts
)

from analyze_aetna_ma_enrollment import run_aetna_analysis
from market_dashboards import run_market_dashboards
from forecast import run_forecast
from report import generate_metrics_report


def main():
    print("Starting full CVS / Atlanta Health analysis...")

    setup_folders(clear_outputs=True)

    data = load_all_data()

    sex_data = get_sex_data(data)
    race_data = get_race_data(data)
    cause_data = get_cause_data(data)

    save_csv(sex_data, "Sex Data")
    save_csv(race_data, "Race Data")
    save_csv(cause_data, "Cause Data")

    graph_heatmaps_by_source_and_county(cause_data)
    graph_combined_pie_dashboards(sex_data, race_data, cause_data)

    social_raw = load_social_data()
    social_data = get_social_data(social_raw)

    save_csv(social_data, "Social Determinants Data")

    graph_social_determinants(social_data)
    graph_race_social_breakdowns(social_data)
    graph_social_sunbursts(social_data)

    print("Running Aetna enrollment analysis...")
    aetna_summary = run_aetna_analysis()

    print("Running market opportunity dashboard...")
    market_summary = run_market_dashboards()

    print("Running CVS forecast analysis...")
    forecast_summary = run_forecast()

    generate_metrics_report(
        sex_data=sex_data,
        race_data=race_data,
        cause_data=cause_data,
        social_data=social_data,
        aetna_summary=aetna_summary,
        market_summary=market_summary,
        forecast_summary=forecast_summary
    )

    package_project()

    print("Done.")
    print("Check outputs/png, outputs/html, outputs/csv, and outputs/report.")


if __name__ == "__main__":
    main()

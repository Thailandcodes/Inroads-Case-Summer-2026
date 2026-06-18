from helpers import (
    setup_folders,
    load_all_data,
    get_total_data,
    get_age_data,
    get_sex_data,
    get_race_data,
    get_cause_data,
    save_csv,
    package_project
)

from graphs import (
    graph_total_deaths,
    graph_age_trends,
    graph_sex_comparison,
    graph_race_comparison,
    graph_common_causes,
    graph_top_causes_by_source,
    graph_heatmaps_by_source_and_county,
    graph_pie_charts,
    graph_dashboard_summary
)


def main():
    print("Starting Atlanta Health EDA...")

    # Create folders for outputs
    setup_folders()

    # Load all three Excel files
    data = load_all_data()

    print("Data loaded.")
    print(data.head())
    print("\nRows by source:")
    print(data["Source"].value_counts())
    print("\nRows by county:")
    print(data["Geography"].value_counts())

    # Create smaller datasets for each analysis category
    total_data = get_total_data(data)
    age_data = get_age_data(data)
    sex_data = get_sex_data(data)
    race_data = get_race_data(data)
    cause_data = get_cause_data(data)

    # Save cleaned datasets as CSVs
    save_csv(total_data, "total_deaths")
    save_csv(age_data, "age_data")
    save_csv(sex_data, "sex_data")
    save_csv(race_data, "race_data")
    save_csv(cause_data, "cause_data")

    print("\nCleaned datasets saved.")

    # Create graphs
    graph_total_deaths(total_data)
    graph_age_trends(age_data)
    graph_sex_comparison(sex_data)
    graph_race_comparison(race_data)
    graph_common_causes(cause_data)
    graph_top_causes_by_source(cause_data)
    graph_heatmaps_by_source_and_county(cause_data)
    graph_pie_charts(sex_data, race_data, cause_data)
    graph_dashboard_summary(total_data, age_data, sex_data, cause_data)

    print("\nGraphs created.")

    # Build Share folder and ZIP file
    package_project()

    print("\nDone.")
    print("Check the outputs folder for graphs and CSV files.")
    print("Check AtlantaHealthEDA.zip for the shareable project package.")


if __name__ == "__main__":
    main()
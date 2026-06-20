from helpers import (
    setup_folders,
    load_all_data,
    get_sex_data,
    get_race_data,
    get_cause_data,
    save_csv,
    package_project,
    load_social_data,
    get_social_data
)

from graphs import (
    graph_heatmaps_by_source_and_county,
    graph_social_determinants,
    graph_race_social_breakdowns,
    graph_social_sunbursts,
    graph_sex_comparison,
    graph_race_comparison,
    graph_pie_charts,
    graph_original_bar_dashboard,
    graph_original_pie_dashboards
)


def main():
    print("Starting Atlanta Health EDA...")

    setup_folders()

    data = load_all_data()

    print("Data loaded.")
    print("\nRows by source:")
    print(data["Source"].value_counts())
    print("\nRows by county:")
    print(data["Geography"].value_counts())

    sex_data = get_sex_data(data)
    race_data = get_race_data(data)
    cause_data = get_cause_data(data)

    save_csv(sex_data, "sex_data")
    save_csv(race_data, "race_data")
    save_csv(cause_data, "cause_data")

    print("\nCleaned datasets saved.")

    graph_original_bar_dashboard(sex_data, race_data)
    graph_original_pie_dashboards(sex_data, race_data, cause_data)
    graph_heatmaps_by_source_and_county(cause_data)

    print("\nStarting social determinants analysis...")

    social_raw = load_social_data()
    social_data = get_social_data(social_raw)

    save_csv(social_data, "social_determinants_data")

    graph_social_determinants(social_data)
    graph_race_social_breakdowns(social_data)
    graph_social_sunbursts(social_data)

    print("\nSocial determinants analysis complete.")
    print("\nGraphs created.")

    package_project()

    print("\nDone.")
    print("Check the outputs folder for graphs and CSV files.")
    print("Check AtlantaHealthEDA.zip for the shareable project package.")


if __name__ == "__main__":
    main()
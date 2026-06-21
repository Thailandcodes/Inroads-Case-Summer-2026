
from helpers import (
    setup_folders,
    load_mortality_data,
    load_social_data,
    get_sex_data,
    get_race_data,
    get_cause_data,
    save_csv,
    try_load_market_summary,
)
from graphs import (
    graph_demographic_dashboard,
    graph_health_burden_dashboard,
    graph_social_dashboard,
    graph_target_group_dashboard,
    graph_clean_sunbursts,
    graph_market_dashboard,
)
from report import generate_report


def main():
    print("Starting Atlanta Health EDA patch run...")
    setup_folders(clear_outputs=True)

    mortality = load_mortality_data()
    sex_data = get_sex_data(mortality)
    race_data = get_race_data(mortality)
    cause_data = get_cause_data(mortality)
    social_data = load_social_data()
    market_summary = try_load_market_summary()

    save_csv(sex_data, "sex_data")
    save_csv(race_data, "race_data")
    save_csv(cause_data, "cause_data")
    save_csv(social_data, "social_determinants_data")

    graph_demographic_dashboard(sex_data, race_data)
    graph_health_burden_dashboard(cause_data)
    graph_social_dashboard(social_data)
    graph_target_group_dashboard(social_data)
    graph_clean_sunbursts(social_data)
    graph_market_dashboard(market_summary)

    generate_report(sex_data, race_data, cause_data, social_data, market_summary)

    print("Done. Use outputs/png for dashboard images, outputs/html for interactive charts, and outputs/report for the metrics report.")


if __name__ == "__main__":
    main()

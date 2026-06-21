from pathlib import Path
import pandas as pd


REPORT_DIR = Path("outputs/report")
REPORT_DIR.mkdir(parents=True, exist_ok=True)


def nice_table(df):
    if df is None or df.empty:
        return "No data available.\n"

    return df.to_markdown(index=False)


def top_row(df, group_col, value_col="Deaths"):
    if df is None or df.empty:
        return None

    grouped = (
        df.groupby(group_col, as_index=False)[value_col]
        .sum()
        .sort_values(value_col, ascending=False)
    )

    if grouped.empty:
        return None

    return grouped.iloc[0]


def generate_metrics_report(
    sex_data,
    race_data,
    cause_data,
    social_data,
    aetna_summary=None,
    market_summary=None,
    forecast_summary=None
):
    report = "# Atlanta Health EDA Metrics Report\n\n"

    report += "## Data Sources\n\n"
    report += "- Georgia Rankable Causes Fulton and DeKalb 2024\n"
    report += "- OASIS Rankable Causes Fulton and DeKalb 2024\n"
    report += "- NCHS Rankable Causes Fulton and DeKalb 2024\n"
    report += "- Georgia, OASIS, and NCHS social determinants files with education and SES vulnerability\n"
    report += "- CMS CPSC Medicare Advantage enrollment file for Aetna contract-level enrollment\n"
    report += "- U.S. Census ACS S0101 Age and Sex table for age 65+ population\n"
    report += "- CVS Health Care Benefits segment revenue data, 2023-2025\n\n"

    report += "## Important Method Note\n\n"
    report += (
        "NCHS is kept separate from Georgia and OASIS in combined visuals because "
        "its structure and category naming are not directly comparable. Separate NCHS "
        "charts are generated for cleaner interpretation.\n\n"
    )

    report += "## Core Mortality Metrics\n\n"

    top_cause = top_row(cause_data, "Cause")
    top_race = top_row(race_data, "Race")
    top_sex = top_row(sex_data, "Sex")

    if top_cause is not None:
        report += f"- Highest total cause of death in the analysis: **{top_cause['Cause']}** ({top_cause['Deaths']:,.0f} deaths).\n"

    if top_race is not None:
        report += f"- Highest total race category in the mortality data: **{top_race['Race']}** ({top_race['Deaths']:,.0f} deaths).\n"

    if top_sex is not None:
        report += f"- Highest total sex category in the mortality data: **{top_sex['Sex']}** ({top_sex['Deaths']:,.0f} deaths).\n"

    report += "\n## Top Causes by Source and County\n\n"

    top_source_county = (
        cause_data.sort_values("Deaths", ascending=False)
        .groupby(["Source", "Geography"])
        .head(5)
        [["Source", "Geography", "Cause", "Deaths", "Percent"]]
    )

    report += nice_table(top_source_county)
    report += "\n\n"

    report += "## Social Determinants Metrics\n\n"

    if social_data is not None and not social_data.empty:
        social_top = (
            social_data.groupby(["Source", "Geography", "Education", "SES Vulnerability", "Race", "Cause"], as_index=False)["Deaths"]
            .sum()
            .sort_values("Deaths", ascending=False)
            .head(15)
        )

        report += nice_table(social_top)
        report += "\n\n"

    report += "## Aetna Medicare Advantage Enrollment\n\n"

    if aetna_summary is not None:
        report += nice_table(aetna_summary)
        report += "\n\n"

    report += "## Age 65+ Market Opportunity\n\n"

    if market_summary is not None:
        report += nice_table(market_summary)
        report += "\n\n"

    report += "## CVS Health Care Benefits Forecast\n\n"

    if forecast_summary is not None:
        report += "### Revenue Forecast\n\n"
        report += nice_table(forecast_summary["forecast"])
        report += "\n\n"

        report += "### Potential Aetna Market Opportunity\n\n"
        report += nice_table(forecast_summary["opportunity"])
        report += "\n\n"

    report += "## Generated Outputs\n\n"
    report += "- Separate health burden heatmaps by source and county\n"
    report += "- Combined Georgia/OASIS pie chart dashboards\n"
    report += "- Separate NCHS pie chart dashboards\n"
    report += "- Education and SES heatmaps by source and county\n"
    report += "- Sunburst charts for Georgia/OASIS and separate NCHS sunburst charts\n"
    report += "- Aetna enrollment chart\n"
    report += "- Age 65+ market opportunity dashboard\n"
    report += "- CVS revenue forecast charts\n"
    report += "- Aetna market opportunity revenue chart\n"

    report_path = REPORT_DIR / "metrics_report.md"
    report_path.write_text(report, encoding="utf-8")

    print(f"Metrics report created: {report_path}")

    return report_path

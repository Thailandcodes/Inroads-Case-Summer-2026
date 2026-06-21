
from pathlib import Path
import pandas as pd


def fmt_number(value):
    try:
        return f"{float(value):,.0f}"
    except Exception:
        return str(value)


def fmt_percent(value):
    try:
        return f"{float(value):.1f}%"
    except Exception:
        return str(value)


def generate_report(sex_data, race_data, cause_data, social_data, market_summary=None):
    # Report metrics
    lines = []
    lines.append("# Atlanta Health EDA Metrics Report")
    lines.append("")
    lines.append("## Data Coverage")
    lines.append(f"- Sources: {', '.join(sorted(cause_data['Source'].unique()))}")
    lines.append(f"- Counties: {', '.join(sorted(cause_data['Geography'].unique()))}")
    lines.append(f"- Mortality rows analyzed: {fmt_number(len(cause_data))}")
    lines.append(f"- Social determinant rows analyzed: {fmt_number(len(social_data))}")
    lines.append("")

    lines.append("## Leading Causes of Death")
    top_causes = cause_data.groupby("Cause Label")["Deaths"].sum().sort_values(ascending=False).head(8)
    for cause, value in top_causes.items():
        lines.append(f"- {cause}: {fmt_number(value)} deaths")
    lines.append("")

    lines.append("## Race Pattern")
    top_race = race_data.groupby("Race Label")["Deaths"].sum().sort_values(ascending=False).head(5)
    for race, value in top_race.items():
        lines.append(f"- {race}: {fmt_number(value)} deaths")
    lines.append("")

    lines.append("## Sex Pattern")
    top_sex = sex_data.groupby("Sex Label")["Deaths"].sum().sort_values(ascending=False)
    for sex, value in top_sex.items():
        lines.append(f"- {sex}: {fmt_number(value)} deaths")
    lines.append("")

    lines.append("## Education and SES Signals")
    edu = social_data[(social_data["Education"] != "Selected Educations Total") & (social_data["Race"] == "Selected Races Total")].groupby("Education Label")["Deaths"].sum().sort_values(ascending=False).head(5)
    ses = social_data[(social_data["SES Vulnerability"] != "Selected SES Vulnerability Total") & (social_data["Race"] == "Selected Races Total")].groupby("SES Label")["Deaths"].sum().sort_values(ascending=False).head(5)
    lines.append("Top education categories:")
    for label, value in edu.items():
        lines.append(f"- {label}: {fmt_number(value)} deaths")
    lines.append("Top SES vulnerability categories:")
    for label, value in ses.items():
        lines.append(f"- {label}: {fmt_number(value)} deaths")
    lines.append("")

    if market_summary is not None and not market_summary.empty:
        lines.append("## Aetna / Age 65+ Market Opportunity")
        for _, row in market_summary.iterrows():
            county = str(row.get("county", "")).title()
            lines.append(f"- {county}: {fmt_number(row.get('age65_population'))} residents age 65+, {fmt_number(row.get('known_enrollment'))} known Aetna MA members, {fmt_percent(row.get('penetration_rate'))} penetration")
        lines.append("")

    lines.append("## Generated Outputs")
    lines.append("- PNG dashboards: outputs/png/")
    lines.append("- Interactive dashboards: outputs/html/")
    lines.append("- Cleaned data files: outputs/csv/")
    lines.append("")

    Path("outputs/report").mkdir(parents=True, exist_ok=True)
    Path("outputs/report/metrics_report.md").write_text("\n".join(lines), encoding="utf-8")
    print("Report saved to outputs/report/metrics_report.md")

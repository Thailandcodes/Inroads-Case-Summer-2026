from pathlib import Path
from html import escape
import base64
import pandas as pd


REPORT_DIR = Path("outputs/report")
PNG_DIR = Path("outputs/png")
HTML_DIR = Path("outputs/html")

REPORT_DIR.mkdir(parents=True, exist_ok=True)


def nice_table(df):
    if df is None or df.empty:
        return "No data available.\n"
    return df.to_markdown(index=False)


def df_to_html(df):
    if df is None or df.empty:
        return "<p>No data available.</p>"
    return df.to_html(index=False, classes="data-table", border=0)


def image_to_base64(path):
    if not path.exists():
        return ""
    encoded = base64.b64encode(path.read_bytes()).decode("utf-8")
    return f"data:image/png;base64,{encoded}"


def image_block(filename, caption):
    path = PNG_DIR / filename

    if not path.exists():
        return ""

    return f"""
    <figure>
        <img src="{image_to_base64(path)}" alt="{escape(caption)}">
        <figcaption>{escape(caption)}</figcaption>
    </figure>
    """


def interactive_links():
    links = ""

    for file in sorted(HTML_DIR.glob("*.html")):
        label = file.stem.replace("_", " ")
        links += f'<li><a href="../html/{escape(file.name)}" target="_blank">{escape(label)}</a></li>\n'

    return links


def top_rows(df, cols, n=10):
    if df is None or df.empty:
        return pd.DataFrame()

    return (
        df.groupby(cols, as_index=False)["Deaths"]
        .sum()
        .sort_values("Deaths", ascending=False)
        .head(n)
    )


def generate_metrics_report(
    sex_data,
    race_data,
    cause_data,
    social_data,
    aetna_summary=None,
    market_summary=None,
    forecast_summary=None
):
    md_path = REPORT_DIR / "metrics_report.md"
    html_path = REPORT_DIR / "metrics_report.html"
    pdf_path = REPORT_DIR / "metrics_report.pdf"

    top_causes = top_rows(
        cause_data,
        ["Source", "Geography", "Cause"],
        n=15
    )

    top_social = top_rows(
        social_data,
        ["Source", "Geography", "Education", "SES Vulnerability", "Race", "Cause"],
        n=15
    )

    markdown = "# Atlanta Health EDA Metrics Report\n\n"
    markdown += "## Executive Summary\n\n"
    markdown += (
        "This report connects mortality burden, social determinants, Aetna Medicare Advantage enrollment, "
        "age 65+ market opportunity, and CVS Health Care Benefits forecast outputs.\n\n"
    )

    markdown += "## Method Notes\n\n"
    markdown += "- NCHS is kept separate from Georgia and OASIS because its categories are not directly comparable.\n"
    markdown += "- Age 65+ population is used as a proxy for Medicare-age market opportunity.\n"
    markdown += "- Forecast outputs use analyst assumptions, not CVS-reported projections.\n"
    markdown += "- HTML report includes interactive chart links. PDF report includes static chart images.\n\n"

    markdown += "## Top Mortality Patterns\n\n"
    markdown += nice_table(top_causes)
    markdown += "\n\n"

    markdown += "## Social Determinants Patterns\n\n"
    markdown += nice_table(top_social)
    markdown += "\n\n"

    markdown += "## Aetna Enrollment\n\n"
    markdown += nice_table(aetna_summary)
    markdown += "\n\n"

    markdown += "## Age 65+ Market Opportunity\n\n"
    markdown += nice_table(market_summary)
    markdown += "\n\n"

    if forecast_summary is not None:
        markdown += "## CVS Health Care Benefits Forecast\n\n"
        markdown += nice_table(forecast_summary["forecast"])
        markdown += "\n\n"

        markdown += "## Potential Aetna Market Opportunity\n\n"
        markdown += nice_table(forecast_summary["opportunity"])
        markdown += "\n\n"

    md_path.write_text(markdown, encoding="utf-8")

    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Atlanta Health EDA Report</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            color: #3B0D0C;
            margin: 0;
            background: white;
        }}

        header {{
            background: #F9E7E2;
            border-bottom: 7px solid #C7462D;
            padding: 36px 52px;
        }}

        h1 {{
            margin: 0;
            font-size: 34px;
            color: #3B0D0C;
        }}

        h2 {{
            color: #C7462D;
            border-bottom: 2px solid #F3B2A6;
            padding-bottom: 8px;
            margin-top: 38px;
        }}

        h3 {{
            color: #8C3B2E;
        }}

        main {{
            padding: 32px 52px;
            max-width: 1200px;
            margin: auto;
        }}

        .callout {{
            background: #F9E7E2;
            border-left: 7px solid #C7462D;
            padding: 18px 22px;
            border-radius: 10px;
            margin: 20px 0;
        }}

        .grid {{
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 22px;
        }}

        figure {{
            margin: 0;
            border: 1px solid #F3B2A6;
            border-radius: 14px;
            padding: 12px;
            background: white;
        }}

        img {{
            max-width: 100%;
            height: auto;
            display: block;
        }}

        figcaption {{
            font-size: 13px;
            color: #8C3B2E;
            margin-top: 8px;
        }}

        .data-table {{
            border-collapse: collapse;
            width: 100%;
            font-size: 13px;
            margin: 12px 0 24px;
        }}

        .data-table th {{
            background: #C7462D;
            color: white;
            padding: 8px;
            text-align: left;
        }}

        .data-table td {{
            border-bottom: 1px solid #F3B2A6;
            padding: 8px;
        }}

        a {{
            color: #C7462D;
            font-weight: bold;
        }}

        @media print {{
            .grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>

<body>
<header>
    <h1>Atlanta Health EDA Report</h1>
    <p>Health burden, social determinants, Aetna opportunity, and CVS forecast analysis.</p>
</header>

<main>
    <div class="callout">
        <strong>Core story:</strong> This project identifies where mortality burden is concentrated,
        connects those patterns to social determinants, sizes the Medicare-age opportunity using age 65+
        population, and estimates possible CVS/Aetna business impact through forecast scenarios.
    </div>

    <h2>1. Health Burden</h2>
    <p>These charts show the leading causes of death by source and county. NCHS is kept separate when needed because its categories are not directly comparable.</p>

    <div class="grid">
        {image_block("Health Burden Heatmap - Georgia - Fulton.png", "Georgia - Fulton top causes of death")}
        {image_block("Health Burden Heatmap - Georgia - DeKalb.png", "Georgia - DeKalb top causes of death")}
        {image_block("Health Burden Heatmap - OASIS - Fulton.png", "OASIS - Fulton top causes of death")}
        {image_block("Health Burden Heatmap - OASIS - DeKalb.png", "OASIS - DeKalb top causes of death")}
    </div>

    <h2>2. Demographic and Cause Dashboards</h2>
    <p>These dashboards summarize sex, race, and cause distributions without creating dozens of repeated single charts.</p>

    <div class="grid">
        {image_block("Demographics Pie Dashboard - Sex.png", "Sex distribution dashboard")}
        {image_block("Demographics Pie Dashboard - Race.png", "Race distribution dashboard")}
        {image_block("Top Causes Pie Dashboard.png", "Top causes dashboard")}
        {image_block("NCHS Pie Dashboard - Top Causes.png", "NCHS top causes dashboard")}
    </div>

    <h2>3. Social Determinants</h2>
    <p>Education and SES vulnerability views show how mortality burden changes across economic and educational categories.</p>

    <div class="grid">
        {image_block("SES Heatmap - Georgia - Fulton.png", "Georgia - Fulton SES heatmap")}
        {image_block("SES Heatmap - Georgia - DeKalb.png", "Georgia - DeKalb SES heatmap")}
        {image_block("Education Heatmap - Georgia - Fulton.png", "Georgia - Fulton education heatmap")}
        {image_block("Education Heatmap - Georgia - DeKalb.png", "Georgia - DeKalb education heatmap")}
    </div>

    <h2>4. Interactive Graphs</h2>
    <p>The HTML report links to every interactive graph, including sunbursts and interactive heatmaps.</p>

    <ul>
        {interactive_links()}
    </ul>

    <h2>5. Aetna Enrollment and Age 65+ Opportunity</h2>
    <p>Known Aetna Medicare Advantage enrollment is compared against the age 65+ population as a proxy for Medicare-age opportunity.</p>

    <div class="grid">
        {image_block("Aetna Enrollment by County.png", "Known Aetna enrollment by county")}
        {image_block("Market Opportunity Dashboard.png", "Age 65+ market opportunity dashboard")}
        {image_block("Aetna Age 65 Penetration Dashboard.png", "Aetna penetration of age 65+ population")}
    </div>

    <h2>6. CVS Forecast</h2>
    <p>The forecast section combines CVS Health Care Benefits historical revenue, scenario-based revenue forecasts, and potential incremental Aetna opportunity using capture-rate assumptions.</p>

    <div class="grid">
        {image_block("CVS Health Care Benefits Revenue.png", "CVS Health Care Benefits historical revenue")}
        {image_block("CVS Revenue Forecast Scenarios.png", "CVS revenue forecast scenarios")}
        {image_block("Aetna Market Opportunity Revenue.png", "Potential incremental Aetna revenue")}
    </div>

    <h2>7. Metrics Tables</h2>

    <h3>Top Mortality Patterns</h3>
    {df_to_html(top_causes)}

    <h3>Social Determinants Patterns</h3>
    {df_to_html(top_social)}

    <h3>Aetna Enrollment</h3>
    {df_to_html(aetna_summary)}

    <h3>Age 65+ Market Opportunity</h3>
    {df_to_html(market_summary)}

    <h3>CVS Forecast</h3>
    {df_to_html(forecast_summary["forecast"] if forecast_summary is not None else None)}

    <h3>Potential Aetna Opportunity</h3>
    {df_to_html(forecast_summary["opportunity"] if forecast_summary is not None else None)}
</main>
</body>
</html>
"""

    html_path.write_text(html, encoding="utf-8")

    try:
        from weasyprint import HTML
        HTML(filename=str(html_path)).write_pdf(str(pdf_path))
        print(f"PDF report created: {pdf_path}")
    except Exception:
        print("PDF report not created. Install WeasyPrint or open the HTML report and print/save as PDF.")

    print(f"Markdown report created: {md_path}")
    print(f"HTML report created: {html_path}")

    return {
        "markdown": md_path,
        "html": html_path,
        "pdf": pdf_path if pdf_path.exists() else None
    }
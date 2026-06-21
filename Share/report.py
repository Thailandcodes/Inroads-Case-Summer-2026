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
        "This report tells the full project story from health burden to business opportunity. "
        "It begins by identifying the leading causes of death in Fulton and DeKalb Counties, "
        "then connects those outcomes to education and socioeconomic vulnerability. The analysis "
        "then shifts to CVS/Aetna's opportunity by comparing known Aetna Medicare Advantage "
        "enrollment against the age 65+ population and estimating potential incremental revenue "
        "under scenario-based capture assumptions.\n\n"
    )

    markdown += "## Method Notes\n\n"
    markdown += "- NCHS is kept separate from Georgia and OASIS because its categories are not directly comparable.\n"
    markdown += "- Age 65+ population is used as a proxy for Medicare-age market opportunity.\n"
    markdown += "- Forecast outputs use analyst assumptions, not CVS-reported projections.\n"
    markdown += "- Interactive charts are generated separately in the `outputs/html` folder.\n\n"

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
    margin: 0;
    background: white;
    color: #3B0D0C;
}}

header {{
    background: #F9E7E2;
    border-bottom: 8px solid #C7462D;
    padding: 40px 55px;
}}

h1 {{
    margin: 0;
    font-size: 34px;
}}

h2 {{
    color: #C7462D;
    border-bottom: 2px solid #F3B2A6;
    padding-bottom: 8px;
    margin-top: 42px;
}}

h3 {{
    color: #8C3B2E;
}}

main {{
    max-width: 1200px;
    margin: auto;
    padding: 35px 55px;
}}

.callout {{
    background: #F9E7E2;
    border-left: 7px solid #C7462D;
    padding: 20px;
    border-radius: 10px;
}}

.grid {{
    display: grid;
    grid-template-columns: repeat(2,minmax(0,1fr));
    gap: 24px;
}}

figure {{
    border: 1px solid #F3B2A6;
    border-radius: 12px;
    padding: 12px;
    margin: 0;
}}

img {{
    width: 100%;
}}

figcaption {{
    margin-top: 10px;
    color: #8C3B2E;
    font-size: 13px;
}}

.data-table {{
    border-collapse: collapse;
    width: 100%;
    font-size: 13px;
}}

.data-table th {{
    background: #C7462D;
    color: white;
    padding: 8px;
    text-align: left;
}}

.data-table td {{
    padding: 8px;
    border-bottom: 1px solid #F3B2A6;
}}

.note {{
    color: #8C3B2E;
    font-size: 14px;
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
<p>Connecting community health burden, Medicare opportunity, and future CVS Health growth.</p>
</header>

<main>

<div class="callout">
<strong>Executive Summary</strong>
<p>
This analysis moves from public health need to business opportunity. It first identifies the leading causes of death in
Fulton and DeKalb Counties, then examines how those outcomes intersect with education, socioeconomic vulnerability, and
race. The report then sizes the Medicare-age opportunity using age 65+ population, compares that opportunity to current
Aetna Medicare Advantage enrollment, and closes with a CVS forecast that estimates potential value from targeted outreach.
</p>
</div>

<h2>1. Community Health Burden</h2>
<p>
The mortality analysis shows which conditions create the greatest burden across Fulton and DeKalb. Chronic diseases such
as heart disease, stroke, cancer, and diabetes remain central to the story. NCHS is kept separate because its categories
are not directly comparable to Georgia and OASIS.
</p>

<div class="grid">
{image_block("Health Burden Heatmap - Georgia - Fulton.png", "Georgia - Fulton Health Burden")}
{image_block("Health Burden Heatmap - Georgia - DeKalb.png", "Georgia - DeKalb Health Burden")}
{image_block("Health Burden Heatmap - OASIS - Fulton.png", "OASIS - Fulton Health Burden")}
{image_block("Health Burden Heatmap - OASIS - DeKalb.png", "OASIS - DeKalb Health Burden")}
</div>

<h2>2. Population Demographics</h2>
<p>
The demographic dashboards summarize race, sex, and leading cause distributions without overwhelming the reader with dozens
of individual pie charts. Labels were moved to legends to improve readability and reduce overlap.
</p>

<div class="grid">
{image_block("Demographics Pie Dashboard - Sex.png", "Sex Distribution Dashboard")}
{image_block("Demographics Pie Dashboard - Race.png", "Race Distribution Dashboard")}
{image_block("Top Causes Pie Dashboard.png", "Leading Causes Dashboard")}
{image_block("NCHS Pie Dashboard - Top Causes.png", "NCHS Leading Causes Dashboard")}
</div>

<h2>3. Social Determinants of Health</h2>
<p>
Education level and socioeconomic vulnerability help explain where the mortality burden is concentrated. These charts support
the case for a targeted intervention rather than a broad, unfocused outreach campaign.
</p>

<div class="grid">
{image_block("SES Heatmap - Georgia - Fulton.png", "SES Vulnerability - Fulton")}
{image_block("SES Heatmap - Georgia - DeKalb.png", "SES Vulnerability - DeKalb")}
{image_block("Education Heatmap - Georgia - Fulton.png", "Education - Fulton")}
{image_block("Education Heatmap - Georgia - DeKalb.png", "Education - DeKalb")}
</div>

<h2>4. Interactive Visualizations</h2>
<p class="note">
Interactive Plotly charts are generated in the <strong>outputs/html</strong> folder. The report does not include links here
because relative links can break when the report is moved, zipped, downloaded, or opened outside the project folder.
</p>

<h2>5. Aetna Enrollment and Market Opportunity</h2>
<p>
The Aetna analysis compares known Medicare Advantage enrollment against the age 65+ population. This frames the difference
between Aetna's current footprint and the broader Medicare-age population CVS could reach through prevention, care navigation,
screening, and chronic disease support.
</p>

<div class="grid">
{image_block("Aetna Enrollment by County.png", "Known Aetna Medicare Advantage Enrollment")}
{image_block("Market Opportunity Dashboard.png", "Age 65+ Market Opportunity Dashboard")}
{image_block("Aetna Age 65 Penetration Dashboard.png", "Aetna Penetration of the Age 65+ Population")}
</div>

<h2>6. CVS Health Care Benefits Forecast</h2>
<p>
The forecast section links the local opportunity back to CVS Health Care Benefits growth. Historical revenue provides the
baseline, scenario forecasts show possible future trajectories, and the incremental Aetna opportunity chart translates
potential capture rates into revenue impact.
</p>

<div class="grid">
{image_block("CVS Health Care Benefits Revenue.png", "CVS Health Care Benefits Historical Revenue")}
{image_block("CVS Revenue Forecast Scenarios.png", "CVS Health Care Benefits Forecast Scenarios")}
{image_block("Aetna Market Opportunity Revenue.png", "Potential Incremental Aetna Revenue")}
</div>

<h2>7. Strategic Interpretation</h2>
<div class="callout">
<p>
The strongest finding is the overlap between community need and market opportunity. Communities experiencing high chronic
disease burden are also the communities where CVS and Aetna could justify targeted outreach through screenings, food and
nutrition support, medication adherence, transportation assistance, and care navigation. This creates a path to both health
impact and measurable business value.
</p>
</div>

<h2>8. Metrics Tables</h2>

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
    except Exception as error:
        print("PDF report not created. Install WeasyPrint or open the HTML report and print/save as PDF.")
        print(f"PDF error: {error}")

    print(f"Markdown report created: {md_path}")
    print(f"HTML report created: {html_path}")

    return {
        "markdown": md_path,
        "html": html_path,
        "pdf": pdf_path if pdf_path.exists() else None
    }

from pathlib import Path
from html import escape
import base64
import pandas as pd


REPORT_DIR = Path("outputs/report")
PNG_DIR = Path("outputs/png")
HTML_DIR = Path("outputs/html")

REPORT_DIR.mkdir(parents=True, exist_ok=True)


CAUSE_NAMES = {
    "Diseases of Heart": "Heart Disease",
    "Diseases of the Heart": "Heart Disease",
    "Ischemic Heart and Vascular Disease": "Heart Disease",
    "Cerebrovascular Disease": "Stroke",
    "Malignant Neoplasms": "Cancer",
    "Alzheimer's Disease": "Alzheimer's",
    "Diabetes Mellitus": "Diabetes",
    "Influenza and Pneumonia": "Flu & Pneumonia",
    "All Other Endocrine, Nutritional and Metabolic Diseases": "Other Endocrine Diseases",
    "All Other Diseases": "Other Diseases",
    "All Other Diseases of the Nervous System": "Other Nervous System Diseases",
    "Unintentional Injuries": "Unintentional Injury",
    "Assault (Homicide)": "Homicide",
}


REFERENCES = [
    "Georgia Department of Public Health rankable causes of death data, Fulton and DeKalb, 2024.",
    "Georgia OASIS rankable causes of death data, Fulton and DeKalb, 2024.",
    "National Center for Health Statistics rankable causes of death data, Fulton and DeKalb, 2024.",
    "Georgia, OASIS, and NCHS social determinant datasets for education, SES vulnerability, race, and cause of death.",
    "Centers for Medicare & Medicaid Services CPSC Medicare Advantage enrollment data.",
    "U.S. Census ACS S0101 Age and Sex data.",
    "CVS Health Care Benefits segment revenue data, 2023-2025.",
    "Centers for Disease Control and Prevention heart disease risk factor guidance.",
    "Fulton County Access to Healthy Foods Analysis.",
    "DeKalb County Community Needs Assessment, June 2024.",
    "USDA Economic Research Service Food Availability Data System.",
    "U.S. Bureau of Labor Statistics Atlanta-area Consumer Price Index context.",
]


def clean_label(value):
    value = str(value)
    value = value.replace("_", " ")
    value = value.replace("Selected ", "")
    value = value.replace("Total", "")
    value = value.replace("  ", " ")
    return value.strip()


def clean_cause(value):
    value = clean_label(value)
    return CAUSE_NAMES.get(value, value)


def format_number(value):
    try:
        return f"{float(value):,.0f}"
    except Exception:
        return str(value)


def format_percent(value):
    try:
        return f"{float(value):.1f}%"
    except Exception:
        return str(value)


def format_money_millions(value):
    try:
        return f"${float(value):,.1f}M"
    except Exception:
        return str(value)


def safe_copy(df):
    if df is None or df.empty:
        return pd.DataFrame()
    return df.copy()


def nice_table(df):
    current = safe_copy(df)

    if current.empty:
        return "No data available.\n"

    try:
        return current.to_markdown(index=False)
    except Exception:
        return current.to_string(index=False)


def df_to_html(df):
    current = safe_copy(df)

    if current.empty:
        return "<p>No data available.</p>"

    return current.to_html(
        index=False,
        classes="data-table",
        border=0,
        escape=True
    )


def image_to_base64(path):
    if not path.exists():
        return ""

    encoded = base64.b64encode(path.read_bytes()).decode("utf-8")
    return f"data:image/png;base64,{encoded}"


def caption_from_filename(path):
    caption = path.stem
    caption = caption.replace(" - ", ": ")
    caption = caption.replace("_", " ")
    return caption


def find_images(patterns, max_images=None):
    matches = []

    for pattern in patterns:
        exact_path = PNG_DIR / pattern

        if exact_path.exists():
            matches.append(exact_path)
        else:
            matches.extend(list(PNG_DIR.glob(pattern)))

    unique = []
    seen = set()

    for path in matches:
        key = str(path)

        if path.exists() and key not in seen:
            unique.append(path)
            seen.add(key)

    unique = sorted(unique, key=lambda p: p.name)

    if max_images is not None:
        unique = unique[:max_images]

    return unique


def image_gallery(patterns, max_images=None):
    paths = find_images(patterns, max_images=max_images)

    if not paths:
        return (
            "<p class='note'>No chart image was found for this section. "
            "Run <code>python main.py</code> to regenerate project outputs.</p>"
        )

    html_parts = ["<div class='grid'>"]

    for path in paths:
        caption = caption_from_filename(path)
        image_src = image_to_base64(path)

        html_parts.append(
            f"""
            <figure>
                <img src="{image_src}" alt="{escape(caption)}">
                <figcaption>{escape(caption)}</figcaption>
            </figure>
            """
        )

    html_parts.append("</div>")
    return "\n".join(html_parts)


def markdown_image_gallery(patterns, max_images=None):
    paths = find_images(patterns, max_images=max_images)

    if not paths:
        return "_No chart image was found for this section. Run `python main.py` to regenerate project outputs._\n"

    lines = []

    for path in paths:
        caption = caption_from_filename(path)
        relative_path = f"../png/{path.name}"
        lines.append(f"![{caption}]({relative_path})")

    return "\n\n".join(lines) + "\n"


def top_rows(df, cols, n=10):
    current = safe_copy(df)

    if current.empty or "Deaths" not in current.columns:
        return pd.DataFrame()

    current["Deaths"] = pd.to_numeric(current["Deaths"], errors="coerce")
    current = current.dropna(subset=["Deaths"])

    if current.empty:
        return pd.DataFrame()

    summary = (
        current.groupby(cols, as_index=False)["Deaths"]
        .sum()
        .sort_values("Deaths", ascending=False)
        .head(n)
    )

    if "Cause" in summary.columns:
        summary["Cause"] = summary["Cause"].apply(clean_cause)

    if "Education" in summary.columns:
        summary["Education"] = summary["Education"].apply(clean_label)

    if "SES Vulnerability" in summary.columns:
        summary["SES Vulnerability"] = summary["SES Vulnerability"].apply(clean_label)

    if "Race" in summary.columns:
        summary["Race"] = summary["Race"].apply(clean_label)

    summary["Deaths"] = summary["Deaths"].round(0).astype(int)

    return summary


def get_combined_value(df, column):
    current = safe_copy(df)

    if current.empty or column not in current.columns:
        return None

    if "County" in current.columns:
        combined = current[current["County"].astype(str).str.upper() == "COMBINED"]

        if not combined.empty:
            return combined.iloc[0][column]

    try:
        return pd.to_numeric(current[column], errors="coerce").sum()
    except Exception:
        return None


def build_metric_cards(aetna_summary, market_summary):
    known_enrollment = get_combined_value(aetna_summary, "Known Enrollment")
    age_65_population = get_combined_value(market_summary, "Age 65+ Population")
    remaining_opportunity = get_combined_value(market_summary, "Remaining Opportunity")

    cards = []

    if known_enrollment is not None:
        cards.append(("Known Aetna Enrollment", format_number(known_enrollment)))

    if age_65_population is not None:
        cards.append(("Age 65+ Population", format_number(age_65_population)))

    if remaining_opportunity is not None:
        cards.append(("Remaining Opportunity", format_number(remaining_opportunity)))

    if not cards:
        return ""

    card_html = ""

    for title, value in cards:
        card_html += (
            "<div class='metric-card'>"
            f"<span>{escape(title)}</span>"
            f"<strong>{escape(value)}</strong>"
            "</div>"
        )

    return f"<div class='metric-grid'>{card_html}</div>"


def short_bullet_list(items):
    return "\n".join([f"- {item}" for item in items])


def reference_list_html():
    items = ""

    for ref in REFERENCES:
        items += f"<li>{escape(ref)}</li>"

    return f"<ul class='reference-list'>{items}</ul>"


def interactive_section_html():
    if not HTML_DIR.exists():
        return (
            "<p>No interactive files were found. Run <code>python main.py</code> "
            "to regenerate HTML outputs.</p>"
        )

    html_files = sorted(HTML_DIR.glob("*.html"), key=lambda p: p.name)

    if not html_files:
        return (
            "<p>No interactive files were found. Run <code>python main.py</code> "
            "to regenerate HTML outputs.</p>"
        )

    items = ""

    for path in html_files:
        label = caption_from_filename(path)
        relative_path = f"../html/{path.name}"
        items += f"<li><a href='{escape(relative_path)}'>{escape(label)}</a></li>"

    return f"""
    <p>
    Interactive Plotly versions of selected diagrams are generated in the
    <strong>outputs/html</strong> folder. These files can be opened directly
    for deeper review or displayed inside the HTML report when the project
    folder structure is preserved.
    </p>
    <ul class='reference-list'>
        {items}
    </ul>
    """


def build_markdown_report(
    top_causes,
    top_social,
    aetna_summary,
    market_summary,
    forecast_summary
):
    markdown = "# Atlanta Health EDA Report\n\n"

    markdown += "## Executive Summary\n\n"
    markdown += (
        "This report explains the full project story from community health burden "
        "to strategic CVS/Aetna opportunity. The central finding is that Fulton "
        "County and DeKalb County show a repeated burden from chronic disease, "
        "especially heart disease, stroke, cancer, and diabetes. Those outcomes "
        "intersect with education, socioeconomic vulnerability, race, and access "
        "barriers that shape whether residents can prevent disease, manage existing "
        "conditions, and receive care early.\n\n"
    )
    markdown += (
        "The business implication is that CVS and Aetna can use targeted preventive "
        "care outreach to reach communities with both high health need and measurable "
        "Medicare-age market opportunity. A targeted model focused on screenings, "
        "nutrition support, care navigation, medication adherence, and partnership-based "
        "outreach creates a path to health impact while supporting future member growth "
        "and retention.\n\n"
    )

    markdown += "## How to Read This Report\n\n"
    markdown += (
        "Each section introduces the diagram type, defines important terms, explains "
        "the finding, and connects that finding to the next part of the analysis. "
        "Rankable causes of death are causes that can be compared across categories "
        "to identify which conditions create the largest mortality burden. Death "
        "counts show volume. Percent of deaths shows each cause's share within a "
        "selected source and county. Heatmaps use darker shading to show larger "
        "values. NCHS is kept separate from Georgia and OASIS because its source "
        "structure and cause groupings are not directly comparable.\n\n"
    )

    markdown += "## 1. Community Health Burden\n\n"
    markdown += (
        "The first set of diagrams identifies the leading causes of death in Fulton "
        "and DeKalb Counties. A heatmap is read by comparing the cause labels with "
        "the values inside each cell. Darker cells indicate a larger burden. The "
        "repeated finding is that chronic disease is central to the health access "
        "problem. This matters because chronic conditions are often affected by "
        "prevention, food access, medication adherence, screening, transportation, "
        "and consistent care.\n\n"
    )
    markdown += markdown_image_gallery(["Health Burden Heatmap - *.png"])
    markdown += "\n### Top Mortality Patterns\n\n"
    markdown += nice_table(top_causes) + "\n\n"

    markdown += "## 2. Population Demographics\n\n"
    markdown += (
        "The demographic dashboards summarize mortality by sex, race, and cause. "
        "A pie chart shows how a whole is divided among categories. These charts "
        "are not meant to claim that identity alone causes worse outcomes. They "
        "show where the burden is concentrated so outreach can be culturally "
        "specific, geographically specific, and connected to trusted community "
        "channels.\n\n"
    )
    markdown += markdown_image_gallery([
        "Demographics Pie Dashboard - Sex.png",
        "Demographics Pie Dashboard - Race.png",
        "Top Causes Pie Dashboard.png",
        "NCHS Pie Dashboard - Sex.png",
        "NCHS Pie Dashboard - Race.png",
        "NCHS Pie Dashboard - Top Causes.png",
    ])

    markdown += "## 3. Social Determinants of Health\n\n"
    markdown += (
        "Social determinants of health are the non-medical conditions that shape a "
        "person's ability to stay healthy. Education level is used as a proxy for "
        "long-term access to opportunity, health literacy, employment stability, "
        "and navigation of complex health systems. SES vulnerability refers to "
        "socioeconomic risk that can make care, transportation, healthy food, and "
        "medication harder to obtain. The key finding is that high chronic disease "
        "burden overlaps with social vulnerability, which supports a targeted "
        "intervention rather than broad outreach.\n\n"
    )
    markdown += markdown_image_gallery([
        "Education Heatmap - *.png",
        "SES Heatmap - *.png",
        "*Mortality Ranking - Race and Education.png",
        "*Mortality Ranking - Race and SES.png",
    ])
    markdown += "\n### Social Determinants Patterns\n\n"
    markdown += nice_table(top_social) + "\n\n"

    markdown += "## 4. Aetna Enrollment and Age 65+ Market Opportunity\n\n"
    markdown += (
        "The Aetna enrollment analysis compares known Aetna Medicare Advantage "
        "enrollment with the broader age 65+ population. The term age 65+ market "
        "opportunity means the estimated number of older residents who may be "
        "eligible for Medicare-related outreach. Penetration rate compares known "
        "Aetna enrollment to the age 65+ population. Remaining opportunity is the "
        "difference between the age 65+ population and known enrollment.\n\n"
    )
    markdown += markdown_image_gallery([
        "Aetna Enrollment by County.png",
        "Market Opportunity Dashboard.png",
        "Aetna Age 65 Penetration Dashboard.png",
    ])
    markdown += "\n### Aetna Enrollment\n\n"
    markdown += nice_table(aetna_summary) + "\n\n"
    markdown += "### Age 65+ Market Opportunity\n\n"
    markdown += nice_table(market_summary) + "\n\n"

    markdown += "## 5. CVS Health Care Benefits Forecast\n\n"
    markdown += (
        "The forecast section connects local outreach to CVS Health's larger Health "
        "Care Benefits segment. The revenue driver is member growth and retention "
        "in health benefits, especially through Medicare Advantage opportunity. "
        "This is a volume-based driver because more covered members can increase "
        "plan-related revenue, and it is also an engagement driver because better "
        "preventive care can strengthen retention and reduce avoidable high-cost "
        "events. The forecast uses analyst assumptions, not CVS-reported projections.\n\n"
    )
    markdown += markdown_image_gallery([
        "CVS Health Care Benefits Revenue.png",
        "CVS Revenue Forecast Scenarios.png",
        "Aetna Market Opportunity Revenue.png",
    ])

    if forecast_summary is not None:
        markdown += "\n### CVS Forecast\n\n"
        markdown += nice_table(forecast_summary.get("forecast")) + "\n\n"

        markdown += "### Potential Aetna Market Opportunity\n\n"
        markdown += nice_table(forecast_summary.get("opportunity")) + "\n\n"

    markdown += "## 6. Strategic Interpretation\n\n"
    markdown += (
        "The evidence points to a focused strategy: target communities where chronic "
        "disease burden, social vulnerability, and Medicare-age opportunity overlap. "
        "A broad campaign would spread resources too thin. A targeted model allows "
        "CVS/Aetna to concentrate outreach where the need is strongest and where "
        "the business case is measurable. The proposed solution should be framed "
        "as preventive access, not just marketing.\n\n"
    )

    markdown += "## 7. Risks and Limitations\n\n"
    markdown += (
        "This analysis identifies patterns and priority populations, but it does not "
        "prove direct causation. Mortality data shows where death burden is concentrated; "
        "it does not by itself prove why each individual death occurred. The market "
        "opportunity analysis uses age 65+ population as a proxy for Medicare-age "
        "opportunity. The revenue forecast is scenario-based and depends on capture "
        "assumptions, competitive response, CMS rules, member retention, and execution quality.\n\n"
    )

    markdown += "## 8. References\n\n"
    markdown += short_bullet_list(REFERENCES) + "\n\n"

    markdown += "## 9. Acknowledgements\n\n"
    markdown += (
        "This report was developed for the INROADS Summer 2026 Case Competition. "
        "We acknowledge the public agencies and organizations whose datasets and "
        "reports made this analysis possible, including Georgia DPH, Georgia OASIS, "
        "NCHS, CMS, the U.S. Census Bureau, CDC, Fulton County, DeKalb Public Health, "
        "USDA ERS, BLS, and CVS public reporting. We also acknowledge the case "
        "competition mentors, reviewers, and team members who shaped the project "
        "direction and helped connect the analysis to a practical healthcare access solution.\n\n"
    )

    markdown += "## 10. Interactive Diagram Appendix\n\n"
    markdown += (
        "Interactive Plotly versions of selected diagrams are generated in the "
        "`outputs/html` folder. These files can be opened directly for deeper review "
        "or displayed inside the HTML report when the project folder structure is preserved.\n"
    )

    return markdown


def build_html_report(
    top_causes,
    top_social,
    aetna_summary,
    market_summary,
    forecast_summary
):
    metric_cards = build_metric_cards(aetna_summary, market_summary)

    forecast_table = None
    opportunity_table = None

    if forecast_summary is not None:
        forecast_table = forecast_summary.get("forecast")
        opportunity_table = forecast_summary.get("opportunity")

    css = """
    <style>
    body {
        font-family: Arial, sans-serif;
        margin: 0;
        background: #fffdfc;
        color: #3B0D0C;
        line-height: 1.6;
    }

    header {
        background: linear-gradient(135deg, #F9E7E2 0%, #ffffff 100%);
        border-bottom: 8px solid #C7462D;
        padding: 46px 60px;
    }

    header p {
        max-width: 900px;
        font-size: 18px;
        margin-bottom: 0;
    }

    h1 {
        margin: 0;
        font-size: 38px;
    }

    h2 {
        color: #C7462D;
        border-bottom: 2px solid #F3B2A6;
        padding-bottom: 8px;
        margin-top: 48px;
    }

    h3 {
        color: #8C3B2E;
        margin-top: 30px;
    }

    main {
        max-width: 1220px;
        margin: auto;
        padding: 35px 55px 70px;
    }

    p {
        font-size: 16px;
    }

    .callout {
        background: #F9E7E2;
        border-left: 7px solid #C7462D;
        padding: 22px 24px;
        border-radius: 12px;
        margin: 22px 0;
    }

    .bridge {
        background: #fff8f5;
        border: 1px solid #F3B2A6;
        padding: 16px 18px;
        border-radius: 10px;
        color: #8C3B2E;
        font-weight: bold;
    }

    .grid {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 24px;
        margin: 22px 0 34px;
    }

    figure {
        background: white;
        border: 1px solid #F3B2A6;
        border-radius: 12px;
        padding: 12px;
        margin: 0;
        box-shadow: 0 6px 16px rgba(59, 13, 12, 0.06);
    }

    img {
        width: 100%;
        display: block;
    }

    figcaption {
        margin-top: 10px;
        color: #8C3B2E;
        font-size: 13px;
    }

    .metric-grid {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 16px;
        margin: 24px 0;
    }

    .metric-card {
        background: white;
        border: 1px solid #F3B2A6;
        border-top: 6px solid #C7462D;
        border-radius: 12px;
        padding: 18px;
    }

    .metric-card span {
        display: block;
        color: #8C3B2E;
        font-size: 13px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .metric-card strong {
        display: block;
        font-size: 26px;
        margin-top: 6px;
    }

    .data-table {
        border-collapse: collapse;
        width: 100%;
        font-size: 13px;
        margin: 16px 0 30px;
        background: white;
    }

    .data-table th {
        background: #C7462D;
        color: white;
        padding: 9px;
        text-align: left;
    }

    .data-table td {
        padding: 8px;
        border-bottom: 1px solid #F3B2A6;
    }

    .note {
        color: #8C3B2E;
        font-size: 14px;
    }

    .reference-list li {
        margin-bottom: 8px;
    }

    code {
        background: #F9E7E2;
        padding: 2px 5px;
        border-radius: 4px;
    }

    @media print {
        body {
            background: white;
        }

        main {
            padding: 20px;
        }

        .grid, .metric-grid {
            grid-template-columns: 1fr;
        }
    }
    </style>
    """

    html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Atlanta Health EDA Report</title>
{css}
</head>

<body>
<header>
<h1>Atlanta Health EDA Report</h1>
<p>
Connecting Fulton and DeKalb community health burden, social determinants,
Medicare-age opportunity, and CVS/Aetna growth strategy.
</p>
</header>

<main>

<div class="callout">
<h2 style="margin-top:0; border-bottom:0; padding-bottom:0;">Executive Summary</h2>
<p>
This report explains the full project story from community health burden to strategic CVS/Aetna opportunity. The central
finding is that Fulton County and DeKalb County show a repeated burden from chronic disease, especially heart disease,
stroke, cancer, and diabetes. Those outcomes do not exist in isolation. They intersect with education, socioeconomic
vulnerability, race, and access barriers that shape whether residents can prevent disease, manage existing conditions,
and receive care early.
</p>
<p>
The business implication is that CVS and Aetna can use targeted preventive care outreach to reach communities with both
high health need and measurable Medicare-age market opportunity. A targeted model focused on screenings, nutrition
support, care navigation, medication adherence, and partnership-based community outreach creates a path to health impact
while supporting future member growth and retention.
</p>
</div>

{metric_cards}

<h2>How to Read This Report</h2>
<p>
This report is organized like a presentation. Each section introduces the diagram type, defines the terms that appear for
the first time, explains the finding, and connects that finding to the next part of the analysis.
</p>
<p>
<strong>Rankable causes of death</strong> are causes that can be compared across categories to identify which conditions create
the largest mortality burden. <strong>Deaths</strong> are counts, while <strong>percent of deaths</strong> shows each cause's share of all deaths
within the selected source and county. <strong>Heatmaps</strong> use darker shading to show larger values. In this report, darker red
generally means a greater burden. <strong>NCHS</strong> is kept separate from Georgia and OASIS because the source structure and cause
groupings are not directly comparable.
</p>

<h2>1. Community Health Burden</h2>
<p>
The first set of diagrams identifies the leading causes of death in Fulton and DeKalb Counties. These heatmaps answer a
simple question: which conditions account for the largest share of deaths in each county and data source? The rows list
causes of death. The values show the share of deaths or death burden represented by each cause. Darker cells indicate a
larger burden.
</p>
<p>
The key finding is that chronic disease is the dominant health burden. Heart disease, stroke, cancer, diabetes, and related
chronic conditions repeatedly appear near the top. This matters because chronic conditions are often influenced by prevention,
food access, medication adherence, screening, transportation, and consistent primary care.
</p>

{image_gallery(["Health Burden Heatmap - *.png"])}

<p class="bridge">
Connection to the next section: once we know which diseases are causing the most harm, the next question is who is most
affected and whether the burden falls evenly across the population.
</p>

<h3>Top Mortality Patterns</h3>
{df_to_html(top_causes)}

<h2>2. Population Demographics</h2>
<p>
The demographic dashboards summarize mortality by sex, race, and leading cause. A pie chart shows how a whole is divided
among categories. Each slice represents a share of deaths for a demographic group or cause category. The purpose is not to
claim that one identity alone causes worse outcomes. Instead, the diagrams help identify where the burden is concentrated
and where outreach must be culturally and locally specific.
</p>
<p>
The race and sex distributions help frame equity. If one group represents a large share of deaths, the solution should not
be generic. It should be designed around where people live, how they access care, what barriers they face, and what trusted
partners already serve them.
</p>

{image_gallery([
    "Demographics Pie Dashboard - Sex.png",
    "Demographics Pie Dashboard - Race.png",
    "Top Causes Pie Dashboard.png",
    "NCHS Pie Dashboard - Sex.png",
    "NCHS Pie Dashboard - Race.png",
    "NCHS Pie Dashboard - Top Causes.png",
])}

<p class="bridge">
Connection to the next section: demographics alone do not explain why health outcomes differ. To understand the pattern
more deeply, the next section looks at education and socioeconomic vulnerability.
</p>

<h2>3. Social Determinants of Health</h2>
<p>
Social determinants of health are the non-medical conditions that shape a person's ability to stay healthy. In this report,
the two main social determinant lenses are education and socioeconomic vulnerability. <strong>Education level</strong> is used as a
proxy for long-term access to opportunity, health literacy, employment stability, and navigation of complex health systems.
<strong>SES vulnerability</strong> refers to socioeconomic risk, including financial stressors that can make care, transportation,
healthy food, and medication harder to obtain.
</p>
<p>
The education and SES heatmaps show how deaths are distributed across causes within each social category. Rows represent
education or SES groups. Columns represent causes of death. Larger numbers and darker cells show where mortality is
concentrated. The main finding is that high chronic disease burden overlaps with social vulnerability.
</p>

{image_gallery([
    "Education Heatmap - *.png",
    "SES Heatmap - *.png",
    "*Mortality Ranking - Race and Education.png",
    "*Mortality Ranking - Race and SES.png",
])}

<p class="bridge">
Connection to the next section: communities with high need are also places where CVS and Aetna can create value through
prevention and care navigation.
</p>

<h3>Social Determinants Patterns</h3>
{df_to_html(top_social)}

<h2>4. Aetna Enrollment and Age 65+ Market Opportunity</h2>
<p>
The Aetna enrollment analysis compares known Aetna Medicare Advantage enrollment with the broader age 65+ population in
Fulton and DeKalb. The term <strong>age 65+ market opportunity</strong> means the estimated number of older residents who may be
eligible for Medicare-related outreach. This is not the same as guaranteed enrollment; it is a directional measure of
potential reach.
</p>
<p>
The <strong>penetration rate</strong> compares known Aetna enrollment to the age 65+ population. A lower penetration rate means there
may be more room for growth, while a higher rate suggests Aetna already has a stronger footprint. The <strong>remaining
opportunity</strong> is the difference between the age 65+ population and known enrollment.
</p>

{image_gallery([
    "Aetna Enrollment by County.png",
    "Market Opportunity Dashboard.png",
    "Aetna Age 65 Penetration Dashboard.png",
])}

<p class="bridge">
Connection to the next section: the market opportunity becomes more meaningful when translated into revenue scenarios.
</p>

<h3>Aetna Enrollment</h3>
{df_to_html(aetna_summary)}

<h3>Age 65+ Market Opportunity</h3>
{df_to_html(market_summary)}

<h2>5. CVS Health Care Benefits Forecast</h2>
<p>
The forecast section connects the local opportunity back to CVS Health Care Benefits growth. Historical revenue provides
the baseline, scenario forecasts show possible future trajectories, and the incremental Aetna opportunity chart translates
potential capture rates into revenue impact.
</p>
<p>
The revenue driver is <strong>member growth and retention</strong> in health benefits, especially through Medicare Advantage
opportunity. This is a <strong>volume-based driver</strong> because more covered members can increase plan-related revenue. It is also
an <strong>engagement driver</strong> because better preventive care can improve outcomes, reduce avoidable high-cost events, and
strengthen the value of the plan relationship.
</p>

{image_gallery([
    "CVS Health Care Benefits Revenue.png",
    "CVS Revenue Forecast Scenarios.png",
    "Aetna Market Opportunity Revenue.png",
])}

<h3>CVS Forecast</h3>
{df_to_html(forecast_table)}

<h3>Potential Aetna Market Opportunity</h3>
{df_to_html(opportunity_table)}

<h2>6. Strategic Interpretation</h2>
<div class="callout">
<p>
The evidence points to a focused strategy: target communities where chronic disease burden, social vulnerability, and
Medicare-age opportunity overlap. A broad campaign would spread resources too thin. A targeted model allows CVS/Aetna to
concentrate outreach where the need is strongest and where the business case is measurable.
</p>
<p>
The proposed solution should be framed as preventive access, not just marketing. The strongest intervention is a partner-based
outreach model that combines food and nutrition support, basic health screenings, care navigation, and Aetna/CVS follow-up.
This approach fits the data because the leading health burdens are chronic conditions, and chronic conditions are shaped by
daily access to food, medication, transportation, and consistent care.
</p>
</div>

<h2>7. Risks and Limitations</h2>
<p>
This analysis identifies patterns and priority populations, but it does not prove direct causation. Mortality data shows
where death burden is concentrated; it does not by itself prove why each individual death occurred. Education and SES
categories help describe vulnerability, but they cannot capture every factor affecting a resident's health.
</p>
<p>
The market opportunity analysis uses age 65+ population as a proxy for Medicare-age opportunity. Some residents may already
be enrolled in non-Aetna plans, may not be eligible for a specific product, or may not be reachable through the proposed
channels. The revenue forecast is scenario-based and depends on capture assumptions, revenue-per-member assumptions,
competitive response, CMS rules, member retention, and execution quality.
</p>

<h2>8. References</h2>
{reference_list_html()}

<h2>9. Acknowledgements</h2>
<p>
This report was developed for the INROADS Summer 2026 Case Competition. We acknowledge the public agencies and organizations
whose datasets and reports made this analysis possible, including Georgia DPH, Georgia OASIS, NCHS, CMS, the U.S. Census
Bureau, CDC, Fulton County, DeKalb Public Health, USDA ERS, BLS, and CVS public reporting. We also acknowledge the case
competition mentors, reviewers, and team members who shaped the project direction and helped connect the analysis to a
practical healthcare access solution.
</p>

<h2>10. Interactive Diagram Appendix</h2>
{interactive_section_html()}

</main>
</body>
</html>
"""

    return html


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

    markdown = build_markdown_report(
        top_causes=top_causes,
        top_social=top_social,
        aetna_summary=aetna_summary,
        market_summary=market_summary,
        forecast_summary=forecast_summary
    )

    html = build_html_report(
        top_causes=top_causes,
        top_social=top_social,
        aetna_summary=aetna_summary,
        market_summary=market_summary,
        forecast_summary=forecast_summary
    )

    md_path.write_text(markdown, encoding="utf-8")
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
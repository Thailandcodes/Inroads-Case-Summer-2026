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


def safe_copy(df):
    if df is None or df.empty:
        return pd.DataFrame()
    return df.copy()


def is_total_category(value):
    if pd.isna(value):
        return False

    text = str(value).strip().lower()
    text = text.replace("_", " ")
    text = " ".join(text.split())

    total_markers = [
        "selected educations total",
        "selected education total",
        "selected ses vulnerability total",
        "selected races total",
        "selected race total",
        "education total",
        "educations total",
        "ses vulnerability total",
        "race total",
        "races total",
        "total",
    ]

    return text in total_markers or text.endswith(" total")


def remove_total_category_rows(df):
    current = safe_copy(df)

    if current.empty:
        return current

    columns_to_check = [
        "Education",
        "SES Vulnerability",
        "Race",
    ]

    for col in columns_to_check:
        if col in current.columns:
            current = current[~current[col].apply(is_total_category)]

    return current


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
        return ""

    return current.to_html(
        index=False,
        classes="data-table",
        border=0,
        escape=True,
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


def find_files(folder, patterns, max_items=None):
    matches = []

    for pattern in patterns:
        exact_path = folder / pattern

        if exact_path.exists():
            matches.append(exact_path)
        else:
            matches.extend(list(folder.glob(pattern)))

    unique = []
    seen = set()

    for path in matches:
        key = str(path)

        if path.exists() and key not in seen:
            unique.append(path)
            seen.add(key)

    unique = sorted(unique, key=lambda p: p.name)

    if max_items is not None:
        unique = unique[:max_items]

    return unique


def image_gallery(patterns, max_images=None):
    paths = find_files(PNG_DIR, patterns, max_items=max_images)

    if not paths:
        return ""

    html_parts = ["<div class='grid'>"]

    for path in paths:
        caption = caption_from_filename(path)
        image_src = image_to_base64(path)

        html_parts.append(
            f"""
            <figure class="figure-card">
                <img src="{image_src}" alt="{escape(caption)}">
                <figcaption>{escape(caption)}</figcaption>
            </figure>
            """
        )

    html_parts.append("</div>")
    return "\n".join(html_parts)


def html_file_as_srcdoc(path):
    try:
        raw_html = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        raw_html = path.read_text(encoding="latin-1")

    raw_html = raw_html.replace(
        '<head><meta charset="utf-8" /></head>',
        '<head><meta charset="utf-8" /><meta name="viewport" content="width=device-width, initial-scale=1.0" />'
        '<style>html,body{margin:0;padding:0;background:#f5efea;overflow:auto;width:100%;height:100%;}'
        'body{font-family:Arial,sans-serif;}'
        '.js-plotly-plot,.plot-container,.plotly,.plotly-graph-div{width:100% !important;max-width:none !important;}'
        '</style></head>'
    )

    replacements = {
        'height:650px; width:1200px;': 'height:980px; width:100%;',
        'height:650px; width:1000px;': 'height:980px; width:100%;',
        'height:700px; width:1200px;': 'height:1050px; width:100%;',
        'height:700px; width:1000px;': 'height:1050px; width:100%;',
        'height:800px; width:1200px;': 'height:1100px; width:100%;',
        'height:800px; width:1000px;': 'height:1100px; width:100%;',
    }

    for old, new in replacements.items():
        raw_html = raw_html.replace(old, new)

    resize_script = """
    <script>
    window.addEventListener('load', function () {
        function resizePlots() {
            var plots = document.querySelectorAll('.js-plotly-plot');
            plots.forEach(function(plot){
                try {
                    plot.style.width = '100%';
                    plot.style.maxWidth = 'none';
                    if (window.Plotly) {
                        Plotly.Plots.resize(plot);
                    }
                } catch (e) {}
            });
        }
        resizePlots();
        setTimeout(resizePlots, 250);
        setTimeout(resizePlots, 800);
        setTimeout(resizePlots, 1600);
        window.addEventListener('resize', resizePlots);
    });
    </script>
    """

    if '</body>' in raw_html:
        raw_html = raw_html.replace('</body>', resize_script + '</body>')
    else:
        raw_html += resize_script

    return escape(raw_html, quote=True)

def interactive_gallery(html_patterns, png_patterns=None, max_items=None):
    html_paths = find_files(HTML_DIR, html_patterns, max_items=max_items)

    if html_paths:
        html_parts = ["<div class='interactive-grid'>"]

        for path in html_paths:
            caption = caption_from_filename(path)
            srcdoc_html = html_file_as_srcdoc(path)
            lower_name = path.name.lower()
            extra_classes = ["interactive-card"]
            label = "Interactive figure embedded in report"

            if "sunburst" in lower_name:
                extra_classes.extend(["hero-card", "sunburst-card"])
                label = "Interactive sunburst embedded in report"
            elif "heatmap" in lower_name:
                extra_classes.extend(["hero-card", "heatmap-card"])
                label = "Interactive heatmap embedded in report"

            class_attr = " ".join(extra_classes)

            html_parts.append(
                f"""
                <section class="{class_attr}">
                    <div class="interactive-label">{escape(label)}</div>
                    <h3>{escape(caption)}</h3>
                    <iframe srcdoc="{srcdoc_html}" loading="lazy"></iframe>
                </section>
                """
            )

        html_parts.append("</div>")
        return "\n".join(html_parts)

    if png_patterns:
        return image_gallery(png_patterns, max_images=max_items)

    return ""

def markdown_image_gallery(patterns, max_images=None):
    paths = find_files(PNG_DIR, patterns, max_items=max_images)

    if not paths:
        return ""

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

    current = remove_total_category_rows(current)

    if current.empty:
        return pd.DataFrame()

    current["Deaths"] = pd.to_numeric(current["Deaths"], errors="coerce")
    current = current.dropna(subset=["Deaths"])

    if current.empty:
        return pd.DataFrame()

    usable_cols = []

    for col in cols:
        if col in current.columns:
            usable_cols.append(col)

    if not usable_cols:
        return pd.DataFrame()

    summary = (
        current.groupby(usable_cols, as_index=False)["Deaths"]
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
        cards.append(("Known Aetna Enrollment", format_number(known_enrollment), "coral"))

    if age_65_population is not None:
        cards.append(("Age 65+ Population", format_number(age_65_population), "gold"))

    if remaining_opportunity is not None:
        cards.append(("Remaining Opportunity", format_number(remaining_opportunity), "rose"))

    if not cards:
        return ""

    card_html = ""

    for title, value, style_name in cards:
        card_html += (
            f"<div class='metric-card {style_name}'>"
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


def build_markdown_report(
    top_causes,
    top_social,
    aetna_summary,
    market_summary,
    forecast_summary,
):
    markdown = "# Project HEART\n\n"
    markdown += "## A Data-Driven Strategy for Expanding Healthcare Access in Fulton and DeKalb Counties\n\n"

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
    markdown += markdown_image_gallery(["Health Burden Heatmap - *OASIS* - *.png"])
    markdown += "\n### Top Mortality Patterns\n\n"
    markdown += nice_table(top_causes) + "\n\n"
    markdown += (
        "**Connection to the next section:** once we know which diseases are causing "
        "the most harm, the next question is who is most affected and whether the "
        "burden falls evenly across the population.\n\n"
    )

    markdown += "## 2. Population Demographics\n\n"
    markdown += (
        "The demographic dashboards summarize mortality by sex, race, and cause. "
        "A pie chart shows how a whole is divided among categories. These charts "
        "are not meant to claim that identity alone causes worse outcomes. They "
        "show where the burden is concentrated so outreach can be culturally "
        "specific, geographically specific, and connected to trusted community "
        "channels.\n\n"
    )
    markdown += "_Embedded HTML report uses OASIS-only visuals for consistency; demographic metrics remain available in the tables._\n"
    markdown += (
        "\n**Connection to the next section:** demographics alone do not explain why "
        "health outcomes differ. To understand the pattern more deeply, the next "
        "section looks at education and socioeconomic vulnerability.\n\n"
    )

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
        "Education Heatmap - *OASIS* - *.png",
        "SES Heatmap - *OASIS* - *.png",
    ])
    markdown += "\n### Social Determinants Patterns\n\n"
    markdown += nice_table(top_social) + "\n\n"
    markdown += (
        "**Connection to the next section:** communities with high need are also "
        "places where CVS and Aetna can create value through prevention and care navigation.\n\n"
    )

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
    markdown += (
        "**Connection to the next section:** the market opportunity becomes more "
        "meaningful when translated into revenue scenarios.\n\n"
    )

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

    markdown += (
        "**Connection to the next section:** the financial case supports the strategic "
        "recommendation, but execution must still be targeted, practical, and grounded "
        "in community access barriers.\n\n"
    )

    markdown += "## 6. Strategic Interpretation\n\n"
    markdown += (
        "The evidence points to a focused strategy: target communities where chronic "
        "disease burden, social vulnerability, and Medicare-age opportunity overlap. "
        "A broad campaign would spread resources too thin. A targeted model allows "
        "CVS/Aetna to concentrate outreach where the need is strongest and where "
        "the business case is measurable. The proposed solution should be framed "
        "as preventive access, not just marketing.\n\n"
    )
    markdown += (
        "**Connection to the next section:** because this strategy is built from real "
        "data but still depends on assumptions, the final step is to state the risks "
        "and limits clearly.\n\n"
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
    markdown += (
        "**Connection to the close:** these limitations do not weaken the recommendation; "
        "they clarify how CVS should measure results, validate assumptions, and refine "
        "the program after launch.\n\n"
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
        "direction and helped connect the analysis to a practical healthcare access solution.\n"
    )

    return markdown


def build_html_report(
    top_causes,
    top_social,
    aetna_summary,
    market_summary,
    forecast_summary,
):
    metric_cards = build_metric_cards(aetna_summary, market_summary)

    forecast_table = None
    opportunity_table = None

    if forecast_summary is not None:
        forecast_table = forecast_summary.get("forecast")
        opportunity_table = forecast_summary.get("opportunity")

    # Keep report visualizations focused on one mortality data source: OASIS.
    # The tables and metrics still use all available sources, but the embedded visuals
    # stay cleaner and more premium for judges.
    health_burden_charts = interactive_gallery(
        html_patterns=["interactive_oasis_top_causes_heatmap.html"],
        png_patterns=["Health Burden Heatmap - *OASIS* - *.png"],
    )

    oasis_sunburst_charts = interactive_gallery(
        html_patterns=[
            "interactive_education_race_cause_sunburst.html",
            "interactive_ses_race_cause_sunburst.html",
        ],
        png_patterns=None,
    )

    demographic_charts = ""

    social_heatmaps = interactive_gallery(
        html_patterns=[
            "interactive_oasis_dekalb_education_by_cause_heatmap.html",
            "interactive_oasis_fulton_education_by_cause_heatmap.html",
            "interactive_oasis_dekalb_ses_by_cause_heatmap.html",
            "interactive_oasis_fulton_ses_by_cause_heatmap.html",
        ],
        png_patterns=[
            "Education Heatmap - *OASIS* - *.png",
            "SES Heatmap - *OASIS* - *.png",
        ],
    )

    social_rankings = ""

    market_charts = image_gallery([
        "Aetna Enrollment by County.png",
        "Market Opportunity Dashboard.png",
        "Aetna Age 65 Penetration Dashboard.png",
    ])

    forecast_charts = image_gallery([
        "CVS Health Care Benefits Revenue.png",
        "CVS Revenue Forecast Scenarios.png",
        "Aetna Market Opportunity Revenue.png",
    ])
    css = """
    <style>
    :root {
        --coral: #C7462D;
        --coral-light: #F3B2A6;
        --rose: #E87561;
        --burgundy: #3B0D0C;
        --muted-red: #8C3B2E;
        --cream: #fffaf7;
        --soft-cream: #F9E7E2;
        --gold: #D6A55C;
        --gold-light: #FFF3D8;
        --blue-gray: #EAF1F4;
        --deep-teal: #315A63;
        --soft-gray: #F5F2F0;
    }

    body {
        font-family: Arial, sans-serif;
        margin: 0;
        background: var(--cream);
        color: var(--burgundy);
        line-height: 1.6;
    }

    header {
        background:
            linear-gradient(135deg, rgba(249,231,226,0.95) 0%, rgba(255,250,247,0.96) 55%, rgba(255,243,216,0.85) 100%);
        border-bottom: 8px solid var(--coral);
        padding: 52px 64px;
    }

    header .eyebrow {
        color: var(--muted-red);
        font-weight: bold;
        letter-spacing: 1.4px;
        text-transform: uppercase;
        font-size: 13px;
        margin-bottom: 12px;
    }

    header h1 {
        margin: 0;
        font-size: 44px;
        letter-spacing: -0.8px;
    }

    header h2 {
        border: 0;
        color: var(--burgundy);
        margin: 6px 0 0;
        padding: 0;
        font-size: 22px;
        font-weight: normal;
    }

    header p {
        max-width: 900px;
        font-size: 18px;
        margin-bottom: 0;
    }

    main {
        max-width: 1240px;
        margin: auto;
        padding: 36px 56px 70px;
    }

    h2 {
        color: var(--coral);
        border-bottom: 2px solid var(--coral-light);
        padding-bottom: 8px;
        margin-top: 52px;
    }

    h3 {
        color: var(--muted-red);
        margin-top: 30px;
    }

    p {
        font-size: 16px;
    }

    .callout {
        background: white;
        border-left: 7px solid var(--coral);
        padding: 24px 26px;
        border-radius: 14px;
        margin: 24px 0;
        box-shadow: 0 8px 22px rgba(59, 13, 12, 0.06);
    }

    .gold-callout {
        background: var(--gold-light);
        border-left: 7px solid var(--gold);
    }

    .risk-callout {
        background: var(--soft-gray);
        border-left: 7px solid var(--muted-red);
    }

    .bridge {
        background: #fff8f5;
        border: 1px solid var(--coral-light);
        border-left: 7px solid var(--gold);
        padding: 16px 18px;
        border-radius: 10px;
        color: var(--muted-red);
        font-weight: bold;
        margin-top: 22px;
    }

    .grid {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 24px;
        margin: 22px 0 34px;
    }

    .interactive-grid {
        display: grid;
        grid-template-columns: 1fr;
        gap: 26px;
        margin: 24px 0 34px;
    }

    .figure-card,
    .interactive-card {
        background: white;
        border: 1px solid var(--coral-light);
        border-radius: 14px;
        padding: 14px;
        margin: 0;
        box-shadow: 0 6px 16px rgba(59, 13, 12, 0.06);
    }

    .interactive-card {
        border-top: 6px solid var(--deep-teal);
    }

    .interactive-label {
        display: inline-block;
        background: var(--blue-gray);
        color: var(--deep-teal);
        font-weight: bold;
        font-size: 12px;
        padding: 4px 8px;
        border-radius: 999px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .interactive-card h3 {
        margin-top: 10px;
    }

    iframe {
        width: 100%;
        height: 880px;
        border: 1px solid var(--coral-light);
        border-radius: 10px;
        background: white;
    }

    img {
        width: 100%;
        display: block;
    }

    figcaption {
        margin-top: 10px;
        color: var(--muted-red);
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
        border: 1px solid var(--coral-light);
        border-radius: 14px;
        padding: 18px;
        box-shadow: 0 6px 16px rgba(59, 13, 12, 0.05);
    }

    .metric-card.coral {
        border-top: 6px solid var(--coral);
    }

    .metric-card.gold {
        border-top: 6px solid var(--gold);
    }

    .metric-card.rose {
        border-top: 6px solid var(--rose);
    }

    .metric-card span {
        display: block;
        color: var(--muted-red);
        font-size: 13px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .metric-card strong {
        display: block;
        font-size: 28px;
        margin-top: 6px;
    }

    .definition-grid {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 14px;
        margin: 22px 0;
    }

    .definition-card {
        background: white;
        border: 1px solid var(--blue-gray);
        border-top: 5px solid var(--deep-teal);
        border-radius: 12px;
        padding: 14px;
    }

    .definition-card strong {
        color: var(--deep-teal);
        display: block;
        margin-bottom: 6px;
    }

    .data-table {
        border-collapse: collapse;
        width: 100%;
        font-size: 13px;
        margin: 16px 0 30px;
        background: white;
        box-shadow: 0 4px 12px rgba(59, 13, 12, 0.04);
    }

    .data-table th {
        background: var(--coral);
        color: white;
        padding: 9px;
        text-align: left;
    }

    .data-table td {
        padding: 8px;
        border-bottom: 1px solid var(--coral-light);
    }

    .note {
        color: var(--muted-red);
        font-size: 14px;
    }

    .reference-list li {
        margin-bottom: 8px;
    }

    code {
        background: var(--soft-cream);
        padding: 2px 5px;
        border-radius: 4px;
    }

    footer {
        margin-top: 56px;
        padding-top: 22px;
        border-top: 2px solid var(--coral-light);
        color: var(--muted-red);
        font-size: 13px;
    }

    @media print {
        body {
            background: white;
        }

        main {
            padding: 20px;
        }

        .grid,
        .metric-grid,
        .definition-grid {
            grid-template-columns: 1fr;
        }

        iframe {
            display: none;
        }
    }

    body {
        background: radial-gradient(circle at top, #4b0f20 0%, #220913 48%, #13060d 100%);
        color: #f6ece5;
    }

    header {
        background: linear-gradient(135deg, rgba(69,11,25,0.98) 0%, rgba(31,10,18,0.96) 65%, rgba(92,33,23,0.93) 100%);
        border-bottom: 3px solid rgba(223, 173, 104, 0.9);
        box-shadow: 0 20px 50px rgba(0,0,0,0.28);
    }

    header .eyebrow,
    header h1,
    header h2,
    header p {
        color: #f7efe8;
    }

    main {
        background: linear-gradient(180deg, rgba(42,17,27,0.94) 0%, rgba(26,11,19,0.97) 100%);
        border: 1px solid rgba(214,165,92,0.30);
        border-radius: 22px;
        box-shadow: 0 25px 70px rgba(0,0,0,0.38);
        margin-top: 28px;
        margin-bottom: 36px;
    }

    h2 {
        color: #f0b38f;
        border-bottom-color: rgba(214,165,92,0.35);
    }

    h3,
    p,
    .metric-card span,
    .definition-card,
    .reference-list li,
    footer,
    .bridge,
    .note {
        color: #f4e8e0;
    }

    .callout,
    .metric-card,
    .definition-card,
    .figure-card,
    .interactive-card {
        background: linear-gradient(180deg, rgba(76,28,40,0.96) 0%, rgba(50,20,29,0.98) 100%);
        border-color: rgba(240,179,143,0.35);
        box-shadow: 0 12px 30px rgba(0,0,0,0.28);
    }

    .gold-callout {
        background: linear-gradient(180deg, rgba(90,53,23,0.96) 0%, rgba(63,34,17,0.98) 100%);
    }

    .risk-callout {
        background: linear-gradient(180deg, rgba(54,31,38,0.96) 0%, rgba(40,22,28,0.98) 100%);
    }

    .definition-card strong,
    .interactive-label {
        color: #ffe6ba;
    }

    .interactive-label {
        background: rgba(214,165,92,0.18);
    }

    .bridge {
        background: rgba(214,165,92,0.12);
        border-color: rgba(214,165,92,0.45);
        border-left-color: #dfad68;
    }

    .data-table,
    .data-table td,
    .data-table th {
        background: rgba(248,240,232,0.98);
        color: #38131a;
    }

    .data-table th {
        background: #9e3f35;
        color: #fff;
    }

    .interactive-grid {
        gap: 34px;
    }

    .interactive-card {
        padding: 18px;
    }

    .interactive-card.hero-card iframe {
        background: #f5efea;
    }

    .interactive-card.heatmap-card iframe {
        height: 1250px;
    }

    .interactive-card.sunburst-card iframe {
        height: 1050px;
    }

    .interactive-card iframe {
        height: 1020px;
    }

    .grid {
        grid-template-columns: 1fr;
    }

    .note {
        display: none;
    }

    footer {
        border-top-color: rgba(214,165,92,0.35);
    }
    </style>
    """

    html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Project HEART Report</title>
{css}
</head>

<body>
<header>
<div class="eyebrow">INROADS Summer 2026 Case Competition</div>
<h1>Project HEART</h1>
<h2>A Data-Driven Strategy for Expanding Healthcare Access in Fulton and DeKalb Counties</h2>
<p>
A digital case report connecting community health burden, social determinants, Medicare-age opportunity,
and CVS/Aetna growth strategy.
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

<div class="definition-grid">
    <div class="definition-card">
        <strong>Rankable Causes</strong>
        Causes of death that can be compared across categories to identify the largest mortality burden.
    </div>
    <div class="definition-card">
        <strong>Heatmap</strong>
        A chart where darker shading signals a larger value or greater burden.
    </div>
    <div class="definition-card">
        <strong>SES Vulnerability</strong>
        Socioeconomic risk that can make care, food, medication, or transportation harder to access.
    </div>
    <div class="definition-card">
        <strong>Penetration Rate</strong>
        Known Aetna enrollment compared with the broader age 65+ population.
    </div>
</div>

<p>
<strong>NCHS</strong> is kept separate from Georgia and OASIS because the source structure and cause groupings are not directly comparable.
</p>

<h2>1. Community Health Burden</h2>
<p>
The first set of diagrams uses OASIS visuals to identify the leading causes of death in Fulton and DeKalb Counties.
The tables still summarize all available sources, but the visual story is kept to OASIS so the report stays focused and
easy to follow. These heatmaps answer a simple question: which conditions account for the largest share of deaths in each
county? The rows list causes of death. The values show the share of deaths or death burden represented by each cause.
Darker cells indicate a larger burden.
</p>
<p>
The key finding is that chronic disease is the dominant health burden. Heart disease, stroke, cancer, diabetes, and related
chronic conditions repeatedly appear near the top. This matters because chronic conditions are often influenced by prevention,
food access, medication adherence, screening, transportation, and consistent primary care.
</p>

{health_burden_charts}

<h3>OASIS Sunburst Views</h3>
<p>
The sunburst views add depth by showing how disease burden cascades through connected categories. Together they help show how leading causes of death relate to education, socioeconomic vulnerability, race, and age patterns in a single visual hierarchy.
</p>

{oasis_sunburst_charts}

<h3>Top Mortality Patterns Across All Sources</h3>
{df_to_html(top_causes)}

<p class="bridge">
Connection to the next section: once we know which diseases are causing the most harm, the next question is who is most
affected and whether the burden falls evenly across the population.
</p>

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

<p class="note">
For visual consistency, this report keeps embedded mortality visuals to OASIS. The demographic interpretation is still
supported by the all-source summary tables produced by the analysis pipeline.
</p>

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
The OASIS education and SES heatmaps show how deaths are distributed across causes within each social category. Rows
represent education or SES groups. Columns represent causes of death. Larger numbers and darker cells show where mortality
is concentrated. The main finding is that high chronic disease burden overlaps with social vulnerability.
</p>

{social_heatmaps}

<h3>Social Determinants Patterns Across All Sources</h3>
{df_to_html(top_social)}

<p class="bridge">
Connection to the next section: communities with high need are also places where CVS and Aetna can create value through
prevention and care navigation.
</p>

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

{market_charts}

<h3>Aetna Enrollment</h3>
{df_to_html(aetna_summary)}

<h3>Age 65+ Market Opportunity</h3>
{df_to_html(market_summary)}

<p class="bridge">
Connection to the next section: the market opportunity becomes more meaningful when translated into revenue scenarios.
</p>

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

{forecast_charts}

<h3>CVS Forecast</h3>
{df_to_html(forecast_table)}

<h3>Potential Aetna Market Opportunity</h3>
{df_to_html(opportunity_table)}

<p class="bridge">
Connection to the next section: the financial case supports the strategic recommendation, but execution must still be
targeted, practical, and grounded in community access barriers.
</p>

<h2>6. Strategic Interpretation</h2>
<div class="callout gold-callout">
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

<p class="bridge">
Connection to the next section: because this strategy is built from real data but still depends on assumptions, the final
step is to state the risks and limits clearly.
</p>

<h2>7. Risks and Limitations</h2>
<div class="callout risk-callout">
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
</div>

<p class="bridge">
Connection to the close: these limitations do not weaken the recommendation; they clarify how CVS should measure results,
validate assumptions, and refine the program after launch.
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

<footer>
Project HEART digital case report. Generated from Python outputs. Interactive charts are embedded directly into this HTML report.
</footer>

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
    forecast_summary=None,
):
    md_path = REPORT_DIR / "metrics_report.md"
    html_path = REPORT_DIR / "metrics_report.html"

    top_causes = top_rows(
        cause_data,
        ["Source", "Geography", "Cause"],
        n=15,
    )

    top_social = top_rows(
        social_data,
        ["Source", "Geography", "Education", "SES Vulnerability", "Race", "Cause"],
        n=15,
    )

    markdown = build_markdown_report(
        top_causes=top_causes,
        top_social=top_social,
        aetna_summary=aetna_summary,
        market_summary=market_summary,
        forecast_summary=forecast_summary,
    )

    html = build_html_report(
        top_causes=top_causes,
        top_social=top_social,
        aetna_summary=aetna_summary,
        market_summary=market_summary,
        forecast_summary=forecast_summary,
    )

    md_path.write_text(markdown, encoding="utf-8")
    html_path.write_text(html, encoding="utf-8")

    print(f"Markdown report created: {md_path}")
    print(f"HTML report created: {html_path}")
    print("PDF report skipped by design. Use the HTML report as the final digital case report.")

    return {
        "markdown": md_path,
        "html": html_path,
        "pdf": None,
    }

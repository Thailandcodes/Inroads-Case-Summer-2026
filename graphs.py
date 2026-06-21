import os
import textwrap
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

from helpers import clean_label, format_number, format_percent
from style import (
    PNG_DIR,
    HTML_DIR,
    SOURCE_COLORS,
    COUNTY_COLORS,
    CHART_COLORS,
    setup_chart_style
)


setup_chart_style()
os.makedirs(PNG_DIR, exist_ok=True)
os.makedirs(HTML_DIR, exist_ok=True)


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
    "Assault (Homicide)": "Homicide"
}

BAD_RACE_PATTERNS = (
    "Selected|Total|All Races|Races|Unknown|Not Stated|Not Reported"
)


def short_label(value, width=28):
    return "\n".join(textwrap.wrap(clean_label(value), width))


def clean_cause(value):
    value = clean_label(value)
    return CAUSE_NAMES.get(value, value)


def clean_race_data(data):
    current = data.copy()

    current = current[
        ~current["Race"].astype(str).str.contains(
            BAD_RACE_PATTERNS,
            case=False,
            na=False
        )
    ]

    return current


def save_png(filename):
    plt.tight_layout()
    plt.savefig(PNG_DIR / filename, dpi=200, bbox_inches="tight")
    plt.close()


def add_bar_labels(ax, percent=False):
    for container in ax.containers:
        labels = []

        for value in container.datavalues:
            labels.append(format_percent(value) if percent else format_number(value))

        ax.bar_label(container, labels=labels, fontsize=9, padding=3)


def keep_top_causes_per_group(data, group_cols, top_n=5):
    ranked = (
        data.groupby(group_cols + ["Cause"], as_index=False)["Deaths"]
        .sum()
        .sort_values("Deaths", ascending=False)
    )

    if group_cols:
        ranked["Rank"] = ranked.groupby(group_cols)["Deaths"].rank(
            method="first",
            ascending=False
        )
        ranked = ranked[ranked["Rank"] <= top_n]
    else:
        ranked = ranked.head(top_n)

    return data.merge(
        ranked[group_cols + ["Cause"]],
        on=group_cols + ["Cause"],
        how="inner"
    )


def graph_heatmaps_by_source_and_county(cause_data):
    for source in sorted(cause_data["Source"].unique()):
        for county in sorted(cause_data["Geography"].unique()):
            current = cause_data[
                (cause_data["Source"] == source) &
                (cause_data["Geography"] == county)
            ].copy()

            if current.empty:
                continue

            current["Cause"] = current["Cause"].apply(clean_cause)

            top_causes = (
                current.groupby("Cause")["Percent"]
                .sum()
                .sort_values(ascending=False)
                .head(12)
                .index
            )

            current = current[current["Cause"].isin(top_causes)]

            pivot = current.pivot_table(
                index="Cause",
                values="Percent",
                aggfunc="sum"
            ).sort_values("Percent", ascending=False)

            pivot.index = [short_label(x, 38) for x in pivot.index]

            plt.figure(figsize=(10, 8))

            sns.heatmap(
                pivot,
                annot=True,
                fmt=".1f",
                cmap="Reds",
                linewidths=0.5,
                cbar_kws={"label": "Percent of Deaths"}
            )

            plt.title(f"Top Causes of Death\n{source} - {county}")
            plt.xlabel("")
            plt.ylabel("Cause of Death")

            save_png(f"Health Burden Heatmap - {source} - {county}.png")

            fig = px.imshow(
                pivot,
                text_auto=".1f",
                color_continuous_scale="Reds",
                title=f"Top Causes of Death: {source} - {county}"
            )

            fig.update_layout(
                font=dict(size=13, color="#3B0D0C"),
                xaxis_title="",
                yaxis_title="Cause of Death",
                paper_bgcolor="white",
                plot_bgcolor="white"
            )

            fig.write_html(
                HTML_DIR / f"Health Burden Heatmap - {source} - {county}.html"
            )


def graph_combined_pie_dashboards(sex_data, race_data, cause_data):
    non_nchs_sex = sex_data[sex_data["Source"] != "NCHS"].copy()
    non_nchs_race = race_data[race_data["Source"] != "NCHS"].copy()
    non_nchs_cause = cause_data[cause_data["Source"] != "NCHS"].copy()

    nchs_sex = sex_data[sex_data["Source"] == "NCHS"].copy()
    nchs_race = race_data[race_data["Source"] == "NCHS"].copy()
    nchs_cause = cause_data[cause_data["Source"] == "NCHS"].copy()

    non_nchs_race = clean_race_data(non_nchs_race)
    nchs_race = clean_race_data(nchs_race)

    non_nchs_cause["Cause"] = non_nchs_cause["Cause"].apply(clean_cause)
    nchs_cause["Cause"] = nchs_cause["Cause"].apply(clean_cause)

    make_pie_dashboard(
        data=non_nchs_sex,
        category_col="Sex",
        title="Sex Distribution: Georgia and OASIS",
        filename="Demographics Pie Dashboard - Sex.png"
    )

    make_pie_dashboard(
        data=non_nchs_race,
        category_col="Race",
        title="Race Distribution: Georgia and OASIS",
        filename="Demographics Pie Dashboard - Race.png"
    )

    make_pie_dashboard(
        data=non_nchs_cause,
        category_col="Cause",
        title="Top Causes of Death: Georgia and OASIS",
        filename="Top Causes Pie Dashboard.png",
        top_n=6
    )

    make_pie_dashboard(
        data=nchs_sex,
        category_col="Sex",
        title="NCHS Sex Distribution",
        filename="NCHS Pie Dashboard - Sex.png"
    )

    make_pie_dashboard(
        data=nchs_race,
        category_col="Race",
        title="NCHS Race Distribution",
        filename="NCHS Pie Dashboard - Race.png"
    )

    make_pie_dashboard(
        data=nchs_cause,
        category_col="Cause",
        title="NCHS Top Causes of Death",
        filename="NCHS Pie Dashboard - Top Causes.png",
        top_n=6
    )


def make_pie_dashboard(data, category_col, title, filename, top_n=None):
    if data.empty:
        return

    groups = (
        data[["Source", "Geography"]]
        .drop_duplicates()
        .sort_values(["Source", "Geography"])
    )

    rows = 2 if len(groups) <= 4 else 3
    fig, axes = plt.subplots(rows, 2, figsize=(18, rows * 5.8))
    axes = axes.flatten()

    for i, (_, group) in enumerate(groups.iterrows()):
        source = group["Source"]
        county = group["Geography"]

        current = data[
            (data["Source"] == source) &
            (data["Geography"] == county)
        ].copy()

        if top_n:
            top_values = (
                current.groupby(category_col)["Deaths"]
                .sum()
                .sort_values(ascending=False)
                .head(top_n)
                .index
            )

            current[category_col] = current[category_col].where(
                current[category_col].isin(top_values),
                "Other"
            )

        pie_data = (
            current.groupby(category_col)["Deaths"]
            .sum()
            .sort_values(ascending=False)
        )

        pie_data.index = [clean_label(x) for x in pie_data.index]

        wedges, texts, autotexts = axes[i].pie(
            pie_data.values,
            labels=None,
            autopct="%1.1f%%",
            startangle=90,
            colors=CHART_COLORS[:len(pie_data)],
            pctdistance=0.75,
            textprops={"fontsize": 9}
        )

        axes[i].legend(
            wedges,
            pie_data.index,
            title=category_col,
            loc="center left",
            bbox_to_anchor=(1.0, 0.5),
            fontsize=8
        )

        axes[i].set_title(f"{source} - {county}", fontsize=12)

    for j in range(len(groups), len(axes)):
        axes[j].axis("off")

    fig.suptitle(title, fontsize=18, fontweight="bold")
    save_png(filename)


def graph_social_determinants(social_data):
    make_social_heatmaps(
        social_data=social_data,
        social_col="Education",
        file_label="Education"
    )

    make_social_heatmaps(
        social_data=social_data,
        social_col="SES Vulnerability",
        file_label="SES"
    )


def make_social_heatmaps(social_data, social_col, file_label):
    for source in sorted(social_data["Source"].unique()):
        for county in sorted(social_data["Geography"].unique()):
            current = social_data[
                (social_data["Source"] == source) &
                (social_data["Geography"] == county)
            ].copy()

            if current.empty:
                continue

            current["Cause"] = current["Cause"].apply(clean_cause)

            current = keep_top_causes_per_group(
                current,
                group_cols=[social_col],
                top_n=8
            )

            pivot = current.pivot_table(
                index=social_col,
                columns="Cause",
                values="Deaths",
                aggfunc="sum",
                fill_value=0
            )

            pivot.columns = [short_label(x, 24) for x in pivot.columns]
            pivot.index = [clean_label(x) for x in pivot.index]

            plt.figure(figsize=(16, 7))

            sns.heatmap(
                pivot,
                annot=True,
                fmt=".0f",
                cmap="Reds",
                linewidths=0.5,
                cbar_kws={"label": "Deaths"}
            )

            plt.title(f"{file_label} by Cause of Death\n{source} - {county}")
            plt.xlabel("Cause of Death")
            plt.ylabel(file_label)
            plt.xticks(rotation=35, ha="right")

            save_png(f"{file_label} Heatmap - {source} - {county}.png")

            fig = px.imshow(
                pivot,
                text_auto=".0f",
                color_continuous_scale="Reds",
                title=f"{file_label} by Cause of Death: {source} - {county}"
            )

            fig.update_layout(
                font=dict(size=13, color="#3B0D0C"),
                xaxis_title="Cause of Death",
                yaxis_title=file_label,
                paper_bgcolor="white",
                plot_bgcolor="white"
            )

            fig.write_html(
                HTML_DIR / f"{file_label} Heatmap - {source} - {county}.html"
            )


def graph_race_social_breakdowns(social_data):
    for data_name, current_data in [
        ("Georgia and OASIS", social_data[social_data["Source"] != "NCHS"].copy()),
        ("NCHS", social_data[social_data["Source"] == "NCHS"].copy())
    ]:
        current_data = clean_race_data(current_data)

        for social_col, file_label in [
            ("Education", "Race and Education"),
            ("SES Vulnerability", "Race and SES")
        ]:
            if current_data.empty:
                continue

            current_data["Cause"] = current_data["Cause"].apply(clean_cause)

            current = keep_top_causes_per_group(
                current_data,
                group_cols=["Source", "Geography", social_col, "Race"],
                top_n=5
            )

            summary = (
                current.groupby([social_col, "Race"], as_index=False)["Deaths"]
                .sum()
                .sort_values("Deaths", ascending=False)
                .head(15)
            )

            summary[social_col] = summary[social_col].apply(clean_label)
            summary["Race"] = summary["Race"].apply(clean_label)
            summary["Group"] = summary[social_col] + " | " + summary["Race"]

            plt.figure(figsize=(12, 8))

            ax = sns.barplot(
                data=summary,
                y="Group",
                x="Deaths",
                color="#C7462D"
            )

            ax.set_title(f"{data_name}: Highest Mortality Groups - {file_label}")
            ax.set_xlabel("Deaths")
            ax.set_ylabel("")
            add_bar_labels(ax)

            save_png(f"{data_name} Mortality Ranking - {file_label}.png")


def graph_age_cause_sunbursts(age_cause_data):
    for source in sorted(age_cause_data["Source"].unique()):
        current = age_cause_data[
            age_cause_data["Source"] == source
        ].copy()

        if current.empty:
            continue

        make_age_cause_sunburst(
            data=current,
            source=source
        )


def make_age_cause_sunburst(data, source):
    current = data.copy()

    current["Cause"] = current["Cause"].apply(clean_cause)
    current["Age"] = current["Age"].apply(clean_label)

    current = keep_top_causes_per_group(
        current,
        group_cols=[],
        top_n=5
    )

    summary = (
        current.groupby(
            ["Cause", "Age"],
            as_index=False
        )["Deaths"]
        .sum()
    )

    fig = px.sunburst(
        summary,
        path=["Cause", "Age"],
        values="Deaths",
        title=f"{source}: Top 5 Causes of Death by Age Group",
        color="Cause",
        color_discrete_sequence=CHART_COLORS
    )

    fig.update_traces(
        textinfo="label+percent parent",
        insidetextorientation="radial",
        maxdepth=2,
        textfont_size=13,
        hovertemplate=(
            "<b>%{label}</b><br>"
            "Deaths: %{value:,.0f}<br>"
            "Share: %{percentParent:.1%}"
            "<extra></extra>"
        )
    )

    fig.update_layout(
        width=1200,
        height=850,
        font=dict(size=14, color="#3B0D0C"),
        paper_bgcolor="white",
        plot_bgcolor="white",
        margin=dict(t=80, l=20, r=20, b=20)
    )

    fig.write_html(
        HTML_DIR / f"{source} Sunburst - Disease Age.html"
    )

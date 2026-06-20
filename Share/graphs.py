import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px


sns.set_theme(style="whitegrid")


# ----------------------------------------------------
# Helper functions
# ----------------------------------------------------

def save_png(filename):
    plt.tight_layout()
    plt.savefig(f"outputs/png/{filename}.png", dpi=200)
    plt.savefig(f"outputs/png/{filename}.svg")
    plt.show()
    plt.close()


def print_stats(name, df, column):
    print(f"\n{name}")
    print(f"Mean: {df[column].mean():.2f}")
    print(f"Median: {df[column].median():.2f}")
    print(f"Std Dev: {df[column].std():.2f}")
    print(f"Min: {df[column].min():.2f}")
    print(f"Max: {df[column].max():.2f}")


def add_horizontal_mean(df, column):
    mean_value = df[column].mean()

    plt.axhline(
        mean_value,
        linestyle="--",
        color="black",
        linewidth=1
    )

    plt.text(
        0,
        mean_value,
        f"Mean: {mean_value:.2f}",
        va="bottom",
        fontsize=10,
        color="black"
    )


def add_bar_labels(ax, percent=True):
    for container in ax.containers:
        if percent:
            ax.bar_label(container, fmt="%.1f%%", fontsize=8)
        else:
            ax.bar_label(container, fmt="%.0f", fontsize=8)


def shorten_names(text, max_length=28):
    text = str(text)

    if len(text) > max_length:
        return text[:max_length] + "..."

    return text


def update_pie_labels(fig):
    fig.update_traces(
        textposition="inside",
        textinfo="percent+label+value"
    )
    return fig


def filter_source_county(data, source, county):
    return data[
        (data["Source"] == source) &
        (data["Geography"] == county)
    ].copy()


# ----------------------------------------------------
# Main demographic graphs
# ----------------------------------------------------

def graph_sex_comparison(sex_data):
    print_stats("Sex Distribution", sex_data, "Percent")

    plt.figure(figsize=(12, 6))

    sns.barplot(
        data=sex_data,
        x="Sex",
        y="Percent",
        hue="Group"
    )

    add_horizontal_mean(sex_data, "Percent")

    plt.title("Sex Distribution by Source and County")
    plt.ylabel("Percent of Deaths")
    plt.xlabel("Sex")
    plt.xticks(rotation=20, ha="right")
    save_png("sex_distribution_all_sources_counties")

    fig = px.bar(
        sex_data,
        x="Sex",
        y="Percent",
        color="Group",
        barmode="group",
        text="Percent",
        title="Sex Distribution by Source and County"
    )

    fig.update_traces(texttemplate="%{text:.1f}%")

    fig.add_hline(
        y=sex_data["Percent"].mean(),
        line_dash="dash",
        annotation_text=f"Mean: {sex_data['Percent'].mean():.2f}%"
    )

    fig.write_html("outputs/html/interactive_sex_distribution_all_sources_counties.html")


def graph_race_comparison(race_data):
    print_stats("Race Distribution", race_data, "Percent")

    plt.figure(figsize=(16, 8))

    sns.barplot(
        data=race_data,
        x="Race",
        y="Percent",
        hue="Group"
    )

    add_horizontal_mean(race_data, "Percent")

    plt.title("Race Distribution by Source and County")
    plt.ylabel("Percent of Deaths")
    plt.xlabel("Race")
    plt.xticks(rotation=35, ha="right")
    save_png("race_distribution_all_sources_counties")

    fig = px.bar(
        race_data,
        x="Race",
        y="Percent",
        color="Group",
        barmode="group",
        text="Percent",
        title="Race Distribution by Source and County"
    )

    fig.update_traces(texttemplate="%{text:.1f}%")

    fig.add_hline(
        y=race_data["Percent"].mean(),
        line_dash="dash",
        annotation_text=f"Mean: {race_data['Percent'].mean():.2f}%"
    )

    fig.write_html("outputs/html/interactive_race_distribution_all_sources_counties.html")


def graph_heatmaps_by_source_and_county(cause_data):
    for source in cause_data["Source"].unique():
        source_data = cause_data[cause_data["Source"] == source].copy()

        top_causes = (
            source_data.groupby("Cause")["Deaths"]
            .sum()
            .sort_values(ascending=False)
            .head(15)
            .index
        )

        top_data = source_data[source_data["Cause"].isin(top_causes)]

        heat_table = top_data.pivot_table(
            index="Cause",
            columns="Geography",
            values="Percent"
        )

        plt.figure(figsize=(8, 9))

        sns.heatmap(
            heat_table,
            annot=True,
            fmt=".1f",
            cmap="Reds"
        )

        plt.title(f"{source}: Top Causes Heatmap (%)")
        save_png(f"{source.lower()}_top_causes_heatmap")

        fig = px.imshow(
            heat_table,
            text_auto=".1f",
            title=f"{source}: Top Causes Heatmap (%)",
            labels=dict(x="County", y="Cause", color="Percent")
        )

        fig.write_html(
            f"outputs/html/interactive_{source.lower()}_top_causes_heatmap.html"
        )


def graph_pie_charts(sex_data, race_data, cause_data):
    for source in sex_data["Source"].unique():
        for county in sex_data["Geography"].unique():
            temp = filter_source_county(sex_data, source, county)

            fig = px.pie(
                temp,
                names="Sex",
                values="Deaths",
                title=f"{source} - {county}: Deaths by Sex"
            )
            fig = update_pie_labels(fig)

            fig.write_html(
                f"outputs/html/{source.lower()}_{county.lower()}_sex_pie.html"
            )

    for source in race_data["Source"].unique():
        for county in race_data["Geography"].unique():
            temp = filter_source_county(race_data, source, county)

            fig = px.pie(
                temp,
                names="Race",
                values="Deaths",
                title=f"{source} - {county}: Deaths by Race"
            )
            fig = update_pie_labels(fig)

            fig.write_html(
                f"outputs/html/{source.lower()}_{county.lower()}_race_pie.html"
            )

    for source in cause_data["Source"].unique():
        for county in cause_data["Geography"].unique():
            temp = filter_source_county(cause_data, source, county)

            top_causes = (
                temp.groupby("Cause")["Deaths"]
                .sum()
                .sort_values(ascending=False)
                .head(10)
                .index
            )

            temp = temp[temp["Cause"].isin(top_causes)]

            fig = px.pie(
                temp,
                names="Cause",
                values="Deaths",
                title=f"{source} - {county}: Top Causes"
            )
            fig = update_pie_labels(fig)

            fig.write_html(
                f"outputs/html/{source.lower()}_{county.lower()}_cause_pie.html"
            )


# ----------------------------------------------------
# Social determinants graphs
# ----------------------------------------------------

def graph_social_determinants(social_data):
    """
    Analyzes deaths by education, SES vulnerability, race, and cause.
    """

    for source in social_data["Source"].unique():
        for county in social_data["Geography"].unique():
            current = filter_source_county(social_data, source, county)

            top_causes = (
                current[
                    (current["Race"] == "Selected Races Total") &
                    (current["Sex"] == "Selected Sexes Total") &
                    (current["Education"] == "Selected Educations Total") &
                    (current["SES Vulnerability"] == "Selected SES Vulnerability Total")
                ]
                .groupby("Cause")["Deaths"]
                .sum()
                .sort_values(ascending=False)
                .head(8)
                .index
            )

            current = current[current["Cause"].isin(top_causes)].copy()
            current["Short Cause"] = current["Cause"].apply(shorten_names)

            education_data = current[
                (current["Race"] == "Selected Races Total") &
                (current["Sex"] == "Selected Sexes Total") &
                (current["Education"] != "Selected Educations Total") &
                (current["SES Vulnerability"] == "Selected SES Vulnerability Total")
            ].copy()

            education_heat = education_data.pivot_table(
                index="Education",
                columns="Short Cause",
                values="Deaths",
                aggfunc="sum",
                fill_value=0
            )

            education_heat = education_heat.loc[
                education_heat.sum(axis=1) > 0
            ]

            plt.figure(figsize=(17, 7))

            sns.heatmap(
                education_heat,
                annot=True,
                fmt=".0f",
                cmap="Purples",
                linewidths=0.5,
                annot_kws={"size": 9}
            )

            plt.title(f"{source} - {county}: Education Level by Cause of Death")
            plt.xlabel("Cause of Death")
            plt.ylabel("Education Level")
            plt.xticks(rotation=35, ha="right")

            save_png(
                f"{source.lower()}_{county.lower()}_education_by_cause_heatmap"
            )

            fig = px.imshow(
                education_heat,
                text_auto=True,
                title=f"{source} - {county}: Education Level by Cause of Death",
                labels=dict(
                    x="Cause of Death",
                    y="Education Level",
                    color="Deaths"
                )
            )

            fig.update_layout(width=1200, height=650, xaxis_tickangle=-35)

            fig.write_html(
                f"outputs/html/interactive_{source.lower()}_{county.lower()}_education_by_cause_heatmap.html"
            )

            ses_data = current[
                (current["Race"] == "Selected Races Total") &
                (current["Sex"] == "Selected Sexes Total") &
                (current["Education"] == "Selected Educations Total") &
                (current["SES Vulnerability"] != "Selected SES Vulnerability Total")
            ].copy()

            ses_heat = ses_data.pivot_table(
                index="SES Vulnerability",
                columns="Short Cause",
                values="Deaths",
                aggfunc="sum",
                fill_value=0
            )

            ses_order = ["Very Low", "Low", "Average", "High", "Very High"]
            ses_heat = ses_heat.reindex([x for x in ses_order if x in ses_heat.index])

            plt.figure(figsize=(17, 7))

            sns.heatmap(
                ses_heat,
                annot=True,
                fmt=".0f",
                cmap="Oranges",
                linewidths=0.5,
                annot_kws={"size": 9}
            )

            plt.title(f"{source} - {county}: SES Vulnerability by Cause of Death")
            plt.xlabel("Cause of Death")
            plt.ylabel("SES Vulnerability")
            plt.xticks(rotation=35, ha="right")

            save_png(
                f"{source.lower()}_{county.lower()}_ses_by_cause_heatmap"
            )

            fig = px.imshow(
                ses_heat,
                text_auto=True,
                title=f"{source} - {county}: SES Vulnerability by Cause of Death",
                labels=dict(
                    x="Cause of Death",
                    y="SES Vulnerability",
                    color="Deaths"
                )
            )

            fig.update_layout(width=1200, height=650, xaxis_tickangle=-35)

            fig.write_html(
                f"outputs/html/interactive_{source.lower()}_{county.lower()}_ses_by_cause_heatmap.html"
            )


def graph_race_social_breakdowns(social_data):
    """
    Shows how race fits into education/cause and SES/cause patterns.
    """

    race_education = social_data[
        (social_data["Race"] != "Selected Races Total") &
        (social_data["Sex"] == "Selected Sexes Total") &
        (social_data["Education"] != "Selected Educations Total") &
        (social_data["SES Vulnerability"] == "Selected SES Vulnerability Total")
    ].copy()

    race_education = (
        race_education
        .groupby(["Source", "Geography", "Race", "Education", "Cause"])["Deaths"]
        .sum()
        .reset_index()
        .sort_values("Deaths", ascending=False)
    )

    race_education.to_csv(
        "outputs/csv/race_education_cause_rankings.csv",
        index=False
    )

    top_education = race_education.head(25).copy()
    top_education["Short Cause"] = top_education["Cause"].apply(shorten_names)

    top_education["Label"] = (
        top_education["Geography"] + " | " +
        top_education["Race"] + " | " +
        top_education["Education"] + " | " +
        top_education["Short Cause"]
    )

    plt.figure(figsize=(16, 11))

    ax = sns.barplot(
        data=top_education,
        x="Deaths",
        y="Label",
        hue="Source"
    )

    add_bar_labels(ax, percent=False)

    plt.title("Top Race + Education + Cause Mortality Groups")
    plt.xlabel("Deaths")
    plt.ylabel("Group")

    save_png("top_race_education_cause_groups")

    fig = px.bar(
        top_education,
        x="Deaths",
        y="Label",
        color="Source",
        orientation="h",
        text="Deaths",
        title="Top Race + Education + Cause Mortality Groups",
        hover_data=["Geography", "Race", "Education", "Cause"]
    )

    fig.update_traces(textposition="outside")
    fig.update_layout(width=1300, height=950, yaxis=dict(autorange="reversed"))

    fig.write_html(
        "outputs/html/interactive_top_race_education_cause_groups.html"
    )

    race_ses = social_data[
        (social_data["Race"] != "Selected Races Total") &
        (social_data["Sex"] == "Selected Sexes Total") &
        (social_data["Education"] == "Selected Educations Total") &
        (social_data["SES Vulnerability"] != "Selected SES Vulnerability Total")
    ].copy()

    race_ses = (
        race_ses
        .groupby(["Source", "Geography", "Race", "SES Vulnerability", "Cause"])["Deaths"]
        .sum()
        .reset_index()
        .sort_values("Deaths", ascending=False)
    )

    race_ses.to_csv(
        "outputs/csv/race_ses_cause_rankings.csv",
        index=False
    )

    top_ses = race_ses.head(25).copy()
    top_ses["Short Cause"] = top_ses["Cause"].apply(shorten_names)

    top_ses["Label"] = (
        top_ses["Geography"] + " | " +
        top_ses["Race"] + " | " +
        top_ses["SES Vulnerability"] + " SES | " +
        top_ses["Short Cause"]
    )

    plt.figure(figsize=(16, 11))

    ax = sns.barplot(
        data=top_ses,
        x="Deaths",
        y="Label",
        hue="Source"
    )

    add_bar_labels(ax, percent=False)

    plt.title("Top Race + SES Vulnerability + Cause Mortality Groups")
    plt.xlabel("Deaths")
    plt.ylabel("Group")

    save_png("top_race_ses_cause_groups")

    fig = px.bar(
        top_ses,
        x="Deaths",
        y="Label",
        color="Source",
        orientation="h",
        text="Deaths",
        title="Top Race + SES Vulnerability + Cause Mortality Groups",
        hover_data=["Geography", "Race", "SES Vulnerability", "Cause"]
    )

    fig.update_traces(textposition="outside")
    fig.update_layout(width=1300, height=950, yaxis=dict(autorange="reversed"))

    fig.write_html(
        "outputs/html/interactive_top_race_ses_cause_groups.html"
    )


def keep_top_causes_per_group(df, group_cols, top_n=5):
    cause_totals = (
        df.groupby(group_cols + ["Cause"], as_index=False)["Deaths"]
        .sum()
    )

    cause_totals["Rank"] = (
        cause_totals
        .groupby(group_cols)["Deaths"]
        .rank(method="first", ascending=False)
    )

    return cause_totals[cause_totals["Rank"] <= top_n].copy()


def graph_social_sunbursts(social_data):
    """
    Creates interactive drill-down charts.

    Hierarchy:
    Source -> County -> SES/Education -> Race -> Top 5 Causes
    """

    education_base = social_data[
        (social_data["Race"] != "Selected Races Total") &
        (social_data["Sex"] == "Selected Sexes Total") &
        (social_data["Education"] != "Selected Educations Total") &
        (social_data["SES Vulnerability"] == "Selected SES Vulnerability Total") &
        (social_data["Deaths"] > 0)
    ].copy()

    education_sunburst = keep_top_causes_per_group(
        education_base,
        ["Source", "Geography", "Education", "Race"],
        top_n=5
    )

    fig = px.sunburst(
        education_sunburst,
        path=["Source", "Geography", "Education", "Race", "Cause"],
        values="Deaths",
        title="Education, Race, and Cause of Death Drilldown - Top 5 Causes per Group"
    )

    fig.update_traces(maxdepth=5, insidetextorientation="radial")
    fig.update_layout(width=1200, height=900)

    fig.write_html(
        "outputs/html/interactive_education_race_cause_sunburst.html"
    )

    ses_base = social_data[
        (social_data["Race"] != "Selected Races Total") &
        (social_data["Sex"] == "Selected Sexes Total") &
        (social_data["Education"] == "Selected Educations Total") &
        (social_data["SES Vulnerability"] != "Selected SES Vulnerability Total") &
        (social_data["Deaths"] > 0)
    ].copy()

    ses_sunburst = keep_top_causes_per_group(
        ses_base,
        ["Source", "Geography", "SES Vulnerability", "Race"],
        top_n=5
    )

    fig = px.sunburst(
        ses_sunburst,
        path=["Source", "Geography", "SES Vulnerability", "Race", "Cause"],
        values="Deaths",
        title="SES Vulnerability, Race, and Cause of Death Drilldown - Top 5 Causes per Group"
    )

    fig.update_traces(maxdepth=5, insidetextorientation="radial")
    fig.update_layout(width=1200, height=900)

    fig.write_html(
        "outputs/html/interactive_ses_race_cause_sunburst.html"
    )
def graph_original_bar_dashboard(sex_data, race_data):
    """
    One PNG dashboard for the main bar chart comparisons.
    Replaces separate sex/race bar chart files.
    """

    fig, axes = plt.subplots(2, 1, figsize=(18, 14))

    sns.barplot(
        data=sex_data,
        x="Sex",
        y="Percent",
        hue="Group",
        ax=axes[0]
    )

    axes[0].set_title("Sex Distribution by Source and County")
    axes[0].set_ylabel("Percent of Deaths")
    axes[0].set_xlabel("Sex")

    sns.barplot(
        data=race_data,
        x="Race",
        y="Percent",
        hue="Group",
        ax=axes[1]
    )

    axes[1].set_title("Race Distribution by Source and County")
    axes[1].set_ylabel("Percent of Deaths")
    axes[1].set_xlabel("Race")
    axes[1].tick_params(axis="x", rotation=35)

    plt.tight_layout()
    plt.savefig("outputs/png/original_demographic_bar_dashboard.png", dpi=200)
    plt.close()


def graph_original_pie_dashboards(sex_data, race_data, cause_data):
    """
    Creates dashboard PNGs instead of many separate pie chart files.
    """

    datasets = [
        ("Sex", sex_data, "Sex", "original_sex_pie_dashboard.png"),
        ("Race", race_data, "Race", "original_race_pie_dashboard.png"),
        ("Top Causes", cause_data, "Cause", "original_cause_pie_dashboard.png")
    ]

    for title, data, category_col, filename in datasets:
        groups = data[["Source", "Geography"]].drop_duplicates()

        fig, axes = plt.subplots(3, 2, figsize=(18, 18))
        axes = axes.flatten()

        for i, (_, group) in enumerate(groups.iterrows()):
            source = group["Source"]
            county = group["Geography"]

            temp = data[
                (data["Source"] == source) &
                (data["Geography"] == county)
            ].copy()

            if category_col == "Cause":
                top_causes = (
                    temp.groupby("Cause")["Deaths"]
                    .sum()
                    .sort_values(ascending=False)
                    .head(6)
                    .index
                )

                temp = temp[temp["Cause"].isin(top_causes)]

            temp = (
                temp.groupby(category_col)["Deaths"]
                .sum()
                .sort_values(ascending=False)
            )

            axes[i].pie(
                temp.values,
                labels=temp.index,
                autopct="%1.1f%%",
                startangle=90
            )

            axes[i].set_title(f"{source} - {county}")

        for j in range(len(groups), len(axes)):
            axes[j].axis("off")

        fig.suptitle(f"{title} Distribution Dashboard", fontsize=18)
        plt.tight_layout()
        plt.savefig(f"outputs/png/{filename}", dpi=200)
        plt.close()

def graph_original_bar_dashboard(sex_data, race_data):
    fig, axes = plt.subplots(2, 1, figsize=(18, 14))

    sns.barplot(data=sex_data, x="Sex", y="Percent", hue="Group", ax=axes[0])
    axes[0].set_title("Sex Distribution by Source and County")
    axes[0].set_ylabel("Percent of Deaths")
    axes[0].set_xlabel("Sex")

    sns.barplot(data=race_data, x="Race", y="Percent", hue="Group", ax=axes[1])
    axes[1].set_title("Race Distribution by Source and County")
    axes[1].set_ylabel("Percent of Deaths")
    axes[1].set_xlabel("Race")
    axes[1].tick_params(axis="x", rotation=35)

    plt.tight_layout()
    plt.savefig("outputs/png/original_demographic_bar_dashboard.png", dpi=200)
    plt.close()


def graph_original_pie_dashboards(sex_data, race_data, cause_data):
    datasets = [
        ("Sex", sex_data, "Sex", "original_sex_pie_dashboard.png"),
        ("Race", race_data, "Race", "original_race_pie_dashboard.png"),
        ("Top Causes", cause_data, "Cause", "original_cause_pie_dashboard.png")
    ]

    for title, data, category_col, filename in datasets:
        groups = data[["Source", "Geography"]].drop_duplicates()

        fig, axes = plt.subplots(3, 2, figsize=(18, 18))
        axes = axes.flatten()

        for i, (_, group) in enumerate(groups.iterrows()):
            source = group["Source"]
            county = group["Geography"]

            temp = data[
                (data["Source"] == source) &
                (data["Geography"] == county)
            ].copy()

            if category_col == "Cause":
                top_causes = (
                    temp.groupby("Cause")["Deaths"]
                    .sum()
                    .sort_values(ascending=False)
                    .head(6)
                    .index
                )
                temp = temp[temp["Cause"].isin(top_causes)]

            temp = (
                temp.groupby(category_col)["Deaths"]
                .sum()
                .sort_values(ascending=False)
            )

            axes[i].pie(
                temp.values,
                labels=temp.index,
                autopct="%1.1f%%",
                startangle=90
            )

            axes[i].set_title(f"{source} - {county}")

        for j in range(len(groups), len(axes)):
            axes[j].axis("off")

        fig.suptitle(f"{title} Distribution Dashboard", fontsize=18)
        plt.tight_layout()
        plt.savefig(f"outputs/png/{filename}", dpi=200)
        plt.close()
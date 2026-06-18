import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px


# ----------------------------------------------------
# Project colors
# ----------------------------------------------------

SOURCE_COLORS = {
    "Georgia": "#2ca02c",
    "OASIS": "#9467bd",
    "NCHS": "#d62728"
}

COUNTY_COLORS = {
    "Fulton": "#1f77b4",
    "DeKalb": "#ff7f0e"
}


sns.set_theme(style="whitegrid")


# ----------------------------------------------------
# Helper functions
# ----------------------------------------------------

def save_png(filename):
    plt.tight_layout()
    plt.savefig(f"outputs/png/{filename}.png", dpi=300)
    plt.savefig(f"outputs/png/{filename}.svg")
    plt.show()
    plt.close()


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


def add_vertical_mean(df, column):
    mean_value = df[column].mean()

    plt.axvline(
        mean_value,
        linestyle="--",
        color="black",
        linewidth=1
    )

    plt.text(
        mean_value,
        0,
        f"Mean: {mean_value:.2f}",
        rotation=90,
        va="bottom",
        fontsize=10,
        color="black"
    )


def print_stats(name, df, column):
    print(f"\n{name}")
    print(f"Mean: {df[column].mean():.2f}")
    print(f"Median: {df[column].median():.2f}")
    print(f"Std Dev: {df[column].std():.2f}")
    print(f"Min: {df[column].min():.2f}")
    print(f"Max: {df[column].max():.2f}")


# ----------------------------------------------------
# 1. Total deaths
# ----------------------------------------------------

def graph_total_deaths(total_data):
    print_stats("Total Deaths", total_data, "Deaths")

    plt.figure(figsize=(12, 6))

    sns.barplot(
        data=total_data,
        x="Source",
        y="Deaths",
        hue="Geography",
        palette=COUNTY_COLORS
    )

    add_horizontal_mean(total_data, "Deaths")

    plt.title("Total Deaths by Source and County")
    plt.ylabel("Deaths")
    plt.xlabel("Data Source")
    save_png("total_deaths_by_source_county")

    fig = px.bar(
        total_data,
        x="Source",
        y="Deaths",
        color="Geography",
        barmode="group",
        color_discrete_map=COUNTY_COLORS,
        title="Total Deaths by Source and County"
    )

    fig.add_hline(
        y=total_data["Deaths"].mean(),
        line_dash="dash",
        annotation_text=f"Mean: {total_data['Deaths'].mean():.2f}"
    )

    fig.write_html("outputs/html/interactive_total_deaths_by_source_county.html")


# ----------------------------------------------------
# 2. Age trend graph
# ----------------------------------------------------

def graph_age_trends(age_data):
    print_stats("Age Distribution", age_data, "Percent")

    plt.figure(figsize=(16, 8))

    sns.lineplot(
        data=age_data,
        x="Age",
        y="Percent",
        hue="Group",
        marker="o"
    )

    add_horizontal_mean(age_data, "Percent")

    plt.title("Age Distribution of Deaths by Source and County")
    plt.ylabel("Percent of Deaths")
    plt.xlabel("Age Group")
    plt.xticks(rotation=45, ha="right")
    save_png("age_trends_all_sources_counties")

    fig = px.line(
        age_data,
        x="Age",
        y="Percent",
        color="Group",
        markers=True,
        title="Age Distribution of Deaths by Source and County"
    )

    fig.add_hline(
        y=age_data["Percent"].mean(),
        line_dash="dash",
        annotation_text=f"Mean: {age_data['Percent'].mean():.2f}%"
    )

    fig.write_html("outputs/html/interactive_age_trends_all_sources_counties.html")


# ----------------------------------------------------
# 3. Sex comparison
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
        title="Sex Distribution by Source and County"
    )

    fig.add_hline(
        y=sex_data["Percent"].mean(),
        line_dash="dash",
        annotation_text=f"Mean: {sex_data['Percent'].mean():.2f}%"
    )

    fig.write_html("outputs/html/interactive_sex_distribution_all_sources_counties.html")


# ----------------------------------------------------
# 4. Race comparison
# ----------------------------------------------------

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
        title="Race Distribution by Source and County"
    )

    fig.add_hline(
        y=race_data["Percent"].mean(),
        line_dash="dash",
        annotation_text=f"Mean: {race_data['Percent'].mean():.2f}%"
    )

    fig.write_html("outputs/html/interactive_race_distribution_all_sources_counties.html")


# ----------------------------------------------------
# 5. Common causes across all sources
# ----------------------------------------------------

def graph_common_causes(cause_data):
    """
    Creates source-specific top cause graphs.

    This is safer than combining all sources into one graph because
    different sources may name or group causes of death differently.
    """

    for source in cause_data["Source"].unique():
        source_data = cause_data[
            cause_data["Source"] == source
        ].copy()

        top_causes = (
            source_data.groupby("Cause")["Deaths"]
            .sum()
            .sort_values(ascending=False)
            .head(10)
            .index
        )

        top_data = source_data[
            source_data["Cause"].isin(top_causes)
        ].copy()

        print_stats(
            f"{source} Source-Specific Top Causes",
            top_data,
            "Percent"
        )

        plt.figure(figsize=(14, 8))

        sns.barplot(
            data=top_data,
            x="Percent",
            y="Cause",
            hue="Geography",
            palette=COUNTY_COLORS
        )

        add_vertical_mean(top_data, "Percent")

        plt.title(
            f"{source}: Top Causes of Death by County"
        )
        plt.xlabel("Percent of Deaths")
        plt.ylabel("Cause of Death")

        save_png(
            f"{source.lower()}_source_specific_top_causes"
        )

        fig = px.bar(
            top_data,
            x="Percent",
            y="Cause",
            color="Geography",
            barmode="group",
            orientation="h",
            color_discrete_map=COUNTY_COLORS,
            title=f"{source}: Top Causes of Death by County"
        )

        fig.add_vline(
            x=top_data["Percent"].mean(),
            line_dash="dash",
            annotation_text=f"Mean: {top_data['Percent'].mean():.2f}%"
        )

        fig.write_html(
            f"outputs/html/interactive_{source.lower()}_source_specific_top_causes.html"
        )

# ----------------------------------------------------
# 6. Top causes by source
# ----------------------------------------------------

def graph_top_causes_by_source(cause_data):
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

        print_stats(f"{source} Top Causes", top_data, "Percent")

        plt.figure(figsize=(14, 9))

        sns.barplot(
            data=top_data,
            x="Percent",
            y="Cause",
            hue="Geography",
            palette=COUNTY_COLORS
        )

        add_vertical_mean(top_data, "Percent")

        plt.title(f"{source}: Top Causes of Death by County")
        plt.xlabel("Percent of Deaths")
        plt.ylabel("Cause of Death")
        save_png(f"{source.lower()}_top_causes_by_county")

        fig = px.bar(
            top_data,
            x="Percent",
            y="Cause",
            color="Geography",
            barmode="group",
            orientation="h",
            color_discrete_map=COUNTY_COLORS,
            title=f"{source}: Top Causes of Death by County"
        )

        fig.add_vline(
            x=top_data["Percent"].mean(),
            line_dash="dash",
            annotation_text=f"Mean: {top_data['Percent'].mean():.2f}%"
        )

        fig.write_html(
            f"outputs/html/interactive_{source.lower()}_top_causes_by_county.html"
        )


# ----------------------------------------------------
# 7. Heatmaps
# ----------------------------------------------------

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


# ----------------------------------------------------
# 8. Pie charts
# ----------------------------------------------------

def graph_pie_charts(sex_data, race_data, cause_data):
    for source in sex_data["Source"].unique():
        for county in sex_data["Geography"].unique():
            temp = sex_data[
                (sex_data["Source"] == source) &
                (sex_data["Geography"] == county)
            ]

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
            temp = race_data[
                (race_data["Source"] == source) &
                (race_data["Geography"] == county)
            ]

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
            temp = cause_data[
                (cause_data["Source"] == source) &
                (cause_data["Geography"] == county)
            ].copy()

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
# 9. Dashboard summary
# ----------------------------------------------------

def graph_dashboard_summary(total_data, age_data, sex_data, cause_data):
    fig, axes = plt.subplots(2, 2, figsize=(20, 13))

    sns.barplot(
        data=total_data,
        x="Source",
        y="Deaths",
        hue="Geography",
        palette=COUNTY_COLORS,
        ax=axes[0, 0]
    )

    total_mean = total_data["Deaths"].mean()

    axes[0, 0].axhline(total_mean, linestyle="--", color="black")
    axes[0, 0].text(0, total_mean, f"Mean: {total_mean:.2f}")
    axes[0, 0].set_title("Total Deaths")

    sns.lineplot(
        data=age_data,
        x="Age",
        y="Percent",
        hue="Group",
        marker="o",
        ax=axes[0, 1]
    )

    age_mean = age_data["Percent"].mean()

    axes[0, 1].axhline(age_mean, linestyle="--", color="black")
    axes[0, 1].text(0, age_mean, f"Mean: {age_mean:.2f}%")
    axes[0, 1].set_title("Age Distribution")
    axes[0, 1].tick_params(axis="x", rotation=45)

    sns.barplot(
        data=sex_data,
        x="Sex",
        y="Percent",
        hue="Group",
        ax=axes[1, 0]
    )

    sex_mean = sex_data["Percent"].mean()

    axes[1, 0].axhline(sex_mean, linestyle="--", color="black")
    axes[1, 0].text(0, sex_mean, f"Mean: {sex_mean:.2f}%")
    axes[1, 0].set_title("Sex Distribution")

    top_causes = (
        cause_data.groupby("Cause")["Deaths"]
        .sum()
        .sort_values(ascending=False)
        .head(8)
        .index
    )

    top_data = cause_data[cause_data["Cause"].isin(top_causes)]

    sns.barplot(
        data=top_data,
        x="Percent",
        y="Cause",
        hue="Group",
        ax=axes[1, 1]
    )

    cause_mean = top_data["Percent"].mean()

    axes[1, 1].axvline(cause_mean, linestyle="--", color="black")
    axes[1, 1].text(cause_mean, 0, f"Mean: {cause_mean:.2f}%", rotation=90)
    axes[1, 1].set_title("Top Causes")

    plt.suptitle("Atlanta Health EDA Dashboard", fontsize=20)
    plt.tight_layout()
    plt.savefig("outputs/png/dashboard_summary.png", dpi=300)
    plt.savefig("outputs/png/dashboard_summary.svg")
    plt.show()
    plt.close()

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

def graph_target_population_heatmaps(target_data):
    """
    Makes readable target population graphs.

    Age x Cause and Race x Cause stay as heatmaps.
    Sex x Cause becomes a bar chart because there are only two sex categories.
    """

    for source in target_data["Source"].unique():
        for county in target_data["Geography"].unique():

            current = target_data[
                (target_data["Source"] == source) &
                (target_data["Geography"] == county)
            ].copy()

            top_causes = (
                current.groupby("Cause")["Deaths"]
                .sum()
                .sort_values(ascending=False)
                .head(8)
                .index
            )

            current = current[current["Cause"].isin(top_causes)].copy()

            current["Short Cause"] = current["Cause"].apply(shorten_names)

            # -------------------------------
            # Age x Cause Heatmap
            # -------------------------------

            age_heat = current.pivot_table(
                index="Age",
                columns="Short Cause",
                values="Deaths",
                aggfunc="sum",
                fill_value=0
            )

            # Remove empty rows
            age_heat = age_heat.loc[age_heat.sum(axis=1) > 0]

            plt.figure(figsize=(18, 10))

            sns.heatmap(
                age_heat,
                annot=True,
                fmt=".0f",
                cmap="Reds",
                linewidths=0.5,
                annot_kws={"size": 8}
            )

            plt.title(f"{source} - {county}: Age by Cause of Death")
            plt.xlabel("Cause of Death")
            plt.ylabel("Age Group")
            plt.xticks(rotation=35, ha="right", fontsize=9)
            plt.yticks(rotation=0, fontsize=9)

            save_png(
                f"{source.lower()}_{county.lower()}_age_by_cause_heatmap"
            )

            fig = px.imshow(
                age_heat,
                text_auto=True,
                title=f"{source} - {county}: Age by Cause of Death",
                labels=dict(
                    x="Cause of Death",
                    y="Age Group",
                    color="Deaths"
                )
            )

            fig.update_layout(
                width=1200,
                height=800,
                xaxis_tickangle=-35
            )

            fig.write_html(
                f"outputs/html/interactive_{source.lower()}_{county.lower()}_age_by_cause_heatmap.html"
            )

            # -------------------------------
            # Race x Cause Heatmap
            # -------------------------------

            race_heat = current.pivot_table(
                index="Race",
                columns="Short Cause",
                values="Deaths",
                aggfunc="sum",
                fill_value=0
            )

            race_heat = race_heat.loc[race_heat.sum(axis=1) > 0]

            plt.figure(figsize=(16, 7))

            sns.heatmap(
                race_heat,
                annot=True,
                fmt=".0f",
                cmap="Blues",
                linewidths=0.5,
                annot_kws={"size": 9}
            )

            plt.title(f"{source} - {county}: Race by Cause of Death")
            plt.xlabel("Cause of Death")
            plt.ylabel("Race")
            plt.xticks(rotation=35, ha="right", fontsize=9)
            plt.yticks(rotation=0, fontsize=9)

            save_png(
                f"{source.lower()}_{county.lower()}_race_by_cause_heatmap"
            )

            fig = px.imshow(
                race_heat,
                text_auto=True,
                title=f"{source} - {county}: Race by Cause of Death",
                labels=dict(
                    x="Cause of Death",
                    y="Race",
                    color="Deaths"
                )
            )

            fig.update_layout(
                width=1200,
                height=650,
                xaxis_tickangle=-35
            )

            fig.write_html(
                f"outputs/html/interactive_{source.lower()}_{county.lower()}_race_by_cause_heatmap.html"
            )

            # -------------------------------
            # Sex x Cause Bar Chart
            # -------------------------------

            sex_data = (
                current.groupby(["Sex", "Short Cause"])["Deaths"]
                .sum()
                .reset_index()
            )

            plt.figure(figsize=(15, 7))

            ax = sns.barplot(
                data=sex_data,
                x="Deaths",
                y="Short Cause",
                hue="Sex"
            )

            add_bar_labels(ax, percent=False)

            plt.title(f"{source} - {county}: Sex by Cause of Death")
            plt.xlabel("Deaths")
            plt.ylabel("Cause of Death")

            save_png(
                f"{source.lower()}_{county.lower()}_sex_by_cause_bar"
            )

            fig = px.bar(
                sex_data,
                x="Deaths",
                y="Short Cause",
                color="Sex",
                barmode="group",
                orientation="h",
                text="Deaths",
                title=f"{source} - {county}: Sex by Cause of Death"
            )

            fig.update_traces(textposition="outside")

            fig.update_layout(
                width=1100,
                height=700
            )

            fig.write_html(
                f"outputs/html/interactive_{source.lower()}_{county.lower()}_sex_by_cause_bar.html"
            )

def graph_target_population_rankings(target_data):
    """
    Creates a readable leaderboard of the highest-risk target population groups.
    """

    rankings = (
        target_data.groupby(
            ["Source", "Geography", "Cause", "Age", "Race", "Sex"]
        )["Deaths"]
        .sum()
        .reset_index()
        .sort_values("Deaths", ascending=False)
    )

    rankings["Priority Score"] = rankings["Deaths"]

    rankings.to_csv(
        "outputs/csv/target_population_rankings.csv",
        index=False
    )

    top_20 = rankings.head(20).copy()

    top_20["Short Cause"] = top_20["Cause"].apply(shorten_names)

    top_20["Label"] = (
        top_20["Geography"] + " | " +
        top_20["Age"] + " | " +
        top_20["Race"] + " | " +
        top_20["Sex"] + " | " +
        top_20["Short Cause"]
    )

    plt.figure(figsize=(16, 11))

    ax = sns.barplot(
        data=top_20,
        x="Deaths",
        y="Label",
        hue="Source"
    )

    add_bar_labels(ax, percent=False)

    plt.title("Top 20 Target Population Opportunities")
    plt.xlabel("Deaths")
    plt.ylabel("Population Group")

    save_png("top_target_population_opportunities")

    fig = px.bar(
        top_20,
        x="Deaths",
        y="Label",
        color="Source",
        orientation="h",
        text="Deaths",
        title="Top 20 Target Population Opportunities",
        hover_data=[
            "Geography",
            "Cause",
            "Age",
            "Race",
            "Sex",
            "Priority Score"
        ]
    )

    fig.update_traces(textposition="outside")

    fig.update_layout(
        width=1300,
        height=900,
        yaxis=dict(autorange="reversed")
    )

    fig.write_html(
        "outputs/html/interactive_top_target_population_opportunities.html"
    )

def update_pie_labels(fig):
    fig.update_traces(
        textposition="inside",
        textinfo="percent+label+value"
    )
    return fig

def graph_social_determinants(social_data):
    """
    Analyzes deaths by education, SES vulnerability, race, and cause.
    """

    for source in social_data["Source"].unique():
        for county in social_data["Geography"].unique():

            current = social_data[
                (social_data["Source"] == source) &
                (social_data["Geography"] == county)
            ].copy()

            # Pick top causes for this source/county
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

            # ==================================================
            # Education x Cause Heatmap
            # ==================================================

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

            # ==================================================
            # SES Vulnerability x Cause Heatmap
            # ==================================================

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

            ses_heat = ses_heat.reindex(
                [x for x in ses_order if x in ses_heat.index]
            )

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

    # ==================================================
    # Race + Education + Cause leaderboard
    # ==================================================

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

    # ==================================================
    # Race + SES + Cause leaderboard
    # ==================================================

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


def graph_social_sunbursts(social_data):
    """
    Creates interactive drill-down charts.
    These are HTML-only because sunbursts are meant to be interactive.
    """

    education_sunburst = social_data[
        (social_data["Race"] != "Selected Races Total") &
        (social_data["Sex"] == "Selected Sexes Total") &
        (social_data["Education"] != "Selected Educations Total") &
        (social_data["SES Vulnerability"] == "Selected SES Vulnerability Total")
    ].copy()

    education_sunburst = (
        education_sunburst
        .groupby(["Source", "Geography", "Education", "Race", "Cause"])["Deaths"]
        .sum()
        .reset_index()
    )

    education_sunburst = education_sunburst[
        education_sunburst["Deaths"] > 0
    ]

    fig = px.sunburst(
        education_sunburst,
        path=["Source", "Geography", "Education", "Race", "Cause"],
        values="Deaths",
        title="Education, Race, and Cause of Death Drilldown"
    )

    fig.write_html(
        "outputs/html/interactive_education_race_cause_sunburst.html"
    )

    ses_sunburst = social_data[
        (social_data["Race"] != "Selected Races Total") &
        (social_data["Sex"] == "Selected Sexes Total") &
        (social_data["Education"] == "Selected Educations Total") &
        (social_data["SES Vulnerability"] != "Selected SES Vulnerability Total")
    ].copy()

    ses_sunburst = (
        ses_sunburst
        .groupby(["Source", "Geography", "SES Vulnerability", "Race", "Cause"])["Deaths"]
        .sum()
        .reset_index()
    )

    ses_sunburst = ses_sunburst[
        ses_sunburst["Deaths"] > 0
    ]

    fig = px.sunburst(
        ses_sunburst,
        path=["Source", "Geography", "SES Vulnerability", "Race", "Cause"],
        values="Deaths",
        title="SES Vulnerability, Race, and Cause of Death Drilldown"
    )

    fig.write_html(
        "outputs/html/interactive_ses_race_cause_sunburst.html"
    )
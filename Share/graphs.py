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
    cause_sets = []

    for source in cause_data["Source"].unique():
        source_causes = set(
            cause_data[cause_data["Source"] == source]["Cause"]
        )

        cause_sets.append(source_causes)

    common_causes = set.intersection(*cause_sets)

    print(f"\nMatching causes across all sources: {len(common_causes)}")

    if len(common_causes) < 5:
        print("Not enough matching causes for a clean combined cause graph.")
        return

    common_data = cause_data[cause_data["Cause"].isin(common_causes)].copy()

    top_causes = (
        common_data.groupby("Cause")["Deaths"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .index
    )

    common_data = common_data[common_data["Cause"].isin(top_causes)]

    print_stats("Common Causes", common_data, "Percent")

    plt.figure(figsize=(17, 8))

    sns.lineplot(
        data=common_data,
        x="Cause",
        y="Percent",
        hue="Group",
        marker="o"
    )

    add_horizontal_mean(common_data, "Percent")

    plt.title("Common Causes Across Sources and Counties")
    plt.ylabel("Percent of Deaths")
    plt.xlabel("Cause of Death")
    plt.xticks(rotation=45, ha="right")
    save_png("common_causes_all_sources_counties")

    fig = px.line(
        common_data,
        x="Cause",
        y="Percent",
        color="Group",
        markers=True,
        title="Common Causes Across Sources and Counties"
    )

    fig.add_hline(
        y=common_data["Percent"].mean(),
        line_dash="dash",
        annotation_text=f"Mean: {common_data['Percent'].mean():.2f}%"
    )

    fig.write_html("outputs/html/interactive_common_causes_all_sources_counties.html")


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
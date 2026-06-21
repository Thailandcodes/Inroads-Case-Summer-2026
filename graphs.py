
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from style import SOURCE_COLORS, GROUP_COLORS, COLORS, set_theme, label_bars, save_figure, clean_axis

set_theme()


def top_n_by_group(df, group_cols, value_col="Deaths", n=5):
    ranked = df.groupby(group_cols + ["Cause Label"], as_index=False)[value_col].sum()
    ranked["Rank"] = ranked.groupby(group_cols)[value_col].rank(method="first", ascending=False)
    return ranked[ranked["Rank"] <= n].copy()


def graph_demographic_dashboard(sex_data, race_data):
    # Graphs for core demographics
    fig, axes = plt.subplots(2, 1, figsize=(16, 12))
    sns.barplot(data=sex_data, x="Sex Label", y="Percent", hue="Group", palette=GROUP_COLORS, ax=axes[0])
    axes[0].set_title("Deaths by Sex")
    axes[0].set_xlabel("Sex")
    axes[0].set_ylabel("Percent of Deaths")
    axes[0].legend(title="Source and County", ncols=3)
    label_bars(axes[0], "percent")
    clean_axis(axes[0])

    race_plot = race_data[race_data["Percent"] > 0.2].copy()
    sns.barplot(data=race_plot, x="Race Label", y="Percent", hue="Group", palette=GROUP_COLORS, ax=axes[1])
    axes[1].set_title("Deaths by Race")
    axes[1].set_xlabel("Race")
    axes[1].set_ylabel("Percent of Deaths")
    axes[1].tick_params(axis="x", rotation=25)
    axes[1].legend(title="Source and County", ncols=3)
    clean_axis(axes[1])
    save_figure(fig, "dashboard_demographics")


def graph_health_burden_dashboard(cause_data):
    # Graphs for leading causes of death
    top_causes = cause_data.groupby("Cause Label")["Deaths"].sum().sort_values(ascending=False).head(8).index
    plot_data = cause_data[cause_data["Cause Label"].isin(top_causes)].copy()
    fig, axes = plt.subplots(1, 3, figsize=(20, 8), sharey=True)
    for ax, source in zip(axes, ["Georgia", "OASIS", "NCHS"]):
        current = plot_data[plot_data["Source"] == source]
        table = current.pivot_table(index="Cause Label", columns="Geography", values="Percent", aggfunc="sum", fill_value=0)
        table = table.reindex(top_causes)
        sns.heatmap(table, annot=True, fmt=".1f", cmap="Blues", linewidths=.5, ax=ax, cbar=ax is axes[-1])
        ax.set_title(source)
        ax.set_xlabel("County")
        ax.set_ylabel("Cause of Death" if ax is axes[0] else "")
    fig.suptitle("Leading Causes of Death by Source and County")
    save_figure(fig, "dashboard_health_burden")

    interactive = plot_data.pivot_table(index="Cause Label", columns="Group", values="Percent", aggfunc="sum", fill_value=0)
    fig_html = px.imshow(interactive, text_auto=".1f", color_continuous_scale="Blues", title="Leading Causes of Death by Source and County", labels={"x":"Source and County", "y":"Cause of Death", "color":"Percent"})
    fig_html.update_layout(width=1100, height=650, font=dict(size=13))
    fig_html.write_html("outputs/html/dashboard_health_burden.html")


def graph_social_dashboard(social_data):
    # Graphs for education and economic vulnerability
    base = social_data[(social_data["Race"] == "Selected Races Total") & (social_data["Sex"] == "Selected Sexes Total")].copy()
    top_causes = base.groupby("Cause Label")["Deaths"].sum().sort_values(ascending=False).head(6).index
    base = base[base["Cause Label"].isin(top_causes)]

    education = base[(base["Education"] != "Selected Educations Total") & (base["SES Vulnerability"] == "Selected SES Vulnerability Total")]
    ses = base[(base["Education"] == "Selected Educations Total") & (base["SES Vulnerability"] != "Selected SES Vulnerability Total")]

    edu_table = education.pivot_table(index="Education Label", columns="Cause Label", values="Deaths", aggfunc="sum", fill_value=0)
    ses_table = ses.pivot_table(index="SES Label", columns="Cause Label", values="Deaths", aggfunc="sum", fill_value=0)
    ses_order = [x for x in ["Very Low", "Low", "Average", "High", "Very High"] if x in ses_table.index]
    ses_table = ses_table.reindex(ses_order)

    fig, axes = plt.subplots(2, 1, figsize=(16, 12))
    sns.heatmap(edu_table, annot=True, fmt=",.0f", cmap="Greens", linewidths=.5, ax=axes[0])
    axes[0].set_title("Deaths by Education Level and Cause")
    axes[0].set_xlabel("Cause of Death")
    axes[0].set_ylabel("Education Level")
    axes[0].tick_params(axis="x", rotation=25)

    sns.heatmap(ses_table, annot=True, fmt=",.0f", cmap="Oranges", linewidths=.5, ax=axes[1])
    axes[1].set_title("Deaths by SES Vulnerability and Cause")
    axes[1].set_xlabel("Cause of Death")
    axes[1].set_ylabel("SES Vulnerability")
    axes[1].tick_params(axis="x", rotation=25)
    save_figure(fig, "dashboard_social_determinants")

    px.imshow(edu_table, text_auto=True, color_continuous_scale="Greens", title="Deaths by Education Level and Cause", labels={"x":"Cause of Death", "y":"Education Level", "color":"Deaths"}).write_html("outputs/html/dashboard_education_by_cause.html")
    px.imshow(ses_table, text_auto=True, color_continuous_scale="Oranges", title="Deaths by SES Vulnerability and Cause", labels={"x":"Cause of Death", "y":"SES Vulnerability", "color":"Deaths"}).write_html("outputs/html/dashboard_ses_by_cause.html")


def graph_target_group_dashboard(social_data):
    # Graphs for race within education and SES patterns
    race_education = social_data[(social_data["Race"] != "Selected Races Total") & (social_data["Sex"] == "Selected Sexes Total") & (social_data["Education"] != "Selected Educations Total") & (social_data["SES Vulnerability"] == "Selected SES Vulnerability Total")]
    race_ses = social_data[(social_data["Race"] != "Selected Races Total") & (social_data["Sex"] == "Selected Sexes Total") & (social_data["Education"] == "Selected Educations Total") & (social_data["SES Vulnerability"] != "Selected SES Vulnerability Total")]

    edu = race_education.groupby(["Race Label", "Education Label"], as_index=False)["Deaths"].sum().sort_values("Deaths", ascending=False).head(10)
    ses = race_ses.groupby(["Race Label", "SES Label"], as_index=False)["Deaths"].sum().sort_values("Deaths", ascending=False).head(10)
    edu["Group"] = edu["Race Label"] + " | " + edu["Education Label"]
    ses["Group"] = ses["Race Label"] + " | " + ses["SES Label"]

    fig, axes = plt.subplots(1, 2, figsize=(20, 8))
    sns.barplot(data=edu, x="Deaths", y="Group", color=COLORS["blue"], ax=axes[0])
    axes[0].set_title("Top Race + Education Groups")
    axes[0].set_xlabel("Deaths")
    axes[0].set_ylabel("Group")
    label_bars(axes[0], "number")
    clean_axis(axes[0])

    sns.barplot(data=ses, x="Deaths", y="Group", color=COLORS["green"], ax=axes[1])
    axes[1].set_title("Top Race + SES Groups")
    axes[1].set_xlabel("Deaths")
    axes[1].set_ylabel("Group")
    label_bars(axes[1], "number")
    clean_axis(axes[1])
    save_figure(fig, "dashboard_target_groups")

    edu.to_csv("outputs/csv/top_race_education_groups.csv", index=False)
    ses.to_csv("outputs/csv/top_race_ses_groups.csv", index=False)


def graph_clean_sunbursts(social_data):
    # Interactive drilldowns kept shallow so labels stay readable
    education_base = social_data[(social_data["Race"] != "Selected Races Total") & (social_data["Sex"] == "Selected Sexes Total") & (social_data["Education"] != "Selected Educations Total") & (social_data["SES Vulnerability"] == "Selected SES Vulnerability Total") & (social_data["Deaths"] > 0)].copy()
    education = top_n_by_group(education_base, ["Source", "Geography", "Education Label", "Race Label"], n=3)
    fig = px.sunburst(education, path=["Source", "Geography", "Education Label", "Race Label", "Cause Label"], values="Deaths", title="Education, Race, and Cause Drilldown")
    fig.update_traces(maxdepth=3, textinfo="label+percent parent", insidetextorientation="horizontal")
    fig.update_layout(width=1200, height=850, uniformtext=dict(minsize=11, mode="hide"), font=dict(size=13))
    fig.write_html("outputs/html/drilldown_education_race_cause.html")

    ses_base = social_data[(social_data["Race"] != "Selected Races Total") & (social_data["Sex"] == "Selected Sexes Total") & (social_data["Education"] == "Selected Educations Total") & (social_data["SES Vulnerability"] != "Selected SES Vulnerability Total") & (social_data["Deaths"] > 0)].copy()
    ses = top_n_by_group(ses_base, ["Source", "Geography", "SES Label", "Race Label"], n=3)
    fig = px.sunburst(ses, path=["Source", "Geography", "SES Label", "Race Label", "Cause Label"], values="Deaths", title="SES, Race, and Cause Drilldown")
    fig.update_traces(maxdepth=3, textinfo="label+percent parent", insidetextorientation="horizontal")
    fig.update_layout(width=1200, height=850, uniformtext=dict(minsize=11, mode="hide"), font=dict(size=13))
    fig.write_html("outputs/html/drilldown_ses_race_cause.html")


def graph_market_dashboard(market_summary):
    if market_summary is None or market_summary.empty:
        return
    df = market_summary.copy()
    df["county"] = df["county"].astype(str).str.title()
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    sns.barplot(data=df, x="county", y="age65_population", palette=[COLORS["blue"], COLORS["green"]], ax=axes[0])
    axes[0].set_title("Population Age 65+")
    axes[0].set_xlabel("County")
    axes[0].set_ylabel("Residents")
    label_bars(axes[0], "number")
    clean_axis(axes[0])

    sns.barplot(data=df, x="county", y="known_enrollment", palette=[COLORS["blue"], COLORS["green"]], ax=axes[1])
    axes[1].set_title("Known Aetna MA Members")
    axes[1].set_xlabel("County")
    axes[1].set_ylabel("Members")
    label_bars(axes[1], "number")
    clean_axis(axes[1])

    sns.barplot(data=df, x="county", y="penetration_rate", palette=[COLORS["blue"], COLORS["green"]], ax=axes[2])
    axes[2].set_title("Aetna Penetration of Age 65+")
    axes[2].set_xlabel("County")
    axes[2].set_ylabel("Percent")
    label_bars(axes[2], "percent")
    clean_axis(axes[2])
    save_figure(fig, "dashboard_market_opportunity")

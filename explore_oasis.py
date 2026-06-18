import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

# Make output folder
os.makedirs("outputs", exist_ok=True)

# Files being used
files = {
    "Fulton": "Oasis Data Fulton County 2024.xlsx",
    "DeKalb": "Oasis Data Dekalb County 2024.xlsx"
}

all_data = []

# Read each file
for county, filename in files.items():
    df = pd.read_excel(filename, sheet_name="Data", skiprows=2)

    df = df.rename(columns={2024: "Deaths", "2024": "Deaths"})
    df = df[df["Deaths"] != "Deaths"]

    for col in ["Race", "Cause", "Age", "Sex"]:
        df[col] = df[col].astype(str).str.strip()

    df["Deaths"] = pd.to_numeric(df["Deaths"], errors="coerce")
    df["County"] = county

    all_data.append(df)

# Combine Fulton and DeKalb into one dataframe
data = pd.concat(all_data, ignore_index=True)
data = data.dropna(subset=["Deaths"])

print(data.head())
print(data["County"].value_counts())


# ==================================================
# Total deaths by county
# ==================================================

county_data = data[
    (data["Race"] == "Selected Races Total") &
    (data["Sex"] == "Selected Sexes Total") &
    (data["Age"] == "Selected Ages Total") &
    (data["Cause"] == "Selected Causes Total")
]

plt.figure(figsize=(7, 5))
sns.barplot(data=county_data, x="County", y="Deaths")
plt.title("Total Deaths by County")
plt.ylabel("Deaths")
plt.tight_layout()
plt.savefig("outputs/total_deaths_by_county.png")
plt.show()
plt.close()

county_data.to_csv("outputs/total_deaths_by_county.csv", index=False)


# ==================================================
# Age group data
# ==================================================

age_data = data[
    (data["Race"] == "Selected Races Total") &
    (data["Sex"] == "Selected Sexes Total") &
    (data["Cause"] == "Selected Causes Total") &
    (data["Age"] != "Selected Ages Total")
].copy()

age_data["Percent"] = (
    age_data["Deaths"] /
    age_data.groupby("County")["Deaths"].transform("sum")
) * 100

plt.figure(figsize=(12, 6))
sns.barplot(data=age_data, x="Age", y="Percent", hue="County")
plt.title("Deaths by Age Group")
plt.ylabel("Percent of Deaths")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig("outputs/deaths_by_age.png")
plt.show()
plt.close()

age_data.to_csv("outputs/deaths_by_age.csv", index=False)

# Interactive age chart
fig = px.bar(
    age_data,
    x="Age",
    y="Percent",
    color="County",
    barmode="group",
    title="Deaths by Age Group (%)"
)
fig.write_html("outputs/interactive_deaths_by_age.html")


# ==================================================
# Race data
# ==================================================

race_data = data[
    (data["Race"] != "Selected Races Total") &
    (data["Sex"] == "Selected Sexes Total") &
    (data["Age"] == "Selected Ages Total") &
    (data["Cause"] == "Selected Causes Total")
].copy()

race_data["Percent"] = (
    race_data["Deaths"] /
    race_data.groupby("County")["Deaths"].transform("sum")
) * 100

plt.figure(figsize=(12, 6))
sns.barplot(data=race_data, x="Race", y="Percent", hue="County")
plt.title("Deaths by Race")
plt.ylabel("Percent of Deaths")
plt.xticks(rotation=35, ha="right")
plt.tight_layout()
plt.savefig("outputs/deaths_by_race.png")
plt.show()
plt.close()

race_data.to_csv("outputs/deaths_by_race.csv", index=False)

# Pie chart by race for each county
for county in race_data["County"].unique():
    county_race = race_data[race_data["County"] == county]

    fig = px.pie(
        county_race,
        names="Race",
        values="Deaths",
        title=f"{county} Deaths by Race"
    )

    fig.write_html(f"outputs/{county.lower()}_race_pie.html")


# ==================================================
# Sex data
# ==================================================

sex_data = data[
    (data["Race"] == "Selected Races Total") &
    (data["Sex"] != "Selected Sexes Total") &
    (data["Age"] == "Selected Ages Total") &
    (data["Cause"] == "Selected Causes Total")
].copy()

sex_data["Percent"] = (
    sex_data["Deaths"] /
    sex_data.groupby("County")["Deaths"].transform("sum")
) * 100

plt.figure(figsize=(7, 5))
sns.barplot(data=sex_data, x="Sex", y="Percent", hue="County")
plt.title("Deaths by Sex")
plt.ylabel("Percent of Deaths")
plt.tight_layout()
plt.savefig("outputs/deaths_by_sex.png")
plt.show()
plt.close()

sex_data.to_csv("outputs/deaths_by_sex.csv", index=False)

# Pie chart by sex for each county
for county in sex_data["County"].unique():
    county_sex = sex_data[sex_data["County"] == county]

    fig = px.pie(
        county_sex,
        names="Sex",
        values="Deaths",
        title=f"{county} Deaths by Sex"
    )

    fig.write_html(f"outputs/{county.lower()}_sex_pie.html")


# ==================================================
# Cause of death data
# ==================================================

cause_data = data[
    (data["Race"] == "Selected Races Total") &
    (data["Sex"] == "Selected Sexes Total") &
    (data["Age"] == "Selected Ages Total") &
    (data["Cause"] != "Selected Causes Total")
].copy()

# Extra safety: remove anything with Total in the cause name
cause_data = cause_data[
    ~cause_data["Cause"].str.contains("Total", na=False)
]

cause_data["Percent"] = (
    cause_data["Deaths"] /
    cause_data.groupby("County")["Deaths"].transform("sum")
) * 100

top_causes = (
    cause_data.groupby("Cause")["Deaths"]
    .sum()
    .sort_values(ascending=False)
    .head(15)
    .index
)

top_cause_data = cause_data[cause_data["Cause"].isin(top_causes)]

plt.figure(figsize=(12, 8))
sns.barplot(data=top_cause_data, x="Percent", y="Cause", hue="County")
plt.title("Top Causes of Death by County")
plt.xlabel("Percent of Deaths")
plt.tight_layout()
plt.savefig("outputs/top_causes_by_county.png")
plt.show()
plt.close()

top_cause_data.to_csv("outputs/top_causes_by_county.csv", index=False)

# Interactive bar chart
fig = px.bar(
    top_cause_data,
    x="Percent",
    y="Cause",
    color="County",
    barmode="group",
    orientation="h",
    title="Top Causes of Death by County (%)"
)
fig.write_html("outputs/interactive_top_causes_by_county.html")


# ==================================================
# Pie charts for top causes by county
# ==================================================

for county in top_cause_data["County"].unique():
    county_causes = top_cause_data[top_cause_data["County"] == county]

    fig = px.pie(
        county_causes,
        names="Cause",
        values="Deaths",
        title=f"{county} Top Causes of Death"
    )

    fig.write_html(f"outputs/{county.lower()}_top_causes_pie.html")


# ==================================================
# Combined heatmap
# ==================================================

heatmap_data = top_cause_data.pivot(
    index="Cause",
    columns="County",
    values="Percent"
)

plt.figure(figsize=(8, 8))
sns.heatmap(heatmap_data, annot=True, fmt=".1f", cmap="Reds")
plt.title("Top Causes by County (%)")
plt.tight_layout()
plt.savefig("outputs/top_causes_heatmap_combined.png")
plt.show()
plt.close()


# ==================================================
# Separate heatmaps by county
# ==================================================

for county in top_cause_data["County"].unique():
    county_heatmap = top_cause_data[top_cause_data["County"] == county]

    county_heatmap = county_heatmap.sort_values("Percent", ascending=False)

    heatmap_table = county_heatmap.pivot_table(
        index="Cause",
        values="Percent"
    )

    plt.figure(figsize=(6, 8))
    sns.heatmap(
        heatmap_table,
        annot=True,
        fmt=".1f",
        cmap="Reds"
    )

    plt.title(f"{county} Top Causes (%)")
    plt.tight_layout()
    plt.savefig(f"outputs/{county.lower()}_top_causes_heatmap.png")
    plt.show()
    plt.close()


print("Done. All charts saved in the outputs folder.")
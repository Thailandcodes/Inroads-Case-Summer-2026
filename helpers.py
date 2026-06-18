import os
import shutil
import pandas as pd


# These are the three Excel files we are using
SOURCES = {
    "Georgia": "data/Georgia Rankable Causes Fulton and Dekalb 2024.xlsx",
    "OASIS": "data/Oasis Rankable Causes Fulton and Dekalb 2024.xlsx",
    "NCHS": "data/NCHS Rankable Causes Fulton and Dekalb 2024.xlsx"
}


# Ordered age groups so line graphs do not appear random
AGE_ORDER = [
    "<1 year",
    "1-4 years",
    "5-9 years",
    "10-14 years",
    "15-17 years",
    "18-19 years",
    "20-24 years",
    "25-29 years",
    "30-34 years",
    "35-39 years",
    "40-44 years",
    "45-49 years",
    "50-54 years",
    "55-59 years",
    "60-64 years",
    "65-69 years",
    "70-74 years",
    "75-79 years",
    "80-84 years",
    "85+ years"
]


def setup_folders():
    os.makedirs("outputs", exist_ok=True)
    os.makedirs("outputs/png", exist_ok=True)
    os.makedirs("outputs/html", exist_ok=True)
    os.makedirs("outputs/csv", exist_ok=True)
    os.makedirs("Share", exist_ok=True)


def load_all_data():
    all_data = []

    for source_name, file_path in SOURCES.items():
        df = pd.read_excel(
            file_path,
            sheet_name="Data",
            skiprows=2
        )

        # Rename year column safely
        df = df.rename(columns={2024: "Deaths", "2024": "Deaths"})

        # Remove repeated header rows
        df = df[df["Deaths"] != "Deaths"]

        # Clean text columns
        for col in ["Geography", "Race", "Cause", "Age", "Sex"]:
            df[col] = df[col].astype(str).str.strip()

        # Convert deaths into numbers
        df["Deaths"] = pd.to_numeric(df["Deaths"], errors="coerce")

        # Add source column
        df["Source"] = source_name

        all_data.append(df)

    data = pd.concat(all_data, ignore_index=True)

    # Keep only Fulton and DeKalb
    data = data[data["Geography"].isin(["Fulton", "DeKalb"])]

    # Remove blank death rows
    data = data.dropna(subset=["Deaths"])

    return data


def get_total_data(data):
    total_data = data[
        (data["Race"] == "Selected Races Total") &
        (data["Sex"] == "Selected Sexes Total") &
        (data["Age"] == "Selected Ages Total") &
        (data["Cause"] == "Selected Causes Total")
    ].copy()

    return total_data


def get_age_data(data):
    age_data = data[
        (data["Race"] == "Selected Races Total") &
        (data["Sex"] == "Selected Sexes Total") &
        (data["Cause"] == "Selected Causes Total") &
        (data["Age"] != "Selected Ages Total")
    ].copy()

    age_data["Percent"] = (
        age_data["Deaths"] /
        age_data.groupby(["Source", "Geography"])["Deaths"].transform("sum")
    ) * 100

    age_data["Age"] = pd.Categorical(
        age_data["Age"],
        categories=AGE_ORDER,
        ordered=True
    )

    age_data = age_data.sort_values("Age")

    age_data["Group"] = (
        age_data["Source"] + " - " + age_data["Geography"]
    )

    return age_data


def get_sex_data(data):
    sex_data = data[
        (data["Race"] == "Selected Races Total") &
        (data["Sex"] != "Selected Sexes Total") &
        (data["Age"] == "Selected Ages Total") &
        (data["Cause"] == "Selected Causes Total")
    ].copy()

    sex_data["Percent"] = (
        sex_data["Deaths"] /
        sex_data.groupby(["Source", "Geography"])["Deaths"].transform("sum")
    ) * 100

    sex_data["Group"] = (
        sex_data["Source"] + " - " + sex_data["Geography"]
    )

    return sex_data


def get_race_data(data):
    race_data = data[
        (data["Race"] != "Selected Races Total") &
        (data["Sex"] == "Selected Sexes Total") &
        (data["Age"] == "Selected Ages Total") &
        (data["Cause"] == "Selected Causes Total")
    ].copy()

    race_data["Percent"] = (
        race_data["Deaths"] /
        race_data.groupby(["Source", "Geography"])["Deaths"].transform("sum")
    ) * 100

    race_data["Group"] = (
        race_data["Source"] + " - " + race_data["Geography"]
    )

    return race_data


def get_cause_data(data):
    cause_data = data[
        (data["Race"] == "Selected Races Total") &
        (data["Sex"] == "Selected Sexes Total") &
        (data["Age"] == "Selected Ages Total") &
        (data["Cause"] != "Selected Causes Total")
    ].copy()

    # Extra cleanup to remove total rows
    cause_data = cause_data[
        ~cause_data["Cause"].str.contains("Total", na=False)
    ]

    cause_data["Percent"] = (
        cause_data["Deaths"] /
        cause_data.groupby(["Source", "Geography"])["Deaths"].transform("sum")
    ) * 100

    cause_data["Group"] = (
        cause_data["Source"] + " - " + cause_data["Geography"]
    )

    return cause_data


def save_csv(df, filename):
    df.to_csv(f"outputs/csv/{filename}.csv", index=False)


def package_project():
    # Clear old Share folder contents
    if os.path.exists("Share"):
        shutil.rmtree("Share")

    os.makedirs("Share", exist_ok=True)

    # Copy outputs into Share
    shutil.copytree("outputs", "Share/outputs")

    # Copy source files
    files_to_copy = [
        "explore_oasis.py",
        "helpers.py",
        "graphs.py",
        "requirements.txt",
        "README.md"
    ]

    for file in files_to_copy:
        if os.path.exists(file):
            shutil.copy(file, "Share")

    # Copy data folder
    if os.path.exists("data"):
        shutil.copytree("data", "Share/data")

    # Create zip
    shutil.make_archive(
        "AtlantaHealthEDA",
        "zip",
        "Share"
    )

    print("Share folder created.")
    print("AtlantaHealthEDA.zip created.")
import os
import shutil
from pathlib import Path
import pandas as pd


SOURCES = {
    "Georgia": "data/Georgia Rankable Causes Fulton and Dekalb 2024.xlsx",
    "OASIS": "data/Oasis Rankable Causes Fulton and Dekalb 2024.xlsx",
    "NCHS": "data/NCHS Rankable Causes Fulton and Dekalb 2024.xlsx"
}

SOCIAL_SOURCES = {
    "Georgia": "data/Georgia 2024.xlsx",
    "OASIS": "data/Oasis 2024.xlsx",
    "NCHS": "data/NCHS 2024.xlsx"
}

OUTPUT_FOLDERS = [
    "outputs",
    "outputs/png",
    "outputs/html",
    "outputs/csv",
    "outputs/report"
]


def setup_folders(clear_outputs=True):
    if clear_outputs and os.path.exists("outputs"):
        shutil.rmtree("outputs")

    for folder in OUTPUT_FOLDERS:
        os.makedirs(folder, exist_ok=True)


def clean_label(value):
    value = str(value)
    value = value.replace("_", " ")
    value = value.replace("Selected ", "")
    value = value.replace("Total", "")
    value = value.replace("  ", " ")
    return value.strip()


def format_number(value):
    return f"{float(value):,.0f}"


def format_percent(value):
    return f"{float(value):.1f}%"


def load_all_data():
    all_data = []

    for source_name, file_path in SOURCES.items():
        df = pd.read_excel(file_path, sheet_name="Data", skiprows=2)
        df = df.rename(columns={2024: "Deaths", "2024": "Deaths"})
        df = df[df["Deaths"] != "Deaths"]

        for col in ["Geography", "Race", "Cause", "Age", "Sex"]:
            df[col] = df[col].astype(str).str.strip()

        df["Deaths"] = pd.to_numeric(df["Deaths"], errors="coerce")
        df["Source"] = source_name
        all_data.append(df)

    data = pd.concat(all_data, ignore_index=True)
    data = data[data["Geography"].isin(["Fulton", "DeKalb"])]
    data = data.dropna(subset=["Deaths"])

    return data


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

    sex_data["Group"] = sex_data["Source"] + " - " + sex_data["Geography"]

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

    race_data["Group"] = race_data["Source"] + " - " + race_data["Geography"]

    return race_data


def get_cause_data(data):
    cause_data = data[
        (data["Race"] == "Selected Races Total") &
        (data["Sex"] == "Selected Sexes Total") &
        (data["Age"] == "Selected Ages Total") &
        (data["Cause"] != "Selected Causes Total")
    ].copy()

    cause_data = cause_data[~cause_data["Cause"].str.contains("Total", na=False)]

    cause_data["Percent"] = (
        cause_data["Deaths"] /
        cause_data.groupby(["Source", "Geography"])["Deaths"].transform("sum")
    ) * 100

    cause_data["Group"] = cause_data["Source"] + " - " + cause_data["Geography"]

    return cause_data


def load_social_data():
    all_data = []

    for source_name, file_path in SOCIAL_SOURCES.items():
        raw = pd.read_excel(file_path, sheet_name="Data", header=None)

        header_row = raw[
            raw.apply(
                lambda row: row.astype(str).str.contains("Geography").any(),
                axis=1
            )
        ].index[0]

        df = pd.read_excel(file_path, sheet_name="Data", skiprows=header_row)
        df = df.rename(columns={2024: "Deaths", "2024": "Deaths"})
        df = df[df["Deaths"] != "Deaths"]

        for col in [
            "Geography",
            "Race",
            "Cause",
            "Sex",
            "Education",
            "SES Vulnerability"
        ]:
            df[col] = df[col].astype(str).str.strip()

        df["Deaths"] = pd.to_numeric(df["Deaths"], errors="coerce")
        df["Source"] = source_name

        df = df[df["Geography"].isin(["Fulton", "DeKalb"])]
        df = df.dropna(subset=["Deaths"])

        all_data.append(df)

    return pd.concat(all_data, ignore_index=True)


def get_social_data(data):
    social = data[
        (data["Cause"] != "Selected Causes Total") &
        ~data["Cause"].str.contains("Total", na=False)
    ].copy()

    social["Group"] = social["Source"] + " - " + social["Geography"]

    return social


def save_csv(df, filename):
    safe_name = filename.replace(" ", "_")
    df.to_csv(f"outputs/csv/{safe_name}.csv", index=False)


def package_project():
    if os.path.exists("Share"):
        shutil.rmtree("Share")

    os.makedirs("Share", exist_ok=True)

    if os.path.exists("outputs"):
        shutil.copytree("outputs", "Share/outputs")

    files_to_copy = [
        "main.py",
        "helpers.py",
        "graphs.py",
        "style.py",
        "report.py",
        "analyze_aetna_ma_enrollment.py",
        "market_dashboards.py",
        "forecast.py",
        "requirements.txt",
        "README.md"
    ]

    for file in files_to_copy:
        if os.path.exists(file):
            shutil.copy(file, "Share")

    shutil.make_archive("AtlantaHealthEDA", "zip", "Share")
    print("Share folder and AtlantaHealthEDA.zip created.")

def get_age_cause_data(data):
    age_cause_data = data[
        (data["Race"] == "Selected Races Total") &
        (data["Sex"] == "Selected Sexes Total") &
        (data["Age"] != "Selected Ages Total") &
        (data["Cause"] != "Selected Causes Total")
    ].copy()

    age_cause_data = age_cause_data[
        ~age_cause_data["Cause"].str.contains("Total", na=False)
    ]

    return age_cause_data
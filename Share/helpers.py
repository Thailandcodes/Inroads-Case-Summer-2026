import os
import shutil
import pandas as pd


# These are the three Excel files we are using for the main mortality analysis
SOURCES = {
    "Georgia": "data/Georgia Rankable Causes Fulton and Dekalb 2024.xlsx",
    "OASIS": "data/Oasis Rankable Causes Fulton and Dekalb 2024.xlsx",
    "NCHS": "data/NCHS Rankable Causes Fulton and Dekalb 2024.xlsx"
}


# These are the three Excel files we are using for education and SES analysis
SOCIAL_SOURCES = {
    "Georgia": "data/Georgia 2024.xlsx",
    "OASIS": "data/Oasis 2024.xlsx",
    "NCHS": "data/NCHS 2024.xlsx"
}


def setup_folders():
    os.makedirs("outputs", exist_ok=True)
    os.makedirs("outputs/png", exist_ok=True)
    os.makedirs("outputs/html", exist_ok=True)
    os.makedirs("outputs/csv", exist_ok=True)


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


def load_social_data():
    all_data = []

    for source_name, file_path in SOCIAL_SOURCES.items():
        raw = pd.read_excel(file_path, sheet_name="Data", header=None)

        # Find the real header row
        header_row = raw[
            raw.apply(
                lambda row: row.astype(str).str.contains("Geography").any(),
                axis=1
            )
        ].index[0]

        df = pd.read_excel(
            file_path,
            sheet_name="Data",
            skiprows=header_row
        )

        df = df.rename(columns={2024: "Deaths", "2024": "Deaths"})

        # Remove repeated header rows
        df = df[df["Deaths"] != "Deaths"]

        # Clean text columns
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
    df.to_csv(f"outputs/csv/{filename}.csv", index=False)


def package_project():
    # Clear old Share folder contents
    if os.path.exists("Share"):
        shutil.rmtree("Share")

    os.makedirs("Share", exist_ok=True)
    os.makedirs("Share/outputs", exist_ok=True)
    os.makedirs("Share/data", exist_ok=True)

    # Only copy useful output folders
    output_folders = [
        "outputs/png",
        "outputs/html",
        "outputs/csv"
    ]

    for folder in output_folders:
        if os.path.exists(folder):
            shutil.copytree(
                folder,
                os.path.join("Share", folder)
            )

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

    # Copy only the data files used by the project
    data_files = list(SOURCES.values()) + list(SOCIAL_SOURCES.values())

    for file in data_files:
        if os.path.exists(file):
            shutil.copy(file, "Share/data")

    # Create zip
    shutil.make_archive(
        "AtlantaHealthEDA",
        "zip",
        "Share"
    )

    print("Share folder created.")
    print("AtlantaHealthEDA.zip created.")

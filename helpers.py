
from pathlib import Path
import shutil
import pandas as pd

SOURCE_FILES = {
    "Georgia": "data/Georgia Rankable Causes Fulton and Dekalb 2024.xlsx",
    "OASIS": "data/Oasis Rankable Causes Fulton and Dekalb 2024.xlsx",
    "NCHS": "data/NCHS Rankable Causes Fulton and Dekalb 2024.xlsx",
}

SOCIAL_FILES = {
    "Georgia": "data/Georgia 2024.xlsx",
    "OASIS": "data/Oasis 2024.xlsx",
    "NCHS": "data/NCHS 2024.xlsx",
}

OUTPUTS = {
    "png": Path("outputs/png"),
    "html": Path("outputs/html"),
    "csv": Path("outputs/csv"),
    "report": Path("outputs/report"),
}

COUNTIES = ["Fulton", "DeKalb"]


def setup_folders(clear_outputs=True):
    if clear_outputs and Path("outputs").exists():
        shutil.rmtree("outputs")
    for folder in OUTPUTS.values():
        folder.mkdir(parents=True, exist_ok=True)


def clean_label(value):
    text = str(value).strip()
    replacements = {
        "Selected Races Total": "All Races",
        "Selected Sexes Total": "All Sexes",
        "Selected Ages Total": "All Ages",
        "Selected Causes Total": "All Causes",
        "Selected Educations Total": "All Education Levels",
        "Selected SES Vulnerability Total": "All SES Levels",
        "Black or African-American": "Black",
        "American Indian or Alaskan Native": "American Indian/Alaska Native",
        "Native Hawaiian or Other Pacific Islander": "Pacific Islander",
        "Obstructive Heart Disease (incl. Heart Attack)": "Heart Disease",
        "Ischemic Heart and Vascular Disease": "Heart Disease",
        "All other Diseases of the Nervous System": "Nervous System Diseases",
        "All other Endocrine, Nutritional and Metabolic Diseases": "Endocrine/Metabolic Diseases",
        "All other Chronic Lower Respiratory Diseases": "Chronic Respiratory Diseases",
        "All other Mental and Behavioral Disorders": "Mental/Behavioral Disorders",
    }
    return replacements.get(text, text.replace("_", " "))


def clean_columns(df):
    df = df.copy()
    df.columns = [clean_label(c) for c in df.columns]
    return df


def save_csv(df, name):
    df.to_csv(OUTPUTS["csv"] / f"{name}.csv", index=False)


def load_mortality_data():
    frames = []
    for source, path in SOURCE_FILES.items():
        df = pd.read_excel(path, sheet_name="Data", skiprows=2)
        df = df.rename(columns={2024: "Deaths", "2024": "Deaths"})
        df = df[df["Deaths"] != "Deaths"].copy()
        for col in ["Geography", "Race", "Cause", "Age", "Sex"]:
            df[col] = df[col].astype(str).str.strip()
        df["Deaths"] = pd.to_numeric(df["Deaths"], errors="coerce")
        df["Source"] = source
        frames.append(df)
    data = pd.concat(frames, ignore_index=True)
    data = data[data["Geography"].isin(COUNTIES)].dropna(subset=["Deaths"])
    data["Race Label"] = data["Race"].apply(clean_label)
    data["Cause Label"] = data["Cause"].apply(clean_label)
    data["Sex Label"] = data["Sex"].apply(clean_label)
    data["Group"] = data["Source"] + " - " + data["Geography"]
    return data


def load_social_data():
    frames = []
    for source, path in SOCIAL_FILES.items():
        raw = pd.read_excel(path, sheet_name="Data", header=None)
        header_row = raw[raw.apply(lambda row: row.astype(str).str.contains("Geography").any(), axis=1)].index[0]
        df = pd.read_excel(path, sheet_name="Data", skiprows=header_row)
        df = df.rename(columns={2024: "Deaths", "2024": "Deaths"})
        df = df[df["Deaths"] != "Deaths"].copy()
        for col in ["Geography", "Race", "Cause", "Sex", "Education", "SES Vulnerability"]:
            df[col] = df[col].astype(str).str.strip()
        df["Deaths"] = pd.to_numeric(df["Deaths"], errors="coerce")
        df["Source"] = source
        frames.append(df)
    data = pd.concat(frames, ignore_index=True)
    data = data[data["Geography"].isin(COUNTIES)].dropna(subset=["Deaths"])
    data = data[(data["Cause"] != "Selected Causes Total") & ~data["Cause"].str.contains("Total", na=False)].copy()
    data["Race Label"] = data["Race"].apply(clean_label)
    data["Cause Label"] = data["Cause"].apply(clean_label)
    data["Education Label"] = data["Education"].apply(clean_label)
    data["SES Label"] = data["SES Vulnerability"].apply(clean_label)
    data["Group"] = data["Source"] + " - " + data["Geography"]
    return data


def get_sex_data(data):
    out = data[(data["Race"] == "Selected Races Total") & (data["Sex"] != "Selected Sexes Total") & (data["Age"] == "Selected Ages Total") & (data["Cause"] == "Selected Causes Total")].copy()
    out["Percent"] = out["Deaths"] / out.groupby(["Source", "Geography"])["Deaths"].transform("sum") * 100
    return out


def get_race_data(data):
    out = data[(data["Race"] != "Selected Races Total") & (data["Sex"] == "Selected Sexes Total") & (data["Age"] == "Selected Ages Total") & (data["Cause"] == "Selected Causes Total")].copy()
    out["Percent"] = out["Deaths"] / out.groupby(["Source", "Geography"])["Deaths"].transform("sum") * 100
    return out


def get_cause_data(data):
    out = data[(data["Race"] == "Selected Races Total") & (data["Sex"] == "Selected Sexes Total") & (data["Age"] == "Selected Ages Total") & (data["Cause"] != "Selected Causes Total")].copy()
    out = out[~out["Cause"].str.contains("Total", na=False)]
    out["Percent"] = out["Deaths"] / out.groupby(["Source", "Geography"])["Deaths"].transform("sum") * 100
    return out


def try_load_market_summary():
    path = Path("outputs/csv/market_opportunity_summary.csv")
    if path.exists():
        return pd.read_csv(path)
    return None

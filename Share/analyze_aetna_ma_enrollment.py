from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

from helpers import format_number
from style import PNG_DIR, setup_chart_style


setup_chart_style()

CSV_PATH = Path("data/CPSC_Enrollment_Info_2026_01.csv")
OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)
PNG_DIR.mkdir(parents=True, exist_ok=True)

PRIMARY = "#C7462D"
SECONDARY = "#E87561"
DARK = "#3B0D0C"


AETNA_CONTRACTS = [
    "H1608",
    "H2663",
    "H3312",
    "H5521",
    "H8597"
]

COUNTY_FIPS = {
    "13121": "FULTON",
    "13089": "DEKALB"
}


def read_cms_csv(csv_path: Path) -> pd.DataFrame:
    if not csv_path.exists():
        raise FileNotFoundError(f"Could not find file: {csv_path}")

    try:
        df = pd.read_csv(csv_path, dtype=str)
    except Exception:
        df = pd.read_csv(csv_path, dtype=str, sep="|")

    df.columns = [c.strip() for c in df.columns]
    return df


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    rename_map = {}

    for col in df.columns:
        clean = col.strip().lower().replace(" ", "_")

        if clean in ["contract_number", "contract_id", "contract"]:
            rename_map[col] = "Contract Number"
        elif clean in ["plan_id", "plan"]:
            rename_map[col] = "Plan ID"
        elif clean in ["fips_state_county_code", "fips_county_code"]:
            rename_map[col] = "FIPS Code"
        elif clean in ["enrollment", "enrolled"]:
            rename_map[col] = "Enrollment"

    df = df.rename(columns=rename_map)

    required = ["Contract Number", "FIPS Code", "Enrollment"]
    missing = [col for col in required if col not in df.columns]

    if missing:
        raise ValueError(
            f"Missing required columns: {missing}\n"
            f"Found columns: {list(df.columns)}"
        )

    return df


def filter_aetna_fulton_dekalb(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    for col in df.columns:
        df[col] = df[col].astype(str).str.strip()

    df["Contract"] = df["Contract Number"].str.upper()

    df["FIPS Clean"] = (
        df["FIPS Code"]
        .str.replace(".0", "", regex=False)
        .str.zfill(5)
    )

    df["County"] = df["FIPS Clean"].map(COUNTY_FIPS)

    filtered = df[
        (df["Contract"].isin(AETNA_CONTRACTS)) &
        (df["FIPS Clean"].isin(COUNTY_FIPS.keys()))
    ].copy()

    return filtered


def summarize_by_county(filtered: pd.DataFrame) -> pd.DataFrame:
    filtered = filtered.copy()

    filtered["Suppressed"] = filtered["Enrollment"].astype(str).str.strip().eq("*")
    filtered["Known Enrollment"] = pd.to_numeric(
        filtered["Enrollment"],
        errors="coerce"
    )

    summary = (
        filtered.groupby("County")
        .agg(
            **{
                "Known Enrollment": ("Known Enrollment", "sum"),
                "Suppressed Rows": ("Suppressed", "sum"),
                "Plan Rows": ("Enrollment", "count")
            }
        )
        .reset_index()
    )

    summary["Known Enrollment"] = summary["Known Enrollment"].fillna(0).astype(int)
    summary["Max Suppressed Enrollment"] = summary["Suppressed Rows"] * 10
    summary["Minimum Possible Total"] = summary["Known Enrollment"]
    summary["Maximum Possible Total"] = (
        summary["Known Enrollment"] + summary["Max Suppressed Enrollment"]
    )

    combined = pd.DataFrame([{
        "County": "COMBINED",
        "Known Enrollment": summary["Known Enrollment"].sum(),
        "Suppressed Rows": summary["Suppressed Rows"].sum(),
        "Plan Rows": summary["Plan Rows"].sum(),
        "Max Suppressed Enrollment": summary["Max Suppressed Enrollment"].sum(),
        "Minimum Possible Total": summary["Minimum Possible Total"].sum(),
        "Maximum Possible Total": summary["Maximum Possible Total"].sum()
    }])

    return pd.concat([summary, combined], ignore_index=True)


def make_chart(summary: pd.DataFrame):
    chart_df = summary[summary["County"] != "COMBINED"].copy()

    plt.figure(figsize=(8, 5))

    bars = plt.bar(
        chart_df["County"],
        chart_df["Known Enrollment"],
        color=[PRIMARY, SECONDARY],
        edgecolor=DARK,
        linewidth=0.7
    )

    plt.title(
        "Known Aetna Medicare Advantage Enrollment",
        fontweight="bold",
        color=DARK
    )
    plt.xlabel("County")
    plt.ylabel("Known Enrollment")

    for bar in bars:
        height = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            height,
            format_number(height),
            ha="center",
            va="bottom",
            color=DARK
        )

    plt.tight_layout()
    plt.savefig(PNG_DIR / "Aetna Enrollment by County.png", dpi=200)
    plt.close()


def run_aetna_analysis():
    df = read_cms_csv(CSV_PATH)
    df = normalize_columns(df)
    filtered = filter_aetna_fulton_dekalb(df)

    if filtered.empty:
        raise ValueError("No Aetna rows found for Fulton/DeKalb.")

    summary = summarize_by_county(filtered)

    filtered.to_csv(OUTPUT_DIR / "aetna_fulton_dekalb_plan_rows.csv", index=False)
    summary.to_csv(OUTPUT_DIR / "aetna_fulton_dekalb_county_totals.csv", index=False)

    make_chart(summary)

    return summary


def main():
    summary = run_aetna_analysis()
    print("\nAetna Medicare Advantage Enrollment: Fulton + DeKalb")
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
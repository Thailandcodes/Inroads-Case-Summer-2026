"""
Analyze CMS Medicare Advantage enrollment for Aetna Medicare in Fulton and DeKalb.

Input:
    data/cpsc_enrollment_2026_01.zip

Output:
    outputs/aetna_fulton_dekalb_plan_rows.csv
    outputs/aetna_fulton_dekalb_county_totals.csv
    outputs/aetna_fulton_dekalb_enrollment_chart.png

Notes:
    CMS uses "*" to suppress enrollment counts of 10 or fewer.
    This script does NOT make up suppressed values.
    It reports known numeric enrollment and counts suppressed rows separately.
"""

from pathlib import Path
import zipfile
import pandas as pd
import matplotlib.pyplot as plt


ZIP_PATH = Path("data/cpsc_enrollment_2026_01.zip")
OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)


TARGET_STATE = "GA"
TARGET_COUNTIES = ["FULTON", "DEKALB"]
AETNA_KEYWORD = "AETNA"


def find_data_file(zip_path: Path) -> str:
    """Find the main CSV/TXT enrollment file inside the CMS zip."""
    with zipfile.ZipFile(zip_path, "r") as z:
        files = [f for f in z.namelist() if f.lower().endswith((".csv", ".txt"))]
        if not files:
            raise FileNotFoundError("No CSV or TXT file found inside zip.")
        return files[0]


def read_cms_zip(zip_path: Path) -> pd.DataFrame:
    """Read CMS enrollment file from zip."""
    data_file = find_data_file(zip_path)

    with zipfile.ZipFile(zip_path, "r") as z:
        with z.open(data_file) as f:
            # CMS files are usually comma-delimited, but this fallback handles pipes/tabs too.
            try:
                df = pd.read_csv(f, dtype=str)
            except Exception:
                f.seek(0)
                df = pd.read_csv(f, dtype=str, sep="|")

    df.columns = [c.strip() for c in df.columns]
    return df


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Standardize likely CMS column names."""
    rename_map = {}

    for col in df.columns:
        clean = col.strip().lower().replace(" ", "_")

        if clean in ["state", "state_code"]:
            rename_map[col] = "state"
        elif clean in ["county", "county_name"]:
            rename_map[col] = "county"
        elif clean in ["contract_number", "contract_id", "contract"]:
            rename_map[col] = "contract_number"
        elif clean in ["plan_id", "plan"]:
            rename_map[col] = "plan_id"
        elif clean in ["organization_name", "org_name"]:
            rename_map[col] = "organization_name"
        elif clean in ["organization_marketing_name", "org_marketing_name"]:
            rename_map[col] = "organization_marketing_name"
        elif clean in ["plan_name"]:
            rename_map[col] = "plan_name"
        elif clean in ["enrollment", "enrolled"]:
            rename_map[col] = "enrollment"

    df = df.rename(columns=rename_map)

    required = ["state", "county", "enrollment"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns after normalization: {missing}. Found columns: {list(df.columns)}")

    return df


def filter_aetna_fulton_dekalb(df: pd.DataFrame) -> pd.DataFrame:
    """Filter to Georgia, Fulton/DeKalb, and Aetna rows."""
    df = df.copy()

    for col in df.columns:
        df[col] = df[col].astype(str).str.strip()

    df["state_upper"] = df["state"].str.upper()
    df["county_upper"] = df["county"].str.upper()

    name_cols = [
        c for c in ["organization_name", "organization_marketing_name", "plan_name"]
        if c in df.columns
    ]

    if not name_cols:
        raise ValueError(
            "No organization/plan name column found. "
            "Use the contract-level file with organization names, or add Aetna contract IDs manually."
        )

    combined_name = ""
    for col in name_cols:
        combined_name = combined_name + " " + df[col].fillna("").astype(str)

    df["combined_name_upper"] = combined_name.str.upper()

    filtered = df[
        (df["state_upper"] == TARGET_STATE)
        & (df["county_upper"].isin(TARGET_COUNTIES))
        & (df["combined_name_upper"].str.contains(AETNA_KEYWORD, na=False))
    ].copy()

    return filtered


def summarize_by_county(filtered: pd.DataFrame) -> pd.DataFrame:
    """Summarize known enrollment and suppressed rows by county."""
    filtered = filtered.copy()

    filtered["is_suppressed"] = filtered["enrollment"].astype(str).str.strip().eq("*")
    filtered["enrollment_numeric"] = pd.to_numeric(filtered["enrollment"], errors="coerce")

    summary = (
        filtered.groupby("county_upper")
        .agg(
            known_enrollment=("enrollment_numeric", "sum"),
            suppressed_rows=("is_suppressed", "sum"),
            total_plan_rows=("enrollment", "count"),
        )
        .reset_index()
        .rename(columns={"county_upper": "county"})
    )

    summary["known_enrollment"] = summary["known_enrollment"].astype(int)
    summary["max_possible_suppressed_enrollment"] = summary["suppressed_rows"] * 10
    summary["minimum_possible_total"] = summary["known_enrollment"]
    summary["maximum_possible_total"] = (
        summary["known_enrollment"] + summary["max_possible_suppressed_enrollment"]
    )

    combined = pd.DataFrame([{
        "county": "COMBINED",
        "known_enrollment": summary["known_enrollment"].sum(),
        "suppressed_rows": summary["suppressed_rows"].sum(),
        "total_plan_rows": summary["total_plan_rows"].sum(),
        "max_possible_suppressed_enrollment": summary["max_possible_suppressed_enrollment"].sum(),
        "minimum_possible_total": summary["minimum_possible_total"].sum(),
        "maximum_possible_total": summary["maximum_possible_total"].sum(),
    }])

    return pd.concat([summary, combined], ignore_index=True)


def make_chart(summary: pd.DataFrame) -> None:
    """Create bar chart for known enrollment by county."""
    chart_df = summary[summary["county"] != "COMBINED"].copy()

    plt.figure()
    plt.bar(chart_df["county"], chart_df["known_enrollment"])
    plt.title("Known Aetna Medicare Advantage Enrollment")
    plt.xlabel("County")
    plt.ylabel("Known Enrollment")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "aetna_fulton_dekalb_enrollment_chart.png", dpi=300)
    plt.close()


def main() -> None:
    df = read_cms_zip(ZIP_PATH)
    df = normalize_columns(df)

    filtered = filter_aetna_fulton_dekalb(df)

    if filtered.empty:
        raise ValueError(
            "No Aetna rows found for Fulton/DeKalb. "
            "Check whether this CMS file includes organization names or whether Aetna appears under another name."
        )

    summary = summarize_by_county(filtered)

    filtered.to_csv(OUTPUT_DIR / "aetna_fulton_dekalb_plan_rows.csv", index=False)
    summary.to_csv(OUTPUT_DIR / "aetna_fulton_dekalb_county_totals.csv", index=False)

    make_chart(summary)

    print("\nAetna Medicare Advantage Enrollment: Fulton + DeKalb")
    print(summary.to_string(index=False))
    print("\nFiles created in outputs/:")
    print("- aetna_fulton_dekalb_plan_rows.csv")
    print("- aetna_fulton_dekalb_county_totals.csv")
    print("- aetna_fulton_dekalb_enrollment_chart.png")


if __name__ == "__main__":
    main()

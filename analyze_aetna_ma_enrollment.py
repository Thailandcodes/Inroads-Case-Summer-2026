"""
Analyze CMS Medicare Advantage enrollment for Aetna Medicare in Fulton and DeKalb.

Input:
    data/CPSC_Enrollment_Info_2026_01.csv

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
import pandas as pd
import matplotlib.pyplot as plt


CSV_PATH = Path("data/CPSC_Enrollment_Info_2026_01.csv")
OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)


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
    """Read CMS enrollment CSV directly from the data folder."""
    if not csv_path.exists():
        raise FileNotFoundError(f"Could not find file: {csv_path}")

    try:
        df = pd.read_csv(csv_path, dtype=str)
    except Exception:
        df = pd.read_csv(csv_path, dtype=str, sep="|")

    df.columns = [c.strip() for c in df.columns]
    return df


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Standardize CMS column names."""
    rename_map = {}

    for col in df.columns:
        clean = col.strip().lower().replace(" ", "_")

        if clean in ["contract_number", "contract_id", "contract"]:
            rename_map[col] = "contract_number"
        elif clean in ["plan_id", "plan"]:
            rename_map[col] = "plan_id"
        elif clean in ["ssa_state_county_code", "ssa_county_code"]:
            rename_map[col] = "ssa_state_county_code"
        elif clean in ["fips_state_county_code", "fips_county_code"]:
            rename_map[col] = "fips_state_county_code"
        elif clean in ["state", "state_code"]:
            rename_map[col] = "state"
        elif clean in ["county", "county_name"]:
            rename_map[col] = "county"
        elif clean in ["enrollment", "enrolled"]:
            rename_map[col] = "enrollment"

    df = df.rename(columns=rename_map)

    required = [
        "contract_number",
        "fips_state_county_code",
        "enrollment"
    ]

    missing = [c for c in required if c not in df.columns]

    if missing:
        raise ValueError(
            f"Missing required columns after normalization: {missing}\n"
            f"Found columns: {list(df.columns)}"
        )

    return df


def filter_aetna_fulton_dekalb(df: pd.DataFrame) -> pd.DataFrame:
    """Filter to Fulton/DeKalb and Aetna contract IDs."""
    df = df.copy()

    for col in df.columns:
        df[col] = df[col].astype(str).str.strip()

    df["contract_upper"] = df["contract_number"].str.upper()

    df["fips_clean"] = (
        df["fips_state_county_code"]
        .str.replace(".0", "", regex=False)
        .str.zfill(5)
    )

    df["county_upper"] = df["fips_clean"].map(COUNTY_FIPS)

    filtered = df[
        (df["contract_upper"].isin(AETNA_CONTRACTS)) &
        (df["fips_clean"].isin(COUNTY_FIPS.keys()))
    ].copy()

    return filtered


def summarize_by_county(filtered: pd.DataFrame) -> pd.DataFrame:
    """Summarize known enrollment and suppressed rows by county."""
    filtered = filtered.copy()

    filtered["is_suppressed"] = (
        filtered["enrollment"]
        .astype(str)
        .str.strip()
        .eq("*")
    )

    filtered["enrollment_numeric"] = pd.to_numeric(
        filtered["enrollment"],
        errors="coerce"
    )

    summary = (
        filtered.groupby("county_upper")
        .agg(
            known_enrollment=("enrollment_numeric", "sum"),
            suppressed_rows=("is_suppressed", "sum"),
            total_plan_rows=("enrollment", "count")
        )
        .reset_index()
        .rename(columns={"county_upper": "county"})
    )

    summary["known_enrollment"] = summary["known_enrollment"].fillna(0).astype(int)
    summary["max_possible_suppressed_enrollment"] = summary["suppressed_rows"] * 10
    summary["minimum_possible_total"] = summary["known_enrollment"]
    summary["maximum_possible_total"] = (
        summary["known_enrollment"] +
        summary["max_possible_suppressed_enrollment"]
    )

    combined = pd.DataFrame([{
        "county": "COMBINED",
        "known_enrollment": summary["known_enrollment"].sum(),
        "suppressed_rows": summary["suppressed_rows"].sum(),
        "total_plan_rows": summary["total_plan_rows"].sum(),
        "max_possible_suppressed_enrollment": summary["max_possible_suppressed_enrollment"].sum(),
        "minimum_possible_total": summary["minimum_possible_total"].sum(),
        "maximum_possible_total": summary["maximum_possible_total"].sum()
    }])

    return pd.concat([summary, combined], ignore_index=True)


def make_chart(summary: pd.DataFrame) -> None:
    """Create simple bar chart for known enrollment by county."""
    chart_df = summary[summary["county"] != "COMBINED"].copy()

    plt.figure(figsize=(8, 5))

    bars = plt.bar(
        chart_df["county"],
        chart_df["known_enrollment"]
    )

    plt.title("Known Aetna Medicare Advantage Enrollment")
    plt.xlabel("County")
    plt.ylabel("Known Enrollment")

    for bar in bars:
        height = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            height,
            f"{int(height):,}",
            ha="center",
            va="bottom"
        )

    plt.tight_layout()
    plt.savefig(
        OUTPUT_DIR / "aetna_fulton_dekalb_enrollment_chart.png",
        dpi=200
    )
    plt.close()


def main() -> None:
    df = read_cms_csv(CSV_PATH)
    df = normalize_columns(df)

    filtered = filter_aetna_fulton_dekalb(df)

    if filtered.empty:
        raise ValueError(
            "No Aetna rows found for Fulton/DeKalb using the listed contract IDs. "
            "Check the AETNA_CONTRACTS list or inspect the contract numbers in the CSV."
        )

    summary = summarize_by_county(filtered)

    filtered.to_csv(
        OUTPUT_DIR / "aetna_fulton_dekalb_plan_rows.csv",
        index=False
    )

    summary.to_csv(
        OUTPUT_DIR / "aetna_fulton_dekalb_county_totals.csv",
        index=False
    )

    make_chart(summary)

    print("\nAetna Medicare Advantage Enrollment: Fulton + DeKalb")
    print(summary.to_string(index=False))

    print("\nFiles created in outputs/:")
    print("- aetna_fulton_dekalb_plan_rows.csv")
    print("- aetna_fulton_dekalb_county_totals.csv")
    print("- aetna_fulton_dekalb_enrollment_chart.png")


if __name__ == "__main__":
    main()
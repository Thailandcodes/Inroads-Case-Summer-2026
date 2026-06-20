"""
Creates market opportunity dashboards using:
1. ACS age 65+ population data
2. Aetna Medicare Advantage enrollment totals

Inputs:
    data/ACSST1Y2024.S0101-2026-06-20T225846.csv
    outputs/aetna_fulton_dekalb_county_totals.csv

Outputs:
    outputs/png/market_opportunity_dashboard.png
    outputs/png/aetna_age65_penetration_dashboard.png
    outputs/csv/market_opportunity_summary.csv
"""

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt


ACS_PATH = Path("data/ACSST1Y2024.S0101-2026-06-20T225846.csv")
AETNA_PATH = Path("outputs/aetna_fulton_dekalb_county_totals.csv")

OUTPUT_PNG = Path("outputs/png")
OUTPUT_CSV = Path("outputs/csv")

OUTPUT_PNG.mkdir(parents=True, exist_ok=True)
OUTPUT_CSV.mkdir(parents=True, exist_ok=True)


def clean_number(value):
    """Turns Census strings like '146,945' into numbers."""
    return int(str(value).replace(",", "").strip())


def load_age65_data():
    df = pd.read_csv(ACS_PATH)

    label_col = "Label (Grouping)"

    row = df[
        df[label_col]
        .astype(str)
        .str.contains("65 years and over", case=False, na=False)
    ].iloc[0]

    age65 = pd.DataFrame([
        {
            "county": "DEKALB",
            "age65_population": clean_number(
                row["DeKalb County, Georgia!!Total!!Estimate"]
            )
        },
        {
            "county": "FULTON",
            "age65_population": clean_number(
                row["Fulton County, Georgia!!Total!!Estimate"]
            )
        }
    ])

    return age65


def load_aetna_data():
    df = pd.read_csv(AETNA_PATH)

    df = df[df["county"] != "COMBINED"].copy()
    df["county"] = df["county"].str.upper()

    return df[["county", "known_enrollment"]]


def build_market_summary():
    age65 = load_age65_data()
    aetna = load_aetna_data()

    summary = age65.merge(aetna, on="county", how="left")
    summary["known_enrollment"] = summary["known_enrollment"].fillna(0).astype(int)

    summary["penetration_rate"] = (
        summary["known_enrollment"] / summary["age65_population"]
    ) * 100

    summary["remaining_opportunity"] = (
        summary["age65_population"] - summary["known_enrollment"]
    )

    summary.to_csv(
        OUTPUT_CSV / "market_opportunity_summary.csv",
        index=False
    )

    return summary


def add_value_labels(ax, values, percent=False):
    for i, value in enumerate(values):
        if percent:
            label = f"{value:.1f}%"
        else:
            label = f"{int(value):,}"

        ax.text(
            i,
            value,
            label,
            ha="center",
            va="bottom",
            fontsize=10
        )


def make_market_opportunity_dashboard(summary):
    fig, axes = plt.subplots(2, 2, figsize=(16, 10))

    fig.suptitle(
        "CVS / Aetna Medicare Market Opportunity",
        fontsize=20,
        fontweight="bold"
    )

    # --------------------------------------------------
    # Chart 1: Age 65+ population
    # --------------------------------------------------
    axes[0, 0].bar(
        summary["county"],
        summary["age65_population"]
    )

    axes[0, 0].set_title("Population Age 65+")
    axes[0, 0].set_ylabel("Residents")
    add_value_labels(axes[0, 0], summary["age65_population"])

    # --------------------------------------------------
    # Chart 2: Current Aetna enrollment
    # --------------------------------------------------
    axes[0, 1].bar(
        summary["county"],
        summary["known_enrollment"]
    )

    axes[0, 1].set_title("Known Aetna MA Enrollment")
    axes[0, 1].set_ylabel("Members")
    add_value_labels(axes[0, 1], summary["known_enrollment"])

    # --------------------------------------------------
    # Chart 3: Penetration rate
    # --------------------------------------------------
    axes[1, 0].bar(
        summary["county"],
        summary["penetration_rate"]
    )

    axes[1, 0].set_title("Aetna Penetration of Age 65+ Population")
    axes[1, 0].set_ylabel("Percent")
    add_value_labels(axes[1, 0], summary["penetration_rate"], percent=True)

    # --------------------------------------------------
    # Chart 4: Remaining opportunity
    # --------------------------------------------------
    axes[1, 1].bar(
        summary["county"],
        summary["remaining_opportunity"]
    )

    axes[1, 1].set_title("Remaining Age 65+ Opportunity")
    axes[1, 1].set_ylabel("Residents")
    add_value_labels(axes[1, 1], summary["remaining_opportunity"])

    plt.tight_layout()
    plt.savefig(
        OUTPUT_PNG / "market_opportunity_dashboard.png",
        dpi=200
    )
    plt.close()


def make_penetration_dashboard(summary):
    fig, ax = plt.subplots(figsize=(10, 6))

    ax.bar(
        summary["county"],
        summary["penetration_rate"]
    )

    ax.set_title(
        "Aetna Medicare Advantage Penetration",
        fontsize=16,
        fontweight="bold"
    )

    ax.set_ylabel("Aetna Members as % of Age 65+ Population")
    ax.set_xlabel("County")

    add_value_labels(ax, summary["penetration_rate"], percent=True)

    note = (
        "Note: Age 65+ population is used as a proxy for Medicare-age market size. "
        "Aetna enrollment reflects known enrollment only."
    )

    fig.text(
        0.5,
        0.01,
        note,
        ha="center",
        fontsize=9
    )

    plt.tight_layout(rect=[0, 0.05, 1, 1])
    plt.savefig(
        OUTPUT_PNG / "aetna_age65_penetration_dashboard.png",
        dpi=200
    )
    plt.close()


def main():
    summary = build_market_summary()

    make_market_opportunity_dashboard(summary)
    make_penetration_dashboard(summary)

    print("\nMarket opportunity summary:")
    print(summary.to_string(index=False))

    print("\nFiles created:")
    print("- outputs/csv/market_opportunity_summary.csv")
    print("- outputs/png/market_opportunity_dashboard.png")
    print("- outputs/png/aetna_age65_penetration_dashboard.png")


if __name__ == "__main__":
    main()
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

from helpers import format_number, format_percent
from style import PNG_DIR, CSV_DIR, setup_chart_style


setup_chart_style()

ACS_PATH = Path("data/ACSST1Y2024.S0101-2026-06-20T225846.csv")
AETNA_PATH = Path("outputs/aetna_fulton_dekalb_county_totals.csv")

PNG_DIR.mkdir(parents=True, exist_ok=True)
CSV_DIR.mkdir(parents=True, exist_ok=True)

PRIMARY = "#C7462D"
SECONDARY = "#E87561"
LIGHT = "#F3B2A6"
DARK = "#3B0D0C"
MUTED = "#8C3B2E"


def clean_number(value):
    return int(str(value).replace(",", "").strip())


def load_age65_data():
    df = pd.read_csv(ACS_PATH)

    label_col = "Label (Grouping)"
    row = df[
        df[label_col]
        .astype(str)
        .str.contains("65 years and over", case=False, na=False)
    ].iloc[0]

    return pd.DataFrame([
        {
            "County": "DEKALB",
            "Age 65+ Population": clean_number(
                row["DeKalb County, Georgia!!Total!!Estimate"]
            )
        },
        {
            "County": "FULTON",
            "Age 65+ Population": clean_number(
                row["Fulton County, Georgia!!Total!!Estimate"]
            )
        }
    ])


def load_aetna_data():
    df = pd.read_csv(AETNA_PATH)
    df = df[df["County"] != "COMBINED"].copy()
    df["County"] = df["County"].str.upper()
    return df[["County", "Known Enrollment"]]


def build_market_summary():
    age65 = load_age65_data()
    aetna = load_aetna_data()

    summary = age65.merge(aetna, on="County", how="left")
    summary["Known Enrollment"] = summary["Known Enrollment"].fillna(0).astype(int)

    summary["Penetration Rate"] = (
        summary["Known Enrollment"] / summary["Age 65+ Population"]
    ) * 100

    summary["Remaining Opportunity"] = (
        summary["Age 65+ Population"] - summary["Known Enrollment"]
    )

    summary.to_csv(CSV_DIR / "market_opportunity_summary.csv", index=False)

    return summary


def add_labels(ax, values, percent=False):
    for i, value in enumerate(values):
        label = format_percent(value) if percent else format_number(value)

        ax.text(
            i,
            value,
            label,
            ha="center",
            va="bottom",
            fontsize=10,
            color=DARK
        )


def make_market_opportunity_dashboard(summary):
    fig, axes = plt.subplots(2, 2, figsize=(16, 10))

    fig.suptitle(
        "CVS / Aetna Medicare Market Opportunity",
        fontsize=20,
        fontweight="bold",
        color=DARK
    )

    axes[0, 0].bar(
        summary["County"],
        summary["Age 65+ Population"],
        color=PRIMARY,
        edgecolor=DARK,
        linewidth=0.7
    )
    axes[0, 0].set_title("Population Age 65+")
    axes[0, 0].set_ylabel("Residents")
    add_labels(axes[0, 0], summary["Age 65+ Population"])

    axes[0, 1].bar(
        summary["County"],
        summary["Known Enrollment"],
        color=SECONDARY,
        edgecolor=DARK,
        linewidth=0.7
    )
    axes[0, 1].set_title("Known Aetna Medicare Advantage Enrollment")
    axes[0, 1].set_ylabel("Members")
    add_labels(axes[0, 1], summary["Known Enrollment"])

    axes[1, 0].bar(
        summary["County"],
        summary["Penetration Rate"],
        color=MUTED,
        edgecolor=DARK,
        linewidth=0.7
    )
    axes[1, 0].set_title("Aetna Penetration of Age 65+ Population")
    axes[1, 0].set_ylabel("Percent")
    add_labels(axes[1, 0], summary["Penetration Rate"], percent=True)

    axes[1, 1].bar(
        summary["County"],
        summary["Remaining Opportunity"],
        color=LIGHT,
        edgecolor=DARK,
        linewidth=0.7
    )
    axes[1, 1].set_title("Remaining Age 65+ Opportunity")
    axes[1, 1].set_ylabel("Residents")
    add_labels(axes[1, 1], summary["Remaining Opportunity"])

    plt.tight_layout()
    plt.savefig(PNG_DIR / "Market Opportunity Dashboard.png", dpi=200)
    plt.close()


def make_penetration_dashboard(summary):
    fig, ax = plt.subplots(figsize=(10, 6))

    ax.bar(
        summary["County"],
        summary["Penetration Rate"],
        color=PRIMARY,
        edgecolor=DARK,
        linewidth=0.7
    )

    ax.set_title(
        "Aetna Medicare Advantage Penetration",
        fontsize=16,
        fontweight="bold",
        color=DARK
    )
    ax.set_ylabel("Aetna Members as Percent of Age 65+ Population")
    ax.set_xlabel("County")

    add_labels(ax, summary["Penetration Rate"], percent=True)

    note = (
        "Note: Age 65+ population is used as a proxy for Medicare-age market size. "
        "Aetna enrollment reflects known enrollment only."
    )

    fig.text(0.5, 0.01, note, ha="center", fontsize=9, color=DARK)

    plt.tight_layout(rect=[0, 0.05, 1, 1])
    plt.savefig(PNG_DIR / "Aetna Age 65 Penetration Dashboard.png", dpi=200)
    plt.close()


def run_market_dashboards():
    summary = build_market_summary()
    make_market_opportunity_dashboard(summary)
    make_penetration_dashboard(summary)
    return summary


def main():
    summary = run_market_dashboards()
    print("\nMarket opportunity summary:")
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
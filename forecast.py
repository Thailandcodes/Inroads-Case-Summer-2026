"""
Forecast CVS Health Care Benefits segment revenue and estimate potential
incremental Aetna revenue from the age 65+ market opportunity.

Inputs:
    data/cvs_health_care_benefits_2023_2025.csv
    outputs/csv/market_opportunity_summary.csv

Outputs:
    outputs/health_care_benefits_revenue_forecast.csv
    outputs/incremental_aetna_market_opportunity.csv
    outputs/historical_health_care_benefits_revenue.png
    outputs/health_care_benefits_forecast_scenarios.png
    outputs/aetna_market_opportunity_revenue.png

Important:
    CVS segment revenue forecast uses CVS-reported revenue.
    Aetna market opportunity uses analyst assumptions.
"""

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt


DATA_PATH = Path("data/cvs_health_care_benefits_2023_2025.csv")
MARKET_PATH = Path("outputs/csv/market_opportunity_summary.csv")

OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)


REVENUE_PER_MEMBER = 5391
CAPTURE_RATES = [0.01, 0.03, 0.05]


def load_data(path: Path = DATA_PATH) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Could not find file: {path}")

    df = pd.read_csv(path)
    df.columns = df.columns.str.strip().str.lower()

    required = ["year", "total_revenues_millions"]
    missing = [col for col in required if col not in df.columns]

    if missing:
        raise ValueError(
            f"Missing required columns: {missing}\n"
            f"Found columns: {list(df.columns)}"
        )

    df["year"] = pd.to_numeric(df["year"], errors="coerce")
    df["total_revenues_millions"] = pd.to_numeric(
        df["total_revenues_millions"],
        errors="coerce"
    )

    df = df.dropna(subset=["year", "total_revenues_millions"])
    df = df.sort_values("year").reset_index(drop=True)

    df["total_revenue_yoy_growth"] = df["total_revenues_millions"].pct_change()

    return df


def calculate_cagr(start_value: float, end_value: float, periods: int) -> float:
    return (end_value / start_value) ** (1 / periods) - 1


def build_segment_revenue_forecast(
    df: pd.DataFrame,
    years_forward: int = 3
) -> pd.DataFrame:
    first = df.iloc[0]
    last = df.iloc[-1]

    cagr = calculate_cagr(
        first["total_revenues_millions"],
        last["total_revenues_millions"],
        int(last["year"] - first["year"])
    )

    scenarios = {
        "Conservative": cagr * 0.50,
        "Base": cagr,
        "Aggressive": cagr * 1.25
    }

    forecast_rows = []

    for scenario, growth_rate in scenarios.items():
        revenue = last["total_revenues_millions"]

        for i in range(1, years_forward + 1):
            year = int(last["year"] + i)
            revenue = revenue * (1 + growth_rate)

            forecast_rows.append({
                "scenario": scenario,
                "year": year,
                "growth_rate_used": growth_rate,
                "forecast_total_revenue_millions": revenue
            })

    return pd.DataFrame(forecast_rows)


def build_aetna_market_opportunity() -> pd.DataFrame:
    if not MARKET_PATH.exists():
        raise FileNotFoundError(
            f"Could not find {MARKET_PATH}. "
            "Run market_dashboards.py first."
        )

    market = pd.read_csv(MARKET_PATH)

    rows = []

    for _, county_row in market.iterrows():
        county = county_row["county"]
        remaining_opportunity = county_row["remaining_opportunity"]

        for rate in CAPTURE_RATES:
            potential_members = remaining_opportunity * rate
            incremental_revenue = potential_members * REVENUE_PER_MEMBER

            rows.append({
                "county": county,
                "capture_rate": rate,
                "potential_members": potential_members,
                "revenue_per_member_assumption": REVENUE_PER_MEMBER,
                "incremental_revenue": incremental_revenue,
                "incremental_revenue_millions": incremental_revenue / 1_000_000
            })

    opportunity = pd.DataFrame(rows)

    opportunity.to_csv(
        OUTPUT_DIR / "incremental_aetna_market_opportunity.csv",
        index=False
    )

    return opportunity


def add_line_labels(x_values, y_values, money=False):
    for x, y in zip(x_values, y_values):
        if money:
            label = f"${y:,.0f}M"
        else:
            label = f"{y:,.0f}"

        plt.text(
            x,
            y,
            label,
            ha="center",
            va="bottom",
            fontsize=9
        )


def make_charts(
    df: pd.DataFrame,
    forecast_df: pd.DataFrame,
    opportunity_df: pd.DataFrame
) -> None:
    # Historical CVS reported revenue
    plt.figure(figsize=(8, 5))

    plt.plot(
        df["year"],
        df["total_revenues_millions"],
        marker="o"
    )

    add_line_labels(
        df["year"],
        df["total_revenues_millions"],
        money=True
    )

    plt.title("CVS Health Care Benefits Revenue")
    plt.xlabel("Year")
    plt.ylabel("Revenue ($ millions)")
    plt.tight_layout()
    plt.savefig(
        OUTPUT_DIR / "historical_health_care_benefits_revenue.png",
        dpi=200
    )
    plt.close()

    # Forecast scenarios
    plt.figure(figsize=(9, 5))

    for scenario in forecast_df["scenario"].unique():
        subset = forecast_df[forecast_df["scenario"] == scenario]

        plt.plot(
            subset["year"],
            subset["forecast_total_revenue_millions"],
            marker="o",
            label=scenario
        )

        add_line_labels(
            subset["year"],
            subset["forecast_total_revenue_millions"],
            money=True
        )

    plt.title("Health Care Benefits Revenue Forecast Scenarios")
    plt.xlabel("Year")
    plt.ylabel("Forecast Revenue ($ millions)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(
        OUTPUT_DIR / "health_care_benefits_forecast_scenarios.png",
        dpi=200
    )
    plt.close()

    # Aetna market opportunity revenue
    chart_df = opportunity_df.copy()
    chart_df["capture_rate_label"] = (
        (chart_df["capture_rate"] * 100).astype(int).astype(str) + "%"
    )

    pivot = chart_df.pivot(
        index="county",
        columns="capture_rate_label",
        values="incremental_revenue_millions"
    )

    ax = pivot.plot(
        kind="bar",
        figsize=(10, 6)
    )

    plt.title("Potential Incremental Aetna Revenue from 65+ Opportunity")
    plt.xlabel("County")
    plt.ylabel("Incremental Revenue ($ millions)")
    plt.xticks(rotation=0)

    for container in ax.containers:
        ax.bar_label(
            container,
            fmt="$%.1fM",
            fontsize=9
        )

    plt.tight_layout()
    plt.savefig(
        OUTPUT_DIR / "aetna_market_opportunity_revenue.png",
        dpi=200
    )
    plt.close()


def main() -> None:
    df = load_data()
    forecast_df = build_segment_revenue_forecast(df)
    opportunity_df = build_aetna_market_opportunity()

    forecast_df.to_csv(
        OUTPUT_DIR / "health_care_benefits_revenue_forecast.csv",
        index=False
    )

    make_charts(df, forecast_df, opportunity_df)

    print("\nHistorical CVS Health Care Benefits data:")
    print(df.to_string(index=False))

    print("\nSegment revenue forecast:")
    print(forecast_df.to_string(index=False))

    print("\nPotential Aetna market opportunity:")
    print(opportunity_df.to_string(index=False))

    print("\nFiles created in outputs/:")
    print("- health_care_benefits_revenue_forecast.csv")
    print("- incremental_aetna_market_opportunity.csv")
    print("- historical_health_care_benefits_revenue.png")
    print("- health_care_benefits_forecast_scenarios.png")
    print("- aetna_market_opportunity_revenue.png")


if __name__ == "__main__":
    main()
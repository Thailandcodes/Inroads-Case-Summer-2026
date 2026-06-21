from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

from helpers import format_number
from style import PNG_DIR, OUTPUT_DIR, setup_chart_style


setup_chart_style()

DATA_PATH = Path("data/cvs_health_care_benefits_2023_2025.csv")
MARKET_PATH = Path("outputs/csv/market_opportunity_summary.csv")

OUTPUT_DIR.mkdir(exist_ok=True)
PNG_DIR.mkdir(parents=True, exist_ok=True)

REVENUE_PER_MEMBER = 5391
CAPTURE_RATES = [0.01, 0.03, 0.05]

CORAL_PRIMARY = "#C7462D"
CORAL_SECONDARY = "#E87561"
CORAL_LIGHT = "#F3B2A6"
BURGUNDY = "#3B0D0C"
BROWN_RED = "#8C3B2E"
GOLD_ACCENT = "#D6A55C"

FORECAST_COLORS = {
    "Conservative": CORAL_SECONDARY,
    "Base": CORAL_PRIMARY,
    "Aggressive": BURGUNDY
}

CAPTURE_COLORS = {
    "1%": CORAL_LIGHT,
    "3%": CORAL_PRIMARY,
    "5%": BURGUNDY
}


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


def build_segment_revenue_forecast(df: pd.DataFrame, years_forward: int = 3):
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
                "Scenario": scenario,
                "Year": year,
                "Growth Rate Used": growth_rate,
                "Forecast Total Revenue Millions": revenue
            })

    return pd.DataFrame(forecast_rows)


def build_aetna_market_opportunity():
    if not MARKET_PATH.exists():
        raise FileNotFoundError(
            f"Could not find {MARKET_PATH}. Run market_dashboards.py first."
        )

    market = pd.read_csv(MARKET_PATH)

    rows = []

    for _, county_row in market.iterrows():
        county = county_row["County"]
        remaining_opportunity = county_row["Remaining Opportunity"]

        for rate in CAPTURE_RATES:
            potential_members = remaining_opportunity * rate
            incremental_revenue = potential_members * REVENUE_PER_MEMBER

            rows.append({
                "County": county,
                "Capture Rate": rate,
                "Potential Members": potential_members,
                "Revenue Per Member Assumption": REVENUE_PER_MEMBER,
                "Incremental Revenue": incremental_revenue,
                "Incremental Revenue Millions": incremental_revenue / 1_000_000
            })

    opportunity = pd.DataFrame(rows)
    opportunity.to_csv(
        OUTPUT_DIR / "incremental_aetna_market_opportunity.csv",
        index=False
    )

    return opportunity


def add_line_labels(x_values, y_values, money=False):
    for x, y in zip(x_values, y_values):
        label = f"${y:,.0f}M" if money else format_number(y)

        plt.text(
            x,
            y,
            label,
            ha="center",
            va="bottom",
            fontsize=9,
            color=BURGUNDY
        )


def make_charts(df, forecast_df, opportunity_df):
    plt.figure(figsize=(8, 5))

    plt.plot(
        df["year"],
        df["total_revenues_millions"],
        marker="o",
        linewidth=2.8,
        color=CORAL_PRIMARY
    )

    add_line_labels(df["year"], df["total_revenues_millions"], money=True)

    plt.title("CVS Health Care Benefits Revenue")
    plt.xlabel("Year")
    plt.ylabel("Revenue ($ millions)")
    plt.tight_layout()
    plt.savefig(PNG_DIR / "CVS Health Care Benefits Revenue.png", dpi=200)
    plt.close()

    plt.figure(figsize=(9, 5))

    line_styles = {
        "Conservative": "--",
        "Base": "-",
        "Aggressive": "-."
    }

    for scenario in ["Conservative", "Base", "Aggressive"]:
        subset = forecast_df[forecast_df["Scenario"] == scenario]

        if subset.empty:
            continue

        plt.plot(
            subset["Year"],
            subset["Forecast Total Revenue Millions"],
            marker="o",
            linewidth=2.8,
            linestyle=line_styles.get(scenario, "-"),
            label=scenario,
            color=FORECAST_COLORS[scenario]
        )

        add_line_labels(
            subset["Year"],
            subset["Forecast Total Revenue Millions"],
            money=True
        )

    plt.title("Health Care Benefits Revenue Forecast Scenarios")
    plt.xlabel("Year")
    plt.ylabel("Forecast Revenue ($ millions)")
    plt.legend(title="Scenario")
    plt.tight_layout()
    plt.savefig(PNG_DIR / "CVS Revenue Forecast Scenarios.png", dpi=200)
    plt.close()

    chart_df = opportunity_df.copy()
    chart_df["Capture Rate Label"] = (
        (chart_df["Capture Rate"] * 100).astype(int).astype(str) + "%"
    )

    pivot = chart_df.pivot(
        index="County",
        columns="Capture Rate Label",
        values="Incremental Revenue Millions"
    )

    ordered_columns = ["1%", "3%", "5%"]
    pivot = pivot[[col for col in ordered_columns if col in pivot.columns]]

    bar_colors = [
        CAPTURE_COLORS[col]
        for col in pivot.columns
    ]

    ax = pivot.plot(
        kind="bar",
        figsize=(10, 6),
        color=bar_colors,
        edgecolor=BURGUNDY,
        linewidth=0.6
    )

    plt.title("Potential Incremental Aetna Revenue from Age 65+ Opportunity")
    plt.xlabel("County")
    plt.ylabel("Incremental Revenue ($ millions)")
    plt.xticks(rotation=0)
    plt.legend(title="Capture Rate")

    for container in ax.containers:
        ax.bar_label(container, fmt="$%.1fM", fontsize=9, color=BURGUNDY)

    plt.tight_layout()
    plt.savefig(PNG_DIR / "Aetna Market Opportunity Revenue.png", dpi=200)
    plt.close()


def run_forecast():
    df = load_data()
    forecast_df = build_segment_revenue_forecast(df)
    opportunity_df = build_aetna_market_opportunity()

    forecast_df.to_csv(
        OUTPUT_DIR / "health_care_benefits_revenue_forecast.csv",
        index=False
    )

    make_charts(df, forecast_df, opportunity_df)

    return {
        "historical": df,
        "forecast": forecast_df,
        "opportunity": opportunity_df
    }


def main():
    forecast_summary = run_forecast()

    print("\nHistorical CVS Health Care Benefits data:")
    print(forecast_summary["historical"].to_string(index=False))

    print("\nSegment revenue forecast:")
    print(forecast_summary["forecast"].to_string(index=False))

    print("\nPotential Aetna market opportunity:")
    print(forecast_summary["opportunity"].to_string(index=False))


if __name__ == "__main__":
    main()
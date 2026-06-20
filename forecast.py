"""
Forecast CVS Health Care Benefits segment revenue using CVS-reported data.

Input:
    data/cvs_health_care_benefits_2023_2025.csv

Source:
    CVS Health 2025 Annual Report, page 70, Health Care Benefits Segment table.

Important:
    This script forecasts segment revenue from reported segment revenue.
    It does NOT claim revenue is directly caused by members unless you add a
    clearly labeled analyst assumption for revenue per converted member.
"""

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt


DATA_PATH = Path("data/cvs_health_care_benefits_2023_2025.csv")
OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)


def load_data(path: Path = DATA_PATH) -> pd.DataFrame:
    df = pd.read_csv(path)
    df = df.sort_values("year").reset_index(drop=True)

    # Year-over-year growth from CVS-reported total revenue
    df["total_revenue_yoy_growth"] = df["total_revenues_millions"].pct_change()

    return df


def calculate_cagr(start_value: float, end_value: float, periods: int) -> float:
    return (end_value / start_value) ** (1 / periods) - 1


def build_segment_revenue_forecast(df: pd.DataFrame, years_forward: int = 3) -> pd.DataFrame:
    """
    Builds conservative/base/aggressive forecasts using historical growth.

    Conservative = half of historical CAGR
    Base = historical CAGR
    Aggressive = 1.25x historical CAGR
    """
    first = df.iloc[0]
    last = df.iloc[-1]

    cagr = calculate_cagr(
        first["total_revenues_millions"],
        last["total_revenues_millions"],
        int(last["year"] - first["year"])
    )

    scenarios = {
        "conservative": cagr * 0.50,
        "base": cagr,
        "aggressive": cagr * 1.25,
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
                "forecast_total_revenue_millions": revenue,
            })

    return pd.DataFrame(forecast_rows)


def build_incremental_enrollment_forecast(
    revenue_per_member: float,
    residents_reached: int = 10000,
    screening_rate: float = 0.40,
    high_risk_rate: float = 0.50,
    referral_acceptance_rate: float = 0.60,
    oak_street_conversion_rate: float = 0.75,
    aetna_enrollment_rate: float = 0.40,
) -> pd.DataFrame:
    """
    Optional funnel model for your project.

    revenue_per_member is an analyst assumption.
    Do not treat it as a CVS-reported figure unless you cite the exact source.
    """
    screened = residents_reached * screening_rate
    high_risk = screened * high_risk_rate
    accepted_referral = high_risk * referral_acceptance_rate
    oak_street_patients = accepted_referral * oak_street_conversion_rate
    new_aetna_members = oak_street_patients * aetna_enrollment_rate
    incremental_revenue = new_aetna_members * revenue_per_member

    return pd.DataFrame([{
        "residents_reached": residents_reached,
        "screened": screened,
        "high_risk_identified": high_risk,
        "accepted_referral": accepted_referral,
        "oak_street_patients": oak_street_patients,
        "new_aetna_members": new_aetna_members,
        "revenue_per_member_assumption": revenue_per_member,
        "incremental_annual_revenue": incremental_revenue,
    }])


def make_charts(df: pd.DataFrame, forecast_df: pd.DataFrame) -> None:
    plt.figure()
    plt.plot(df["year"], df["total_revenues_millions"], marker="o")
    plt.title("CVS Health Care Benefits Revenue")
    plt.xlabel("Year")
    plt.ylabel("Revenue ($ millions)")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "historical_health_care_benefits_revenue.png", dpi=300)
    plt.close()

    plt.figure()
    for scenario in forecast_df["scenario"].unique():
        subset = forecast_df[forecast_df["scenario"] == scenario]
        plt.plot(
            subset["year"],
            subset["forecast_total_revenue_millions"],
            marker="o",
            label=scenario.title()
        )
    plt.title("Health Care Benefits Revenue Forecast Scenarios")
    plt.xlabel("Year")
    plt.ylabel("Forecast Revenue ($ millions)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "health_care_benefits_forecast_scenarios.png", dpi=300)
    plt.close()


def main() -> None:
    df = load_data()
    forecast_df = build_segment_revenue_forecast(df)

    forecast_df.to_csv(OUTPUT_DIR / "health_care_benefits_revenue_forecast.csv", index=False)

    # Optional project funnel example.
    # Replace 5391 with your final defensible revenue-per-member assumption,
    # or remove this section if you only want the segment revenue forecast.
    funnel_df = build_incremental_enrollment_forecast(revenue_per_member=5391)
    funnel_df.to_csv(OUTPUT_DIR / "incremental_enrollment_forecast_example.csv", index=False)

    make_charts(df, forecast_df)

    print("Historical data:")
    print(df)

    print("\nSegment revenue forecast:")
    print(forecast_df)

    print("\nOptional incremental enrollment funnel:")
    print(funnel_df)


if __name__ == "__main__":
    main()

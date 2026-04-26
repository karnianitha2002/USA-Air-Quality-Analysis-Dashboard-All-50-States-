"""Generate a synthetic cleaned AQI dataset for demo and dashboard testing."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


STATE_CITY_BASELINES = [
    ("Alabama", "Birmingham", 68),
    ("Alaska", "Anchorage", 34),
    ("Arizona", "Phoenix", 86),
    ("Arkansas", "Little Rock", 63),
    ("California", "Los Angeles", 104),
    ("Colorado", "Denver", 59),
    ("Connecticut", "Hartford", 48),
    ("Delaware", "Wilmington", 52),
    ("Florida", "Miami", 66),
    ("Georgia", "Atlanta", 74),
    ("Hawaii", "Honolulu", 29),
    ("Idaho", "Boise", 43),
    ("Illinois", "Chicago", 77),
    ("Indiana", "Indianapolis", 72),
    ("Iowa", "Des Moines", 49),
    ("Kansas", "Wichita", 58),
    ("Kentucky", "Louisville", 69),
    ("Louisiana", "Baton Rouge", 81),
    ("Maine", "Portland", 31),
    ("Maryland", "Baltimore", 61),
    ("Massachusetts", "Boston", 47),
    ("Michigan", "Detroit", 65),
    ("Minnesota", "Minneapolis", 45),
    ("Mississippi", "Jackson", 71),
    ("Missouri", "St. Louis", 73),
    ("Montana", "Billings", 39),
    ("Nebraska", "Omaha", 50),
    ("Nevada", "Las Vegas", 78),
    ("New Hampshire", "Manchester", 35),
    ("New Jersey", "Newark", 67),
    ("New Mexico", "Albuquerque", 54),
    ("New York", "New York City", 62),
    ("North Carolina", "Charlotte", 64),
    ("North Dakota", "Fargo", 37),
    ("Ohio", "Columbus", 70),
    ("Oklahoma", "Oklahoma City", 75),
    ("Oregon", "Portland", 41),
    ("Pennsylvania", "Philadelphia", 68),
    ("Rhode Island", "Providence", 44),
    ("South Carolina", "Charleston", 60),
    ("South Dakota", "Sioux Falls", 38),
    ("Tennessee", "Nashville", 67),
    ("Texas", "Houston", 88),
    ("Utah", "Salt Lake City", 64),
    ("Vermont", "Burlington", 28),
    ("Virginia", "Richmond", 57),
    ("Washington", "Seattle", 40),
    ("West Virginia", "Charleston", 62),
    ("Wisconsin", "Milwaukee", 51),
    ("Wyoming", "Cheyenne", 33),
]

MONTHLY_ADJUSTMENTS = [4, 2, 6, 8, 10, 13, 15, 12, 7, 5, 3, 1]


def build_sample_dataframe() -> pd.DataFrame:
    rows = []

    for state_index, (state, city, baseline_aqi) in enumerate(STATE_CITY_BASELINES):
        for month_index, seasonal_boost in enumerate(MONTHLY_ADJUSTMENTS, start=1):
            aqi = baseline_aqi + seasonal_boost + (state_index % 5) - 2
            pm25 = round(max(4.0, aqi * 0.28 + (month_index % 3) * 0.8), 2)
            pm10 = round(max(8.0, aqi * 0.42 + (state_index % 4) * 1.1), 2)
            no2 = round(max(3.0, aqi * 0.18 + (month_index % 4) * 0.6), 2)
            so2 = round(max(1.0, aqi * 0.08 + (state_index % 3) * 0.4), 2)
            co = round(max(0.2, aqi * 0.012 + (month_index % 2) * 0.03), 2)
            o3 = round(max(6.0, aqi * 0.24 + (month_index % 5) * 0.7), 2)

            rows.append(
                {
                    "State": state,
                    "City": city,
                    "Date": f"2024-{month_index:02d}-15",
                    "AQI": int(aqi),
                    "PM2.5": pm25,
                    "PM10": pm10,
                    "NO2": no2,
                    "SO2": so2,
                    "CO": co,
                    "O3": o3,
                }
            )

    return pd.DataFrame(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a synthetic cleaned AQI CSV for all 50 U.S. states.")
    parser.add_argument(
        "--output",
        default="data/processed/sample_aqi_2024_cleaned.csv",
        help="Path for the generated sample CSV.",
    )
    args = parser.parse_args()

    output_path = Path(args.output).expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    df = build_sample_dataframe()
    df.to_csv(output_path, index=False)

    print(f"Sample dataset saved to: {output_path}")
    print(f"Rows: {len(df)}")
    print(f"States: {df['State'].nunique()}")


if __name__ == "__main__":
    main()

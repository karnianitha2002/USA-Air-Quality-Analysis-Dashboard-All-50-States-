"""Phase 2 data cleaning pipeline for the AQI dashboard project."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
from typing import Dict, Iterable, List, Tuple

import pandas as pd


CANONICAL_COLUMN_ALIASES = {
    "State": {"state", "state_name", "province_state", "province"},
    "City": {"city", "city_name"},
    "Date": {"date", "observation_date", "report_date", "local_date"},
    "AQI": {"aqi", "air_quality_index", "us_aqi", "aqi_value"},
    "PM2.5": {"pm25", "pm2_5", "pm2.5", "pm_2_5", "pm25_value"},
    "PM10": {"pm10", "pm10_value"},
    "NO2": {"no2", "nitrogen_dioxide"},
    "SO2": {"so2", "sulfur_dioxide", "sulphur_dioxide"},
    "CO": {"co", "carbon_monoxide"},
    "O3": {"o3", "ozone"},
}

RETAINED_COLUMNS = ["State", "City", "Date", "AQI", "PM2.5", "PM10", "NO2", "SO2", "CO", "O3"]
NUMERIC_COLUMNS = ["AQI", "PM2.5", "PM10", "NO2", "SO2", "CO", "O3"]

STATE_NAME_MAP = {
    "AL": "Alabama",
    "AK": "Alaska",
    "AZ": "Arizona",
    "AR": "Arkansas",
    "CA": "California",
    "CO": "Colorado",
    "CT": "Connecticut",
    "DE": "Delaware",
    "FL": "Florida",
    "GA": "Georgia",
    "HI": "Hawaii",
    "ID": "Idaho",
    "IL": "Illinois",
    "IN": "Indiana",
    "IA": "Iowa",
    "KS": "Kansas",
    "KY": "Kentucky",
    "LA": "Louisiana",
    "ME": "Maine",
    "MD": "Maryland",
    "MA": "Massachusetts",
    "MI": "Michigan",
    "MN": "Minnesota",
    "MS": "Mississippi",
    "MO": "Missouri",
    "MT": "Montana",
    "NE": "Nebraska",
    "NV": "Nevada",
    "NH": "New Hampshire",
    "NJ": "New Jersey",
    "NM": "New Mexico",
    "NY": "New York",
    "NC": "North Carolina",
    "ND": "North Dakota",
    "OH": "Ohio",
    "OK": "Oklahoma",
    "OR": "Oregon",
    "PA": "Pennsylvania",
    "RI": "Rhode Island",
    "SC": "South Carolina",
    "SD": "South Dakota",
    "TN": "Tennessee",
    "TX": "Texas",
    "UT": "Utah",
    "VT": "Vermont",
    "VA": "Virginia",
    "WA": "Washington",
    "WV": "West Virginia",
    "WI": "Wisconsin",
    "WY": "Wyoming",
    "DC": "District of Columbia",
}

FULL_STATE_NAMES = {name.upper(): name for name in STATE_NAME_MAP.values()}


def _normalize_header(header: str) -> str:
    """Collapse casing and separators so similar source columns map together."""
    return re.sub(r"[^a-z0-9]+", "_", header.strip().lower()).strip("_")


def _build_rename_map(columns: Iterable[str]) -> Dict[str, str]:
    normalized_to_original = {_normalize_header(column): column for column in columns}
    rename_map: Dict[str, str] = {}

    for canonical, aliases in CANONICAL_COLUMN_ALIASES.items():
        for alias in aliases:
            original = normalized_to_original.get(alias)
            if original:
                rename_map[original] = canonical
                break

    return rename_map


def _standardize_state_name(value: object) -> object:
    if pd.isna(value):
        return value

    cleaned = str(value).strip()
    if not cleaned:
        return pd.NA

    compact = re.sub(r"\s+", " ", cleaned).upper()

    if compact in STATE_NAME_MAP:
        return STATE_NAME_MAP[compact]

    if compact in FULL_STATE_NAMES:
        return FULL_STATE_NAMES[compact]

    return re.sub(r"\s+", " ", cleaned).title()


def clean_air_quality_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, object]]:
    """Return a cleaned AQI dataframe plus a compact quality summary."""
    original_row_count = len(df)
    renamed_df = df.rename(columns=_build_rename_map(df.columns)).copy()

    missing_required = [column for column in ["State", "AQI"] if column not in renamed_df.columns]
    if missing_required:
        raise ValueError(
            "Missing required columns after normalization: "
            + ", ".join(missing_required)
        )

    retained_columns = [column for column in RETAINED_COLUMNS if column in renamed_df.columns]
    cleaned_df = renamed_df[retained_columns].copy()

    cleaned_df["State"] = cleaned_df["State"].apply(_standardize_state_name)

    if "City" in cleaned_df.columns:
        cleaned_df["City"] = cleaned_df["City"].astype("string").str.strip()
        cleaned_df["City"] = cleaned_df["City"].replace({"": pd.NA, "nan": pd.NA, "None": pd.NA})

    for column in NUMERIC_COLUMNS:
        if column in cleaned_df.columns:
            cleaned_df[column] = pd.to_numeric(cleaned_df[column], errors="coerce")

    if "Date" in cleaned_df.columns:
        cleaned_df["Date"] = pd.to_datetime(cleaned_df["Date"], errors="coerce")

    before_required_filter = len(cleaned_df)
    cleaned_df = cleaned_df.dropna(subset=["State", "AQI"])
    dropped_missing_core = before_required_filter - len(cleaned_df)

    before_dedup = len(cleaned_df)
    cleaned_df = cleaned_df.drop_duplicates().reset_index(drop=True)
    duplicates_removed = before_dedup - len(cleaned_df)

    summary: Dict[str, object] = {
        "input_rows": int(original_row_count),
        "output_rows": int(len(cleaned_df)),
        "dropped_missing_state_or_aqi": int(dropped_missing_core),
        "duplicates_removed": int(duplicates_removed),
        "columns_retained": retained_columns,
        "states_found": int(cleaned_df["State"].nunique()),
    }

    if "Date" in cleaned_df.columns:
        valid_dates = cleaned_df["Date"].dropna()
        summary["valid_date_rows"] = int(valid_dates.shape[0])
        summary["date_min"] = valid_dates.min().strftime("%Y-%m-%d") if not valid_dates.empty else None
        summary["date_max"] = valid_dates.max().strftime("%Y-%m-%d") if not valid_dates.empty else None

    return cleaned_df, summary


def process_csv(input_path: Path, output_path: Path, summary_path: Path | None = None) -> Dict[str, object]:
    df = pd.read_csv(input_path)
    cleaned_df, summary = clean_air_quality_data(df)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    cleaned_df.to_csv(output_path, index=False)

    if summary_path is not None:
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    return summary


def _default_output_paths(input_path: Path) -> Tuple[Path, Path]:
    root = Path(__file__).resolve().parent.parent
    file_stem = input_path.stem
    output_path = root / "data" / "processed" / f"{file_stem}_cleaned.csv"
    summary_path = root / "report" / f"{file_stem}_cleaning_summary.json"
    return output_path, summary_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Clean a raw U.S. air quality CSV file.")
    parser.add_argument("--input", required=True, help="Path to the raw CSV file.")
    parser.add_argument("--output", help="Path for the cleaned CSV output.")
    parser.add_argument("--summary", help="Optional path for a JSON cleaning summary.")
    args = parser.parse_args()

    input_path = Path(args.input).expanduser().resolve()
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    default_output_path, default_summary_path = _default_output_paths(input_path)
    output_path = Path(args.output).expanduser().resolve() if args.output else default_output_path
    summary_path = Path(args.summary).expanduser().resolve() if args.summary else default_summary_path

    summary = process_csv(input_path, output_path, summary_path)

    print(f"Cleaned file saved to: {output_path}")
    print(f"Summary saved to: {summary_path}")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

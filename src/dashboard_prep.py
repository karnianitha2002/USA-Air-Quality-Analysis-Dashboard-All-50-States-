"""Phase 4 packaging utilities for Tableau and portfolio deliverables."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd

from src.aqi_analysis import AQI_CATEGORY_BINS, AQI_CATEGORY_LABELS


STATE_LOOKUP: Dict[str, Tuple[str, str]] = {
    "Alabama": ("AL", "South"),
    "Alaska": ("AK", "West"),
    "Arizona": ("AZ", "West"),
    "Arkansas": ("AR", "South"),
    "California": ("CA", "West"),
    "Colorado": ("CO", "West"),
    "Connecticut": ("CT", "Northeast"),
    "Delaware": ("DE", "South"),
    "Florida": ("FL", "South"),
    "Georgia": ("GA", "South"),
    "Hawaii": ("HI", "West"),
    "Idaho": ("ID", "West"),
    "Illinois": ("IL", "Midwest"),
    "Indiana": ("IN", "Midwest"),
    "Iowa": ("IA", "Midwest"),
    "Kansas": ("KS", "Midwest"),
    "Kentucky": ("KY", "South"),
    "Louisiana": ("LA", "South"),
    "Maine": ("ME", "Northeast"),
    "Maryland": ("MD", "South"),
    "Massachusetts": ("MA", "Northeast"),
    "Michigan": ("MI", "Midwest"),
    "Minnesota": ("MN", "Midwest"),
    "Mississippi": ("MS", "South"),
    "Missouri": ("MO", "Midwest"),
    "Montana": ("MT", "West"),
    "Nebraska": ("NE", "Midwest"),
    "Nevada": ("NV", "West"),
    "New Hampshire": ("NH", "Northeast"),
    "New Jersey": ("NJ", "Northeast"),
    "New Mexico": ("NM", "West"),
    "New York": ("NY", "Northeast"),
    "North Carolina": ("NC", "South"),
    "North Dakota": ("ND", "Midwest"),
    "Ohio": ("OH", "Midwest"),
    "Oklahoma": ("OK", "South"),
    "Oregon": ("OR", "West"),
    "Pennsylvania": ("PA", "Northeast"),
    "Rhode Island": ("RI", "Northeast"),
    "South Carolina": ("SC", "South"),
    "South Dakota": ("SD", "Midwest"),
    "Tennessee": ("TN", "South"),
    "Texas": ("TX", "South"),
    "Utah": ("UT", "West"),
    "Vermont": ("VT", "Northeast"),
    "Virginia": ("VA", "South"),
    "Washington": ("WA", "West"),
    "West Virginia": ("WV", "South"),
    "Wisconsin": ("WI", "Midwest"),
    "Wyoming": ("WY", "West"),
    "District of Columbia": ("DC", "South"),
}

POLLUTANT_COLUMNS = ["PM2.5", "PM10", "NO2", "SO2", "CO", "O3"]


def _ensure_required_columns(df: pd.DataFrame) -> None:
    missing = [column for column in ["State", "AQI"] if column not in df.columns]
    if missing:
        raise ValueError("Missing required columns for dashboard prep: " + ", ".join(missing))


def _assign_aqi_category(series: pd.Series) -> pd.Series:
    return pd.cut(series, bins=AQI_CATEGORY_BINS, labels=AQI_CATEGORY_LABELS)


def create_tableau_state_summary(df: pd.DataFrame) -> pd.DataFrame:
    _ensure_required_columns(df)

    working_df = df.copy()
    if "Date" in working_df.columns:
        working_df["Date"] = pd.to_datetime(working_df["Date"], errors="coerce")

    aggregation = {
        "AQI": ["mean", "max", "count"],
    }
    for column in POLLUTANT_COLUMNS:
        if column in working_df.columns:
            aggregation[column] = "mean"

    grouped = working_df.groupby("State").agg(aggregation)
    grouped.columns = [
        "_".join(part for part in column if part).strip("_")
        if isinstance(column, tuple)
        else column
        for column in grouped.columns.to_flat_index()
    ]
    grouped = grouped.reset_index()

    grouped = grouped.rename(
        columns={
            "AQI_mean": "Average_AQI",
            "AQI_max": "Max_AQI",
            "AQI_count": "Observation_Count",
        }
    )

    if "Date" in working_df.columns:
        date_summary = (
            working_df.dropna(subset=["Date"])
            .groupby("State")["Date"]
            .agg(["min", "max"])
            .reset_index()
            .rename(columns={"min": "Start_Date", "max": "End_Date"})
        )
        grouped = grouped.merge(date_summary, on="State", how="left")

    grouped["Average_AQI"] = grouped["Average_AQI"].round(2)
    grouped["Max_AQI"] = grouped["Max_AQI"].round(2)

    for column in POLLUTANT_COLUMNS:
        mean_name = f"{column}_mean"
        if mean_name in grouped.columns:
            grouped = grouped.rename(columns={mean_name: f"Average_{column}"})
            grouped[f"Average_{column}"] = grouped[f"Average_{column}"].round(2)

    grouped = grouped.sort_values("Average_AQI", ascending=False).reset_index(drop=True)
    grouped["Rank"] = range(1, len(grouped) + 1)
    grouped["AQI_Category"] = _assign_aqi_category(grouped["Average_AQI"]).astype("string")
    grouped["State_Code"] = grouped["State"].map(lambda state: STATE_LOOKUP.get(state, ("Unknown", "Unknown"))[0])
    grouped["Region"] = grouped["State"].map(lambda state: STATE_LOOKUP.get(state, ("Unknown", "Unknown"))[1])

    if "Start_Date" in grouped.columns:
        grouped["Start_Date"] = pd.to_datetime(grouped["Start_Date"], errors="coerce").dt.strftime("%Y-%m-%d")
        grouped["End_Date"] = pd.to_datetime(grouped["End_Date"], errors="coerce").dt.strftime("%Y-%m-%d")

    ordered_columns = [
        "Rank",
        "State",
        "State_Code",
        "Region",
        "Average_AQI",
        "Max_AQI",
        "Observation_Count",
        "AQI_Category",
    ]
    optional_columns = [column for column in ["Start_Date", "End_Date"] if column in grouped.columns]
    pollutant_columns = [column for column in grouped.columns if column.startswith("Average_") and column != "Average_AQI"]
    remaining_columns = [column for column in grouped.columns if column not in ordered_columns + optional_columns + pollutant_columns]

    return grouped[ordered_columns + optional_columns + pollutant_columns + remaining_columns]


def create_tableau_monthly_summary(df: pd.DataFrame) -> pd.DataFrame:
    if "Date" not in df.columns:
        return pd.DataFrame(columns=["Month", "Average_AQI", "Observation_Count"])

    working_df = df.copy()
    working_df["Date"] = pd.to_datetime(working_df["Date"], errors="coerce")
    working_df = working_df.dropna(subset=["Date", "AQI"])
    if working_df.empty:
        return pd.DataFrame(columns=["Month", "Average_AQI", "Observation_Count"])

    monthly = (
        working_df.assign(Month=working_df["Date"].dt.to_period("M").astype(str))
        .groupby("Month", as_index=False)
        .agg(Average_AQI=("AQI", "mean"), Observation_Count=("AQI", "count"))
        .sort_values("Month")
        .reset_index(drop=True)
    )
    monthly["Average_AQI"] = monthly["Average_AQI"].round(2)
    return monthly


def create_dashboard_kpis(df: pd.DataFrame, state_summary: pd.DataFrame) -> Dict[str, object]:
    _ensure_required_columns(df)

    total_records = int(len(df))
    states_covered = int(df["State"].nunique())
    national_average_aqi = round(float(df["AQI"].mean()), 2)

    dated_df = df.copy()
    if "Date" in dated_df.columns:
        dated_df["Date"] = pd.to_datetime(dated_df["Date"], errors="coerce")
        valid_dates = dated_df["Date"].dropna()
        date_min = valid_dates.min().strftime("%Y-%m-%d") if not valid_dates.empty else None
        date_max = valid_dates.max().strftime("%Y-%m-%d") if not valid_dates.empty else None
    else:
        date_min = None
        date_max = None

    top_state = state_summary.iloc[0] if not state_summary.empty else None
    bottom_state = state_summary.iloc[-1] if not state_summary.empty else None

    return {
        "total_records": total_records,
        "states_covered": states_covered,
        "national_average_aqi": national_average_aqi,
        "date_range_start": date_min,
        "date_range_end": date_max,
        "most_polluted_state": top_state["State"] if top_state is not None else None,
        "most_polluted_state_average_aqi": float(top_state["Average_AQI"]) if top_state is not None else None,
        "cleanest_state": bottom_state["State"] if bottom_state is not None else None,
        "cleanest_state_average_aqi": float(bottom_state["Average_AQI"]) if bottom_state is not None else None,
    }


def prepare_dashboard_assets(
    input_path: Path,
    tableau_dir: Path,
    report_dir: Path,
) -> Dict[str, object]:
    df = pd.read_csv(input_path)
    _ensure_required_columns(df)

    tableau_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    state_summary = create_tableau_state_summary(df)
    monthly_summary = create_tableau_monthly_summary(df)
    kpis = create_dashboard_kpis(df, state_summary)

    state_summary_path = tableau_dir / "tableau_state_summary.csv"
    monthly_summary_path = tableau_dir / "tableau_monthly_summary.csv"
    kpi_path = tableau_dir / "dashboard_kpis.json"
    manifest_path = report_dir / "phase4_dashboard_manifest.json"

    state_summary.to_csv(state_summary_path, index=False)
    monthly_summary.to_csv(monthly_summary_path, index=False)
    kpi_path.write_text(json.dumps(kpis, indent=2), encoding="utf-8")

    manifest = {
        "input_file": str(input_path),
        "tableau_files": [
            str(state_summary_path),
            str(monthly_summary_path),
            str(kpi_path),
        ],
        "state_rows": int(len(state_summary)),
        "monthly_rows": int(len(monthly_summary)),
        "kpis": kpis,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare Tableau-ready assets for the AQI dashboard.")
    parser.add_argument("--input", required=True, help="Path to the cleaned AQI CSV file.")
    parser.add_argument("--tableau-dir", help="Directory for Tableau-ready files.")
    parser.add_argument("--report-dir", help="Directory for Phase 4 manifest outputs.")
    args = parser.parse_args()

    input_path = Path(args.input).expanduser().resolve()
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    root = Path(__file__).resolve().parent.parent
    tableau_dir = Path(args.tableau_dir).expanduser().resolve() if args.tableau_dir else root / "dashboard" / "tableau"
    report_dir = Path(args.report_dir).expanduser().resolve() if args.report_dir else root / "report"

    manifest = prepare_dashboard_assets(input_path, tableau_dir, report_dir)
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()

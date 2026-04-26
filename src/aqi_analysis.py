"""Phase 3 AQI analysis pipeline for state rankings and visual outputs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, List

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


POLLUTANT_COLUMNS = ["AQI", "PM2.5", "PM10", "NO2", "SO2", "CO", "O3"]
AQI_CATEGORY_BINS = [-1, 50, 100, 150, 200, 300, 500, float("inf")]
AQI_CATEGORY_LABELS = [
    "Good",
    "Moderate",
    "Unhealthy for Sensitive Groups",
    "Unhealthy",
    "Very Unhealthy",
    "Hazardous",
    "Beyond Index",
]


def _ensure_required_columns(df: pd.DataFrame) -> None:
    missing = [column for column in ["State", "AQI"] if column not in df.columns]
    if missing:
        raise ValueError("Missing required columns for analysis: " + ", ".join(missing))


def calculate_state_rankings(df: pd.DataFrame) -> pd.DataFrame:
    _ensure_required_columns(df)

    state_avg_aqi = (
        df.groupby("State", as_index=False)["AQI"]
        .mean()
        .rename(columns={"AQI": "Average_AQI"})
        .sort_values(by="Average_AQI", ascending=False)
        .reset_index(drop=True)
    )
    state_avg_aqi["Average_AQI"] = state_avg_aqi["Average_AQI"].round(2)
    state_avg_aqi["Rank"] = range(1, len(state_avg_aqi) + 1)
    return state_avg_aqi[["Rank", "State", "Average_AQI"]]


def calculate_monthly_trend(df: pd.DataFrame) -> pd.DataFrame:
    if "Date" not in df.columns:
        return pd.DataFrame(columns=["Month", "Average_AQI"])

    dated_df = df.copy()
    dated_df["Date"] = pd.to_datetime(dated_df["Date"], errors="coerce")
    dated_df = dated_df.dropna(subset=["Date", "AQI"])
    if dated_df.empty:
        return pd.DataFrame(columns=["Month", "Average_AQI"])

    monthly_trend = (
        dated_df.assign(Month=dated_df["Date"].dt.to_period("M").astype(str))
        .groupby("Month", as_index=False)["AQI"]
        .mean()
        .rename(columns={"AQI": "Average_AQI"})
        .sort_values("Month")
        .reset_index(drop=True)
    )
    monthly_trend["Average_AQI"] = monthly_trend["Average_AQI"].round(2)
    return monthly_trend


def calculate_pollutant_correlation(df: pd.DataFrame) -> pd.DataFrame:
    available = [column for column in POLLUTANT_COLUMNS if column in df.columns]
    if len(available) < 2:
        return pd.DataFrame()

    numeric_df = df[available].apply(pd.to_numeric, errors="coerce")
    correlation_df = numeric_df.corr().round(3)
    return correlation_df.dropna(how="all").dropna(axis=1, how="all")


def calculate_aqi_category_distribution(df: pd.DataFrame) -> pd.DataFrame:
    _ensure_required_columns(df)

    distribution_df = df.copy()
    distribution_df["AQI_Category"] = pd.cut(
        distribution_df["AQI"],
        bins=AQI_CATEGORY_BINS,
        labels=AQI_CATEGORY_LABELS,
    )

    category_counts = (
        distribution_df["AQI_Category"]
        .value_counts(dropna=False)
        .rename_axis("AQI_Category")
        .reset_index(name="Count")
    )
    category_counts["AQI_Category"] = category_counts["AQI_Category"].astype("string").fillna("Unknown")
    category_counts = category_counts[category_counts["Count"] > 0].reset_index(drop=True)
    return category_counts


def _save_dataframe(df: pd.DataFrame, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)


def _plot_top_states(state_rankings: pd.DataFrame, output_path: Path) -> None:
    top_states = state_rankings.head(10).sort_values("Average_AQI", ascending=True)

    plt.figure(figsize=(10, 6))
    plt.barh(top_states["State"], top_states["Average_AQI"], color="#c0392b")
    plt.xlabel("Average AQI")
    plt.ylabel("State")
    plt.title("Top 10 Most Polluted States by Average AQI")
    plt.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=200)
    plt.close()


def _plot_cleanest_states(state_rankings: pd.DataFrame, output_path: Path) -> None:
    cleanest_states = state_rankings.tail(10).sort_values("Average_AQI", ascending=False)

    plt.figure(figsize=(10, 6))
    plt.barh(cleanest_states["State"], cleanest_states["Average_AQI"], color="#1f7a8c")
    plt.xlabel("Average AQI")
    plt.ylabel("State")
    plt.title("10 Cleanest States by Average AQI")
    plt.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=200)
    plt.close()


def _plot_monthly_trend(monthly_trend: pd.DataFrame, output_path: Path) -> bool:
    if monthly_trend.empty:
        return False

    plt.figure(figsize=(11, 5))
    plt.plot(monthly_trend["Month"], monthly_trend["Average_AQI"], marker="o", color="#2c3e50")
    plt.xticks(rotation=45, ha="right")
    plt.xlabel("Month")
    plt.ylabel("Average AQI")
    plt.title("Monthly Average AQI Trend")
    plt.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=200)
    plt.close()
    return True


def _plot_correlation_heatmap(correlation_df: pd.DataFrame, output_path: Path) -> bool:
    if correlation_df.empty or correlation_df.shape[0] < 2:
        return False

    plt.figure(figsize=(8, 6))
    sns.heatmap(correlation_df, annot=True, cmap="YlOrRd", fmt=".2f", square=True)
    plt.title("Pollutant Correlation Heatmap")
    plt.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=200)
    plt.close()
    return True


def _plot_aqi_category_distribution(category_distribution: pd.DataFrame, output_path: Path) -> bool:
    if category_distribution.empty:
        return False

    plt.figure(figsize=(8, 8))
    plt.pie(
        category_distribution["Count"],
        labels=category_distribution["AQI_Category"],
        autopct="%1.1f%%",
        startangle=140,
    )
    plt.title("AQI Category Distribution")
    plt.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=200)
    plt.close()
    return True


def analyze_air_quality_data(
    input_path: Path,
    processed_dir: Path,
    visuals_dir: Path,
    report_dir: Path,
) -> Dict[str, object]:
    df = pd.read_csv(input_path)
    _ensure_required_columns(df)

    processed_dir.mkdir(parents=True, exist_ok=True)
    visuals_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    state_rankings = calculate_state_rankings(df)
    monthly_trend = calculate_monthly_trend(df)
    correlation_df = calculate_pollutant_correlation(df)
    category_distribution = calculate_aqi_category_distribution(df)

    _save_dataframe(state_rankings, processed_dir / "state_average_aqi.csv")
    _save_dataframe(monthly_trend, processed_dir / "monthly_aqi_trend.csv")
    _save_dataframe(category_distribution, processed_dir / "aqi_category_distribution.csv")
    if not correlation_df.empty:
        _save_dataframe(correlation_df.reset_index(names="Pollutant"), processed_dir / "pollutant_correlation.csv")

    _plot_top_states(state_rankings, visuals_dir / "top_10_polluted_states.png")
    _plot_cleanest_states(state_rankings, visuals_dir / "top_10_cleanest_states.png")
    monthly_chart_created = _plot_monthly_trend(monthly_trend, visuals_dir / "monthly_aqi_trend.png")
    heatmap_created = _plot_correlation_heatmap(correlation_df, visuals_dir / "pollutant_correlation_heatmap.png")
    pie_chart_created = _plot_aqi_category_distribution(
        category_distribution,
        visuals_dir / "aqi_category_distribution.png",
    )

    summary: Dict[str, object] = {
        "input_file": str(input_path),
        "state_count": int(state_rankings["State"].nunique()),
        "records_analyzed": int(len(df)),
        "highest_average_aqi_state": state_rankings.iloc[0]["State"] if not state_rankings.empty else None,
        "highest_average_aqi_value": float(state_rankings.iloc[0]["Average_AQI"]) if not state_rankings.empty else None,
        "lowest_average_aqi_state": state_rankings.iloc[-1]["State"] if not state_rankings.empty else None,
        "lowest_average_aqi_value": float(state_rankings.iloc[-1]["Average_AQI"]) if not state_rankings.empty else None,
        "monthly_trend_created": monthly_chart_created,
        "correlation_heatmap_created": heatmap_created,
        "aqi_category_chart_created": pie_chart_created,
        "files_created": [
            str(processed_dir / "state_average_aqi.csv"),
            str(processed_dir / "monthly_aqi_trend.csv"),
            str(processed_dir / "aqi_category_distribution.csv"),
            str(visuals_dir / "top_10_polluted_states.png"),
            str(visuals_dir / "top_10_cleanest_states.png"),
        ],
    }
    if not correlation_df.empty:
        summary["files_created"].append(str(processed_dir / "pollutant_correlation.csv"))
    if monthly_chart_created:
        summary["files_created"].append(str(visuals_dir / "monthly_aqi_trend.png"))
    if heatmap_created:
        summary["files_created"].append(str(visuals_dir / "pollutant_correlation_heatmap.png"))
    if pie_chart_created:
        summary["files_created"].append(str(visuals_dir / "aqi_category_distribution.png"))

    summary_path = report_dir / "phase3_analysis_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    summary["files_created"].append(str(summary_path))
    return summary


def _default_paths(input_path: Path) -> Dict[str, Path]:
    root = Path(__file__).resolve().parent.parent
    return {
        "processed_dir": root / "data" / "processed",
        "visuals_dir": root / "visuals",
        "report_dir": root / "report",
        "input_path": input_path,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze a cleaned AQI CSV and export Phase 3 outputs.")
    parser.add_argument("--input", required=True, help="Path to the cleaned CSV file.")
    parser.add_argument("--processed-dir", help="Directory for analysis tables.")
    parser.add_argument("--visuals-dir", help="Directory for exported charts.")
    parser.add_argument("--report-dir", help="Directory for summary reports.")
    args = parser.parse_args()

    input_path = Path(args.input).expanduser().resolve()
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    defaults = _default_paths(input_path)
    processed_dir = Path(args.processed_dir).expanduser().resolve() if args.processed_dir else defaults["processed_dir"]
    visuals_dir = Path(args.visuals_dir).expanduser().resolve() if args.visuals_dir else defaults["visuals_dir"]
    report_dir = Path(args.report_dir).expanduser().resolve() if args.report_dir else defaults["report_dir"]

    summary = analyze_air_quality_data(input_path, processed_dir, visuals_dir, report_dir)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

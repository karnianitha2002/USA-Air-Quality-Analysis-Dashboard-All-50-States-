import tempfile
import unittest
from pathlib import Path

import pandas as pd

from src.aqi_analysis import (
    analyze_air_quality_data,
    calculate_aqi_category_distribution,
    calculate_monthly_trend,
    calculate_state_rankings,
)


class AQIAnalysisTests(unittest.TestCase):
    def setUp(self) -> None:
        self.df = pd.DataFrame(
            {
                "State": ["California", "California", "Arizona", "Arizona", "Nevada"],
                "City": ["Los Angeles", "San Diego", "Phoenix", "Tucson", "Reno"],
                "Date": ["2024-01-05", "2024-02-10", "2024-01-15", "2024-02-20", "2024-01-25"],
                "AQI": [90, 110, 70, 80, 50],
                "PM2.5": [20, 25, 15, 18, 10],
                "PM10": [30, 35, 20, 22, 12],
            }
        )

    def test_state_rankings_are_sorted_descending(self) -> None:
        rankings = calculate_state_rankings(self.df)

        self.assertEqual(rankings.iloc[0]["State"], "California")
        self.assertEqual(rankings.iloc[0]["Average_AQI"], 100.0)
        self.assertEqual(rankings.iloc[-1]["State"], "Nevada")
        self.assertEqual(rankings["Rank"].tolist(), [1, 2, 3])

    def test_monthly_trend_and_category_distribution_are_created(self) -> None:
        monthly_trend = calculate_monthly_trend(self.df)
        category_distribution = calculate_aqi_category_distribution(self.df)

        self.assertEqual(monthly_trend["Month"].tolist(), ["2024-01", "2024-02"])
        self.assertEqual(monthly_trend["Average_AQI"].tolist(), [70.0, 95.0])
        self.assertIn("Moderate", category_distribution["AQI_Category"].tolist())

    def test_end_to_end_analysis_writes_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            input_path = tmp_path / "cleaned.csv"
            processed_dir = tmp_path / "processed"
            visuals_dir = tmp_path / "visuals"
            report_dir = tmp_path / "report"

            self.df.to_csv(input_path, index=False)
            summary = analyze_air_quality_data(input_path, processed_dir, visuals_dir, report_dir)

            self.assertTrue((processed_dir / "state_average_aqi.csv").exists())
            self.assertTrue((processed_dir / "monthly_aqi_trend.csv").exists())
            self.assertTrue((processed_dir / "aqi_category_distribution.csv").exists())
            self.assertTrue((processed_dir / "pollutant_correlation.csv").exists())
            self.assertTrue((visuals_dir / "top_10_polluted_states.png").exists())
            self.assertTrue((visuals_dir / "top_10_cleanest_states.png").exists())
            self.assertTrue((visuals_dir / "monthly_aqi_trend.png").exists())
            self.assertTrue((visuals_dir / "pollutant_correlation_heatmap.png").exists())
            self.assertTrue((visuals_dir / "aqi_category_distribution.png").exists())
            self.assertTrue((report_dir / "phase3_analysis_summary.json").exists())
            self.assertEqual(summary["highest_average_aqi_state"], "California")


if __name__ == "__main__":
    unittest.main()

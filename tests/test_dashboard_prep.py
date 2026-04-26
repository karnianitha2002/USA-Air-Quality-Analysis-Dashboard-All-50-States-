import json
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from src.dashboard_prep import (
    create_dashboard_kpis,
    create_tableau_monthly_summary,
    create_tableau_state_summary,
    prepare_dashboard_assets,
)


class DashboardPrepTests(unittest.TestCase):
    def setUp(self) -> None:
        self.df = pd.DataFrame(
            {
                "State": ["California", "California", "Arizona", "Nevada"],
                "Date": ["2024-01-01", "2024-02-01", "2024-01-15", "2024-02-10"],
                "AQI": [100, 120, 80, 55],
                "PM2.5": [25, 28, 18, 12],
                "PM10": [35, 38, 20, 14],
            }
        )

    def test_state_summary_contains_tableau_fields(self) -> None:
        summary = create_tableau_state_summary(self.df)

        self.assertEqual(summary.iloc[0]["State"], "California")
        self.assertEqual(summary.iloc[0]["Rank"], 1)
        self.assertEqual(summary.iloc[0]["State_Code"], "CA")
        self.assertEqual(summary.iloc[0]["Region"], "West")
        self.assertIn("Average_PM2.5", summary.columns)

    def test_monthly_summary_and_kpis_are_computed(self) -> None:
        state_summary = create_tableau_state_summary(self.df)
        monthly_summary = create_tableau_monthly_summary(self.df)
        kpis = create_dashboard_kpis(self.df, state_summary)

        self.assertEqual(monthly_summary["Month"].tolist(), ["2024-01", "2024-02"])
        self.assertEqual(kpis["states_covered"], 3)
        self.assertEqual(kpis["most_polluted_state"], "California")
        self.assertEqual(kpis["cleanest_state"], "Nevada")

    def test_prepare_dashboard_assets_writes_expected_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            input_path = tmp_path / "cleaned.csv"
            tableau_dir = tmp_path / "tableau"
            report_dir = tmp_path / "report"

            self.df.to_csv(input_path, index=False)
            manifest = prepare_dashboard_assets(input_path, tableau_dir, report_dir)

            self.assertTrue((tableau_dir / "tableau_state_summary.csv").exists())
            self.assertTrue((tableau_dir / "tableau_monthly_summary.csv").exists())
            self.assertTrue((tableau_dir / "dashboard_kpis.json").exists())
            self.assertTrue((report_dir / "phase4_dashboard_manifest.json").exists())
            self.assertEqual(manifest["state_rows"], 3)

            saved_kpis = json.loads((tableau_dir / "dashboard_kpis.json").read_text(encoding="utf-8"))
            self.assertEqual(saved_kpis["most_polluted_state"], "California")


if __name__ == "__main__":
    unittest.main()

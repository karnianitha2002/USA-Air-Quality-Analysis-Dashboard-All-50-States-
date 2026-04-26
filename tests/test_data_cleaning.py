import unittest

import pandas as pd

from src.data_cleaning import clean_air_quality_data


class DataCleaningTests(unittest.TestCase):
    def test_cleaning_standardizes_columns_and_states(self) -> None:
        raw_df = pd.DataFrame(
            {
                "state_name": ["ca", "New york", None, "CA"],
                "city_name": ["Los Angeles", "Albany", "Phoenix", "Los Angeles"],
                "observation_date": ["2024-01-01", "2024/01/02", "bad-date", "2024-01-01"],
                "air_quality_index": ["55", "80", "90", "55"],
                "pm2_5": ["12.3", "9.1", "4.2", "12.3"],
            }
        )

        cleaned_df, summary = clean_air_quality_data(raw_df)

        self.assertEqual(list(cleaned_df.columns), ["State", "City", "Date", "AQI", "PM2.5"])
        self.assertEqual(cleaned_df["State"].tolist(), ["California", "New York"])
        self.assertEqual(cleaned_df["AQI"].tolist(), [55, 80])
        self.assertEqual(summary["duplicates_removed"], 1)
        self.assertEqual(summary["dropped_missing_state_or_aqi"], 1)
        self.assertEqual(summary["states_found"], 2)

    def test_missing_required_columns_raises_clear_error(self) -> None:
        raw_df = pd.DataFrame({"city": ["Phoenix"], "pm10": [18]})

        with self.assertRaisesRegex(ValueError, "Missing required columns"):
            clean_air_quality_data(raw_df)


if __name__ == "__main__":
    unittest.main()

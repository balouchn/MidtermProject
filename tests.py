"""Tests for data loading, cleaning, filters, and dashboard calculations."""

from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from data_prep import (
    COUNTRY_CSV,
    REGION_CSV,
    filter_observations,
    format_percentage,
    gdp_share_complete_cases,
    load_datasets,
    rank_countries,
    _read_csv,
)


class RenewableDataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.bundle = load_datasets(COUNTRY_CSV, REGION_CSV)
        cls.country = cls.bundle.country

    def test_supplied_csv_files_load_with_expected_size_and_columns(self) -> None:
        self.assertTrue(Path(COUNTRY_CSV).is_file())
        self.assertTrue(Path(REGION_CSV).is_file())
        self.assertEqual(len(self.country), 17265)
        self.assertEqual(len(self.bundle.region), 6112)
        self.assertIn("renewables_share_elec", self.country.columns)
        self.assertNotIn("renewables_share_elec.1", self.country.columns)
        self.assertEqual(set(self.country.columns), set(self.bundle.region.columns))
        self.assertTrue(pd.api.types.is_integer_dtype(self.country["year"]))
        self.assertTrue(pd.api.types.is_numeric_dtype(self.country["gdp"]))
        self.assertEqual(
            sum(
                self.bundle.diagnostics["country"][
                    "invalid_numeric_conversions"
                ].values()
            ),
            0,
        )

    def test_invalid_numeric_value_is_missing_and_counted(self) -> None:
        with COUNTRY_CSV.open("r", encoding="utf-8-sig", newline="") as source:
            reader = csv.reader(source)
            headers = next(reader)
            first_row = next(reader)
        first_row[headers.index("population")] = "not-a-number"

        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary_csv = Path(temporary_directory) / "invalid_value.csv"
            with temporary_csv.open("w", encoding="utf-8", newline="") as output:
                writer = csv.writer(output)
                writer.writerow(headers)
                writer.writerow(first_row)
            converted, diagnostics = _read_csv(temporary_csv)

        self.assertTrue(pd.isna(converted.loc[0, "population"]))
        self.assertEqual(
            diagnostics["invalid_numeric_conversions"]["population"], 1
        )

    def test_repeated_source_columns_were_identical_and_checked(self) -> None:
        for dataset in ("country", "region"):
            checks = self.bundle.diagnostics[dataset]["duplicate_column_checks"]
            self.assertEqual(
                checks,
                {
                    "renewables_share_energy": True,
                    "renewables_share_elec": True,
                    "renewables_electricity": True,
                },
            )
            self.assertEqual(
                self.bundle.diagnostics[dataset]["exact_duplicate_rows"], 0
            )
            self.assertEqual(
                self.bundle.diagnostics[dataset]["duplicate_country_year_rows"], 0
            )

    def test_year_and_country_filters_are_inclusive_and_do_not_fill_missing(self) -> None:
        filtered = filter_observations(
            self.country,
            countries=["United States"],
            year_range=(2000, 2002),
        )
        self.assertEqual(filtered["year"].astype(int).tolist(), [2000, 2001, 2002])
        original_missing = int(
            self.country.loc[
                self.country["country"] == "Afghanistan", "renewables_share_elec"
            ].isna().sum()
        )
        self.assertEqual(original_missing, 100)

    def test_value_filter_retains_only_observed_values(self) -> None:
        observed = filter_observations(
            self.country,
            year_range=(2022, 2022),
            value_column="renewables_share_elec",
        )
        self.assertTrue(observed["renewables_share_elec"].notna().all())
        self.assertEqual(observed["country"].nunique(), 212)

    def test_invalid_year_range_is_reported(self) -> None:
        with self.assertRaises(ValueError):
            filter_observations(self.country, year_range=(2023, 2022))

    def test_ranking_is_numeric_descending_and_ties_share_rank(self) -> None:
        sample = pd.DataFrame(
            {
                "country": ["Zulu", "Alpha", "Beta", "Missing"],
                "year": [2020] * 4,
                "renewables_share_elec": [80.0, 80.0, 15.0, pd.NA],
            }
        )
        ranked = rank_countries(sample, 2020, limit=5)
        self.assertEqual(ranked["country"].tolist(), ["Alpha", "Zulu", "Beta"])
        self.assertEqual(ranked["rank"].tolist(), [1, 1, 3])
        self.assertFalse(ranked["renewables_share_elec"].isna().any())

    def test_real_country_ranking_order_and_count(self) -> None:
        ranked = rank_countries(self.country, 2022, limit=5)
        expected = (
            self.country.loc[
                (self.country["year"] == 2022)
                & self.country["renewables_share_elec"].notna(),
                ["country", "renewables_share_elec"],
            ]
            .sort_values(
                ["renewables_share_elec", "country"],
                ascending=[False, True],
                kind="stable",
            )
            .head(5)
        )
        self.assertEqual(ranked["country"].tolist(), expected["country"].tolist())
        self.assertEqual(
            ranked["renewables_share_elec"].tolist(),
            expected["renewables_share_elec"].tolist(),
        )
        self.assertEqual(
            self.country.loc[
                (self.country["year"] == 2022)
                & self.country["renewables_share_elec"].notna(),
                "country",
            ].nunique(),
            212,
        )

    def test_gdp_scatter_uses_complete_cases_only(self) -> None:
        cases = gdp_share_complete_cases(self.country, 2022)
        self.assertTrue(cases["gdp"].notna().all())
        self.assertTrue(cases["renewables_share_elec"].notna().all())
        self.assertEqual(cases["country"].nunique(), len(cases))
        self.assertEqual(len(cases), 165)

    def test_missing_year_boundary_returns_empty(self) -> None:
        result = filter_observations(
            self.country,
            countries=["Afghanistan"],
            year_range=(1900, 1900),
            value_column="renewables_share_elec",
        )
        self.assertTrue(result.empty)
        self.assertTrue(filter_observations(self.country, countries=[]).empty)

    def test_percentage_display_does_not_rescale_value(self) -> None:
        self.assertEqual(format_percentage(19.334), "19.3%")
        self.assertEqual(format_percentage(None), "Not available")

    def test_country_and_region_rows_are_not_combined(self) -> None:
        self.assertEqual(len(self.country), 17265)
        self.assertEqual(len(self.bundle.region), 6112)
        self.assertEqual(self.bundle.diagnostics["region"]["entity_count"], 94)
        self.assertTrue(self.bundle.region["iso_code"].isna().all())


if __name__ == "__main__":
    unittest.main()

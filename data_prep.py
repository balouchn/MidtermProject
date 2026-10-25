"""Reproducible loading and validation for the supplied renewable-energy CSVs."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parent
COUNTRY_CSV = ROOT / "data" / "renewable_energy_by_country.csv"
REGION_CSV = ROOT / "data" / "renewable_energy_by_region.csv"

NUMERIC_COLUMNS = (
    "year",
    "population",
    "gdp",
    "primary_energy_consumption",
    "energy_per_capita",
    "fossil_share_energy",
    "fossil_fuel_consumption",
    "electricity_generation",
    "renewables_share_energy",
    "renewables_share_elec",
    "renewables_consumption",
    "renewables_electricity",
    "hydro_electricity",
    "hydro_share_elec",
    "hydro_share_energy",
    "solar_electricity",
    "solar_share_elec",
    "solar_share_energy",
    "wind_electricity",
    "wind_share_elec",
    "wind_share_energy",
    "other_renewable_electricity",
    "other_renewables_share_elec",
    "other_renewables_share_energy",
)
SHARE_COLUMNS = (
    "renewables_share_elec",
    "hydro_share_elec",
    "solar_share_elec",
    "wind_share_elec",
    "other_renewables_share_elec",
)
GENERATION_COLUMNS = (
    "renewables_electricity",
    "hydro_electricity",
    "solar_electricity",
    "wind_electricity",
    "other_renewable_electricity",
)
TECHNOLOGY_COLUMNS = {
    "Hydro": "hydro_electricity",
    "Wind": "wind_electricity",
    "Solar": "solar_electricity",
    "Other renewables": "other_renewable_electricity",
}
DUPLICATE_HEADERS = (
    "renewables_share_energy",
    "renewables_share_elec",
    "renewables_electricity",
)


@dataclass
class DatasetBundle:
    country: pd.DataFrame
    region: pd.DataFrame
    diagnostics: dict[str, dict[str, Any]]


def _read_csv(path: Path) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Read one CSV, validating identical repeated headers before removing copies."""
    if not path.is_file():
        raise FileNotFoundError(f"Required data file was not found: {path}")

    with path.open("r", encoding="utf-8-sig", newline="") as source:
        original_headers = next(csv.reader(source), None)
    if not original_headers:
        raise ValueError(f"CSV has no header row: {path}")

    frame = pd.read_csv(path, dtype={"country": "string", "iso_code": "string"})
    repeated = {name for name in original_headers if original_headers.count(name) > 1}
    if repeated != set(DUPLICATE_HEADERS):
        raise ValueError(
            f"Unexpected repeated headers in {path.name}: {sorted(repeated)}"
        )

    duplicate_column_checks: dict[str, bool] = {}
    for name in DUPLICATE_HEADERS:
        positions = [i for i, value in enumerate(original_headers) if value == name]
        if len(positions) != 2:
            raise ValueError(f"Expected two copies of {name!r} in {path.name}")
        first = frame.iloc[:, positions[0]]
        second = frame.iloc[:, positions[1]]
        equal = first.equals(second)
        duplicate_column_checks[name] = equal
        if not equal:
            raise ValueError(
                f"Repeated {name!r} columns differ in {path.name}; "
                "the data needs investigation before preparation."
            )
        # pandas names duplicate headers with a .1 suffix. Keep the first only
        # after proving the two source columns are identical.
        duplicate_label = f"{name}.1"
        if duplicate_label not in frame.columns:
            raise ValueError(f"Could not locate pandas duplicate column {duplicate_label!r}")
        frame = frame.drop(columns=[duplicate_label])

    initial_rows = len(frame)
    exact_duplicate_rows = int(frame.duplicated().sum())
    duplicate_country_year_rows = int(frame.duplicated(["country", "year"]).sum())
    invalid_numeric: dict[str, int] = {}
    missing_before_conversion: dict[str, int] = {}

    for column in NUMERIC_COLUMNS:
        if column not in frame.columns:
            raise ValueError(f"Required source column is missing: {column}")
        original = frame[column]
        missing_before_conversion[column] = int(original.isna().sum())
        converted = pd.to_numeric(original, errors="coerce")
        invalid_numeric[column] = int((original.notna() & converted.isna()).sum())
        frame[column] = converted

    frame["year"] = frame["year"].astype("Int64")
    frame["country"] = frame["country"].str.strip()
    if "iso_code" in frame:
        frame["iso_code"] = frame["iso_code"].str.strip().replace("", pd.NA)

    diagnostics = {
        "file": path.name,
        "rows": initial_rows,
        "columns_after_verified_deduplication": len(frame.columns),
        "year_min": int(frame["year"].min()),
        "year_max": int(frame["year"].max()),
        "entity_count": int(frame["country"].nunique()),
        "exact_duplicate_rows": exact_duplicate_rows,
        "duplicate_country_year_rows": duplicate_country_year_rows,
        "duplicate_column_checks": duplicate_column_checks,
        "invalid_numeric_conversions": invalid_numeric,
        "missing_before_conversion": missing_before_conversion,
        "missing_counts": {column: int(frame[column].isna().sum()) for column in frame},
    }
    return frame, diagnostics


def load_datasets(
    country_path: str | Path = COUNTRY_CSV,
    region_path: str | Path = REGION_CSV,
) -> DatasetBundle:
    """Load country and regional data separately; neither dataset is appended."""
    country, country_diagnostics = _read_csv(Path(country_path))
    region, region_diagnostics = _read_csv(Path(region_path))
    return DatasetBundle(
        country=country,
        region=region,
        diagnostics={"country": country_diagnostics, "region": region_diagnostics},
    )


def filter_observations(
    frame: pd.DataFrame,
    *,
    countries: list[str] | None = None,
    year_range: tuple[int, int] | None = None,
    value_column: str | None = None,
) -> pd.DataFrame:
    """Filter rows without filling missing measurements."""
    result = frame
    if countries is not None:
        result = result[result["country"].isin(countries)]
    if year_range is not None:
        start, end = year_range
        if start > end:
            raise ValueError("The start year must not be later than the end year.")
        result = result[result["year"].between(start, end)]
    if value_column is not None:
        if value_column not in result.columns:
            raise KeyError(f"Unknown value column: {value_column}")
        result = result[result[value_column].notna()]
    return result.copy()


def rank_countries(
    frame: pd.DataFrame,
    year: int,
    *,
    ascending: bool = False,
    limit: int = 20,
) -> pd.DataFrame:
    """Rank only observed shares; tied values receive the same minimum rank."""
    if limit < 1:
        raise ValueError("Ranking limit must be at least 1.")
    observed = filter_observations(
        frame,
        year_range=(year, year),
        value_column="renewables_share_elec",
    ).copy()
    observed["rank"] = observed["renewables_share_elec"].rank(
        method="min", ascending=ascending
    ).astype(int)
    return observed.sort_values(
        ["renewables_share_elec", "country"],
        ascending=[ascending, True],
        kind="stable",
    ).head(limit)


def gdp_share_complete_cases(frame: pd.DataFrame, year: int) -> pd.DataFrame:
    """Return observations complete for the selected-year GDP/share scatter."""
    return filter_observations(
        frame,
        year_range=(year, year),
    ).dropna(subset=["gdp", "renewables_share_elec"]).copy()


def available_years(frame: pd.DataFrame, column: str) -> list[int]:
    """List years with at least one observed value for a field."""
    if column not in frame:
        raise KeyError(f"Unknown value column: {column}")
    return sorted(frame.loc[frame[column].notna(), "year"].dropna().astype(int).unique())


def format_percentage(value: float | int | None) -> str:
    """Format a percentage value for labels without converting its scale."""
    if value is None or pd.isna(value):
        return "Not available"
    return f"{value:.1f}%"

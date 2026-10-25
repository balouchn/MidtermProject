# Evaluation and verification

## Test design

`tests.py` uses Python's `unittest` and the supplied local CSVs. It checks source file
loading and row counts, unique output columns, verification of repeated headers,
duplicate-record diagnostics, inclusive year/country filtering, preservation of
missing values, numeric conversion and invalid-value diagnostics, complete cases for
GDP/share, ranking order and ties, percentage formatting, separate regional data,
and empty selections.

## Numerical example

The test `test_real_country_ranking_order_and_count` independently filters the raw
prepared country table to year 2022 and nonmissing `renewables_share_elec`, counts
distinct countries, and sorts values descending with country name as a stable
secondary sort. The expected valid-country count is **212**. The `rank_countries`
helper is then compared to the independently sorted first five country/value pairs.
This is a reproducible numerical check against the actual CSV, not a manually entered
ranking.

The GDP scatter test checks that the selected year's output includes only complete
records. The expected number is **165** country observations in 2022 based on the
supplied CSV.

## Boundary case

The missing-share boundary test requests Afghanistan in 1900 with a nonmissing
renewable electricity share. That measure begins in 1985 in this file, so the
expected output is an empty DataFrame. The test confirms that an unavailable value is
not replaced with zero.

Another boundary check rejects a reversed start/end year range rather than quietly
returning confusing results.

## Test execution

Run from the project root:

```powershell
python -m unittest -v
```

The first test run found two incorrect expected values in the tests: Afghanistan has
100 missing share rows (not 85), and 2022 has 165 complete GDP/share observations
(not 159). Those expectations were corrected against the supplied files. The
final run completed **12 tests successfully**, including numeric-conversion coverage:

```text
Ran 12 tests in 0.430s
OK
```

The dashboard was also opened in a local browser. All six section headings rendered
without an app exception. A browser interaction moved the share animation endpoint
from 2010 to 2011 using **Step forward**, and the displayed chart endpoint updated to
2011. The local server returned HTTP 200.

## Data and visualization safeguards

- Duplicate column copies are retained only after exact equality verification.
- No observations are imputed, interpolated or automatically deleted.
- Country and regional records remain separate.
- The map uses source three-character codes and labels its coverage; unmapped/missing
  values are not represented as zero.
- Country rankings exclude missing values and report the valid count.
- GDP uses complete cases for the selected year and makes no causal claim.
- Generation technologies are separate TWh lines, not a stacked total.
- Share percentages and generation TWh are separate views with separate units.
- The 2025 share count is sparse relative to earlier recent years and is explicitly
  called out in the app.

## Limitations and unsupported comparisons

- The original Kaggle CSV snapshot's exact version is unknown. Codebook alignment is
  supported by variable names and units, but the exact processing snapshot is not
  independently established.
- ISO-3 codes may not resolve for every country in Plotly's built-in map.
- Country boundaries, historical names and political changes complicate long-term
  comparisons.
- Regional labels include overlapping or source-specific aggregates; the dashboard
  does not attempt to aggregate them.
- Technology component data has uneven coverage. No totals are inferred from missing
  components.
- GDP and energy data are not available on matching coverage for every entity-year.
- Streamlit interactivity and numerical behavior are testable here; visual rendering
  should also be manually checked in the student's local browser before submission.

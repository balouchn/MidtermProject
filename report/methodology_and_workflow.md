# Methodology and workflow

## Research scope

The project asks: **How have renewable electricity generation and its share changed
across countries, and how do country renewable electricity mixes differ?** The
country-level file is primary; the optional regional file is inspected and documented
but never appended to the country table.

## Data source and structure

The local source files are `data/renewable_energy_by_country.csv` and
`data/renewable_energy_by_region.csv`, downloaded from the Kaggle dataset named
[Global Renewable Energy by Country (1900–2025)](https://www.kaggle.com/datasets/riyagarg0314/global-renewable-energy-by-country-1900-2025).
Country data has 17,265 rows and 29 source columns; regional data has 6,112 rows and
the same 29 source columns. Each row represents an entity-year record, with `country`
used for the entity label. The country table covers 220 labels and the region table
94 labels, each with years 1900–2025.

No data dictionary or exact export-version identifier is embedded in the CSVs. Field
definitions and units are interpreted using the matching Our World in Data
[energy-data documentation](https://github.com/owid/energy-data) and
[codebook](https://github.com/owid/energy-data/blob/master/owid-energy-codebook.csv).
That mapping should be revisited if the Kaggle export changes.

## Reproducible preparation

`data_prep.py` reads both CSV files relative to the project location and returns two
separate DataFrames. It:

1. Reads the raw header row and confirms the expected three repeated names:
   `renewables_share_energy`, `renewables_share_elec`, and
   `renewables_electricity`.
2. Compares both columns in each repeated pair cell by cell. Only if identical, it
   drops the pandas-mangled `.1` duplicate copy. If copies differ, loading fails with
   an explicit error. Raw CSV files remain unchanged.
3. Converts numeric fields with `pandas.to_numeric(errors="coerce")` and counts
   nonblank values that fail conversion. Source blanks stay missing; failures are
   separately reported in diagnostics and are not silently used as valid values.
4. Converts `year` to nullable integer, trims labels/codes, counts exact duplicate
   rows and repeated country-year keys, and does not remove duplicate rows.
5. Provides variable-specific filter, ranking, and complete-case helpers. No
   imputation, interpolation, or derived technology total is used.

The verified source duplicates were equal; both tables had zero exact duplicate rows
and zero repeated entity-year keys in the initial inspection. Data cleaning only
removes duplicate *columns* already proven identical, not observations.

## Field meanings used by the app

| Source field | Meaning used | Unit |
|---|---|---|
| `renewables_share_elec` | Renewable electricity as a fraction of total electricity generation | % |
| `renewables_electricity` | Electricity generation from renewables | TWh |
| `hydro_electricity`, `solar_electricity`, `wind_electricity` | Electricity generation by technology | TWh |
| `other_renewable_electricity` | Other renewable generation; codebook says other-renewables share includes bioenergy | TWh |
| `hydro_share_elec`, `solar_share_elec`, `wind_share_elec` | Technology's share of total electricity generation | % |
| `gdp` | GDP adjusted for inflation and cross-country living-cost differences | 2011 international-$ |
| `renewables_share_energy` | Renewable share of primary energy, not electricity | %; not used as the electricity share |

The codebook attributes GDP to Bolt and van Zanden's Maddison Project Database 2023.
Electricity data sources listed in the codebook include Ember and the Energy Institute.
The files do not identify their exact archived version, so comparisons across long
periods may reflect source/method changes in addition to real change.

## Coverage and missing data

The initial inspection found renewable-share values in 1985–2025 (6,551 country rows),
renewable generation in 1965–2025 (7,897), and GDP in 1900–2022 (11,559). Renewable
share is present for 212 countries in 2022, but only 90 rows in 2025. Counts vary by
indicator. Accordingly:

- The principal comparisons use variable-specific observed values; there is no global
  unweighted average of country shares.
- GDP scatter uses only rows with both GDP and renewable share present for the selected
  year (complete-case filter), and presents no causal claim.
- Generation by technology uses separate lines, not a stack or sum.
- Missing observations remain missing and gaps are visible.
- 2025 is flagged as sparse; charts report the available observations rather than
  suggesting the year represents every country.
- Regional values are not combined with countries, and regional aggregations are not
  summed because labels and boundaries can overlap.

## Story and visualization design

The app proceeds from geography to change over time, technology mix, an exploratory
GDP comparison, year-specific rankings, then direct multi-country transitions:

1. **Choropleth map:** selected-year renewable electricity share; location uses
   the source's ISO alpha-3 code. Missing color means unavailable/unmapped, not zero.
2. **Share time series:** multi-country line chart, selectable years, Plotly play/pause
   animation, year slider, step-forward and reset endpoint controls. Missing years
   remain gaps.
3. **Technology generation:** independently toggled hydro, wind, solar and other
   renewable lines in TWh. Categories are not stacked.
4. **GDP scatter:** selected-year complete cases; GDP is labeled in 2011 international
   dollars and share in percent; association is observational.
5. **Ranking:** ascending or descending year-specific share list. Missing observations
   are excluded; equal values share minimum rank and alphabetical name controls display
   order in a tie.
6. **Transition comparison:** 2–4 countries, selected year window, renewable-share
   comparison and separate technology-generation comparison with shared TWh units.

The sidebar focus country supplies defaults to related views. Selection controls and
chart hover values permit inspection. A reset restores the transition-comparison
defaults.

# Midterm report

## 1. **Abstract**

This project investigates how renewable electricity generation and its share have
changed across countries and how national renewable electricity mixes differ. It
uses a supplied country-level CSV as the primary dataset and implements an interactive
Streamlit dashboard with six connected views: a choropleth map, a time-series
comparison, technology generation lines, a GDP/share scatter plot, country rankings,
and multi-country transition comparisons. Source blanks remain missing; the project
does not interpolate, assign zeros to unknown values, or combine overlapping region
aggregates with countries. The dashboard is designed for general audiences and
undergraduate students to explore patterns without implying unsupported causation.

## 2. **Introduction**

Electricity systems differ across countries and change over time as demand, resources,
technology and policy evolve. A country may generate a large amount of renewable
electricity because its power system is large, while another may generate a smaller
amount but have a higher renewable share. The project therefore considers both
generation (TWh) and renewable share of electricity generation (%).

The approved research question is: **How have renewable electricity generation and
its share changed across countries, and how do country renewable electricity mixes
differ?** The intended audience is general audiences and undergraduate students. The
dashboard's storytelling sequence begins with geographic differences, then traces
trends, separates technology measures, explores GDP association, ranks countries for
a selected year, and ends with direct country-transition comparisons.

## 3. **Related Work**

Our World in Data (OWID) publishes energy and electricity data with documentation
describing source compilation, indicator units and methodological changes. This
project builds on that open-data context and the definitions in its energy codebook,
while adapting an available Kaggle CSV snapshot into a student-scale interactive
story. The dashboard is not a replacement for the underlying source or a claim of new
causal research. It emphasizes country-level comparisons, explicit coverage, and the
difference between total generation and generation share.

OWID documents renewable electricity share as a percentage of total electricity
produced and renewable electricity generation in TWh. Its codebook describes GDP as
adjusted for inflation and cross-country living costs in 2011 international dollars.
The Kaggle CSVs do not record a release identifier, so the exact version match to the
current online documentation remains uncertain.

## 4. **Methodology and Workflow**

### Data and preparation

The local dataset files are `data/renewable_energy_by_country.csv` and
`data/renewable_energy_by_region.csv`, from the Kaggle dataset
[Global Renewable Energy by Country (1900–2025)](
https://www.kaggle.com/datasets/riyagarg0314/global-renewable-energy-by-country-1900-2025).
The country file contains 17,265 entity-year rows for 220 labels and 29 source
columns. The region file contains 6,112 rows for 94 labels and 29 columns. Both span
1900–2025 as a row-level year range, but that is not the coverage of every variable.

The source columns `renewables_share_energy`, `renewables_share_elec` and
`renewables_electricity` each appear twice. The two occurrences were compared cell
by cell in both files and were identical. `data_prep.py` validates that equality and
then excludes the redundant copy; if the copies differ, loading stops with an error.
The original CSVs remain unchanged. The initial inspection found zero exact duplicate
rows and zero duplicate country-year keys in each file.

Numeric columns are converted with pandas while recording invalid nonblank values.
Year is made an integer. Missing values are retained and filters are specific to the
chart's variables. No interpolation, zero filling, derived “other” residual, or
technology aggregation is performed. The regional data remains separate because its
labels represent potentially overlapping aggregates and the regional file has no
country ISO codes.

### Coverage and variable definitions

Renewable electricity share has 6,551 country observations from 1985 to 2025.
Renewable electricity generation has 7,897 from 1965 to 2025. GDP has 11,559 from
1900 to 2022. In 2022, 212 country records contain renewable share, while 2025 has
only 90. These counts are variable-level observations, not proof that every year is
comparable for an unchanged set of countries.

The codebook describes `renewables_share_elec` as a percentage of electricity
generated, and generation fields such as `renewables_electricity`, `hydro_electricity`,
`solar_electricity`, and `wind_electricity` in TWh. `gdp` is in 2011 international
dollars. GDP observations do not extend beyond 2022. These meanings are disclosed in
the application and supplementary methodology notes.

### Dashboard and interaction

Python, pandas, Streamlit and Plotly were selected for a locally runnable, open-source
interactive dashboard. The six views are:

1. A selected-year map of renewable electricity share, with map-code and coverage
   caveats.
2. A share time series with country and year-range selectors, animated year frames,
   Play/Pause, step-forward and reset endpoint controls. Missing years are not joined.
3. Separate source-generation lines for hydro, wind, solar and other renewables, in
   TWh; there is no stacked total.
4. A selected-year GDP/share scatter using complete cases and a non-causal
   interpretation.
5. A sorted country ranking for a selected year, with valid sample size and tied
   values sharing minimum rank.
6. A 2–4 country transition comparison with separate share (%) and generation (TWh)
   charts and a reset control.

Controls and hover tooltips expose actual values and let users select years,
countries, technologies and ranking direction. A sidebar country supplies defaults
to linked views. Missing data remain missing, and views explain what their counts
include.

## 5. **Timeline and Evaluation**

The work is organized in practical stages: inspect the supplied files; implement and
test reproducible preparation; build the six required views; verify calculations and
boundary behavior; then review the documentation and presentation. The core
implementation and test scripts are provided in this workspace.

Automated tests cover CSV loading, expected schema, duplicate-header equality,
filtering, missing values, ranking order/ties, GDP complete cases, percentage format,
separate regional handling and empty selections. A real-data numerical check compares
the 2022 valid-share count (212 countries) and top-five ranking output against an
independent filter and sort. A boundary test asks for Afghanistan's renewable share
in 1900 and expects no observation. Test execution results are recorded in
`report/evaluation_and_verification.md` only after the command is run.

Evaluation should also include a manual browser check of map readability, chart
hover, the animation controls, selected filters, empty states and the six screenshot
captures. The supplied files are local; public deployment is not claimed.

## 6. **Contingency and Collaboration**

If recent-year coverage is sparse, show counts and restrict claims to observed
countries; do not extrapolate. If a country has no reliable map code, omit it from
the mapped layer while keeping the table and country views available. If indicator
definitions or technology compatibility are unclear, retain separate source
indicators and do not derive totals. If installation fails, use the provided
`requirements.txt` in a clean virtual environment and run from the project root. If
charts are slow or time is limited, prioritize correctness, the six core views,
tests, and clear documentation over optional polish. If public deployment is not
available, demonstrate the reproducible local Streamlit app.

The project work is carried out by the student. AI assistance supported planning,
code implementation, debugging and documentation. No contribution by an unknown
teammate is claimed. The student should review the code, run the tests and dashboard,
and be able to explain decisions before submission.

## 7. **Conclusion**

The dashboard makes country renewable-electricity shares and generation comparable
through multiple views, while showing the limits of the supplied data. Renewable
share coverage begins in 1985, generation coverage begins in 1965, GDP ends in 2022,
and 2025 share coverage is notably sparse. Therefore the project supports
year-specific and observed-data comparisons rather than a complete global ranking
for every year or an unsupported global average. Future work could verify the exact
Kaggle export lineage, improve geographic crosswalks, and compare a consistent
country cohort across explicitly documented time windows.

## 8. **References**

1. Garg, Riya. *Global Renewable Energy by Country (1900–2025)*. Kaggle.
   https://www.kaggle.com/datasets/riyagarg0314/global-renewable-energy-by-country-1900-2025
2. Our World in Data. *Data on Energy by Our World in Data*.
   https://github.com/owid/energy-data
3. Our World in Data. *OWID Energy Codebook*.
   https://github.com/owid/energy-data/blob/master/owid-energy-codebook.csv
4. Bolt, Jutta, and Jan Luiten van Zanden. “Maddison style estimates of the evolution
   of the world economy: A new 2023 update.” *Journal of Economic Surveys* (2024).
   https://doi.org/10.1111/joes.12618
5. Streamlit documentation. https://docs.streamlit.io/
6. Plotly Python documentation. https://plotly.com/python/

AI-use disclosure: AI assistance supported planning, code generation/editing,
debugging, and writing. The student is responsible for reviewing and understanding
the implementation and verifying the final submission.

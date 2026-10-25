# Powering the Future

**Exploring Renewable Electricity Across Countries and Time**

An interactive Streamlit dashboard for the approved project question:

> How have renewable electricity generation and its share changed across countries,
> and how do country renewable electricity mixes differ?

The primary dataset is the supplied country CSV. The optional regional CSV remains a
separate dataset and is not appended to country observations.

## Run locally (Windows / VS Code)

1. Open this project folder in VS Code.
2. In the integrated PowerShell terminal, create and activate a virtual environment:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   If PowerShell blocks activation, use the environment's interpreter directly:

   ```powershell
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
   .\.venv\Scripts\python.exe -m streamlit run app.py
   ```

3. Install project dependencies:

   ```powershell
   python -m pip install -r requirements.txt
   ```

4. Start the dashboard from the project root:

   ```powershell
   python -m streamlit run app.py
   ```

   Open the local URL Streamlit prints (normally `http://localhost:8501`).
   No paid API or internet access is required at application runtime.

5. Run the verification tests in another terminal:

   ```powershell
   python -m unittest -v
   ```

The two CSVs must remain in `data/` with their supplied names.

## Project files

- `app.py` — Streamlit storytelling dashboard and six interactive views.
- `data_prep.py` — reusable loading, conversion, validation, filtering, and ranking.
- `tests.py` — automated tests using the real CSVs and targeted boundary cases.
- `.streamlit/config.toml` — light burgundy/ivory application theme, independent of the operating system's dark-mode preference.
- `data/` — the original downloaded CSVs; the app does not modify them.
- `report/` — project methodology, evaluation, sources, presentation plan, and report.
- `screenshots/` — reserved for genuine screenshots captured from the running app.

## Data and decisions

- Dataset: [Kaggle — Global Renewable Energy by Country (1900–2025)](https://www.kaggle.com/datasets/riyagarg0314/global-renewable-energy-by-country-1900-2025).
- Supporting field definitions: [Our World in Data energy documentation](https://github.com/owid/energy-data) and [codebook](https://github.com/owid/energy-data/blob/master/owid-energy-codebook.csv).
- Renewable electricity share is measured as a percent of total electricity generated; generation fields are TWh.
- GDP is documented as 2011 international dollars in the matching OWID codebook.
- Three duplicate column pairs were checked cell by cell and found identical. The loader only removes the repeated copies after checking equality.
- Blank values remain missing. No zeros are inserted, no values are interpolated, and no rows are deleted merely for missing unrelated fields.
- The regional data is not merged with country data. Regional labels can overlap and the file has no ISO country codes.
- Recent observations are uneven. The dashboard exposes selected-year coverage and warns that 2025 is sparse.
- The page uses a burgundy-and-ivory editorial design, a shared country exploration bar, six linked chapter anchors, and a dark timeline view. The shared country feeds the share-trend and technology views; chapter-specific filters remain independent.

See [methodology and workflow](report/methodology_and_workflow.md),
[evaluation and verification](report/evaluation_and_verification.md),
[references and data sources](report/references_and_data_sources.md), and the
[midterm report](report/midterm_report.md).

## Screenshot checklist

Capture screenshots from the actual running dashboard after choosing representative
settings. Do not use mockups. Save one image for each required visualization:

- [ ] `screenshots/01-world-map.png` — show map year and visible coverage note.
- [ ] `screenshots/02-share-over-time.png` — show selected countries and animation controls.
- [ ] `screenshots/03-technology-comparison.png` — show technologies and TWh axis.
- [ ] `screenshots/04-gdp-share.png` — show selected year and complete-case count.
- [ ] `screenshots/05-country-rankings.png` — show year, direction, and valid count.
- [ ] `screenshots/06-transition-comparison.png` — show at least two selected countries.

In VS Code, run the app, scroll each view into position, and use Windows Snipping Tool
or `Win+Shift+S`. These screenshot files are not included until you capture them.

## AI-use disclosure

AI assistance was used to help implement and document the data preparation, dashboard,
and tests. The student should review the code, run the app and tests, verify the data
interpretations, and understand the final submission before presenting it.

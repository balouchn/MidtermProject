# References and data sources

1. Riya Garg. **Global Renewable Energy by Country (1900–2025)**. Kaggle dataset.
   https://www.kaggle.com/datasets/riyagarg0314/global-renewable-energy-by-country-1900-2025
   (Accessed 2026-10-23). The project uses the two CSV files supplied in `data/`.
   The Kaggle page and local CSVs do not identify the exact export version.

2. Our World in Data. **Data on Energy by Our World in Data**. Dataset documentation
   and source-method notes. https://github.com/owid/energy-data (Accessed 2026-10-23).
   The documentation describes energy, electricity-mix data, source compilation and
   changes across releases.

3. Our World in Data. **OWID Energy Codebook**. Variable descriptions, units and
   source attribution.
   https://github.com/owid/energy-data/blob/master/owid-energy-codebook.csv
   (Accessed 2026-10-23). Used to interpret GDP, electricity generation, renewables
   share, technology generation and share fields.

4. Bolt, Jutta, and Jan Luiten van Zanden. **Maddison style estimates of the evolution
   of the world economy: A new 2023 update**. *Journal of Economic Surveys* (2024).
   DOI: https://doi.org/10.1111/joes.12618. The codebook attributes the GDP measure
   to the Maddison Project Database 2023; the paper is cited as background for that
   underlying GDP series.

5. Streamlit. **Streamlit documentation**. https://docs.streamlit.io/ (Accessed
   2026-10-23). Used as documentation for the local interactive application framework.

6. Plotly. **Plotly Python documentation**. https://plotly.com/python/ (Accessed
   2026-10-23). Used as documentation for interactive charts and animation controls.

## Citation and version caveat

Credit both the Kaggle dataset and its upstream data providers in presentations or
reports. The Kaggle page links the data source; the exact transformation/export
version of these local CSVs is not recorded in the files. Do not imply that the
current online OWID release is byte-for-byte identical to the downloaded snapshot.

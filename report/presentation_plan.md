# 15-minute presentation plan

## Timed agenda

| Time | Segment |
|---|---|
| 0:00–1:00 | Introduce the research question and why both share and generation matter |
| 1:00–2:00 | Explain the Kaggle country dataset, source definitions, and missing-data limitation |
| 2:00–4:00 | View 1: map; change year and inspect a country value |
| 4:00–6:00 | View 2: select countries and range; demonstrate Play, Pause, step, reset, and hover |
| 6:00–7:30 | View 3: toggle hydro, wind, solar, and other generation; explain separate TWh lines |
| 7:30–9:00 | View 4: GDP/share complete-case scatter; explain non-causal interpretation |
| 9:00–10:30 | View 5: switch year and top/bottom rankings; discuss valid counts and ties |
| 10:30–12:30 | View 6: compare 2–4 country transitions; demonstrate reset and value inspection |
| 12:30–13:00 | State a data-grounded takeaway and key limitations |
| 13:00–15:00 | Class discussion and interactive question |

The first 13 minutes are explanation and demonstration; the last two minutes are
discussion.

## Opening explanation

“This project asks how renewable electricity generation and its share have changed
across countries, and how the renewable electricity mix differs. A share tells us
what fraction of electricity generation is renewable, while TWh measures the amount
generated. They answer related but different questions.”

## Live demonstration checklist

1. Start at the title and point to the 1985–2025 share coverage and 1965–2025
   generation coverage.
2. On the map, choose 2022, inspect the coverage note, and select a mapped country.
3. On the share trend, choose two countries, set 2000–2022, hover a point, play,
   pause, step forward and reset the endpoint.
4. Toggle individual technologies and explain that separate lines avoid implying
   complete/additive categories.
5. Select 2022 in the GDP view and explain complete-case filtering and why association
   does not prove causation.
6. Change the ranking year/direction and point out the valid country count and tie
   rule.
7. Select 2–4 countries in the final view, inspect shares and TWh separately, and
   restore the default comparison.

## Data limitation and numerical verification

The 2025 share measure has only 90 country rows, compared with 212 in 2022. A sparse
year should not be presented as a complete country comparison. The reproducible
numerical check filters the real file to 2022 and nonmissing renewable shares:
**212 distinct countries**. The test independently sorts those same observed values
and compares the top-five names and values with the ranking helper. The script's
actual test result should be checked before the presentation.

## Conclusion

The charts permit defensible observed-data comparisons, but coverage changes across
indicators and years. The presentation should describe patterns visible in the
selected observations and avoid claiming that the sample is complete, that GDP causes
renewable generation, or that one technology's incomplete values sum to a total.

## Interactive class question

“If you were comparing countries' renewable transitions, would you rather compare
renewable share, total renewable TWh, or both—and what could each measure hide?”

## Likely questions

**Why are there no values for every country in the oldest years?**  
The file includes rows from 1900, but the electricity indicators have much shorter
coverage. Missing values are not assumed to mean zero.

**Why not add hydro, solar, wind, and other renewables?**  
This dashboard avoids assuming those source columns are fully compatible, mutually
exclusive and complete for every row. It compares them as separate indicators.

**Does GDP increase renewable adoption?**  
The scatter is observational and uses complete cases; it cannot establish cause.

**Why show the 2025 selector if coverage is sparse?**  
It can be explored, but the app reports coverage and warns against treating it as a
complete country comparison.

**Why keep the region file?**  
It is preserved as optional supporting data, but region labels can overlap and lack
country ISO identifiers, so it is not merged with country records.

**What did AI do?**  
AI assisted implementation, debugging and documentation. The student should review
and explain the code, rerun tests and verify the local app before submission.

# Data provenance and preprocessing

The processed CSVs in this project reproduce the results verified in Google Colab by the student:

- Population: 55,062 rows after restricting to 2020–2025 and `ethnicity=overall`. The fuller 385,434-row ethnic-disaggregated version is unnecessary for the selected three charts.
- Poverty: 322 rows; 2022=160, 2024=162, 150 exact matched districts across years. No data were interpolated for missing years.
- Teachers: 5,901 rows, with sex-total validation showing no inconsistencies.

Data originate from OpenDOSM and the raw originals attached in the conversation. Legitimate zero observations were preserved; no statistical imputations were performed.

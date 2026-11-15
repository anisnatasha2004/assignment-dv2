# Malaysia Scientific Visualisation Dashboard | 2020–2025

**Three datasets · Three pages · Nine scientific visualisations · Built for Streamlit Community Cloud**

This project implements one visualisation objective per dataset, with three charts, a summary box and interpretations for each page. All CSVs are already cleaned and included. **Google Colab is optional and not required to deploy**.

## Dataset objectives and visualisations

| Page | Objective | Visualisations |
|------|-----------|----------------|
| 1 — Population | Analyse trends, geographical differences and age–sex structure, 2020–2025 | Annual line chart; top-10 district ranking; age–sex population pyramid |
| 2 — Household Poverty | Examine spatial inequalities, association of poverty indicators and changes in matched districts, 2022–2024 | Top-10 absolute poverty ranking; absolute-vs-relative scatter; diverging change chart |
| 3 — Teachers | Compare government-school teacher staffing trends, district variation and gender composition, 2020–2025 | Primary/secondary line chart; district ranking; stacked male–female chart |

Official OpenDOSM datasets: [population_district](https://open.dosm.gov.my/data-catalogue/population_district), [hh_poverty_district](https://open.dosm.gov.my/data-catalogue/hh_poverty_district), [teachers_district](https://open.dosm.gov.my/data-catalogue/teachers_district). The teacher counts originate from education administrative records.

## Upload to GitHub

1. Extract the supplied ZIP on your computer.
2. Open the extracted folder. In GitHub, open the repository and select **Add file → Upload files**.
3. Upload **all contents** of this folder, preserving the `pages/`, `data/processed/`, and `.streamlit/` paths. In particular, `app.py` and `requirements.txt` must be in the **repository root**.
4. Do **not** upload the ZIP itself or a `.venv` folder.
5. Select **Commit changes**.

Expected layout:

```text
app.py
analytics.py
charts.py
ui.py
requirements.txt
pages/
  population_page.py
  poverty_page.py
  teachers_page.py
data/
  processed/
    population_2020_2025.csv
    poverty_2020_2025.csv
    teachers_2020_2025.csv
.streamlit/
  config.toml
```

## Deploy on Streamlit Community Cloud

1. Open https://share.streamlit.io/ and sign in with your GitHub account.
2. Select **Create app → Yup, I have an app**.
3. Select your GitHub repository and branch `main`.
4. For **Main file path**, type exactly **`app.py`**.
5. Select **Deploy**. Once active, copy the `*.streamlit.app` URL for your assignment.

Streamlit automatically installs the libraries from `requirements.txt`.

## Run locally (optional)

```powershell
py -m pip install -r requirements.txt
py -m streamlit run app.py
```

## Data processing and interpretation caveats

- **Population (2020–2025):** 55,062 analysis-ready records. Original population records contain overlapping sex, ethnicity and age categories. This deployment CSV keeps `ethnicity=overall`; chart functions select `sex=both, age=overall` for total population, and age-by-sex detail for the population pyramid. Population values are **in thousands of people**. There are 160 district records per year in 2020–2024 and 166 in 2025, reflecting changing geographic detail.
- **Poverty (2022 and 2024 only):** 322 rows. The file provides only 2022 and 2024 survey snapshots within the requested range. The 2024 dataset lacks Perlis and three federal territories. There are **150 exactly matched districts**, of which **122** recorded declines, **23** increases and **5** no change in absolute poverty rates. Unweighted district statistics must not be mistaken for national estimates.
- **Teachers (2020–2025):** 5,901 rows. National/state `All Districts` rows are distinct from individual district rows. For national totals select `state=Malaysia`, `district=All Districts`, `sex=both` and sum primary and secondary only. For gender composition select male and female rows; **do not add `both` again**. All 0 sex-total consistency differences were checked in the supplied Colab steps.

## Assignment submission

Capture figures 1.1–3.3 from the deployed app, include the objective statements and data interpretations in a report of no more than five pages, export it to PDF, and submit the Streamlit URL together with the PDF. The initial assignment brief specifies one dataset, while this version uses three, per the later project requirements.

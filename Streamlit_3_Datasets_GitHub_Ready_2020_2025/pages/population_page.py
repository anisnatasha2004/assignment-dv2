"""Page 1: Population — one dataset, three scientific visualisations."""
import pandas as pd
import streamlit as st
from analytics import AGE_ORDER, population_annual, population_overall, population_ranking, population_age_sex
from charts import population_trend, population_ranking as population_ranking_chart, population_pyramid
from ui import read_dataset, page_header, figure, csv_download

raw = read_dataset('population')
# Source has mutually overlapping ethnicity, sex and age subtotals. We keep
# ethnicity=overall; the pure data functions choose each appropriate age/sex grain.
df = raw[raw['ethnicity'] == 'overall']

st.sidebar.subheader('Population filters')
state = st.sidebar.selectbox('Geographic scope',
                             ['Malaysia'] + sorted(df['state'].unique().tolist()), key='pop_state')
year = st.sidebar.slider('Reference year', min_value=2020, max_value=2025,
                         value=2025, step=1, key='pop_year')

page_header('Population by District',
            'Dataset 1 / 3 · Malaysia · 2020–2025 · Population measured in thousands',
            'Examine population growth, differences between districts, and the age–sex distribution.',
            'population')

annual = population_annual(df, state)
ref = float(annual.loc[annual['year'] == year, 'population'].iloc[0])
baseline = float(annual.loc[annual['year'] == 2020, 'population'].iloc[0])
growth = 100 * (ref / baseline - 1) if baseline else None
key_count = len(population_overall(df, state).query('year == @year'))

st.subheader('Summary box')
c1, c2, c3 = st.columns(3)
c1.metric(f'Population · {year}', f'{ref/1000:,.2f} million')
c2.metric('Change since 2020', 'N/A' if growth is None else f'{growth:+.1f}%')
c3.metric(f'District keys · {year}', f'{key_count:,}')
st.caption('Population units: **thousand persons** in charts; million persons in the summary box. District keys reflect administrative units recorded for the selected year.')

first = float(annual.iloc[0]['population'])
last = float(annual.iloc[-1]['population'])
diff_pct = 100*(last/first-1) if first else 0
trend = ('increased' if last >= first else 'decreased')
figure('Figure 1.1 — Population trend, 2020–2025', population_trend(annual, state),
       f'Across {state}, the combined district estimates {trend} from {first/1000:,.2f} million persons in 2020 '
       f'to {last/1000:,.2f} million in 2025 ({diff_pct:+.1f}%). '
       'This is a descriptive population estimate, not evidence of a specific cause of change.',
       'Line chart · Source category: sex=both, age=overall, ethnicity=overall; districts summed once per year.')

ranked = population_ranking(df, year, state, n=10)
top = ranked.iloc[-1]
share = 100 * float(top['population']) / ref if ref else 0
figure(f'Figure 1.2 — Largest districts in {year}', population_ranking_chart(ranked),
       f'{top["district"]} ({top["state"]}) has the largest recorded population in this selection, '
       f'at {top["population"]:,.1f} thousand people, about {share:.1f}% of the selected geographic total. '
       'Rankings compare district sizes in the same year, avoiding year-to-year boundary ambiguities.',
       'Horizontal bar chart · Ten highest-population districts (or fewer if the chosen state has fewer districts).')

wide = population_age_sex(df, year, state)
wide['both'] = wide['male'] + wide['female']
max_age = wide.loc[wide['both'].idxmax(), 'age']
older = float(wide.loc[wide['age'].isin(['65-69','70-74','75-79','80-84','85+']), 'both'].sum())
age_total = float(wide['both'].sum())
older_share = 100 * older / age_total if age_total else 0
figure(f'Figure 1.3 — Age–sex population pyramid, {year}', population_pyramid(wide),
       f'The largest five-year age group is {max_age} years. People aged 65 and older account for '
       f'approximately {older_share:.1f}% of the age-group population total in {state}. '
       'The pyramid shows how sex and age structure vary; minor differences from overall totals may arise from source rounding.',
       'Mirrored horizontal bars · Male on the left, female on the right; counts are in thousands.')

st.info('Comparability note: the uploaded population file has 160 districts per year in 2020–2024 and 166 in 2025. '
        'Interpret changes in individual district boundaries cautiously; annual national/state totals are more suitable for broad trends.')
csv_download(df[(df['year'] == year) & ((df['state']==state) if state != 'Malaysia' else True)],
             f'population_{state.replace(" ", "_")}_{year}')

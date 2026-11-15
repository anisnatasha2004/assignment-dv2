"""Page 3: Government-school teachers — school stage, geography and sex."""
import pandas as pd
import streamlit as st
from analytics import teachers_annual, teachers_ranking, teachers_sex_by_stage
from charts import teachers_trend, teachers_ranking as teacher_rank_chart, teachers_sex_chart
from ui import read_dataset, page_header, figure, csv_download

df = read_dataset('teachers')
st.sidebar.subheader('Teacher filters')
state = st.sidebar.selectbox('Geographic scope',
                             ['Malaysia'] + sorted(x for x in df['state'].unique() if x != 'Malaysia'),
                             key='teachers_state')
year = st.sidebar.slider('Reference year', 2020, 2025, value=2025, step=1, key='teachers_year')

page_header('Government-School Teachers by District',
            'Dataset 3 / 3 · Malaysia · 2020–2025 · Primary and secondary government schools',
            'Compare annual teacher staffing by school stage, district variation, and the sex composition of teachers.',
            'teachers')

annual = teachers_annual(df, state)
selected = annual[annual['year'] == year]
total = int(selected['teachers'].sum())
primary = int(selected.loc[selected['stage']=='primary', 'teachers'].sum())
secondary = int(selected.loc[selected['stage']=='secondary', 'teachers'].sum())
st.subheader('Summary box')
cols = st.columns(3)
cols[0].metric(f'Total teachers · {year}', f'{total:,}')
cols[1].metric('Primary-school teachers', f'{primary:,}')
cols[2].metric('Secondary-school teachers', f'{secondary:,}')
st.caption('Totals use the official state/national “All Districts” aggregation and sex=both; '
           'they do not add state totals and district totals together.')

first_total = int(annual[annual['year']==2020]['teachers'].sum())
last_total = int(annual[annual['year']==2025]['teachers'].sum())
trend = last_total - first_total
figure('Figure 3.1 — Teacher counts by school stage, 2020–2025', teachers_trend(annual),
       f'Government primary and secondary schools together report {last_total:,} teachers in 2025, '
       f'compared with {first_total:,} in 2020 (change: {trend:+,} teachers). '
       'The separate lines help identify whether staff counts changed differently across education stages.',
       'Multi-series line graph · The observations are annual administrative snapshots, not monthly averages.')

ranked = teachers_ranking(df, year, state)
if len(ranked):
    top = ranked.iloc[-1]
    figure(f'Figure 3.2 — Districts with most teachers, {year}', teacher_rank_chart(ranked),
           f'{top["district"]} ({top["state"]}) has the largest teacher count among the displayed districts, '
           f'with {int(top["teachers"]):,} government-school teachers across the primary and secondary stages. '
           'A high count does not by itself indicate good or bad teacher supply because student enrolment is not included.',
           'District ranking · Primary + secondary counts with sex=both, excluding state and national aggregate rows.')
else:
    st.warning('No separate district rows available for the selected area and year.')

sex_view = teachers_sex_by_stage(df, year, state)
female = int(sex_view.loc[sex_view['sex']=='female','teachers'].sum())
share = female * 100 / total if total else 0
figure(f'Figure 3.3 — Teacher composition by sex and stage, {year}', teachers_sex_chart(sex_view),
       f'Female teachers represent {share:.1f}% of the {year} government-school teacher workforce '
       f'in {state} ({female:,} out of {total:,} teachers). '
       'The stage-level bars reveal how male and female teacher counts differ between primary and secondary schooling.',
       'Stacked bar chart · Male and female counts sum to the stage total; sex=both rows are excluded.')

st.info('Reference-date note: 2020–2022 records in this CSV are dated 1 January; 2023–2025 records '
        'are dated 30 June. The line chart compares annual published observations, not identically timed daily censuses.')
csv_download(df[(df['year']==year) & ((df['state']==state) if state!='Malaysia' else True)],
             f'teachers_{state.replace(" ","_")}_{year}')

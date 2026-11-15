"""Page 2: District poverty. Only observed survey years; no imputation."""
import pandas as pd
import streamlit as st
from analytics import poverty_view, poverty_changes
from charts import poverty_ranking, poverty_scatter, poverty_change
from ui import read_dataset, page_header, figure, csv_download

df = read_dataset('poverty')
st.sidebar.subheader('Household poverty filters')
years = sorted(df['year'].unique().tolist(), reverse=True)
year = st.sidebar.selectbox('Survey year (available)', years, key='poverty_year')
# Important: 2024 has no rows for 4 geographic areas; do not permit invalid selection.
available_states = sorted(df.loc[df['year'] == year, 'state'].unique().tolist())
state = st.sidebar.selectbox('Geographic scope', ['Malaysia'] + available_states,
                             key='poverty_state')

page_header('Household Poverty by District',
            'Dataset 2 / 3 · Malaysia · 2022 and 2024 only · Percentages (%)',
            'Examine geographical differences in poverty rates, their association, and changes in matched districts.',
            'poverty')
st.info('**Data availability:** The selected 2020–2025 window contains published district-level observations '
        '**only for 2022 and 2024**. This dashboard does not interpolate other years. The 2024 file has '
        'no observations for Perlis, W.P. Kuala Lumpur, W.P. Labuan, or W.P. Putrajaya.')

view = poverty_view(df, year, state)
changes = poverty_changes(df, state)
if view.empty:
    st.warning('No observations available for this year and geographic selection.')
    st.stop()

st.subheader('Summary box')
cols = st.columns(4)
cols[0].metric(f'District observations · {year}', f'{len(view):,}')
cols[1].metric('Median absolute poverty', f'{view["poverty_absolute"].median():.1f}%')
cols[2].metric('Median relative poverty', f'{view["poverty_relative"].median():.1f}%')
cols[3].metric('Matched districts · 2022/24', f'{len(changes):,}')
st.caption('Rate summaries are unweighted statistics over districts, not official national rates. '
           'Changes require exact district-name matches in both years.')

top = view.nlargest(1, 'poverty_absolute').iloc[0]
figure(f'Figure 2.1 — Highest absolute poverty by district, {year}', poverty_ranking(view, state=state),
       f'{top["district"]} ({top["state"]}) has the highest absolute poverty rate among the selected '
       f'districts at {top["poverty_absolute"]:.1f}%. The chart compares the prevalence of poverty among '
       'households, not the total count of people living in poverty.',
       'Horizontal bar chart · District absolute poverty rates (%).')

corr = view[['poverty_absolute', 'poverty_relative']].corr().iloc[0, 1] if len(view) >= 2 else float('nan')
if pd.notna(corr):
    corr_text = f'Pearson correlation is r={corr:+.3f} for the selected districts. '
else:
    corr_text = 'There are insufficient varying observations to calculate Pearson correlation. '
figure(f'Figure 2.2 — Absolute and relative poverty, {year}', poverty_scatter(view, state),
       corr_text + 'The two measures use different poverty thresholds; the correlation is descriptive '
       'and does not demonstrate causation.',
       'Scatter plot · Each marker is a district. Both axes show household rates in percent.')

if not changes.empty:
    biggest = changes.loc[changes['change_pp'].idxmin()]
    improved = int((changes['change_pp'] < 0).sum())
    worsened = int((changes['change_pp'] > 0).sum())
    unchanged = int((changes['change_pp'] == 0).sum())
    text = (f'{len(changes)} districts matched across 2022 and 2024; absolute poverty fell in '
            f'{improved}, rose in {worsened}, and was unchanged in {unchanged}. '
            f'The largest decline occurred in {biggest["district"]} ({biggest["state"]}), '
            f'at {biggest["change_pp"]:+.1f} percentage points. This describes a change '
            'in the reported rate, not its causes.')
    figure('Figure 2.3 — Change in district absolute poverty, 2022–2024', poverty_change(changes),
           text, 'Diverging bar chart · Twelve largest changes among districts observed in both years; percentage points.')
else:
    st.warning('No matched districts available for a 2022–2024 comparison in this geographic selection.')

st.info('**Interpretation limitation:** district coverage changes across survey years. '
        'The 2024 state coverage differs from 2022, so an unweighted average over all rows '
        'is not a like-for-like national poverty estimate.')
csv_download(view, f'poverty_{state.replace(" ","_")}_{year}')

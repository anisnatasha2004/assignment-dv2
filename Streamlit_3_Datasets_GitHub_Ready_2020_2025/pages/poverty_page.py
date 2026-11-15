"""Page 2: Household poverty patterns across Malaysian districts in 2024.

This page presents one survey year only. It does not calculate change since 2022.
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from analytics import poverty_view
from charts import finish, poverty_ranking, poverty_scatter
from ui import read_dataset, page_header, figure, csv_download

YEAR = 2024

# District-level poverty rates, not counts of poor households.
raw = read_dataset('poverty')
data_2024 = raw.loc[raw['year'] == YEAR].copy()
if data_2024.empty:
    st.error('No household poverty observations for 2024 were found in the CSV file.')
    st.stop()

st.sidebar.subheader('Household poverty filters')
state = st.sidebar.selectbox(
    'Geographic scope',
    ['Malaysia'] + sorted(data_2024['state'].dropna().unique().tolist()),
    key='poverty_state',
)
st.sidebar.caption('Reference year: **2024** (fixed)')

page_header(
    'Household Poverty Analysis (2024)',
    'Dataset 2 / 3 · 2024 · District-level household poverty rates (%)',
    'To examine geographic disparities in absolute and relative poverty rates '
    'across Malaysian districts in 2024, including their statistical association '
    'and distribution across states.',
    'poverty',
)

st.info(
    '**Data coverage:** The 2024 dataset contains district observations for '
    '**12 states**; it has no 2024 records for Perlis, W.P. Kuala Lumpur, '
    'W.P. Labuan or W.P. Putrajaya. These locations are not interpreted as '
    'having zero poverty.'
)

view = poverty_view(data_2024, YEAR, state)
if view.empty:
    st.warning('No 2024 observations are available for this geographic selection.')
    st.stop()

# SUMMARY: descriptive statistics over observed districts, not national poverty.
median_absolute = float(view['poverty_absolute'].median())
median_relative = float(view['poverty_relative'].median())
max_row = view.loc[view['poverty_absolute'].idxmax()]

st.subheader('Summary box')
c1, c2, c3, c4 = st.columns(4)
c1.metric('District observations', f'{len(view):,}')
c2.metric('Median absolute poverty', f'{median_absolute:.1f}%')
c3.metric('Median relative poverty', f'{median_relative:.1f}%')
c4.metric('Highest absolute poverty', f'{float(max_row["poverty_absolute"]):.1f}%')
st.caption(
    f'These are unweighted statistics across observed districts in {state}, '
'not official population-weighted national or state poverty rates.'
)

# FIGURE 2.1: Top 10 absolute poverty rates for the selected geographic scope.
top = view.nlargest(1, 'poverty_absolute').iloc[0]
figure(
    'Districts with the highest absolute poverty (2024)',
    poverty_ranking(view, n=10, state=state),
    f'The highest absolute poverty rate among districts in {state} is '
    f'{float(top["poverty_absolute"]):.1f}%, recorded in '
    f'{top["district"]} ({top["state"]}). '
    'The chart ranks household poverty *rates* rather than numbers of poor households.',
    'Horizontal bar chart · Up to 10 districts · Absolute household poverty rate (%).',
)

# FIGURE 2.2: Association between two different poverty measures.
r = view[['poverty_absolute', 'poverty_relative']].corr().iloc[0, 1]
if pd.isna(r):
    association = (
        'Pearson correlation cannot be calculated for this selection because '
        'there are insufficient observations or variation in the rates. '
    )
else:
    direction = 'positive' if r > 0 else 'negative' if r < 0 else 'zero'
    association = (
        f'Across the {len(view)} observed districts in {state}, Pearson '
        f'correlation between absolute and relative poverty is r = {r:+.3f}, '
        f'indicating a {direction} linear association. '
    )
figure(
    'Absolute versus relative poverty (2024)',
    poverty_scatter(view, state=state),
    association +
    'The two measures use different poverty thresholds. Their relationship is '
    'descriptive and does not establish cause and effect.',
    'Scatter plot · Each marker represents one district · Both axes are rates (%).',
)

# FIGURE 2.3: All-state context, showing the percentage of districts in each
# absolute-poverty-rate band. Normalising by district count prevents states
# with many districts from automatically dominating the heatmap.
bins = [-0.001, 5, 10, 20, 30, float('inf')]
labels = ['0–<5%', '5–<10%', '10–<20%', '20–<30%', '30%+']
# right=False means [0,5), [5,10), ... ; negative values are invalid in cleaned data.
all_states = data_2024.copy()
all_states['rate_band'] = pd.cut(
    all_states['poverty_absolute'], bins=bins, labels=labels, right=False
)
count_matrix = (
    all_states.groupby(['state', 'rate_band'], observed=True)
    .size()
    .unstack(fill_value=0)
    .reindex(columns=labels, fill_value=0)
    .sort_index()
)
share_matrix = count_matrix.div(count_matrix.sum(axis=1), axis=0).mul(100.0)
y_labels = [
    f'{name}  ◀ selected' if state != 'Malaysia' and name == state else name
    for name in share_matrix.index
]
heatmap = go.Figure(
    go.Heatmap(
        x=labels,
        y=y_labels,
        z=share_matrix.to_numpy(),
        customdata=count_matrix.to_numpy(),
        colorscale='YlOrRd',
        zmin=0,
        zmax=100,
        colorbar=dict(title='Districts (%)'),
        text=[[f'{value:.0f}%' for value in row] for row in share_matrix.to_numpy()],
        texttemplate='%{text}',
        hovertemplate=(
            'State: %{y}<br>Absolute poverty band: %{x}'
            '<br>Districts: %{customdata}'
            '<br>Share of state districts: %{z:.1f}%<extra></extra>'
        ),
    )
)
heatmap = finish(heatmap, legend=False, height=555)
heatmap.update_layout(
    xaxis_title='Absolute poverty rate band (2024)',
    yaxis_title='',
    margin=dict(l=30, r=45, t=25, b=55),
)
heatmap.update_yaxes(automargin=True, autorange='reversed')

# Dynamic discussion emphasising the high-poverty tail and unequal state coverage.
high_rate = (
    all_states.assign(high_rate=all_states['poverty_absolute'] >= 20)
    .groupby('state', as_index=False)
    .agg(districts=('district', 'size'), high_rate_districts=('high_rate', 'sum'))
)
high_rate['share'] = 100 * high_rate['high_rate_districts'] / high_rate['districts']
leading = high_rate.sort_values(['share', 'high_rate_districts'], ascending=False).iloc[0]
selected_context = (
    f' The row for {state} is marked for comparison with other states.'
    if state != 'Malaysia' else ''
)
figure(
    'District poverty-rate distribution by state (2024)',
    heatmap,
    f'{leading["state"]} has the highest share of observed districts with '
    f'absolute poverty rates of at least 20% '
    f'({int(leading["high_rate_districts"])} of '
    f'{int(leading["districts"])} districts, {leading["share"]:.1f}%). '
    'The heatmap highlights differences in the distribution of district poverty '
    'rates between states; the cells are percentages of districts, not '
    'percentages of poor households.' + selected_context,
    'Heatmap · All 12 covered states · Each row totals 100% of that state’s '
    'observed districts; the state filter highlights a row but does not remove '
    'national comparison rows.',
)

st.info(
    '**Interpretation limitation:** This page uses **2024 only** and cannot '
    'support claims about change over time. Some states and federal territories '
    'have no observations, and unweighted district summaries must not be '
    'treated as official national poverty rates.'
)

csv_download(view, f'poverty_{state.replace(" ", "_")}_2024')

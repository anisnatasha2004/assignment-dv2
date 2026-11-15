"""Page 3: Teacher distribution and gender composition in 2025.

Drop-in replacement for pages/teachers_page.py in the existing Streamlit project.
Uses the original analytics, charts and ui helpers without changing them.
"""

import plotly.graph_objects as go
import streamlit as st

from analytics import teachers_annual, teachers_ranking, teachers_sex_by_stage
from charts import (
    finish,
    teachers_ranking as teachers_ranking_chart,
    teachers_sex_chart,
)
from ui import read_dataset, page_header, figure, csv_download


YEAR = 2025

# Filter once: every indicator and chart on this page uses 2025 only.
# National/state "All Districts" totals overlap with district records, while
# sex="both" overlaps with male and female. Select the right grain per chart.
df = read_dataset('teachers')
df = df[df['year'] == YEAR].copy()

if df.empty:
    st.error('Teacher data for 2025 is unavailable. Check data/processed/teachers_2020_2025.csv.')
    st.stop()

st.sidebar.subheader('Teacher filters')
state_options = ['Malaysia'] + sorted(
    value for value in df['state'].dropna().unique() if value != 'Malaysia'
)
state = st.sidebar.selectbox(
    'Geographic scope', state_options, key='teachers_state'
)
st.sidebar.caption('Reference year: **2025** (fixed)')

page_header(
    'Government-School Teachers Analysis (2025)',
    'Dataset 3 / 3 · 2025 · Primary and secondary government schools',
    'To investigate the geographic distribution and gender composition of '
    'government-school teachers across Malaysian districts and school stages in 2025.',
    'teachers',
)

# Exact 2025 state/national totals: sex=both, district=All Districts.
annual = teachers_annual(df, state)
stage_totals = annual.groupby('stage')['teachers'].sum()

if not {'primary', 'secondary'}.issubset(stage_totals.index):
    st.warning(f'Primary or secondary teacher totals are missing for {state} in 2025.')
    st.stop()

primary = int(stage_totals['primary'])
secondary = int(stage_totals['secondary'])
total = primary + secondary

# For composition, use male and female ONLY (never also sum sex=both).
sex_view = teachers_sex_by_stage(df, YEAR, state)
female = int(sex_view.loc[sex_view['sex'] == 'female', 'teachers'].sum())
male = int(sex_view.loc[sex_view['sex'] == 'male', 'teachers'].sum())
female_share = 100 * female / total if total else 0.0

if female + male != total:
    st.error('Male and female totals do not match the published teacher total.')
    st.stop()

st.subheader('Summary box')
c1, c2, c3, c4 = st.columns(4)
c1.metric('Teachers (2025)', f'{total:,}')
c2.metric('Primary', f'{primary:,}')
c3.metric('Secondary', f'{secondary:,}')
c4.metric('Female teachers', f'{female_share:.1f}%')
st.caption(
    'All figures refer to the selected geographic scope in 2025. Counts use '
    'sex=both for totals; male and female counts are used only for composition.'
)

# FIGURE 3.1 — Largest districts in 2025.
ranked = teachers_ranking(df, YEAR, state, n=10)
if not ranked.empty:
    top = ranked.iloc[-1]
    top_share = 100 * int(top['teachers']) / total if total else 0.0
    figure(
        'Top districts by teacher count (2025)',
        teachers_ranking_chart(ranked),
        f'{top["district"]} ({top["state"]}) records the highest number of '
        f'government-school teachers in the selected comparison: '
        f'{int(top["teachers"]):,} teachers ({top_share:.1f}% of {state}\'s total). '
        'Higher numbers may reflect larger school systems; without student '
        'enrolment data, they cannot be interpreted as teacher adequacy.',
        'Horizontal bar chart · Up to ten districts · primary + secondary, '
        'sex=both; national/state All Districts aggregate rows excluded.',
    )
else:
    st.warning('No separate district-level teacher records for this selection.')

# FIGURE 3.2 — Gender composition by primary/secondary stage.
figure(
    'Teachers by sex and school stage (2025)',
    teachers_sex_chart(sex_view),
    f'Female teachers account for {female_share:.1f}% of the {total:,} '
    f'teachers in {state} ({female:,} female and {male:,} male teachers). '
    f'Primary schools employ {primary:,} teachers, compared with '
    f'{secondary:,} in secondary schools. The bars illustrate the composition '
    'of the teaching workforce, not differences in teaching outcomes.',
    'Stacked bar chart · National/state All Districts totals · male and female '
    'only; sex=both is not added to gender categories.',
)

# FIGURE 3.3 — Nationwide state comparison of two education stages.
# Use state-level aggregation only. Do not add district totals or Malaysia totals.
state_rows = df[
    (df['state'] != 'Malaysia')
    & (df['district'] == 'All Districts')
    & (df['sex'] == 'both')
]
state_stages = state_rows.pivot(
    index='state', columns='stage', values='teachers'
)

if not {'primary', 'secondary'}.issubset(state_stages.columns):
    st.warning('State-level education-stage comparison is unavailable.')
else:
    state_stages = state_stages.dropna(subset=['primary', 'secondary']).copy()
    state_stages['total'] = state_stages['primary'] + state_stages['secondary']
    state_stages = state_stages.sort_values('total', ascending=True)

    axis_labels = [
        f'{name}  (selected)' if state != 'Malaysia' and name == state else name
        for name in state_stages.index
    ]

    comparison = go.Figure()
    comparison.add_bar(
        x=state_stages['primary'],
        y=axis_labels,
        name='Primary',
        orientation='h',
        marker_color='#087e8b',
        customdata=state_stages.index,
        hovertemplate='%{customdata}: %{x:,} primary teachers<extra></extra>',
    )
    comparison.add_bar(
        x=state_stages['secondary'],
        y=axis_labels,
        name='Secondary',
        orientation='h',
        marker_color='#d7833e',
        customdata=state_stages.index,
        hovertemplate='%{customdata}: %{x:,} secondary teachers<extra></extra>',
    )
    comparison = finish(comparison, legend=True, height=620)
    comparison.update_layout(
        barmode='group',
        xaxis_title='Number of government-school teachers',
        yaxis_title='',
        margin=dict(l=25, r=30, t=45, b=45),
    )
    comparison.update_yaxes(automargin=True)

    largest_state = state_stages.iloc[-1]
    largest_name = state_stages.index[-1]
    if state == 'Malaysia':
        discussion = (
            f'{largest_name} has the largest teacher workforce in 2025 '
            f'({int(largest_state["total"]):,} teachers: '
            f'{int(largest_state["primary"]):,} primary and '
            f'{int(largest_state["secondary"]):,} secondary). '
            'Differences across states describe the distribution of staffing, '
            'not staff-to-student ratios.'
        )
    else:
        selected_row = state_stages.loc[state]
        state_rank = int((state_stages['total'] > selected_row['total']).sum() + 1)
        discussion = (
            f'{state} ranks {state_rank} of {len(state_stages)} states and '
            f'federal territories in teacher count, with '
            f'{int(selected_row["primary"]):,} primary and '
            f'{int(selected_row["secondary"]):,} secondary teachers. '
            'The selected state is labelled in the national comparison; '
            'differences in totals may reflect different education-system sizes.'
        )

    figure(
        'Primary and secondary teachers by state (2025)',
        comparison,
        discussion,
        'Grouped horizontal bar chart · All 16 states/federal territories · '
        'sex=both and district=All Districts, excluding Malaysia national aggregate.',
    )

st.info(
    'Methodology: All charts use **2025 only** (published records dated 30 June 2025). '
    'National, state and district rows overlap and must not be added together. '
    'Sex=both overlaps with male and female counts. This page does not analyse '
    'changes over time or teacher-to-student ratios.'
)

export_df = df if state == 'Malaysia' else df[df['state'] == state]


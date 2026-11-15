    'Population is recorded in thousands. The 65+ share uses summed male and '
    'female five-year age groups; source rounding can cause small differences.'
)

# FIGURE 1.1: Largest districts in the selected geographical scope.
ranked = population_ranking(df, YEAR, state, n=10)
if not ranked.empty:
    top = ranked.iloc[-1]
    share = (100 * float(top['population']) / population_thousand) if population_thousand else 0.0
    figure(
        'Figure 1.1 — Top districts by population (2025)',
        population_ranking_chart(ranked),
        f'{top["district"]} ({top["state"]}) has the largest population in the '
        f'selected area, at {top["population"]:,.1f} thousand persons '
        f'({share:.1f}% of the area total). The ranking highlights differences '
        'in population concentration across districts.',
        'Horizontal bar chart · Up to ten districts · sex=both, age=overall, ethnicity=overall.',
    )

# FIGURE 1.2: Population age–sex structure in the selected geography.
if age_total:
    largest_age = wide.loc[wide['both'].idxmax(), 'age']
    figure(
        'Figure 1.2 — Age–sex population pyramid (2025)',
        population_pyramid(wide),
        f'The largest five-year age group in {state} is {largest_age}. '
        f'People aged 65 years and older represent approximately {older_share:.1f}% '
        'of the age-classified population. The chart shows how population '
        'composition differs by age and sex, rather than change over time.',
        'Mirrored horizontal bars · Male (left), female (right) · thousands of persons.',
    )

# FIGURE 1.3: Comparison of every state/federal territory in 2025.
# Deliberately use national data so a selected state can be compared with others.
national = population_overall(df, 'Malaysia')
state_totals = (
    national.groupby('state', as_index=False)['population']
    .sum()
    .sort_values('population', ascending=True)
)

bar_colors = [
    '#e18d42' if (state != 'Malaysia' and name == state) else '#3167a7'
    for name in state_totals['state']
]
state_fig = go.Figure(
    go.Bar(
        x=state_totals['population'],
        y=state_totals['state'],
        orientation='h',
        marker_color=bar_colors,
        text=state_totals['population'],
        texttemplate='%{text:,.0f}',
        textposition='outside',
        hovertemplate='%{y}: %{x:,.1f} thousand persons<extra></extra>',
    )
)
state_fig = finish(state_fig, legend=False, height=540)
state_fig.update_layout(
    xaxis_title='Population (thousand persons)',
    yaxis_title='',
    margin=dict(l=25, r=90, t=25, b=40),
)
state_fig.update_yaxes(automargin=True)

largest_state = state_totals.iloc[-1]
national_total = float(state_totals['population'].sum())
if state == 'Malaysia':
    state_interpretation = (
        f'{largest_state["state"]} has the highest population in 2025, '
        f'with {largest_state["population"] / 1000:,.2f} million persons '
        f'({100 * largest_state["population"] / national_total:.1f}% of the '
        'combined district population). State population totals vary substantially.'
    )
else:
    selected_population = float(
        state_totals.loc[state_totals['state'] == state, 'population'].iloc[0]
    )
    rank = int((state_totals['population'] > selected_population).sum() + 1)
    state_interpretation = (
        f'{state} ranks {rank} of {len(state_totals)} states/federal territories '
        f'by population in 2025, with {selected_population / 1000:,.2f} million '
        f'persons ({100 * selected_population / national_total:.1f}% of the '
        'combined district population). The highlighted bar shows the selected '
        'area in national context.'
    )

figure(
    'Figure 1.3 — Population by state and federal territory (2025)',
    state_fig,
    state_interpretation,
    'Horizontal bar chart · All 16 states/federal territories · totals from non-overlapping district records.',
)

st.info(
    'Methodology: Total population uses sex=both and age=overall, while the '
    'population pyramid uses male and female age-group estimates. Do not sum '
    'all demographic rows together because they contain overlapping subtotals. '
    'This page shows only 2025 and does not make claims about annual growth.'
)

export_df = df if state == 'Malaysia' else df[df['state'] == state]
csv_download(export_df, f'population_{state.replace(" ", "_")}_2025')

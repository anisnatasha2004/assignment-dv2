"""Plotly chart factories, independent of Streamlit for testability."""
from __future__ import annotations
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

BG = '#fff'
NAVY = '#15324b'
TEAL = '#087e8b'
BLUE = '#3167a7'
ORANGE = '#d7833e'
RED = '#b94c53'


def finish(fig: go.Figure, *, legend: bool = True, height: int = 390) -> go.Figure:
    fig.update_layout(template='plotly_white', height=height,
                      margin=dict(l=14,r=24,t=35,b=35),
                      font=dict(family='Arial, sans-serif', size=13, color=NAVY),
                      paper_bgcolor=BG, plot_bgcolor=BG,
                      legend=dict(orientation='h', y=1.12, x=0),
                      showlegend=legend, hovermode='closest')
    return fig


def population_trend(annual: pd.DataFrame, state: str) -> go.Figure:
    fig = px.line(annual, x='year', y='population', markers=True,
                  labels={'year':'Year','population':'Population (thousand persons)'})
    fig.update_traces(line=dict(color=TEAL, width=3), marker=dict(size=9),
                      hovertemplate='%{x}: %{y:,.1f} thousand<extra></extra>')
    fig.update_xaxes(dtick=1)
    return finish(fig, legend=False)


def population_ranking(ranked: pd.DataFrame) -> go.Figure:
    fig = px.bar(ranked, x='population', y='name', orientation='h',
                 labels={'population':'Population (thousand persons)','name':'District'},
                 text='population')
    fig.update_traces(marker_color=BLUE, texttemplate='%{text:,.0f}', textposition='outside', cliponaxis=False)
    fig.update_layout(yaxis_title='', margin=dict(l=20,r=65,t=25,b=35))
    return finish(fig, legend=False, height=430)


def population_pyramid(wide: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_bar(y=wide['age'], x=-wide['male'], orientation='h', name='Male', marker_color=BLUE,
                customdata=wide['male'], hovertemplate='Age %{y}: %{customdata:,.1f} thousand males<extra></extra>')
    fig.add_bar(y=wide['age'], x=wide['female'], orientation='h', name='Female', marker_color=ORANGE,
                hovertemplate='Age %{y}: %{x:,.1f} thousand females<extra></extra>')
    fig.update_layout(barmode='relative', xaxis_title='Population (thousand persons)',
                      yaxis_title='Age group (years)', yaxis=dict(categoryorder='array',categoryarray=list(wide['age'])),
                      bargap=0.12)
    max_val = float(wide[['male','female']].max().max()) * 1.16
    fig.update_xaxes(range=[-max_val, max_val],
                     tickvals=[-max_val*0.8, -max_val*0.4, 0, max_val*0.4, max_val*0.8],
                     ticktext=[f'{max_val*0.8:,.0f}', f'{max_val*0.4:,.0f}', '0',
                               f'{max_val*0.4:,.0f}', f'{max_val*0.8:,.0f}'])
    return finish(fig, legend=True, height=520)


def poverty_ranking(view: pd.DataFrame, n: int = 10, state: str = 'Malaysia') -> go.Figure:
    ranked = view.nlargest(n, 'poverty_absolute').sort_values('poverty_absolute').copy()
    ranked['name'] = ranked['district'] if state != 'Malaysia' else ranked['district'] + ' · ' + ranked['state']
    fig = px.bar(ranked, x='poverty_absolute', y='name', orientation='h',
                 labels={'poverty_absolute':'Absolute poverty rate (%)', 'name':'District'},
                 text='poverty_absolute')
    fig.update_traces(marker_color=RED, texttemplate='%{text:.1f}%', textposition='outside', cliponaxis=False)
    fig.update_layout(yaxis_title='', margin=dict(l=20,r=65,t=25,b=35))
    return finish(fig, legend=False, height=420)


def poverty_scatter(view: pd.DataFrame, state: str = 'Malaysia') -> go.Figure:
    fig = px.scatter(view, x='poverty_absolute', y='poverty_relative',
                     color='state' if state == 'Malaysia' else None,
                     hover_data=['state','district'],
                     labels={'poverty_absolute':'Absolute poverty rate (%)',
                             'poverty_relative':'Relative poverty rate (%)','state':'State'},
                     opacity=0.83)
    fig.update_traces(marker=dict(size=10, line=dict(width=0.5, color='#fff')))
    fig.update_layout(legend_title_text='State')
    return finish(fig, legend=(state=='Malaysia'), height=460)


def poverty_change(changes: pd.DataFrame, n: int = 12) -> go.Figure:
    ranked = changes.assign(abs_change=changes.change_pp.abs()).nlargest(n,'abs_change').sort_values('change_pp')
    fig = px.bar(ranked, x='change_pp', y='name', orientation='h',
                 color=ranked['change_pp'].lt(0).map({True:'Decrease',False:'Increase'}),
                 color_discrete_map={'Decrease':TEAL, 'Increase':RED},
                 labels={'change_pp':'Change in absolute poverty (percentage points)','name':'District'},
                 text='change_pp')
    fig.update_traces(texttemplate='%{text:+.1f} pp', textposition='outside', cliponaxis=False)
    fig.add_vline(x=0, line_color='#777', line_width=1)
    fig.update_layout(yaxis_title='', legend_title_text='2022 to 2024',
                      margin=dict(l=20,r=65,t=25,b=40))
    return finish(fig, legend=True, height=470)


def teachers_trend(annual: pd.DataFrame) -> go.Figure:
    labels = annual.copy()
    labels['stage'] = labels['stage'].str.title()
    fig = px.line(labels, x='year', y='teachers', color='stage', markers=True,
                  color_discrete_map={'Primary':TEAL,'Secondary':ORANGE},
                  labels={'year':'Year', 'teachers':'Number of government-school teachers', 'stage':'School stage'})
    fig.update_xaxes(dtick=1)
    fig.update_traces(line_width=3, marker_size=8)
    return finish(fig, legend=True)


def teachers_ranking(ranked: pd.DataFrame) -> go.Figure:
    fig = px.bar(ranked, x='teachers', y='name', orientation='h',
                 labels={'teachers':'Number of teachers', 'name':'District'}, text='teachers')
    fig.update_traces(marker_color=BLUE, texttemplate='%{text:,}', textposition='outside', cliponaxis=False)
    fig.update_layout(yaxis_title='', margin=dict(l=20,r=65,t=25,b=35))
    return finish(fig, legend=False, height=420)


def teachers_sex_chart(view: pd.DataFrame) -> go.Figure:
    labelled = view.copy()
    labelled['stage'] = labelled['stage'].str.title()
    labelled['sex'] = labelled['sex'].str.title()
    fig = px.bar(labelled, x='stage', y='teachers', color='sex', barmode='stack',
                 color_discrete_map={'Female':ORANGE,'Male':BLUE},
                 text='teachers', labels={'teachers':'Number of teachers','stage':'School stage','sex':'Sex'})
    fig.update_traces(texttemplate='%{text:,}', textposition='outside', cliponaxis=False)
    return finish(fig, legend=True)

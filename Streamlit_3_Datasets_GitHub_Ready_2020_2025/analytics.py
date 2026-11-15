"""Pure data transformations shared by Streamlit pages and unit tests.

These functions deliberately avoid double counting aggregate sex, age, ethnicity,
and state/national rows. Units are not silently converted.
"""
from __future__ import annotations
import pandas as pd

AGE_ORDER = ['0-4','5-9','10-14','15-19','20-24','25-29','30-34',
             '35-39','40-44','45-49','50-54','55-59','60-64',
             '65-69','70-74','75-79','80-84','85+']


def population_overall(df: pd.DataFrame, state: str = 'Malaysia') -> pd.DataFrame:
    view = df[(df['sex'] == 'both') & (df['age'] == 'overall') &
              (df['ethnicity'] == 'overall')]
    if state != 'Malaysia':
        view = view[view['state'] == state]
    return view.copy()


def population_annual(df: pd.DataFrame, state: str = 'Malaysia') -> pd.DataFrame:
    view = population_overall(df, state)
    return (view.groupby('year', as_index=False)['population'].sum()
                .sort_values('year'))


def population_ranking(df: pd.DataFrame, year: int, state: str = 'Malaysia', n: int = 10) -> pd.DataFrame:
    view = population_overall(df, state)
    view = view[view['year'] == year].copy()
    view['name'] = view['district'] if state != 'Malaysia' else view['district'] + ' · ' + view['state']
    return view.nlargest(n, 'population').sort_values('population')


def population_age_sex(df: pd.DataFrame, year: int, state: str = 'Malaysia') -> pd.DataFrame:
    view = df[(df['year'] == year) & df['ethnicity'].eq('overall') &
              df['age'].isin(AGE_ORDER) & df['sex'].isin(['male', 'female'])]
    if state != 'Malaysia':
        view = view[view['state'] == state]
    grouped = view.groupby(['age','sex'], as_index=False)['population'].sum()
    wide = (grouped.pivot(index='age', columns='sex', values='population')
                   .reindex(AGE_ORDER).fillna(0).reset_index())
    for sex in ['male','female']:
        if sex not in wide:
            wide[sex] = 0.0
    return wide


def poverty_view(df: pd.DataFrame, year: int, state: str = 'Malaysia') -> pd.DataFrame:
    view = df[df['year'] == year]
    if state != 'Malaysia':
        view = view[view['state'] == state]
    return view.copy()


def poverty_changes(df: pd.DataFrame, state: str = 'Malaysia') -> pd.DataFrame:
    view = df if state == 'Malaysia' else df[df['state'] == state]
    pivot = view.pivot(index=['state', 'district'], columns='year', values='poverty_absolute')
    if 2022 not in pivot.columns or 2024 not in pivot.columns:
        return pd.DataFrame(columns=['state','district','rate_2022','rate_2024','change_pp','name'])
    matched = pivot[[2022,2024]].dropna().reset_index()
    matched.columns = ['state','district','rate_2022','rate_2024']
    matched['change_pp'] = matched['rate_2024'] - matched['rate_2022']
    matched['name'] = matched['district'] if state != 'Malaysia' else matched['district'] + ' · ' + matched['state']
    return matched


def teachers_annual(df: pd.DataFrame, state: str = 'Malaysia') -> pd.DataFrame:
    view = df[(df['district'] == 'All Districts') & (df['sex'] == 'both') &
              (df['state'] == state)]
    return view.groupby(['year','stage'], as_index=False)['teachers'].sum().sort_values('year')


def teachers_ranking(df: pd.DataFrame, year: int, state: str = 'Malaysia', n: int = 10) -> pd.DataFrame:
    view = df[(df['year'] == year) & (df['state'] != 'Malaysia') &
              (df['district'] != 'All Districts') & (df['sex'] == 'both')]
    if state != 'Malaysia':
        view = view[view['state'] == state]
    view = view.groupby(['state','district'], as_index=False)['teachers'].sum()
    view['name'] = view['district'] if state != 'Malaysia' else view['district'] + ' · ' + view['state']
    return view.nlargest(n, 'teachers').sort_values('teachers')


def teachers_sex_by_stage(df: pd.DataFrame, year: int, state: str = 'Malaysia') -> pd.DataFrame:
    view = df[(df['year'] == year) & (df['state'] == state) &
              (df['district'] == 'All Districts') & (df['sex'].isin(['male','female']))]
    return view.groupby(['stage', 'sex'], as_index=False)['teachers'].sum()

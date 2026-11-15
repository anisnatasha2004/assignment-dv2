"""Common Streamlit UI helpers."""
from pathlib import Path
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent
DATA = ROOT / 'data' / 'processed'
SOURCES = {
    'population': 'https://open.dosm.gov.my/data-catalogue/population_district',
    'poverty': 'https://open.dosm.gov.my/data-catalogue/hh_poverty_district',
    'teachers': 'https://open.dosm.gov.my/data-catalogue/teachers_district',
}

@st.cache_data(show_spinner='Reading validated datasets…')
def read_dataset(name: str) -> pd.DataFrame:
    filename = DATA / f'{name}_2020_2025.csv'
    if not filename.is_file():
        st.error(f'Data file missing: {filename}. Please check that the data/processed directory was uploaded to GitHub.')
        st.stop()
    df = pd.read_csv(filename, low_memory=False)
    df['year'] = df['year'].astype(int)
    return df


def page_header(title: str, subtitle: str, objective: str, source: str) -> None:
    st.title(title)
    st.caption(subtitle)
    st.markdown(f'**Visualisation objective:** {objective}')
    st.caption(f'Source: [OpenDOSM — {source}]({SOURCES[source]}) · Original official datasets, filtered to 2020–2025')
    st.divider()


def figure(title: str, chart, interpretation: str, caption: str) -> None:
    st.subheader(title)
    st.plotly_chart(chart, use_container_width=True)
    st.caption(caption)
    st.markdown(f'**Interpretation.** {interpretation}')
    st.divider()


def csv_download(df: pd.DataFrame, key: str, title: str = 'Download filtered data') -> None:
    st.download_button(title, df.to_csv(index=False).encode('utf-8-sig'),
                       file_name=f'{key}.csv', mime='text/csv', key=f'download_{key}')

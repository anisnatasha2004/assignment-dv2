
"""Main application for Malaysia Scientific Visualisation."""

import streamlit as st

st.set_page_config(
    page_title="Malaysia Scientific Visualisation",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
.block-container {
    max-width: 1180px;
    padding-top: 1.5rem;
    padding-bottom: 3rem;
}
[data-testid="stMetric"] {
    background: rgba(135,151,160,.08);
    border: 1px solid rgba(120,134,143,.15);
    padding: 1.05rem;
    border-radius: 13px;
}
[data-testid="stSidebar"] {
    border-right: 1px solid rgba(130,145,155,.18);
}
h1, h2, h3 {
    letter-spacing: -.02em;
}
</style>
""", unsafe_allow_html=True)

# Define the three dashboard pages
pages = [
    st.Page(
        "pages/population_page.py",
        title="1 · Population",
        icon="👥",
        default=True
    ),
    st.Page(
        "pages/poverty_page.py",
        title="2 · Household poverty",
        icon="🏘️"
    ),
    st.Page(
        "pages/teachers_page.py",
        title="3 · Government-school teachers",
        icon="🎓"
    )
]

# Hide Streamlit's default navigation
page = st.navigation(pages, position="hidden")

# Custom sidebar: heading ABOVE navigation links
st.sidebar.markdown("## Malaysia Data Explorer")
st.sidebar.caption(
    "Scientific Visualisation · Three datasets"
)

st.sidebar.divider()

# Custom navigation links
st.sidebar.page_link(pages[0])
st.sidebar.page_link(pages[1])
st.sidebar.page_link(pages[2])

st.sidebar.divider()

# Run the selected page
page.run()

# Data source note at bottom of sidebar
st.sidebar.caption(
    "Source: DOSM / OpenDOSM and Ministry of Education Malaysia."
)

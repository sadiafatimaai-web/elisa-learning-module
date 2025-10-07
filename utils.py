import streamlit as st

def render_sidebar_nav() -> None:
    # Hide Streamlit's default multipage nav (fallback CSS in case config.toml isn't picked up)
    st.markdown(
        """
        <style>
            section[data-testid="stSidebarNav"] { display: none !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.header("Navigation")
        st.page_link("Home.py", label="Home", icon="🏠")
        st.page_link("pages/1_Types_and_Examples.py", label="Types & Examples")
        st.page_link("pages/2_Simulation_and_Calculation.py", label="Simulation & Calculation")
        st.page_link("pages/3_Quiz.py", label="Quiz")
        st.page_link("pages/4_Troubleshooting.py", label="Troubleshooting")
        st.page_link("pages/5_Glossary.py", label="Glossary")


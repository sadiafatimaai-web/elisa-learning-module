import pandas as pd
from typing import List, Tuple

import streamlit as st

def render_sidebar_nav():
    # (Optional) extra safety: hide default nav via CSS if the config isn’t picked up
    st.markdown("""
        <style>
            /* hides Streamlit's auto page list if still visible */
            section[data-testid="stSidebarNav"] { display: none !important; }
        </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.header("Navigation")
        st.page_link("Home.py", label="Home", icon="🏠")
        st.page_link("pages/1_Types_and_Examples.py", label="Types & Examples")
        st.page_link("pages/2_Simulation_and_Calculation.py", label="Simulation & Calculation")
        st.page_link("pages/3_Quiz.py", label="Quiz")
        st.page_link("pages/4_Troubleshooting.py", label="Troubleshooting")

def calc_cutoff(df: pd.DataFrame, neg_wells: List[str], multiplier: float = 2.1) -> Tuple[float, float]:
    """Return (COV, average_neg). df has columns Well, OD."""
    neg = df[df["Well"].isin(neg_wells)]["OD"]
    if len(neg) == 0:
        return float("nan"), float("nan")
    avg_neg = neg.mean()
    cov = multiplier * avg_neg
    return cov, avg_neg

def classify_samples(df: pd.DataFrame, cov: float, equivocal_margin: float = 0.10) -> pd.DataFrame:
    """Add a Status column based on COV and margin."""
    def status(od):
        if pd.isna(cov):
            return "Unknown"
        if od > cov + equivocal_margin:
            return "Positive"
        elif od < cov - equivocal_margin:
            return "Negative"
        else:
            return "Equivocal"
    out = df.copy()
    out["Status"] = out["OD"].apply(status)
    return out

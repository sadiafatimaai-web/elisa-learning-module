# utils.py
# -----------------------------------------------------------------------------
# Shared helpers for the ELISA Learning Module
# -----------------------------------------------------------------------------

import streamlit as st
import pandas as pd
from typing import List, Tuple, Optional


def render_sidebar_nav() -> None:
    """
    Renders a custom sidebar navigation and hides Streamlit's built-in
    multipage sidebar (in case it's still visible).
    Call this at the very top of Home.py and every file in pages/.
    """
    # Hide Streamlit's default multipage nav if present
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


def calc_cutoff(
    df: pd.DataFrame, neg_wells: List[str], multiplier: float = 2.1
) -> Tuple[float, float]:
    """
    Compute the cut-off value (COV) from selected negative controls.

    Parameters
    ----------
    df : DataFrame with columns ['Well', 'OD']
    neg_wells : list of well names to treat as negatives
    multiplier : factor applied to average negative OD (default 2.1)

    Returns
    -------
    (cov, avg_neg) : tuple of floats
    """
    neg = df[df["Well"].isin(neg_wells)]["OD"]
    if len(neg) == 0:
        return float("nan"), float("nan")
    avg_neg = float(neg.mean())
    cov = float(multiplier * avg_neg)
    return cov, avg_neg


def classify_samples(
    df: pd.DataFrame, cov: float, equivocal_margin: float = 0.10
) -> pd.DataFrame:
    """
    Classify wells based on COV and an equivocal margin.

    Positive  : OD > cov + margin
    Negative  : OD < cov - margin
    Equivocal : otherwise
    """
    def status(od: float) -> str:
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


# Optional convenience: safely display images from assets/
def show_image(path: str, caption: Optional[str] = None) -> None:
    """
    Display an image if it exists; otherwise show a friendly warning.
    Usage: show_image("assets/elisa_plate.jpg", "96-well plate")
    """
    try:
        from pathlib import Path
        p = Path(path)
        if p

# utils.py — shared helpers for the ELISA Learning Module
from pathlib import Path
from typing import List, Tuple, Optional
import pandas as pd
import streamlit as st

# ---- Sidebar navigation ----
def _safe_link(page_path: str, label: str, icon: Optional[str] = None) -> None:
    """Add link only if the target page file exists (prevents PageNotFound)."""
    try:
        if Path(page_path).exists():
            st.page_link(page_path, label=label, icon=icon)
    except Exception:
        pass

def render_sidebar_nav() -> None:
    """Render custom sidebar and hide Streamlit's default one."""
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
        _safe_link("Home.py", label="Home", icon="🏠")
        _safe_link("pages/1_Types_and_Examples.py", label="Types & Examples")
        _safe_link("pages/2_Simulation_and_Calculation.py", label="Simulation & Calculation")
        _safe_link("pages/3_Quiz.py", label="Quiz")
        _safe_link("pages/4_Troubleshooting.py", label="Troubleshooting")
        _safe_link("pages/5_Glossary.py", label="Glossary")

# ---- ELISA helpers ----
def calc_cutoff(df: pd.DataFrame, neg_wells: List[str], multiplier: float = 2.1) -> Tuple[float, float]:
    """COV = multiplier × average(negative ODs). Returns (cov, avg_neg)."""
    neg = df[df["Well"].isin(neg_wells)]["OD"]
    if len(neg) == 0:
        return float("nan"), float("nan")
    avg_neg = float(neg.mean())
    cov = float(multiplier * avg_neg)
    return cov, avg_neg

def classify_samples(df: pd.DataFrame, cov: float, equivocal_margin: float = 0.10) -> pd.DataFrame:
    """Add Status column using COV and margin."""
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



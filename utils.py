import numpy as np
import pandas as pd
import streamlit as st
from scipy.optimize import curve_fit
from scipy.stats import linregress

# =========================
# Models & Fitting Helpers
# =========================

def four_pl(x, a, b, c, d):
    """4-parameter logistic (Bottom=a, Top=b, EC50=c, Hill=d)."""
    x = np.clip(np.asarray(x, dtype=float), 1e-12, None)
    return a + (b - a) / (1.0 + (c / x) ** d)

def inv_linear(y, slope, intercept):
    return (y - intercept) / slope

def inv_log_linear(y, slope, intercept):
    # y = intercept + slope * log10(x)
    return 10 ** ((y - intercept) / slope)

def inv_four_pl(y, a, b, c, d):
    # Invert y = a + (b-a)/(1+(c/x)^d)
    y = np.asarray(y, dtype=float)
    left = (b - a) / (y - a) - 1.0
    return c / (left ** (1.0 / d))

def fit_curve(x, y, kind="linear"):
    """
    Fit linear, log-linear, or 4PL.
    Returns (params:dict, yhat:np.ndarray)
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)

    if kind == "linear":
        res = linregress(x, y)
        params = {"kind": "linear", "slope": res.slope, "intercept": res.intercept}
        yhat = res.intercept + res.slope * x
    elif kind == "log":
        xlog = np.log10(np.clip(x, 1e-12, None))
        res = linregress(xlog, y)
        params = {"kind": "log", "slope": res.slope, "intercept": res.intercept}
        yhat = res.intercept + res.slope * xlog
    else:
        p0 = [float(min(y)), float(max(y)), float(np.median(x)), 1.0]
        bounds = ([-np.inf, -np.inf, 1e-12, 0.01], [np.inf, np.inf, np.inf, 5.0])
        popt, _ = curve_fit(four_pl, x, y, p0=p0, bounds=bounds, maxfev=20000)
        params = {"kind": "4pl", "a": popt[0], "b": popt[1], "c": popt[2], "d": popt[3]}
        yhat = four_pl(x, *popt)
    return params, yhat

def invert_to_conc(y, params):
    """Back-calc concentrations from OD using fitted params."""
    kind = params["kind"]
    if kind == "linear":
        return inv_linear(y, params["slope"], params["intercept"])
    elif kind == "log":
        return inv_log_linear(y, params["slope"], params["intercept"])
    else:
        return inv_four_pl(y, params["a"], params["b"], params["c"], params["d"])

# =========================
# QC / Metrics
# =========================

def coeff_var(vals):
    vals = np.asarray(vals, dtype=float)
    if vals.size == 0:
        return np.nan
    m = np.mean(vals)
    s = np.std(vals, ddof=1) if vals.size > 1 else 0.0
    return np.nan if m <= 0 else (s / m) * 100.0

def lod_loq(blank_vals, params):
    """LOD = mean(blank)+3*SD; LOQ = mean(blank)+10*SD (return both y and x)."""
    mu_b = float(np.mean(blank_vals))
    sd_b = float(np.std(blank_vals, ddof=1)) if len(blank_vals) > 1 else 0.0
    lod_y = mu_b + 3 * sd_b
    loq_y = mu_b + 10 * sd_b
    x_lod = invert_to_conc(lod_y, params)
    x_loq = invert_to_conc(loq_y, params)
    return x_lod, x_loq, lod_y, loq_y

# =========================
# COV Tools (kept for practice)
# =========================

def calc_cutoff(df: pd.DataFrame, neg_wells, multiplier: float = 2.1):
    """
    df must contain columns: ['Well', 'OD']  (OD in absorbance units).
    neg_wells: list of labels from df['Well'] to use as negatives.
    """
    neg = df[df["Well"].isin(neg_wells)]["OD"]
    if len(neg) == 0:
        return float("nan"), float("nan")
    avg_neg = float(neg.mean())
    cov = multiplier * avg_neg
    return cov, avg_neg

def classify_samples(df: pd.DataFrame, cov: float, equivocal_margin: float = 0.10, od_col: str = None) -> pd.DataFrame:
    """
    Classify Positive/Negative/Equivocal based on COV.
    Auto-detect OD column if not provided.
    """
    out = df.copy()
    # try to find an OD-like column
    candidates = ["OD", "od", "mean_od", "Absorbance", "absorbance", "value"]
    if od_col is None:
        for c in candidates:
            if c in out.columns:
                od_col = c
                break
    if od_col is None:
        raise KeyError(f"No OD-like column found. Expected one of {candidates}, got {list(out.columns)}")

    def status(od):
        if np.isnan(cov):
            return "Unknown"
        if od > cov + equivocal_margin:
            return "Positive"
        if od < cov - equivocal_margin:
            return "Negative"
        return "Equivocal"

    out["Status"] = out[od_col].apply(status)
    return out

# =========================
# Sidebar Navigation
# =========================

import streamlit as st

def render_sidebar_nav():
    """Clickable sidebar navigation for ALL pages."""
    with st.sidebar:
        # Fix deprecation: use_container_width (not use_column_width)
        st.image(
            "https://upload.wikimedia.org/wikipedia/commons/0/0a/ELISA_plate.jpg",
            use_container_width=True,
            caption="ELISA Learning Module",
        )

        st.markdown("## 🔬 ELISA Module")
        st.markdown("Navigate between sections:")

        # 🔗 Real, clickable links (requires streamlit >= 1.25)
        st.page_link("Home.py", label="🏠 Home")
        st.page_link("pages/1_Types_and_Examples.py", label="🧫 Types & Examples")
        st.page_link("pages/2_Simulation_and_Calculation.py", label="📈 Simulation & Calculation")
        st.page_link("pages/3_Quiz.py", label="❓ Quiz")
        st.page_link("pages/4_Troubleshooting.py", label="🛠️ Troubleshooting")
        st.page_link("pages/5_Glossary.py", label="📚 Glossary")

        st.markdown("---")
        st.caption("Tip: Click any item above to switch pages.")



       
        )

       

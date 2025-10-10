import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
from scipy.stats import linregress

# ---------- Core models ----------
def four_pl(x, a, b, c, d):
    """4-parameter logistic (Bottom=a, Top=b, EC50=c, Hill=d)."""
    x = np.clip(np.asarray(x), 1e-12, None)
    return a + (b - a) / (1.0 + (c / x) ** d)

def inv_linear(y, slope, intercept):
    return (y - intercept) / slope

def inv_log_linear(y, slope, intercept):
    return 10 ** ((y - intercept) / slope)

def inv_four_pl(y, a, b, c, d):
    left = (b - a) / (y - a) - 1.0
    return c / (left ** (1.0 / d))

# ---------- Fitting & inversion ----------
def fit_curve(x, y, kind="linear"):
    """Fit linear, log-linear, or 4PL. Returns (params:dict, yhat:np.ndarray)."""
    x = np.asarray(x); y = np.asarray(y)
    if kind == "linear":
        res = linregress(x, y)
        params = {"kind": "linear", "slope": res.slope, "intercept": res.intercept}
        yhat = res.intercept + res.slope * x
    elif kind == "log":
        xlog = np.log10(np.clip(x, 1e-12, None))
        res = linregress(xlog, y)
        params = {"kind": "log", "slope": res.slope, "intercept": res.intercept}
        yhat = res.intercept + res.slope * xlog
    else:  # 4pl
        p0 = [min(y), max(y), np.median(x), 1.0]
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

# ---------- Stats / QC ----------
def coeff_var(vals):
    vals = np.asarray(vals, dtype=float)
    if vals.size == 0: return np.nan
    m = np.mean(vals)
    s = np.std(vals, ddof=1) if vals.size > 1 else 0.0
    return np.nan if m <= 0 else (s / m) * 100.0

def lod_loq(blank_vals, params):
    """LOD = mean(blank)+3*SD; LOQ = mean(blank)+10*SD (returned in concentration units)."""
    mu_b = float(np.mean(blank_vals))
    sd_b = float(np.std(blank_vals, ddof=1)) if len(blank_vals) > 1 else 0.0
    lod_y = mu_b + 3 * sd_b
    loq_y = mu_b + 10 * sd_b
    return invert_to_conc(lod_y, params), invert_to_conc(loq_y, params), lod_y, loq_y

# ---------- Existing COV helpers (kept, unchanged behavior) ----------
def calc_cutoff(df: pd.DataFrame, neg_wells, multiplier: float = 2.1):
    neg = df[df["Well"].isin(neg_wells)]["OD"]
    if len(neg) == 0:
        return float("nan"), float("nan")
    avg_neg = float(neg.mean())
    cov = multiplier * avg_neg
    return cov, avg_neg

def classify_samples(df: pd.DataFrame, cov: float, equivocal_margin: float = 0.10) -> pd.DataFrame:
    def status(od):
        if np.isnan(cov): return "Unknown"
        if od > cov + equivocal_margin: return "Positive"
        if od < cov - equivocal_margin: return "Negative"
        return "Equivocal"
    out = df.copy()
    out["Status"] = out["OD"].apply(status)
    return out

    out["Status"] = out["OD"].apply(status)
    return out

import streamlit as st

def render_sidebar_nav():
    """
    Sidebar navigation menu for all pages.
    Appears on every page when called at the top of the script.
    """
    with st.sidebar:
        st.image(
            "https://upload.wikimedia.org/wikipedia/commons/0/0a/ELISA_plate.jpg",
            use_column_width=True,
            caption="ELISA Learning Module"
        )
        st.title("🔬 ELISA Module")
        st.markdown("Navigate between sections:")

        pages = {
            "🏠 Home": "Home",
            "1️⃣ Types & Examples": "pages/1_Types_and_Examples.py",
            "2️⃣ Simulation & Calculation": "pages/2_Simulation_and_Calculation.py",
            "3️⃣ Quiz": "pages/3_Quiz.py",
            "4️⃣ Troubleshooting": "pages/4_Troubleshooting.py",
        }

        for name, path in pages.items():
            st.markdown(f"- {name}")

        st.markdown("---")
        st.info(
            "💡 Tip: Use this sidebar to explore ELISA principles, run simulations, "
            "practice calculations, and troubleshoot common lab issues."
        )

import streamlit as st

def render_sidebar_nav():
    """Clickable sidebar navigation for all pages."""
    with st.sidebar:
        # Header image (fix deprecation: use_container_width)
        st.image(
            "https://upload.wikimedia.org/wikipedia/commons/0/0a/ELISA_plate.jpg",
            use_container_width=True,
            caption="ELISA Learning Module",
        )

        st.markdown("## 🔬 ELISA Module")
        st.markdown("Navigate between sections:")

        # 🔗 Real, clickable links to pages
        st.page_link("Home.py", label="🏠 Home")
        st.page_link("pages/1_Types_and_Examples.py", label="1️⃣ Types & Examples")
        st.page_link("pages/2_Simulation_and_Calculation.py", label="2️⃣ Simulation & Calculation")
        st.page_link("pages/3_Quiz.py", label="3️⃣ Quiz")
        st.page_link("pages/4_Troubleshooting.py", label="4️⃣ Troubleshooting")

        st.markdown("---")
        st.caption("Tip: these buttons switch pages instantly.")


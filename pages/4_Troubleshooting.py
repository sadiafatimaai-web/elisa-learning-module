import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from utils import (
    render_sidebar_nav,
    four_pl, fit_curve, invert_to_conc,
)

# -----------------------------
# Sidebar + Title
# -----------------------------
render_sidebar_nav()
st.title("Page 4 — Troubleshooting Scenarios")
st.caption("Toggle realistic errors and see how they change the curve, residuals, CVs, and back-calculated unknowns.")

# -----------------------------
# Assay design controls
# -----------------------------
n_stds = st.slider("Number of standards", 4, 10, 6)
reps = st.slider("Replicates per level", 1, 6, 3)

c1, c2 = st.columns(2)
with c1:
    conc_min = st.number_input("Min concentration", 0.001, 1_000_000.0, 0.1, format="%.6f")
with c2:
    conc_max = st.number_input("Max concentration", 0.001, 1_000_000.0, 100.0, format="%.6f")

c3, c4, c5 = st.columns(3)
with c3:
    blank_od = st.number_input("Background OD", 0.0, 1.0, 0.05, 0.01)
with c4:
    noise_sd = st.number_input("Well-to-well noise SD", 0.0, 1.0, 0.02, 0.005)
with c5:
    blank_sub = st.checkbox("Subtract mean blank", True)

seed = st.number_input("Random seed", 0, 9999, 7)
rng = np.random.default_rng(seed)

# True (underlying) model for realism: 4PL
st.subheader("True response (4PL)")
tcol1, tcol2, tcol3, tcol4 = st.columns(4)
with tcol1:
    top = st.number_input("True Top (max signal)", 0.2, 5.0, 2.5, 0.1)
with tcol2:
    bottom = st.number_input("True Bottom (min signal)", 0.0, 1.0, 0.05, 0.01)
with tcol3:
    ec50 = st.number_input("True EC50", 0.001, 1_000_000.0, 5.0, format="%.6f")
with tcol4:
    hill = st.number_input("True Hill", 0.1, 4.0, 1.2, 0.1)

fit_kind = st.selectbox("Fit used for calibration", ["linear", "log", "4pl"], index=2)

# -----------------------------
# Error toggles
# -----------------------------
st.subheader("Inject common errors")
e1, e2, e3 = st.columns(3)
with e1:
    pipette_bias = st.checkbox("Pipetting bias (one standard level)")
    reagent_fail = st.checkbox("Reagent failure (weak enzyme/substrate)")
with e2:
    contamination = st.checkbox("Contamination / high background")
    outlier = st.checkbox("Single-well outlier")
with e3:
    wrong_dilution = st.checkbox("Wrong dilution for Unknown 1")

# Parameter widgets for selected errors
params = {}

if pipette_bias:
    lvl = st.selectbox("Biased standard level", list(range(1, n_stds + 1)), index=0) - 1
    frac = st.slider("Bias fraction (+/-)", -0.5, 0.5, 0.2, 0.05)
    params["pipette_level"] = int(lvl)
    params["pipette_frac"] = float(frac)

if reagent_fail:
    scale = st.slider("Reagent scale (1.0 = normal, smaller = weaker)", 0.2, 1.0, 0.6, 0.05)
    params["reagent_scale"] = float(scale)

if contamination:
    bump = st.slider("Background increase (OD)", 0.05, 0.5, 0.15, 0.01)
    params["contam_add"] = float(bump)

if outlier:
    orow = st.selectbox("Outlier at standard level", list(range(1, n_stds + 1)), index=0) - 1
    ocol = st.slider("Outlier replicate index", 0, reps - 1, 0, 1)
    amt = st.slider("Outlier amount to add (OD)", 0.2, 2.0, 1.0, 0.1)
    params["outlier_row"] = int(orow)
    params["outlier_col"] = int(ocol)
    params["outlier_amount"] = float(amt)

if wrong_dilution:
    params["wrong_dilution"] = True

# -----------------------------
# Simulate dataset
# -----------------------------
def make_concs(n: int, lo: float, hi: float) -> np.ndarray:
    return np.logspace(np.log10(lo), np.log10(hi), n)

conc = make_concs(n_stds, conc_min, conc_max)
true_mean = four_pl(conc, bottom, top, ec50, hill)

def make_reps(mean_vec: np.ndarray, k: int) -> np.ndarray:
    arr = []
    for m in mean_vec:
        base = m + blank_od
        arr.append(base + rng.normal(0.0, noise_sd, size=k))
    return np.array(arr)

std_reps = make_reps(true_mean, reps)
blank_vals = blank_od + rng.normal(0.0, noise_sd, size=reps)

# Unknowns and positive control
unk_true = np.array([rng.uniform(conc_min, conc_max), rng.uniform(conc_min, conc_max)])
unk_mean = four_pl(unk_true, bottom, top, ec50, hill)
unk_reps = np.vstack([(m + blank_od) + rng.normal(0.0, noise_sd, size=reps) for m in unk_mean])

pos_conc = conc_max * 1.2
pos_mean = four_pl(pos_conc, bottom, top, ec50, hill)
pos_reps = (pos_mean + blank_od) + rng.normal(0.0, noise_sd, size=reps)

# Apply errors
if "pipette_level" in params:
    std_reps[params["pipette_level"], :] *= (1.0 + params["pipette_frac"])

if "reagent_scale" in params:
    scale = params["reagent_scale"]
    std_reps *= scale
    unk_reps *= scale
    pos_reps *= scale

if "contam_add" in params:
    add = params["contam_add"]
    std_reps += add
    unk_reps += add
    pos_reps += add
    blank_vals += add

if "outlier_row" in params:
    i = params["outlier_row"]
    j = params["outlier_col"]
    a = params["outlier_amount"]
    std_reps[i, j] += a

if params.get("wrong_dilution", False):
    # Push unknown 1 an order of magnitude lower than intended (simulated mistake)
    altered = four_pl(np.full(1, max(unk_true[0] / 10.0, 1e-12)), bottom, top, ec50, hill)[0]
    unk_reps[0, :] = (altered + blank_od) + rng.normal(0.0, noise_sd, size=reps)

# Build tidy DataFrames
std_rows = []
for i in range(n_stds):
    for j in range(reps):
        std_rows.append({"type": "standard", "level": i + 1, "conc": conc[i], "od": std_reps[i, j]})
standards_df = pd.DataFrame(std_rows)

blank_df = pd.DataFrame({"type": "blank", "level": 0, "conc": 0.0, "od": blank_vals})

unk_rows = []
for u in range(2):
    for j in range(reps):
        unk_rows.append({"type": f"unknown_{u+1}", "level": 0, "conc": unk_true[u], "od": unk_reps[u, j]})
unknowns_df = pd.DataFrame(unk_rows)

pos_df = pd.DataFrame({"type": "positive", "level": 0, "conc": pos_conc, "od": pos_reps})

# Optional blank subtraction
if blank_sub:
    mu = float(blank_df["od"].mean())
    for df in (standards_df, unknowns_df, pos_df):
        df["od"] = (df["od"] - mu).clip(lower=0.0)

# Fit curve on standard means
std_means = standards_df.groupby("level", as_index=False).agg(conc=("conc", "mean"), od=("od", "mean"))
params_fit, yhat = fit_curve(std_means["conc"].values, std_means["od"].values, kind=fit_kind)
residuals = std_means["od"].values - yhat

# -----------------------------
# Visualizations
# -----------------------------
cplot, cres = st.columns([3, 2], gap="large")

with cplot:
    st.subheader("A) Curve under error")
    x_dense = np.logspace(np.log10(conc.min() / 1.5), np.log10(conc.max() * 1.5), 200)
    if params_fit["kind"] == "linear":
        y_dense = params_fit["intercept"] + params_fit["slope"] * x_dense
    elif params_fit["kind"] == "log":
        y_dense = params_fit["intercept"] + params_fit["slope"] * np.log10(x_dense)
    else:
        y_dense = four_pl(x_dense, params_fit["a"], params_fit["b"], params_fit["c"], params_fit["d"])
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.scatter(std_means["conc"], std_means["od"], label="Standards (mean)")
    ax.plot(x_dense, y_dense, label=f"Fit: {params_fit['kind'].upper()}")
    ax.set_xscale("log")
    ax.set_xlabel("Concentration")
    ax.set_ylabel("OD")
    ax.legend()
    ax.set_title("Standard curve with injected error(s)")
    st.pyplot(fig, use_container_width=True)

with cres:
    st.subheader("Residual pattern")
    fig, ax = plt.subplots(figsize=(5, 2.8))
    ax.axhline(0.0, lw=1, color="gray")
    ax.bar(std_means["conc"], residuals, width=0.07 * std_means["conc"], align="center")
    ax.set_xscale("log")
    ax.set_xlabel("Concentration")
    ax.set_ylabel("Residual (OD)")
    st.pyplot(fig, use_container_width=True)

# -----------------------------
# Replicate CVs
# -----------------------------
st.subheader("B) Replicate CVs")

def cv_table(df: pd.DataFrame, group_col: str) -> pd.DataFrame:
    tmp = df.copy()
    tmp["grp"] = tmp[group_col]
    out = tmp.groupby("grp").agg(
        n=("od", "count"),
        mean_od=("od", "mean"),
        sd=("od", "std"),
    ).reset_index()
    out["cv_%"] = (out["sd"] / out["mean_od"] * 100.0).round(2)
    return out

col1, col2 = st.columns(2)
with col1:
    st.markdown("**Standards**")
    st.dataframe(cv_table(standards_df, "level"), use_container_width=True)
with col2:
    st.markdown("**Unknowns**")
    tmp = unknowns_df.copy()
    tmp["group"] = tmp["type"]
    st.dataframe(cv_table(tmp, "group"), use_container_width=True)

# -----------------------------
# Back-calculation impact
# -----------------------------
st.subheader("C) Back-calculation impact")

unknown_means = unknowns_df.groupby("type", as_index=False).agg(mean_od=("od", "mean"))
calc_conc = invert_to_conc(unknown_means["mean_od"].values, params_fit)

res_tab = unknown_means.copy()
res_tab["calc_conc"] = calc_conc
res_tab["true_conc"] = np.array([unk_true[0], unk_true[1]])
res_tab["%error"] = (res_tab["calc_conc"] - res_tab["true_conc"]) / res_tab["true_conc"] * 100.0

st.dataframe(
    res_tab.style.format(
        {"mean_od": "{:.3f}", "calc_conc": "{:.3f}", "true_conc": "{:.3f}", "%error": "{:.1f}"}
    ),
    use_container_width=True,
)

st.info(
    "Diagnosis hints:\n"
    "- High background everywhere → contamination or poor washing.\n"
    "- All signals weak (including positive) → reagent failure.\n"
    "- One level unstable / high CV → pipetting error or outlier.\n"
    "- Unknown off by ~10× → wrong dilution."
)

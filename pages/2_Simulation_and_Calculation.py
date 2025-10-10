import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from utils import (
    render_sidebar_nav,
    four_pl, fit_curve, invert_to_conc,
    coeff_var, lod_loq,
    calc_cutoff, classify_samples
)

# -----------------------------
# Sidebar + Title
# -----------------------------
render_sidebar_nav()
st.title("Page 2 — Simulation & Practice Calculation")

st.markdown("""
Use this simulator to **run a virtual ELISA**, build a **standard curve**, back-calculate **unknown concentrations**, and compute **CV / LOD / LOQ**.  
You can also practice a **cut-off (COV)**–based qualitative interpretation using negative controls.
""")

# -----------------------------
# Controls — assay design
# -----------------------------
st.subheader("A) Generate a dataset")

top_row = st.columns(4)
with top_row[0]:
    n_stds = st.slider("Number of standards", 4, 10, 6)
with top_row[1]:
    conc_min = st.number_input("Min conc.", 0.001, 1e6, 0.1, format="%.6f")
with top_row[2]:
    conc_max = st.number_input("Max conc.", 0.001, 1e6, 100.0, format="%.6f")
with top_row[3]:
    reps = st.slider("Replicates per level", 1, 6, 3)

mid_row = st.columns(3)
with mid_row[0]:
    blank_od = st.number_input("Background OD (blank)", 0.0, 1.0, 0.05, 0.01)
with mid_row[1]:
    well_noise = st.number_input("Well-to-well noise SD", 0.0, 1.0, 0.02, 0.005)
with mid_row[2]:
    blank_sub = st.checkbox("Subtract mean blank from all wells", True)

# NEW: ELISA format control (affects the VISUAL bar chart logic)
fmt_row = st.columns(2)
with fmt_row[0]:
    elisa_format = st.selectbox("ELISA format (visual behavior)", ["Indirect", "Sandwich", "Direct", "Competitive"])
with fmt_row[1]:
    fit_kind = st.selectbox("Calibration fit used", ["linear", "log", "4pl"])

# Underlying (true) model for generating data (kept flexible)
true_block = st.columns(2)
with true_block[0]:
    true_model = st.selectbox("True signal model (data generator)", ["linear", "log", "4pl"])
with true_block[1]:
    seed = st.number_input("Random seed", 0, 9999, 42, step=1)

rng = np.random.default_rng(seed)

if true_model in ("linear", "log"):
    s1, s2 = st.columns(2)
    with s1:
        t_slope = st.number_input("True slope", 0.001, 5.0, 0.02, 0.01)
    with s2:
        t_intercept = st.number_input("True intercept", -1.0, 2.0, 0.10, 0.01)
    t_top=t_bottom=t_ec50=t_hill=None
else:
    s1, s2, s3, s4 = st.columns(4)
    with s1:
        t_top     = st.number_input("4PL Top", 0.1, 5.0, 2.5, 0.1)
    with s2:
        t_bottom  = st.number_input("4PL Bottom", 0.0, 1.0, 0.05, 0.01)
    with s3:
        t_ec50    = st.number_input("4PL EC50", 0.001, 1e6, 5.0, format="%.6f")
    with s4:
        t_hill    = st.number_input("4PL Hill", 0.1, 4.0, 1.2, 0.1)

# -----------------------------
# Generate dataset
# -----------------------------
def make_concs(n, lo, hi):
    return np.logspace(np.log10(lo), np.log10(hi), n)

# concentrations for standards (log spaced)
conc = make_concs(n_stds, conc_min, conc_max)

# mean signal (before background/noise), based on chosen true model
if true_model == "linear":
    true_mean = t_intercept + t_slope * conc
elif true_model == "log":
    true_mean = t_intercept + t_slope * np.log10(np.clip(conc,1e-12,None))
else:
    # 4PL (increasing with concentration)
    true_mean = four_pl(conc, t_bottom, t_top, t_ec50, t_hill)

# helper to create replicate wells from means, adding background + noise
def make_reps(mean_vec, k):
    arr = []
    for m in mean_vec:
        base = m + blank_od
        arr.append(base + rng.normal(0, well_noise, size=k))
    return np.array(arr)

# Standards (raw)
std_reps_raw = make_reps(true_mean, reps)

# Blanks (raw)
blank_vals_raw = blank_od + rng.normal(0, well_noise, size=reps)

# Negative controls (raw) — two sets, slightly different to mimic non-specific binding
neg1_raw = blank_od + rng.normal(0, well_noise, size=reps)
neg2_raw = blank_od + 0.02 + rng.normal(0, well_noise, size=reps)  # a touch higher than Neg1 on average

# Positive control (raw)
pos_conc = conc_max * 1.2
if true_model == "linear":
    pos_mean = t_intercept + t_slope * pos_conc
elif true_model == "log":
    pos_mean = t_intercept + t_slope * np.log10(pos_conc)
else:
    pos_mean = four_pl(pos_conc, t_bottom, t_top, t_ec50, t_hill)
pos_reps_raw = (pos_mean + blank_od) + rng.normal(0, well_noise, size=reps)

# Unknowns (raw)
unk_true = np.array([rng.uniform(conc_min, conc_max), rng.uniform(conc_min, conc_max)])
if true_model == "linear":
    unk_mean = t_intercept + t_slope * unk_true
elif true_model == "log":
    unk_mean = t_intercept + t_slope * np.log10(unk_true)
else:
    unk_mean = four_pl(unk_true, t_bottom, t_top, t_ec50, t_hill)
unk_reps_raw = np.vstack([(m + blank_od) + rng.normal(0, well_noise, size=reps) for m in unk_mean])

# ------------- DataFrames (start with RAW values) -------------
standards_df = pd.DataFrame(
    [{"type":"standard","level":i+1,"conc":conc[i],"od":std_reps_raw[i,j]}
     for i in range(n_stds) for j in range(reps)]
)
blank_df = pd.DataFrame({"type":"blank","level":0,"conc":0.0,"od":blank_vals_raw})
neg1_df = pd.DataFrame({"type":"neg1","level":0,"conc":0.0,"od":neg1_raw})
neg2_df = pd.DataFrame({"type":"neg2","level":0,"conc":0.0,"od":neg2_raw})
pos_df = pd.DataFrame({"type":"positive","level":0,"conc":pos_conc,"od":pos_reps_raw})
unknowns_df = pd.DataFrame(
    [{"type":f"unknown_{u+1}","level":0,"conc":unk_true[u],"od":unk_reps_raw[u,j]}
     for u in range(2) for j in range(reps)]
)

# Keep a copy for VISUAL color visualization (before subtraction)
blank_mean_raw = float(blank_df["od"].mean())
neg1_mean_raw = float(neg1_df["od"].mean())
neg2_mean_raw = float(neg2_df["od"].mean())
pos_mean_raw  = float(pos_df["od"].mean())
u1_mean_raw   = float(unknowns_df[unknowns_df["type"]=="unknown_1"]["od"].mean())
u2_mean_raw   = float(unknowns_df[unknowns_df["type"]=="unknown_2"]["od"].mean())

# Optional blank subtraction for quantitative analysis
if blank_sub:
    mu_blank = blank_df["od"].mean()
    for df in (standards_df, unknowns_df, pos_df, neg1_df, neg2_df):
        df["od"] = (df["od"] - mu_blank).clip(lower=0)

# -----------------------------
# A1) NEW — Well intensity preview (bar chart)
# -----------------------------
st.subheader("A1) Well Intensity Preview (by ELISA format)")

# Map “visual” color intensity depending on ELISA format
# For Indirect/Sandwich/Direct: higher analyte → more color (use OD directly)
# For Competitive: higher analyte → less color (invert visually)
labels = ["Blank", "Neg 1", "Neg 2", "Pos", "Patient A", "Patient B"]
od_raw_vals = np.array([blank_mean_raw, neg1_mean_raw, neg2_mean_raw, pos_mean_raw, u1_mean_raw, u2_mean_raw], dtype=float)

if elisa_format == "Competitive":
    # invert visually so more analyte → less color
    vmax, vmin = float(np.max(od_raw_vals)), float(np.min(od_raw_vals))
    # linear inversion around the observed range
    visual_vals = (vmax + vmin) - od_raw_vals
else:
    # direct mapping
    visual_vals = od_raw_vals.copy()

fig, ax = plt.subplots(figsize=(6.5, 3.4))
bars = ax.bar(labels, visual_vals)
ax.set_ylabel("Visual color intensity (relative)")
ax.set_title(f"Well intensities — {elisa_format} ELISA (visualized)")
# Slightly rotate tick labels for clarity
plt.setp(ax.get_xticklabels(), rotation=10, ha="right")
st.pyplot(fig, use_container_width=True)

st.caption(
    "Note: This preview is for **visual understanding**. For **quantitative analysis** (curve fit, back-calculation), "
    "we use the OD values below (with blank subtraction if enabled)."
)

# -----------------------------
# B) Standard curve & residuals
# -----------------------------
st.subheader("B) Standard curve & residuals")

# Fit on means of standards (after optional subtraction)
std_means = standards_df.groupby("level", as_index=False).agg(conc=("conc","mean"), od=("od","mean"))
params, yhat = fit_curve(std_means["conc"].values, std_means["od"].values, kind=fit_kind)
residuals = std_means["od"].values - yhat

c1, c2 = st.columns([3,2], gap="large")

with c1:
    x_dense = np.logspace(np.log10(conc.min()/1.5), np.log10(conc.max()*1.5), 200)
    if params["kind"] == "linear":
        y_dense = params["intercept"] + params["slope"] * x_dense
    elif params["kind"] == "log":
        y_dense = params["intercept"] + params["slope"] * np.log10(x_dense)
    else:
        y_dense = four_pl(x_dense, params["a"], params["b"], params["c"], params["d"])
    fig, ax = plt.subplots(figsize=(6,4))
    ax.scatter(std_means["conc"], std_means["od"], label="Standards (mean)")
    ax.plot(x_dense, y_dense, label=f"Fit: {params['kind'].upper()}")
    ax.set_xscale("log"); ax.set_xlabel("Concentration"); ax.set_ylabel("OD")
    ax.legend(); ax.set_title("Calibration curve")
    st.pyplot(fig, use_container_width=True)

with c2:
    fig, ax = plt.subplots(figsize=(5,2.8))
    ax.axhline(0, lw=1, color="gray")
    ax.bar(std_means["conc"], residuals, width=0.07*std_means["conc"], align='center')
    ax.set_xscale("log"); ax.set_xlabel("Concentration"); ax.set_ylabel("Residual (OD)")
    ax.set_title("Fit residuals")
    st.pyplot(fig, use_container_width=True)

# -----------------------------
# C) Replicate CVs
# -----------------------------
st.subheader("C) Replicate CVs")

def cv_table(df, group_col):
    t = df.copy()
    t["grp"] = t[group_col]
    agg = t.groupby("grp").agg(n=("od","count"), mean_od=("od","mean"), sd=("od","std")).reset_index()
    agg["cv_%"] = (agg["sd"] / agg["mean_od"] * 100).round(2)
    return agg

col1, col2 = st.columns(2)
with col1:
    st.markdown("**Standards**")
    st.dataframe(cv_table(standards_df, "level"), use_container_width=True)
with col2:
    st.markdown("**Unknowns**")
    tmp = unknowns_df.copy(); tmp["group"] = tmp["type"]
    st.dataframe(cv_table(tmp, "group"), use_container_width=True)

# -----------------------------
# D) Back-calc unknowns + LOD/LOQ
# -----------------------------
st.subheader("D) Back-calculate unknown concentrations")

unknown_means = unknowns_df.groupby("type", as_index=False).agg(mean_od=("od","mean"))
calc_conc = invert_to_conc(unknown_means["mean_od"].values, params)
results = unknown_means.copy()
results["calc_conc"] = calc_conc
results["true_conc"] = unk_true
results["%error"] = (results["calc_conc"] - results["true_conc"]) / results["true_conc"] * 100
st.dataframe(results.style.format({"mean_od": "{:.3f}", "calc_conc": "{:.3f}", "true_conc": "{:.3f}", "%error": "{:.1f}"}), use_container_width=True)

st.subheader("E) Detection limits")
x_lod, x_loq, lod_y, loq_y = lod_loq(blank_df["od"].values, params)
a,b,c,d = st.columns(4)
a.metric("Mean blank OD", f"{blank_df['od'].mean():.3f}")
b.metric("LOD (conc.)", f"{x_lod:.3f}")
c.metric("LOQ (conc.)", f"{x_loq:.3f}")
d.metric("Fit model", params["kind"].upper())

st.markdown("---")

# -----------------------------
# F) Practice — COV & qualitative classification
# -----------------------------
st.subheader("F) Practice — Cut-off (COV) & qualitative classification")

# Use CURRENT dataset means as defaults for the practice widget
defaults = {
    "Blank": float(blank_df["od"].mean()),
    "Neg 1": float(neg1_df["od"].mean()),
    "Neg 2": float(neg2_df["od"].mean()),
    "Pos": float(pos_df["od"].mean()),
    "Patient A": float(unknowns_df[unknowns_df["type"]=="unknown_1"]["od"].mean()),
    "Patient B": float(unknowns_df[unknowns_df["type"]=="unknown_2"]["od"].mean()),
}

colA, colB = st.columns(2)
with colA:
    od_blank = st.number_input("Blank OD", 0.00, 3.00, defaults["Blank"], 0.01)
    od_neg1  = st.number_input("Negative Control 1 OD", 0.00, 3.00, defaults["Neg 1"], 0.01)
    od_neg2  = st.number_input("Negative Control 2 OD", 0.00, 3.00, defaults["Neg 2"], 0.01)
with colB:
    od_pos   = st.number_input("Positive Control OD", 0.00, 3.00, defaults["Pos"], 0.01)
    od_s1    = st.number_input("Patient A OD", 0.00, 3.00, defaults["Patient A"], 0.01)
    od_s2    = st.number_input("Patient B OD", 0.00, 3.00, defaults["Patient B"], 0.01)

neg_ods = st.multiselect(
    "Pick **negative controls**",
    ["Blank","Neg 1","Neg 2","Pos","Patient A","Patient B"],
    default=["Neg 1","Neg 2"]
)
multiplier = st.number_input("COV multiplier", 1.0, 5.0, 2.1, 0.1)

# Build DataFrame expected by COV helpers:
df_cov = pd.DataFrame({
    "Well": ["Blank","Neg 1","Neg 2","Pos","Patient A","Patient B"],
    "OD":   [od_blank, od_neg1, od_neg2, od_pos, od_s1, od_s2],
})

if len(neg_ods) == 0:
    st.warning("Pick at least one negative control.")
else:
    cov, avg_neg = calc_cutoff(df_cov, neg_ods, multiplier)
    col1, col2 = st.columns(2)
    col1.metric("Average Negative OD", f"{avg_neg:.3f}")
    col2.metric("Cut-off (COV)", f"{cov:.3f}")
    results_cov = classify_samples(df_cov, cov, equivocal_margin=0.10)  # auto-detects OD column
    st.dataframe(results_cov, use_container_width=True)


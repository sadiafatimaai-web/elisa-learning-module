from utils import render_sidebar_nav
render_sidebar_nav()


import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from utils import four_pl, fit_curve, invert_to_conc, coeff_var

st.title("Page 4 — Troubleshooting Scenarios")

st.markdown("Toggle common errors to see how they distort the curve, CVs, and unknown back-calculations.")

# --- Base assay design (kept simple) ---
n_stds = st.slider("Number of standards", 4, 10, 6)
reps = st.slider("Replicates", 1, 6, 3)
conc_min = st.number_input("Min conc.", 0.001, 1e6, 0.1, format="%.6f")
conc_max = st.number_input("Max conc.", 0.001, 1e6, 100.0, format="%.6f")
blank_od = st.number_input("Background OD", 0.0, 1.0, 0.05, 0.01)
noise = st.number_input("Noise SD", 0.0, 1.0, 0.02, 0.005)
blank_sub = st.checkbox("Subtract mean blank", True)
seed = st.number_input("Seed", 0, 9999, 7)
rng = np.random.default_rng(seed)

# true model (use 4PL for realism)
top = st.number_input("True Top (max signal)", 0.2, 5.0, 2.5, 0.1)
bottom = st.number_input("True Bottom (min)", 0.0, 1.0, 0.05, 0.01)
ec50 = st.number_input("True EC50", 0.001, 1e6, 5.0, format="%.6f")
hill = st.number_input("True Hill", 0.1, 4.0, 1.2, 0.1)
fit_kind = st.selectbox("Fit used by students", ["linear","log","4pl"], index=2)

# --- Error toggles ---
st.subheader("Inject errors")
col1, col2, col3 = st.columns(3)
with col1:
    pipette = st.checkbox("Pipetting bias (one standard level)")
    reagent = st.checkbox("Reagent failure (weak enzyme/substrate)")
with col2:
    contam = st.checkbox("Contamination / high background")
    outlier = st.checkbox("Single-well outlier")
with col3:
    wrong_dil = st.checkbox("Wrong dilution for Unknown 1")

params = dict()

if pipette:
    lvl = st.selectbox("Biased level", list(range(1, n_stds+1)), index=0) - 1
    frac = st.slider("Bias fraction (+/-)", -0.5, 0.5, 0.2, 0.05)
    params["pipette_level"] = lvl; params["pipette_frac"] = frac
if reagent:
    scale = st.slider("Reagent scale (1=normal, smaller=weaker)", 0.2, 1.0, 0.6, 0.05)
    params["reagent_scale"] = scale
if contam:
    add = st.slider("Background increase (OD)", 0.05, 0.5, 0.15, 0.01)
    params["contam_add"] = add
if outlier:
    orow = st.selectbox("Outlier on level", list(range(1, n_stds+1)), index=0) - 1
    ocol = st.slider("Outlier replicate", 0, reps-1, 0, 1)
    amt = st.slider("Outlier amount (OD)", 0.2, 2.0, 1.0, 0.1)
    params["outlier"] = (orow, ocol, amt)
if wrong_dil:
    params["wrong_dil"] = True

# --- Simulate dataset ---
def make_concs(n, lo, hi):
    return np.logspace(np.log10(lo), np.log10(hi), n)

conc = make_concs(n_stds, conc_min, conc_max)
true_mean = four_pl(conc, bottom, top, ec50, hill)

def make_reps(mean_vec, k):
    arr=[]
    for m in mean_vec:
        base = m + blank_od
        arr.append(base + rng.normal(0, noise, size=k))
    return np.array(arr)

std_reps = make_reps(true_mean, reps)
blank_vals = blank_od + rng.normal(0, noise, size=reps)
unk_true = np.array([rng.uniform(conc_min, conc_max), rng.uniform(conc_min, conc_max)])
unk_mean = four_pl(unk_true, bottom, top, ec50, hill)
unk_reps = np.vstack([(m + blank_od) + rng.normal(0, noise, size=reps) for m in unk_mean])
pos_conc = conc_max * 1.2
pos_mean = four_pl(pos_conc, bottom, top, ec50, hill)
pos_reps = (pos_mean + blank_od) + rng.normal(0, noise, size=reps)

# Apply errors
if "pipette_level" in params:
    std_reps[params["pipette_level"], :] *= (1.0 + params["pipette_frac"])
if "reagent_scale" in params:
    scale = params["reagent_scale"]
    std_reps *= scale; unk_reps *= scale; pos_reps *= scale
if "contam_add" in params:
    add = params["contam_add"]
    std_reps += add; unk_reps += add; pos_reps += add; blank_vals += add
if "outlier" in params:
    i, j, a = params["outlier"]; std_reps[i, j] += a
if params.get("wrong_dil"):
    # push unknown 1 10x lower without telling the student
    unk_reps[0, :] = (four_pl(np.full(1, unk_true[0]/10), bottom, top, ec50, hill)[0] + blank_od) \
                      + rng.normal(0, noise, size=reps)

# Build dataframes
std_rows = [{"type":"standard","level":i+1,"conc":conc[i],"od":std_reps[i,j]}
            for i in range(n_stds) for j in range(reps)]
standards_df = pd.DataFrame(std_rows)
blank_df = pd.DataFrame({"type":"blank","level":0,"conc":0.0,"od":blank_vals})
unknowns_df = pd.DataFrame([{"type":f"unknown_{u+1}","level":0,"conc":unk_true[u],"od":unk_reps[u,j]}
                            for u in range(2) for j in range(reps)])
pos_df = pd.DataFrame({"type":"positive","level":0,"conc":pos_conc,"od":pos_reps})

if blank_sub:
    mu = blank_df["od"].mean()
    for df in (standards_df, unknowns_df, pos_df):
        df["od"] = (df["od"] - mu).clip(lower=0)

std_means = standards_df.groupby("level", as_index=False).agg(conc=("conc","mean"), od=("od","mean"))
params_fit, yhat = fit_curve(std_means["conc"].values, std_means["od"].values, kind=fit_kind)
res = std_means["od"].values - yhat

# --- Visuals & QC ---
c1, c2 = st.columns([3,2], gap="large")
with c1:
    x_dense = np.logspace(np.log10(conc.min()/1.5), np.log10(conc.max()*1.5), 200)
    if params_fit["kind"] == "linear":
        y_dense = params_fit["intercept"] + params_fit["slope"] * x_dense
    elif params_fit["kind"] == "log":
        y_dense = params_fit["intercept"] + params_fit["slope"] * np.log10(x_dense)
    else:
        y_dense = four_pl(x_dense, params_fit["a"], params_fit["b"], params_fit["c"], params_fit["d"])
    fig, ax = plt.subplots(figsize=(6,4))
    ax.scatter(std_means["conc"], std_means["od"], label="Standards (mean)")
    ax.plot(x_dense, y_dense, label=f"Fit: {params_fit['kind'].upper()}")
    ax.set_xscale("log"); ax.set_xlabel("Concentration"); ax.set_ylabel("OD")
    ax.legend(); ax.set_title("Curve with injected error(s)")
    st.pyplot(fig, use_container_width=True)

with c2:
    fig, ax = plt.subplots(figsize=(5,2.8))
    ax.axhline(0, lw=1, color="gray")
    ax.bar(std_means["conc"], res, width=0.07*std_means["conc"], align='center')
    ax.set_xscale("log"); ax.set_xlabel("Conc"); ax.set_ylabel("Residual (OD)")
    ax.set_title("Residual pattern")
    st.pyplot(fig, use_container_width=True)

st.subheader("Replicate CVs")
def cv_table(df, group_col):
    t = df.copy(); t["grp"] = t[group_col]
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

st.subheader("Back-calculation impact")
unknown_means = unknowns_df.groupby("type", as_index=False).agg(mean_od=("od","mean"))
calc_conc = invert_to_conc(unknown_means["mean_od"].values, params_fit)
res_tab = unknown_means.copy()
res_tab["calc_conc"] = calc_conc
res_tab["true_conc"] = unk_true
res_tab["%error"] = (res_tab["calc_conc"] - res_tab["true_conc"]) / res_tab["true_conc"] * 100
st.dataframe(res_tab.style.format({"mean_od":"{:.3f}","calc_conc":"{:.3f}","true_conc":"{:.3f}","%error":"{:.1f}"}), use_container_width=True)

st.info(
    "Diagnosis hints:\n"
    "- **High background everywhere** → contamination/poor washing.\n"
    "- **All signals weak** (including positive) → reagent failure.\n"
    "- **One level unstable / high CV** → pipetting error or outlier.\n"
    "- **Unknown off by ~10×** → wrong dilution."
)

elif sig > 1.3*bg:
    st.warning("Marginal separation: consider improving washing or blocking.")
else:
    st.error("Poor separation: reduce background or increase true signal.")

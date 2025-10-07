import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from utils import render_sidebar_nav, calc_cutoff, classify_samples

render_sidebar_nav()
st.title("Page 2 — Simulation & Practice Calculation")

st.markdown("Use this mini-simulator to **visualize color intensity** and **calculate a cut-off (COV)**.")
st.markdown("**Cut-off definition (example):**")
st.latex(r"\mathrm{COV} = 2.1 \times \text{Average Negative OD}")

fmt = st.radio(
    "Choose ELISA format",
    ["Indirect (Ab detection)", "Sandwich (Ag detection)", "Direct (Ag detection)", "Competitive (Ag detection)"],
    horizontal=True
)

# Minimal controls
col1, col2, col3 = st.columns(3)
bg = col1.slider("Background", 0.00, 0.30, 0.06, 0.01)
level_A = col2.slider("Patient A level", 0.00, 1.00, 0.75, 0.01)
level_B = col3.slider("Patient B level", 0.00, 1.00, 0.30, 0.01)

def od_for_format(format_name: str, background: float, level: float) -> float:
    # Simple toy model
    if "Competitive" in format_name:
        od = background + 2.4 * (1.0 - level)
    else:
        od = background + 2.4 * level
    return float(max(0.0, min(3.0, od)))

names = ["Blank", "Neg 1", "Neg 2", "Pos", "Patient A", "Patient B"]
vals  = [
    bg,
    od_for_format(fmt, bg, 0.00),
    od_for_format(fmt, bg, 0.00),
    od_for_format(fmt, bg, 1.00),
    od_for_format(fmt, bg, level_A),
    od_for_format(fmt, bg, level_B),
]

st.subheader("A) Visual color simulation")
fig, ax = plt.subplots(figsize=(6,3))
ax.bar(names, vals)
ax.set_ylim(0, max(2.5, max(vals) + 0.2))
ax.set_ylabel("OD (a.u.)")
ax.set_title("Simulated Well Intensities")
st.pyplot(fig, use_container_width=True)

df = pd.DataFrame({"Well": names, "OD": [round(v, 3) for v in vals]})
st.dataframe(df, use_container_width=True)

HINTS = {
    "Indirect (Ab detection)":"Signal tracks **antibody** amount binding to coated antigen.",
    "Sandwich (Ag detection)":"Signal tracks **antigen** captured by capture+detection antibodies.",
    "Direct (Ag detection)":"Signal from a single labeled antibody bound to coated antigen.",
    "Competitive (Ag detection)":"More antigen → **lower** signal (inverse relation).",
}
st.info(HINTS[fmt])

st.divider()
st.subheader("B) Cut-off & classification")

neg_ods = st.multiselect(
    "Pick **Negative Controls**", options=names, default=["Neg 1", "Neg 2"]
)
multiplier = st.number_input("COV multiplier", 1.0, 5.0, 2.1, 0.1)

if len(neg_ods) == 0:
    st.warning("Pick at least one negative control.")
else:
    cov, avg_neg = calc_cutoff(df, neg_ods, multiplier)
    c1, c2 = st.columns(2)
    c1.metric("Average Negative OD", f"{avg_neg:.3f}")
    c2.metric("Cut-off (COV)", f"{cov:.3f}")

    results = classify_samples(df, cov, equivocal_margin=0.10)
    st.dataframe(results, use_container_width=True)
    st.caption("Rule: Positive if OD > COV + 0.10; Negative if OD < COV − 0.10; else Equivocal.")

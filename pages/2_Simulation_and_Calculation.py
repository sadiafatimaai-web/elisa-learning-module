from utils import render_sidebar_nav
render_sidebar_nav()

import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from utils import calc_cutoff, classify_samples

st.title("Page 2 — Simulation & Practice Calculation")

# ✅ LaTeX fix: use st.latex (or see alt below)
st.markdown("Use this mini-simulator to **visualize color intensity** and **calculate cut-off (COV)**.")
st.markdown("**Cut-off definition (example):**")
st.latex(r"\mathrm{COV} = 2.1 \times \text{Average Negative OD}")

st.subheader("A) Visual color simulation")
st.caption("Darker shade ≈ higher OD")

# Choose format for contextual description
fmt = st.selectbox(
    "Choose ELISA format to simulate",
    ["Indirect (Ab detection)", "Sandwich (Ag detection)", "Direct (Ag detection)", "Competitive (Ag detection)"]
)

colA, colB = st.columns(2)
with colA:
    st.markdown("**Set expected OD values**")
    od_blank = st.number_input("Blank OD", 0.00, 0.20, 0.05, 0.01)
    od_neg1  = st.number_input("Negative Control 1 OD", 0.00, 0.50, 0.15, 0.01)
    od_neg2  = st.number_input("Negative Control 2 OD", 0.00, 0.50, 0.16, 0.01)
    od_pos   = st.number_input("Positive Control OD", 0.20, 3.00, 2.50, 0.05)
    od_samp1 = st.number_input("Patient A OD", 0.00, 3.00, 1.80, 0.05)
    od_samp2 = st.number_input("Patient B OD", 0.00, 3.00, 0.30, 0.05)

with colB:
    st.markdown("**Color preview**")
    ods = [("Blank", od_blank), ("Neg 1", od_neg1), ("Neg 2", od_neg2),
           ("Pos", od_pos), ("Patient A", od_samp1), ("Patient B", od_samp2)]
    # draw simple bars with intensity proportional to OD
    fig, ax = plt.subplots(figsize=(5,3))
    names = [n for n,_ in ods]
    vals  = [v for _,v in ods]
    ax.bar(names, vals)
    ax.set_ylabel("OD (arb. units)")
    ax.set_ylim(0, max(2.5, max(vals)+0.2))
    ax.set_title("Simulated Well Intensities")
    st.pyplot(fig, use_container_width=True)

st.info({
    "Indirect (Ab detection)":"Signal reflects amount of antibody in sample binding to coated antigen.",
    "Sandwich (Ag detection)":"Signal reflects antigen captured by the pair of antibodies (capture + detection).",
    "Direct (Ag detection)":"Single labeled antibody binds coated antigen; simplest, but least sensitive.",
    "Competitive (Ag detection)":"Higher antigen → **lower** signal (inverse relation)."
}[fmt])

st.divider()
st.subheader("B) Practice calculation — Cut-off & classification")

neg_ods = st.multiselect(
    "Select which wells are your **Negative Controls**",
    options=["Blank", "Neg 1", "Neg 2", "Pos", "Patient A", "Patient B"],
    default=["Neg 1", "Neg 2"]
)

multiplier = st.number_input("COV multiplier", 1.0, 5.0, 2.1, 0.1)

df = pd.DataFrame({
    "Well":["Blank","Neg 1","Neg 2","Pos","Patient A","Patient B"],
    "OD":[od_blank, od_neg1, od_neg2, od_pos, od_samp1, od_samp2]
})

if len(neg_ods) == 0:
    st.warning("Pick at least one negative control.")
else:
    cov, avg_neg = calc_cutoff(df, neg_ods, multiplier)
    st.metric("Average Negative OD", f"{avg_neg:.3f}")
    st.metric("Cut-off (COV)", f"{cov:.3f}")

    result_df = classify_samples(df, cov, equivocal_margin=0.10)
    st.dataframe(result_df, use_container_width=True)

    st.caption("Rule example: Positive if OD > COV + 0.10; Negative if OD < COV − 0.10; otherwise Equivocal.")

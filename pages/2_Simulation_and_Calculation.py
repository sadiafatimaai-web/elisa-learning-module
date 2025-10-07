from utils import render_sidebar_nav
render_sidebar_nav()


import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from utils import calc_cutoff, classify_samples

st.title("Page 2 — Simulation & Practice Calculation")

# -- intro & formula (rendered properly) ---------------------------------------
st.markdown("Use this mini-simulator to **visualize color intensity** and **calculate a cut-off (COV)**.")
st.markdown("**Cut-off definition (example):**")
st.latex(r"\mathrm{COV} = 2.1 \times \text{Average Negative OD}")

with st.expander("What the sliders mean (plain language)"):
    st.markdown("""
- **Background**: non-specific color from the plate/antibody/substrate (lower is better).
- **Patient level**: a simple stand-in for “how much target is present”.
- In **Competitive** ELISA, more target → **lower** signal (inverse).
- In the other formats (**Direct**, **Indirect**, **Sandwich**), more target → **higher** signal.
""")

st.divider()

# -- 1) choose format & preset -------------------------------------------------
fmt = st.radio(
    "Choose ELISA format",
    ["Indirect (Ab detection)", "Sandwich (Ag detection)", "Direct (Ag detection)", "Competitive (Ag detection)"],
    horizontal=True
)

preset = st.selectbox(
    "Quick presets",
    ["Clean run (typical)", "Borderline case", "Weak positives", "High background"]
)

# simple preset values
PRESETS = {
    "Clean run (typical)":     {"bg": 0.05, "A": 0.75, "B": 0.15},
    "Borderline case":         {"bg": 0.08, "A": 0.35, "B": 0.25},
    "Weak positives":          {"bg": 0.06, "A": 0.45, "B": 0.30},
    "High background":         {"bg": 0.18, "A": 0.70, "B": 0.30},
}

# initialise state once
if "sim_bg" not in st.session_state:
    st.session_state.sim_bg = PRESETS[preset]["bg"]
    st.session_state.sim_A = PRESETS[preset]["A"]
    st.session_state.sim_B = PRESETS[preset]["B"]

# if preset changes, update sliders
if st.session_state.get("last_preset") != preset:
    st.session_state.sim_bg = PRESETS[preset]["bg"]
    st.session_state.sim_A  = PRESETS[preset]["A"]
    st.session_state.sim_B  = PRESETS[preset]["B"]
    st.session_state.last_preset = preset

# -- 2) minimal controls -------------------------------------------------------
col1, col2, col3 = st.columns(3)
with col1:
    bg = st.slider("Background", 0.00, 0.30, st.session_state.sim_bg, 0.01, key="bg_slider")
with col2:
    level_A = st.slider("Patient A level", 0.00, 1.00, st.session_state.sim_A, 0.01, key="A_slider")
with col3:
    level_B = st.slider("Patient B level", 0.00, 1.00, st.session_state.sim_B, 0.01, key="B_slider")

# keep state in sync (so preset switching updates sliders)
st.session_state.sim_bg = bg
st.session_state.sim_A  = level_A
st.session_state.sim_B  = level_B

st.caption("Tip: **Background** is what your negatives read; **Patient level** is how much target you expect. The simulator turns those into OD values for each well.")

# -- 3) simple signal model → OD values ---------------------------------------
def od_for_format(format_name: str, background: float, level: float) -> float:
    """
    Toy model:
    - For Direct/Indirect/Sandwich: OD = background + 2.4 * level
    - For Competitive:               OD = background + 2.4 * (1 - level)
    Clipped into a realistic 0.0–3.0 range.
    """
    if "Competitive" in format_name:
        od = background + 2.4 * (1.0 - level)
    else:
        od = background + 2.4 * level
    return float(max(0.0, min(3.0, od)))

# define wells (negatives have level=0; positive control ~1.0)
od_blank = bg                     # blank ≈ background
od_neg1  = od_for_format(fmt, bg, 0.00)
od_neg2  = od_for_format(fmt, bg, 0.00)
od_pos   = od_for_format(fmt, bg, 1.00)
od_A     = od_for_format(fmt, bg, level_A)
od_B     = od_for_format(fmt, bg, level_B)

# -- 4) show preview (bar chart + table) --------------------------------------
st.subheader("A) Visual color simulation")
fig, ax = plt.subplots(figsize=(6,3))
names = ["Blank", "Neg 1", "Neg 2", "Pos", "Patient A", "Patient B"]
vals  = [od_blank, od_neg1, od_neg2, od_pos, od_A, od_B]
ax.bar(names, vals)
ax.set_ylim(0, max(2.5, max(vals) + 0.2))
ax.set_ylabel("OD (a.u.)")
ax.set_title("Simulated Well Intensities")
st.pyplot(fig, use_container_width=True)

df = pd.DataFrame({"Well": names, "OD": [round(v, 3) for v in vals]})
st.dataframe(df, use_container_width=True)

# context hint for format
HINTS = {
    "Indirect (Ab detection)":"Signal tracks **antibody** amount binding to coated antigen.",
    "Sandwich (Ag detection)":"Signal tracks **antigen** captured by capture+detection antibodies.",
    "Direct (Ag detection)":"Signal from a single labeled antibody bound to coated antigen.",
    "Competitive (Ag detection)":"More antigen → **lower** signal (inverse relation).",
}
st.info(HINTS[fmt])

st.divider()

# -- 5) COV calculation & classification --------------------------------------
st.subheader("B) Practice calculation — Cut-off & classification")

neg_ods = st.multiselect(
    "Pick which wells are **Negative Controls** (used to compute COV)",
    options=names, default=["Neg 1", "Neg 2"]
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

    st.caption("Rule used: Positive if OD > COV + 0.10; Negative if OD < COV − 0.10; otherwise Equivocal.")

# -- 6) teaching tips ----------------------------------------------------------
with st.expander("How to explain this to beginners"):
    st.markdown("""
1) **Background** is your baseline color (ideally very low).  
2) **Controls** anchor your interpretation: negatives define the **COV**, positives prove the assay worked.  
3) **Patients** are compared to COV with a small buffer (±0.10 here) to avoid over-calling borderline values.  
4) Competitive ELISA flips the relationship: **more target gives less color**.
""")

from utils import render_sidebar_nav
render_sidebar_nav()

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.title("Page 4 — Troubleshooting & Dos / Don’ts")

st.markdown("""
Pick an issue to see likely causes and fixes. Then try the **mini-sim** to see how changes affect signal vs background.
""")

issue = st.selectbox("Observed issue", [
    "High background (negatives too high)",
    "Low/no signal (positives too low)",
    "Poor reproducibility (high CV)",
    "Edge effects / drying artifacts"
])

if issue == "High background (negatives too high)":
    st.markdown("""
**Likely causes**
- Insufficient washing
- Inadequate blocking
- Secondary antibody too concentrated

**Fixes (Dos)**
- Increase wash cycles/volume and soak time
- Use an appropriate blocking buffer (e.g., BSA/casein)
- Titrate secondary Ab to lower concentration

**Don’ts**
- Don’t shorten wash steps
- Don’t skip blocking
""")
elif issue == "Low/no signal (positives too low)":
    st.markdown("""
**Likely causes**
- Primary Ab too dilute or wrong isotype
- Expired substrate/enzyme
- Antigen degraded or poor capture

**Fixes**
- Optimize primary/detection Ab concentrations
- Confirm enzyme/substrate integrity
- Check storage and coating conditions
""")
elif issue == "Poor reproducibility (high CV)":
    st.markdown("""
**Likely causes**
- Inconsistent pipetting/volumes
- Uneven incubation times/temperatures
- Plate not sealed properly

**Fixes**
- Calibrate pipettes, use multichannel
- Standardize timing and shaking
- Seal plates to prevent evaporation
""")
else:
    st.markdown("""
**Likely causes**
- Uneven temperature or airflow
- Plate drying at edges
- Insufficient plate sealing

**Fixes**
- Use humidified chambers or sealers
- Avoid drafts/overheating
- Balance plate position in incubator/reader
""")

st.divider()
st.subheader("Mini-simulation: tweak parameters → see Signal/Background")

wash_cycles = st.slider("Wash cycles", 1, 8, 3)
block_quality = st.selectbox("Blocking quality", ["Poor", "OK", "Good", "Excellent"], index=2)
sec_ab_dil = st.slider("Secondary Ab dilution (1:x)", 1000, 20000, 5000, step=500)

# simple toy model
bg_base = 0.25
sig_base = 1.5

bg = bg_base * (0.8 ** wash_cycles)
bg *= {"Poor":1.2, "OK":1.0, "Good":0.8, "Excellent":0.6}[block_quality]
bg *= (5000/sec_ab_dil)  # more concentrated sec Ab = higher background

sig = sig_base * (sec_ab_dil/5000)**(-0.15)  # too concentrated may increase nonspecific binding
sig *= (1.0 + 0.05*wash_cycles)  # gentle bump with better washing

fig, ax = plt.subplots(figsize=(5,3))
ax.bar(["Signal (Pos)", "Background (Neg)"], [sig, bg])
ax.set_ylim(0, max(sig,bg)*1.3)
ax.set_ylabel("Relative OD (a.u.)")
st.pyplot(fig, use_container_width=True)

if sig > 2*bg:
    st.success("Good separation: Signal is > 2× Background.")
elif sig > 1.3*bg:
    st.warning("Marginal separation: consider improving washing or blocking.")
else:
    st.error("Poor separation: reduce background or increase true signal.")

import streamlit as st
from pathlib import Path

st.title("Page 1 — Types of ELISA & Clinical Examples")

st.markdown("### The Four Core Formats")
st.markdown("""
**Direct ELISA (Ag detection)**
- Primary, enzyme-labeled antibody binds directly to **coated antigen**.
- **Pros:** Fast, simple.  **Cons:** Lower sensitivity, higher background.

**Indirect ELISA (Ab detection)**
- Coated **antigen** binds patient **primary antibody**; an enzyme-labeled **secondary antibody** amplifies signal.
- **Pros:** Sensitive, flexible.  **Cons:** Potential cross-reactivity via secondary Ab.

**Sandwich ELISA (Ag detection)**
- **Capture antibody** on plate grabs antigen; **detection antibody** (enzyme-linked) binds a second epitope → “sandwich”.
- **Pros:** High specificity/sensitivity.  **Cons:** Requires matched Ab pair.

**Competitive ELISA (small molecules / limited epitopes)**
- Sample antigen competes with labeled antigen for a limited antibody binding site.
- **Readout:** **Inversely** proportional to antigen concentration.
""")

st.divider()
st.markdown("### Real-World Examples")

c1, c2 = st.columns(2)
with c1:
    st.subheader("Pregnancy Test (hCG)")
    p = Path("assets/pregnancy_test.jpg")
    if p.exists():
        st.image(str(p), caption="Pregnancy test (lateral-flow variant of immunoassay)", use_container_width=True)
    st.markdown("""
- **Principle:** hCG antigen detection via **sandwich** format (in rapid test it’s lateral-flow, but same immunochemistry).
- **Why Sandwich?** hCG is a larger glycoprotein with multiple epitopes → capture + detection Ab pair.
""")

with c2:
    st.subheader("COVID-19 Antigen Test")
    q = Path("assets/covid_lfa.jpg")
    if q.exists():
        st.image(str(q), caption="COVID-19 rapid antigen test (lateral-flow)", use_container_width=True)
    st.markdown("""
- **Principle:** Detects **viral nucleocapsid** antigen using capture and detection antibodies (a **sandwich** approach).
- **Why not Indirect?** Antigen (not antibody) is the target → sandwich/competitive are better fits.
""")

st.divider()
st.markdown("### Key Differences at a Glance")
st.table({
    "Format": ["Direct", "Indirect", "Sandwich", "Competitive"],
    "Detects": ["Antigen", "Antibody", "Antigen", "Antigen (often small)"],
    "Sensitivity": ["Low–Medium", "Medium–High", "High", "Medium"],
    "Specificity": ["Medium", "Medium", "High", "Medium–High"],
    "Signal vs Concentration": ["Direct", "Direct", "Direct", "Inverse"],
})

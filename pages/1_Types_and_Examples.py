from utils import render_sidebar_nav
render_sidebar_nav()


import streamlit as st
from pathlib import Path
from utils import render_sidebar_nav

render_sidebar_nav()
st.title("Page 1 — Types of ELISA & Clinical Examples")

st.markdown("### The Four Core Formats")
st.markdown("""
**Direct ELISA (Ag detection):** Labeled primary antibody binds coated antigen.  
**Indirect ELISA (Ab detection):** Coated antigen → patient Ab → enzyme-linked secondary Ab.  
**Sandwich ELISA (Ag detection):** Capture Ab + detection Ab bind antigen (two epitopes).  
**Competitive ELISA (Ag detection):** Sample antigen competes with labeled antigen → **inverse** signal.
""")

c1, c2 = st.columns(2)
with c1:
    st.subheader("Pregnancy Test (hCG)")
    p = Path("assets/pregnancy_test.jpg")
    if p.exists():
        st.image(str(p), caption="Pregnancy test (lateral-flow immunoassay)", use_container_width=True)
    st.markdown("- **Format:** Sandwich (capture + detection antibodies)")

with c2:
    st.subheader("COVID-19 Antigen Test")
    q = Path("assets/covid_lfa.jpg")
    if q.exists():
        st.image(str(q), caption="COVID-19 rapid antigen (lateral-flow)", use_container_width=True)
    st.markdown("- **Format:** Sandwich (detects viral nucleocapsid antigen)")

st.markdown("### Differences at a glance")
st.table({
    "Format": ["Direct", "Indirect", "Sandwich", "Competitive"],
    "Detects": ["Antigen", "Antibody", "Antigen", "Antigen (often small)"],
    "Sensitivity": ["Low–Med", "Med–High", "High", "Med"],
    "Specificity": ["Med", "Med", "High", "Med–High"],
    "Signal vs Conc.": ["Direct", "Direct", "Direct", "Inverse"],
})

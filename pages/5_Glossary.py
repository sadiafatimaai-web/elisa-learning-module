from utils import render_sidebar_nav
render_sidebar_nav()


import streamlit as st
import pandas as pd
from utils import render_sidebar_nav

render_sidebar_nav()
st.title("Page 5 — Glossary")
st.caption("Search or browse common terms used in ELISA.")

TERMS = [
    ("Antigen (Ag)", "Molecule recognized by an antibody."),
    ("Antibody (Ab)", "Protein that specifically binds an antigen."),
    ("Capture antibody", "Coated on plate to 'capture' antigen (Sandwich ELISA)."),
    ("Detection antibody", "Enzyme-labeled Ab that binds the captured antigen for readout."),
    ("Optical Density (OD)", "Absorbance reading proportional to color intensity."),
    ("Cut-off Value (COV)", "Threshold derived from negatives (e.g., 2.1 × avg negative OD)."),
    ("Blank", "Well with no sample; measures baseline."),
    ("Negative control", "Known negative; used to compute COV."),
    ("Positive control", "Known positive; confirms assay works."),
]
df = pd.DataFrame(TERMS, columns=["Term", "Definition"])

q = st.text_input("🔎 Search a term").strip()
filtered = df[df.apply(lambda c: c.str.contains(q, case=False, na=False), axis=1).any(axis=1)] if q else df
st.dataframe(filtered, use_container_width=True, height=420)

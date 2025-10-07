pages/5_Glossary.py

import streamlit as st
import pandas as pd
from utils import render_sidebar_nav

render_sidebar_nav()
st.title("Page 5 — Glossary")

st.caption("Search or browse common terms used in ELISA.")

TERMS = [
    ("Antigen (Ag)", "A molecule (often a protein) that is recognized by an antibody."),
    ("Antibody (Ab)", "A Y-shaped protein that specifically binds an antigen."),
    ("Capture antibody", "Antibody coated on the plate to 'capture' antigen (Sandwich ELISA)."),
    ("Detection antibody", "Enzyme-labeled antibody that binds the captured antigen for readout."),
    ("Enzyme (HRP/AP)", "Horseradish peroxidase or alkaline phosphatase; converts substrate to color."),
    ("Substrate (TMB/OPD)", "Chromogenic reagent that becomes colored when acted on by the enzyme."),
    ("Optical Density (OD)", "Absorbance reading proportional to color intensity (amount of target)."),
    ("Cut-off Value (COV)", "Threshold derived from negatives (e.g., 2.1 × average negative OD) to call results."),
    ("Blank", "A well with no sample; measures baseline (instrument/reagent) signal."),
    ("Negative control", "A known negative sample; helps define the COV."),
    ("Positive control", "A known positive sample; confirms the assay works."),
    ("Standard curve", "Serial dilutions of a standard used to convert OD to concentration."),
    ("Coefficient of Variation (CV)", "Variability measure (SD/mean × 100%) across replicates."),
    ("Hook/Prozone effect", "Very high antigen saturates antibodies; paradoxically lowers signal (Sandwich ELISA)."),
    ("Cross-reactivity", "Antibody binds non-target molecules → false signal."),
    ("Matrix effect", "Interference from sample components (e.g., hemolysis, lipemia)."),
    ("Blocking", "Coating with inert protein (BSA/casein) to reduce non-specific binding."),
    ("Wash buffer (PBS-T/TBS-T)", "Buffered saline + Tween-20 used to remove unbound reagents."),
    ("Incubation", "Time/temperature for binding steps (affects sensitivity and specificity)."),
    ("Limit of Detection (LOD)", "Lowest amount that can be reliably detected (above background)."),
    ("Limit of Quantitation (LOQ)", "Lowest amount that can be quantified with acceptable precision/accuracy."),
    ("Dynamic range", "Span of concentrations that the assay measures reliably."),
    ("Replicate", "Repeated measurement of the same sample to assess precision."),
    ("Isotype (IgG/IgM)", "Class of antibody with different constant regions and functions."),
    ("Epitope", "Specific antigen site recognized by an antibody."),
    ("Monoclonal vs Polyclonal", "Mono: single epitope specificity; Poly: mixture to multiple epitopes."),
    ("Background", "Signal not due to the specific antigen-antibody reaction."),
    ("Edge effect", "Systematic differences in outer wells due to evaporation/temperature gradients."),
]

df = pd.DataFrame(TERMS, columns=["Term", "Definition"])

q = st.text_input("🔎 Search a term (e.g., 'COV', 'blocking', 'hook')").strip()
if q:
    mask = df.apply(lambda col: col.str.contains(q, case=False, na=False))
    filtered = df[mask.any(axis=1)]
else:
    filtered = df

# nice compact table
st.dataframe(filtered, use_container_width=True, height=480)

with st.expander("Notes"):
    st.markdown("""
- **COV** is lab/kit-specific; always follow the kit insert or validated SOP.
- Prefer **matched antibody pairs** for Sandwich ELISA to avoid epitope overlap.
- Use **replicates** and **controls** in every run for quality assurance.
""")

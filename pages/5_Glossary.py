import streamlit as st
import pandas as pd
from utils import render_sidebar_nav

# Sidebar navigation for consistency
render_sidebar_nav()

st.title("Page 5 — Glossary")
st.caption("Search or browse common terms used in ELISA experiments, calculations, and troubleshooting.")

# ----------------------------
# Glossary Data
# ----------------------------

TERMS = [
    ("Antigen (Ag)", "A molecule that triggers an immune response and is recognized by antibodies."),
    ("Antibody (Ab)", "A Y-shaped protein that specifically binds to an antigen."),
    ("Enzyme-Linked Immunosorbent Assay (ELISA)", "A test used to detect and measure antibodies or antigens in a sample."),
    ("Capture Antibody", "An antibody coated on the plate to 'capture' the antigen in sandwich ELISA."),
    ("Detection Antibody", "An enzyme-linked antibody that binds the captured antigen to produce a color change."),
    ("Substrate", "A chemical that reacts with the enzyme on the detection antibody to produce a colored product."),
    ("Optical Density (OD)", "The absorbance reading that represents color intensity; higher OD = more antigen/antibody bound."),
    ("Blank", "A well containing only buffer or substrate; measures baseline color (background)."),
    ("Negative Control", "A sample known to be negative; used to determine the cut-off value (COV)."),
    ("Positive Control", "A sample known to be positive; confirms that the assay reagents and steps worked."),
    ("Cut-off Value (COV)", "A threshold OD derived from negative controls (e.g., 2.1 × average negative OD) that separates positive from negative results."),
    ("Coefficient of Variation (CV)", "A measure of precision = (Standard Deviation / Mean) × 100%. Lower CV means better repeatability."),
    ("Limit of Detection (LOD)", "Lowest concentration that can be reliably distinguished from background (mean blank + 3×SD)."),
    ("Limit of Quantification (LOQ)", "Lowest concentration that can be accurately measured (mean blank + 10×SD)."),
    ("Four-Parameter Logistic (4PL) Curve", "A nonlinear model used to fit ELISA standard curves; accounts for upper/lower plateaus."),
    ("Linear Fit", "A straight-line fit used for data that increases linearly with concentration."),
    ("Log-Linear Fit", "A fit using the log of concentration for more accurate modeling of curved data."),
    ("Standard Curve", "Plot of known concentrations vs OD; used to determine unknown sample concentrations."),
    ("Back-Calculation", "Using the fitted curve to calculate the concentration of unknown samples from their OD."),
    ("Equivocal Zone", "Range around the COV where results are uncertain — not clearly positive or negative."),
    ("Replicate", "Multiple measurements of the same sample to check repeatability."),
    ("Residuals", "Difference between observed OD and the predicted OD from the fitted curve."),
    ("Hill Slope", "Describes steepness of the 4PL curve; related to binding strength."),
    ("EC50", "The concentration at which the response (OD) is halfway between the minimum and maximum."),
    ("Blank Subtraction", "Subtracting the average blank OD from all wells to remove background signal."),
    ("Pipetting Error", "Variation caused by inaccurate or inconsistent sample handling."),
    ("Contamination", "Unwanted material (e.g., leftover reagents or microbial growth) that causes high background OD."),
    ("Reagent Failure", "A loss of enzyme or substrate activity leading to weak color development."),
    ("Dilution Error", "Incorrect dilution of standards or samples, affecting concentration accuracy."),
    ("Positive Sample", "A sample whose OD is greater than the cut-off value."),
    ("Negative Sample", "A sample whose OD is below the cut-off value."),
    ("Equivocal Sample", "A sample with OD close to the cut-off — unclear result."),
    ("Simulation", "A virtual model that mimics how ELISA readings behave under certain parameters."),
    ("Troubleshooting", "Process of identifying and fixing assay performance issues such as poor fit or high CV."),
    ("Calibration", "Adjusting the curve using standards to ensure correct quantification of unknowns."),
    ("Absorbance", "Another term for optical density — light absorbed by the colored reaction product."),
]

# ----------------------------
# Display & Search
# ----------------------------

df = pd.DataFrame(TERMS, columns=["Term", "Definition"])

query = st.text_input("🔎 Search a term or abbreviation").strip()

if query:
    filtered = df[df.apply(lambda c: c.str.contains(query, case=False, na=False), axis=1).any(axis=1)]
else:
    filtered = df

st.dataframe(filtered, use_container_width=True, height=500)

st.markdown("---")
st.caption("💡 Tip: Use this glossary alongside the simulation and troubleshooting pages to understand each parameter easily.")

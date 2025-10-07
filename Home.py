from utils import render_sidebar_nav
render_sidebar_nav()

import streamlit as st
from pathlib import Path
with st.sidebar:
    st.page_link("Home.py", label="Home", icon="🏠")
    st.page_link("pages/1_Types_and_Examples.py", label="Types & Examples")
    st.page_link("pages/2_Simulation_and_Calculation.py", label="Simulation & Calculation")
    st.page_link("pages/3_Quiz.py", label="Quiz")
    st.page_link("pages/4_Troubleshooting.py", label="Troubleshooting")
st.set_page_config(page_title="ELISA Learning Module", page_icon="🧪", layout="wide")

st.title("🧪 ELISA Learning Module")
st.write("Enzyme-Linked Immunosorbent Assay (ELISA): Principle, Practice, and Interpretation.")

col1, col2 = st.columns([1,1])
with col1:
    img_path = Path("assets/elisa_plate.jpg")
    if img_path.exists():
        st.image(str(img_path), caption="96-well plate used in ELISA", use_container_width=True)
    else:
        st.info("Add an image at `assets/elisa_plate.jpg` to show here.")

with col2:
    st.markdown("""
**Definition.** ELISA is an immunoassay that detects and/or quantifies **antigens** or **antibodies**. 
A specific **antibody–antigen** interaction is linked to an **enzyme–substrate** color reaction, read as **optical density (OD)**.

**Where it’s used.**
- Infectious disease serology (e.g., HIV, HBV, Dengue)
- Hormones & cytokines (e.g., TSH, IL-6)
- Therapeutic drug monitoring & biomarkers

**You’ll learn to:**
- Distinguish **Direct**, **Indirect**, **Sandwich**, and **Competitive** ELISA
- Run a mini **simulation** and do **cut-off** calculations
- Take a **C2-level quiz** (MBBS Year 2)
- Troubleshoot common problems with **dos & don’ts**
""")
st.success("Tip: Use the left sidebar to open each page.")



# Home.py
import streamlit as st
from pathlib import Path
from utils import render_sidebar_nav
render_sidebar_nav()

st.set_page_config(page_title="ELISA Learning Module", page_icon="🧪", layout="wide")
render_sidebar_nav()

st.title("🧪 ELISA Learning Module")
st.caption("Developed by **Dr Sadia Fatima** — **October 2025**")  # ← added credit line

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

**You’ll learn to:**
- Distinguish **Direct**, **Indirect**, **Sandwich**, and **Competitive** ELISA
- Run a mini **simulation** and do **cut-off** calculations
- Take a **quiz**
- Troubleshoot common problems with **dos & don’ts**
""")

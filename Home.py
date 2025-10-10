# Home.py
import streamlit as st
from utils import render_sidebar_nav

# ---------- Page config ----------
st.set_page_config(page_title="ELISA Learning Module — Home", layout="wide")

# ---------- Sidebar (one call only) ----------
render_sidebar_nav()

# ---------- Small QR helper (local to Home only) ----------
from io import BytesIO
import qrcode
from PIL import Image  # required by qrcode for image export

def make_qr_png_bytes(url: str, box_size: int = 3, border: int = 2) -> bytes:
    """
    Create a compact QR code and return PNG bytes.
    - box_size: pixel size of each QR 'box' (2–10). Smaller = smaller QR.
    - border: white quiet-zone modules around the QR (1–4 typical).
    """
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=box_size,
        border=border,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

# ---------- Main content ----------
st.title("🏠 ELISA Learning Module")
st.caption("A hands-on, simulation-based guide to understanding ELISA experiments, calculations, and troubleshooting.")

st.markdown("## Overview")
st.markdown(
    """
Welcome! This module lets you **simulate an ELISA assay**, calculate and interpret results, and
practice **troubleshooting** real-world problems. It’s designed for beginners and instructors.
Use the sidebar to jump to Simulation, Troubleshooting, Quiz, and the Glossary.
"""
)

st.markdown("## Objectives")
st.markdown(
    """
- Understand how **ELISA** converts binding into a **color (OD)** signal  
- Build and interpret a **standard curve** (linear / log / 4PL)  
- **Back-calculate** unknown concentrations from OD  
- Use a **cut-off (COV)** to classify results as Positive / Negative / Equivocal  
- Evaluate **precision (CV)** and detection limits (**LOD/LOQ**)  
- Identify common issues and **troubleshoot** (pipetting error, reagent failure, contamination, outliers, wrong dilution)
"""
)

# ---------- QR code right under Objectives ----------
qr_url = "https://elisa-learning-module-cyauubipuyelpx7zacsfkz.streamlit.app/"  # change if needed

# Center the small QR under the Objectives
c1, c2, c3 = st.columns([1, 2, 1])
with c2:
    st.markdown("#### 📲 Open this module on your phone")
    # width adjusts the rendered size regardless of internal resolution
    st.image(make_qr_png_bytes(qr_url, box_size=3, border=2), width=120)
    st.caption(qr_url)

st.markdown("---")

st.markdown(
    """
### How to use this module
1. Start with **Simulation & Calculation** to see how standards and unknowns behave.  
2. Explore **Troubleshooting** by turning on common mistakes and watching the data change.  
3. Test yourself in the **Quiz**.  
4. Use the **Glossary** anytime for quick definitions.
"""
)

st.info(
    "Tip: If your residuals show a curved pattern or your CVs are high, try a different fit (e.g., 4PL), "
    "re-check blanks, or look for outliers and dilution mistakes."
)

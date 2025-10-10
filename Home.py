# Home.py
import streamlit as st
from utils import render_sidebar_nav
from io import BytesIO
import qrcode
from PIL import Image  # needed by qrcode

# ---------- Page Config ----------
st.set_page_config(page_title="ELISA Learning Module — Home", layout="wide")

# ---------- Sidebar ----------
render_sidebar_nav()

# ---------- Helper: small QR code ----------
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

# ---------- Header image (restored) ----------
st.image(
    "https://upload.wikimedia.org/wikipedia/commons/0/0a/ELISA_plate.jpg",
    use_container_width=True,
    caption="ELISA microplate (illustrative)"
)

# ---------- Main Content ----------
st.title("🏠 Enzyme-Linked Immunosorbent Assay (ELISA) Learning Module")

st.markdown("""
The **Enzyme-Linked Immunosorbent Assay (ELISA)** is a laboratory technique used to
detect and measure substances such as **proteins, antibodies, antigens, or hormones**
in a sample. It is one of the most commonly used **immunoassays** in diagnostic and research laboratories.

In this test, specific **antibody–antigen interactions** produce a color change
that can be measured as **Optical Density (OD)** using a spectrophotometer.
The strength of the color corresponds to the **amount of target molecule present**.

ELISA is valued for being:
- **Highly sensitive** — able to detect very small amounts of target substance.  
- **Specific** — relies on precise antibody–antigen binding.  
- **Quantitative** — the color intensity (OD) increases with concentration.
""")

st.markdown("---")

# ---------- Illustration panel: "How ELISA Works" (6 simple cards) ----------
st.markdown("## 🧪 How ELISA Works (Simplified)")

card_css = """
<style>
.elisa-grid {display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; margin-top: 8px;}
.elisa-card {border: 1px solid #e6e6e6; border-radius: 12px; padding: 14px; background: #ffffff;}
.elisa-step {font-weight: 700; margin-bottom: 6px;}
.elisa-body {font-size: 0.95rem; line-height: 1.35rem;}
@media (max-width: 1000px) { .elisa-grid {grid-template-columns: 1fr;} }
</style>
"""
st.markdown(card_css, unsafe_allow_html=True)

st.markdown("""
<div class="elisa-grid">
  <div class="elisa-card">
    <div class="elisa-step">1) 🧫 Coating</div>
    <div class="elisa-body">Antigen or antibody is attached to the microplate well surface.</div>
  </div>
  <div class="elisa-card">
    <div class="elisa-step">2) 🚫 Blocking</div>
    <div class="elisa-body">Empty areas are blocked to prevent non-specific sticking.</div>
  </div>
  <div class="elisa-card">
    <div class="elisa-step">3) 🔗 Binding</div>
    <div class="elisa-body">Sample is added; if the target is present, it binds to the coated capture partner.</div>
  </div>
  <div class="elisa-card">
    <div class="elisa-step">4) 🧷 Detection Ab</div>
    <div class="elisa-body">An enzyme-linked detection antibody binds to the captured target.</div>
  </div>
  <div class="elisa-card">
    <div class="elisa-step">5) 🎨 Substrate → Color</div>
    <div class="elisa-body">Substrate reacts with the enzyme to produce a colored product.</div>
  </div>
  <div class="elisa-card">
    <div class="elisa-step">6) 📟 Measure OD</div>
    <div class="elisa-body">A plate reader measures color as Optical Density (OD). More color ⇒ more target.</div>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ---------- NEW: Four ELISA Formats (mini-diagrams) ----------
st.markdown("## 🧫 Four ELISA Formats (at a glance)")

format_css = """
<style>
.fmt-grid {display: grid; grid-template-columns: repeat(2, 1fr); gap: 14px; margin-top: 8px;}
.fmt-card {border: 1px solid #e6e6e6; border-radius: 12px; padding: 14px; background: #ffffff;}
.fmt-title {font-weight: 700; margin-bottom: 6px;}
.fmt-body {font-size: 0.95rem; line-height: 1.35rem;}
.fmt-badge {display:inline-block; padding:2px 8px; border-radius:999px; font-size:0.8rem; margin-left:6px; background:#eef6ff; border:1px solid #cfe3ff;}
.legend {font-size: 0.9rem; color: #555; margin-top: 6px;}
@media (max-width: 1000px) { .fmt-grid {grid-template-columns: 1fr;} }
</style>
"""
st.markdown(format_css, unsafe_allow_html=True)

st.markdown("""
<div class="fmt-grid">
  <div class="fmt-card">
    <div class="fmt-title">1) Direct ELISA <span class="fmt-badge">More analyte → More color</span></div>
    <div class="fmt-body">
      Plate-bound <b>antigen</b> is detected by a single <b>enzyme-linked primary antibody</b>.
      Fewer steps, faster, but may be less signal amplification.
    </div>
  </div>
  <div class="fmt-card">
    <div class="fmt-title">2) Indirect ELISA <span class="fmt-badge">More analyte → More color</span></div>
    <div class="fmt-body">
      Plate-bound <b>antigen</b> + <b>primary antibody</b> (unlabeled) + <b>enzyme-linked secondary antibody</b>.
      Secondary Ab provides <b>signal amplification</b> and flexibility.
    </div>
  </div>
  <div class="fmt-card">
    <div class="fmt-title">3) Sandwich ELISA <span class="fmt-badge">More analyte → More color</span></div>
    <div class="fmt-body">
      Plate-bound <b>capture antibody</b> grabs the <b>antigen</b>; a second <b>enzyme-linked detection antibody</b> binds it.
      High <b>specificity</b> and sensitivity; common for diagnostics.
    </div>
  </div>
  <div class="fmt-card">
    <div class="fmt-title">4) Competitive ELISA <span class="fmt-badge">More analyte → Less color</span></div>
    <div class="fmt-body">
      Sample analyte competes with a labeled version for limited binding sites.
      <b>Higher analyte gives lower signal</b> (inverse relationship).
    </div>
  </div>
</div>
<div class="legend">Legend: “More analyte → More color” means OD increases with concentration. In <b>Competitive</b>, signal is inverted.</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ---------- Credit line ----------
st.markdown("**Developed by Dr. Sadia Fatima — October 2025**")

# ---------- QR Code below the credit ----------
qr_url = "https://elisa-learning-module-cyauubipuyelpx7zacsfkz.streamlit.app/"

c1, c2, c3 = st.columns([1, 2, 1])
with c2:
    st.markdown("#### 📲 Open this module on your phone")
    st.image(make_qr_png_bytes(qr_url, box_size=3, border=2), width=120)
    st.caption(qr_url)

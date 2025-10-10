import streamlit as st
import pandas as pd

from utils import render_sidebar_nav

# -----------------------------
# Sidebar + Title
# -----------------------------
render_sidebar_nav()
st.title("Page 1 — Types of ELISA & Clinical Examples")
st.caption("Choose the right format for your question, then explore real-world examples.")

# =========================================================
# SECTION A — Format Recommender (simple wizard)
# =========================================================
st.subheader("A) Which ELISA format should I choose? (Recommender)")

with st.expander("Open recommender"):
    c1, c2, c3 = st.columns(3)
    with c1:
        target = st.selectbox(
            "What are you detecting?",
            ["Antigen (Ag)", "Antibody (Ab)"],
            help="Antigen = a protein/biomarker from pathogen or sample. Antibody = host immune response."
        )
    with c2:
        size_epitopes = st.selectbox(
            "Is the target large with 2 epitopes?",
            ["Not sure", "Likely yes (protein, multi-epitope)", "Likely no (small molecule/peptide)"],
            help="Sandwich ELISA needs 2 non-overlapping epitopes on the antigen."
        )
    with c3:
        priorities = st.multiselect(
            "Priorities (pick 1–3)",
            ["Highest sensitivity", "Highest specificity", "Fast/least steps", "Cost-efficient", "Inverse signal OK"],
            default=["Highest specificity"]
        )

    def recommend(target, size_epitopes, priorities):
        # Basic logic
        if target == "Antibody (Ab)":
            # Indirect is the classic way to detect Ab with amplification via secondary Ab
            reason = [
                "Detecting antibodies → **Indirect ELISA** is standard.",
                "Secondary antibody gives **signal amplification** and flexibility."
            ]
            fmt = "Indirect ELISA"
        else:
            # Antigen
            if "Inverse signal OK" in priorities or size_epitopes == "Likely no (small molecule/peptide)":
                fmt = "Competitive ELISA"
                reason = [
                    "Antigen detection where **small analyte** or single epitope is likely → **Competitive** works well.",
                    "Note the **inverse signal**: more analyte → less color."
                ]
            elif size_epitopes == "Likely yes (protein, multi-epitope)":
                fmt = "Sandwich ELISA"
                reason = [
                    "Antigen with ≥2 epitopes → **Sandwich ELISA** gives **high sensitivity & specificity**.",
                    "Common choice for diagnostics."
                ]
            else:
                # If still unsure, Direct or Sandwich tradeoff
                fmt = "Direct ELISA"
                reason = [
                    "If minimal steps and fast workflow are key → **Direct ELISA**.",
                    "Fewer steps but **less amplification** than Indirect/Sandwich."
                ]

        # Modify by priorities
        notes = []
        if "Highest sensitivity" in priorities and fmt in ["Direct ELISA", "Competitive ELISA"]:
            notes.append("For **higher sensitivity**, prefer **Sandwich** (Ag) or **Indirect** (Ab).")
        if "Highest specificity" in priorities and fmt != "Sandwich ELISA" and target == "Antigen (Ag)":
            notes.append("For **highest specificity** on antigens, **Sandwich** is typically best.")
        if "Fast/least steps" in priorities and fmt != "Direct ELISA":
            notes.append("For **fastest workflow**, **Direct ELISA** is the simplest.")
        if "Cost-efficient" in priorities and fmt != "Indirect ELISA" and target == "Antibody (Ab)":
            notes.append("**Indirect ELISA** is often **cost-effective** (reusable secondary antibodies).")

        return fmt, reason, notes

    fmt, reason, notes = recommend(target, size_epitopes, priorities)

    st.markdown(f"### ✅ Recommended: **{fmt}**")
    for r in reason:
        st.markdown(f"- {r}")
    if notes:
        st.markdown("**Notes:**")
        for n in notes:
            st.markdown(f"- {n}")

# =========================================================
# SECTION B — Interactive Comparator
# =========================================================
st.subheader("B) Compare formats by what matters to you")

rows = [
    {"Format": "Direct",      "Detects": "Antigen",               "Sensitivity": "Low–Med", "Specificity": "Med",     "Signal vs Conc.": "Direct",  "Steps": "Few", "Cost": "Low"},
    {"Format": "Indirect",    "Detects": "Antibody",              "Sensitivity": "Med–High","Specificity": "Med",     "Signal vs Conc.": "Direct",  "Steps": "Moderate", "Cost": "Low–Med"},
    {"Format": "Sandwich",    "Detects": "Antigen",               "Sensitivity": "High",    "Specificity": "High",    "Signal vs Conc.": "Direct",  "Steps": "More", "Cost": "Med–High"},
    {"Format": "Competitive", "Detects": "Antigen (often small)", "Sensitivity": "Med",     "Specificity": "Med–High","Signal vs Conc.": "Inverse", "Steps": "Moderate", "Cost": "Med"},
]
df = pd.DataFrame(rows)

c1, c2, c3 = st.columns(3)
with c1:
    filt_detects = st.multiselect("Detects", sorted(df["Detects"].unique()))
with c2:
    filt_sens = st.multiselect("Sensitivity", sorted(df["Sensitivity"].unique()))
with c3:
    filt_sig = st.multiselect("Signal vs Conc.", sorted(df["Signal vs Conc."].unique()))

def apply_filters(df):
    out = df.copy()
    if filt_detects:
        out = out[out["Detects"].isin(filt_detects)]
    if filt_sens:
        out = out[out["Sensitivity"].isin(filt_sens)]
    if filt_sig:
        out = out[out["Signal vs Conc."].isin(filt_sig)]
    return out

st.dataframe(apply_filters(df), use_container_width=True, height=240)

st.caption("Tip: “Inverse” means higher analyte gives **lower** signal (Competitive ELISA).")

# =========================================================
# SECTION C — Clinical examples (compact cards)
# =========================================================
st.subheader("C) Clinical examples (fast orientation)")

card_css = """
<style>
.examples-grid {display:grid;grid-template-columns:repeat(2,1fr);gap:14px;margin-top:6px;}
.ex-card {border:1px solid #e8e8e8;border-radius:12px;padding:12px;background:#fff;}
.ex-title {font-weight:700;margin-bottom:6px;}
.ex-body {font-size:0.95rem;line-height:1.35rem;}
.ex-img img {width:100%; border-radius:10px;}
@media(max-width:1000px){.examples-grid{grid-template-columns:1fr;}}
</style>
"""
st.markdown(card_css, unsafe_allow_html=True)

st.markdown("""
<div class="examples-grid">
  <div class="ex-card">
    <div class="ex-title">Pregnancy Test (hCG) — Lateral-Flow Immunoassay</div>
    <div class="ex-img">
      <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/1/12/Pregnancy_test.jpg/640px-Pregnancy_test.jpg" alt="Pregnancy test"/>
    </div>
    <div class="ex-body">
      <b>Format:</b> Sandwich principle (capture + detection antibodies).<br/>
      <b>Why:</b> High specificity and sensitivity for the hCG hormone in urine; fast and portable.<br/>
      <b>Teaching angle:</b> LFIA is a cousin of ELISA—same immunochemistry, different readout device.
    </div>
  </div>
  <div class="ex-card">
    <div class="ex-title">COVID-19 Rapid Antigen — Lateral-Flow</div>
    <div class="ex-img">
      <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/2/2f/SARS-CoV-2_Rapid_Antigen_Test.jpg/640px-SARS-CoV-2_Rapid_Antigen_Test.jpg" alt="COVID antigen test"/>
    </div>
    <div class="ex-body">
      <b>Format:</b> Sandwich detection of viral nucleocapsid antigen.<br/>
      <b>Why:</b> Quick triage; detects active infection when antigen is present.<br/>
      <b>Teaching angle:</b> Compare with lab ELISA: LFIA trades absolute quantitation for speed and convenience.
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# =========================================================
# SECTION D — ELISA vs LFIA (when to use which?)
# =========================================================
st.subheader("D) ELISA vs Lateral-Flow: when to pick each")

col1, col2 = st.columns(2)
with col1:
    st.markdown("#### 🧪 ELISA (plate-based)")
    st.markdown("""
- **Quantitative/semiquantitative** with calibration curve  
- **High throughput** (96-well plates)  
- Great for **confirmatory/diagnostic labs**  
- Requires **plate reader**, more steps  
    """)
with col2:
    st.markdown("#### 📱 Lateral-Flow (LFIA)")
    st.markdown("""
- **Yes/No or semi-quant**, extremely **fast**  
- **Point-of-care** friendly; minimal equipment  
- Ideal for **screening** and field work  
- Less precise than full ELISA workflow  
    """)

# =========================================================
# SECTION E — Bench-side Checklist (practical)
# =========================================================
st.subheader("E) Bench Checklist (practical)")

st.markdown("""
- Pick format by **target** (Ag vs Ab) and **constraints** (sensitivity, speed, cost).  
- If antigen has **two epitopes** → try **Sandwich** first.  
- If antigen is **small/single-epitope** → **Competitive** is a good option (remember inverse signal).  
- Detecting **antibodies** → **Indirect** is classic (amplification via secondary Ab).  
- Pilot a small run to confirm **COV/CV** are reasonable before scaling.
""")

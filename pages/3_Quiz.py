from utils import render_sidebar_nav
render_sidebar_nav()

import streamlit as st

# pages/3_Quiz.py
import streamlit as st

st.title("Page 3 — Quiz")  # ← simplified title
# (remove any caption like "C2 level / MBBS Year 2")

qs = [
    {
        "q": "In an indirect ELISA, which component **directly** generates the colorimetric signal?",
        "opts": ["Coated antigen", "Patient primary antibody", "Enzyme-linked secondary antibody", "Substrate buffer"],
        "ans": 2,
        "exp": "The enzyme-linked **secondary** antibody reacts with substrate to yield the OD signal."
    },
    {
        "q": "A sandwich ELISA fails to detect antigen despite confirmed presence. Most likely cause?",
        "opts": ["Heterophilic antibody interference", "Prozone (hook) effect at high antigen levels", "Insufficient washing increases background", "Low secondary antibody concentration"],
        "ans": 1,
        "exp": "Excess antigen can saturate both antibodies and prevent the proper sandwich, creating a **hook effect**."
    },
    {
        "q": "In a competitive ELISA, increasing the sample antigen concentration will typically:",
        "opts": ["Increase signal proportionally", "Decrease signal", "Not affect signal", "Cause random noise"],
        "ans": 1,
        "exp": "Signal is **inversely** related to antigen in competitive formats."
    },
    {
        "q": "Which change most likely reduces high background in indirect ELISA?",
        "opts": ["Decrease blocking time", "Use a more concentrated secondary antibody", "Increase wash stringency/time", "Incubate at a higher temperature"],
        "ans": 2,
        "exp": "Inadequate washing is a classic source of background; stronger/longer washes help."
    },
    {
        "q": "You observe high CV between replicates. The **first** parameter to standardize is:",
        "opts": ["Plate reader wavelength", "Pipetting technique and volumes", "Blocking buffer brand", "Incubation shaker RPM"],
        "ans": 1,
        "exp": "Pipetting variability is the leading cause of replicate dispersion in ELISA."
    },
    {
        "q": "If two different capture antibodies recognize overlapping epitopes, the likely consequence in sandwich ELISA is:",
        "opts": ["Higher sensitivity", "Improved specificity", "Impaired formation of the antigen sandwich", "No effect"],
        "ans": 2,
        "exp": "Non-complementary epitopes can prevent proper sandwich formation."
    }
]

answers = []
score = 0
for i, item in enumerate(qs, start=1):
    st.markdown(f"**Q{i}.** {item['q']}")
    choice = st.radio("", item["opts"], index=None, key=f"q{i}")
    st.write("")
    answers.append(choice)

if st.button("Submit"):
    for i, item in enumerate(qs, start=1):
        picked = answers[i-1]
        correct = item["opts"][item["ans"]]
        if picked == correct:
            st.success(f"Q{i}: Correct ✅ — {item['exp']}")
            score += 1
        else:
            if picked is None:
                st.warning(f"Q{i}: No answer selected. Correct: **{correct}**. {item['exp']}")
            else:
                st.error(f"Q{i}: Incorrect ❌ — Correct: **{correct}**. {item['exp']}")
    st.info(f"**Score: {score} / {len(qs)}  ({round(100*score/len(qs))}%)**")

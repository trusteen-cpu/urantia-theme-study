import streamlit as st
import pandas as pd
import os
import re

# --------------------------------------------------
# Page Config
# --------------------------------------------------
st.set_page_config(page_title="Urantia Theme Study", layout="wide")

# --------------------------------------------------
# File Paths
# --------------------------------------------------
EN_PATH = os.path.join("data", "urantia_en.txt")
GLOSS_PATH = os.path.join("data", "English_Master_Glossary.xlsx")

# --------------------------------------------------
# Load English text file safely
# --------------------------------------------------
@st.cache_data
def load_texts():
    encodings = ["utf-8", "utf-8-sig", "cp949", "latin-1"]
    for enc in encodings:
        try:
            with open(EN_PATH, "r", encoding=enc) as f:
                return [line.strip() for line in f if line.strip()]
        except Exception:
            continue
    return []

# --------------------------------------------------
# Load Glossary
# --------------------------------------------------
@st.cache_data
def load_glossary():
    try:
        df = pd.read_excel(GLOSS_PATH)
        df.columns = [c.strip().lower() for c in df.columns]
        return df
    except Exception as e:
        st.error(f"⚠️ Glossary load error: {e}")
        return None

# --------------------------------------------------
# Data
# --------------------------------------------------
text_lines = load_texts()
glossary = load_glossary()

st.title("📘 Urantia Theme Study")
st.caption("Keyword-based English search, glossary lookup, and AI-ready theme builder (test version)")

# --------------------------------------------------
# Data existence check
# --------------------------------------------------
st.markdown("### 📦 Data status")
st.write(f"📁 data/ directory exists: {os.path.exists('data')}")
st.write(f"📄 urantia_en.txt exists: {os.path.exists(EN_PATH)} (lines: {len(text_lines)})")
st.write(f"📄 glossary: {os.path.basename(GLOSS_PATH) if os.path.exists(GLOSS_PATH) else '❌ Missing'}")

# --------------------------------------------------
# Search box
# --------------------------------------------------
term = st.text_input("🔍 Enter keyword or theme (e.g., Thought Adjuster, faith, Michael)", "", key="main_input").strip()

if term:
    st.markdown("---")

    # 1️⃣ Glossary lookup
    st.subheader("1. Glossary lookup")
    if glossary is not None:
        df = glossary.copy()
        df.columns = [c.strip().lower() for c in df.columns]

        # normalize
        df["term"] = df["term"].astype(str).str.strip().str.lower()
        df["definition"] = df["definition"].astype(str)
        found = df[df["term"].str.contains(term.lower(), case=False, na=False)]

        if len(found) > 0:
            for _, row in found.iterrows():
                st.markdown(f"**{row['term'].capitalize()}** — {row['definition']}")
        else:
            st.info("No glossary match found for this term.")
    else:
        st.warning("Glossary not loaded.")

    # 2️⃣ English text search
    st.subheader("2. Passages in The Urantia Book")
    matches = [line for line in text_lines if term.lower() in line.lower()]
    if matches:
        for m in matches[:10]:  # limit to first 10 for readability
            st.markdown(f"🔹 {m}")
    else:
        st.info("No passages found in urantia_en.txt containing that keyword.")

    # 3️⃣ Topic importance check
    st.subheader("3. Topic importance check")
    if len(matches) < 2 and len(term.split()) < 2:
        st.info("This topic seems too short or rare for an AI summary.")
    else:
        st.success("✅ Enough material to build an AI-based study later.")

    # 4️⃣ AI Study placeholder
    st.subheader("4. AI study material")
    st.info("AI explanation and PPT builder will appear here (GPT + Gamma integration to be added).")

else:
    st.info("Please enter a keyword or theme above to begin searching.")








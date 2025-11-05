import streamlit as st
import pandas as pd
import os

# -------------------------------------------------------
# 기본 설정
# -------------------------------------------------------
st.set_page_config(page_title="Urantia Theme Study", layout="wide")
st.title("📘 Urantia Theme Study")
st.caption("Keyword search + Glossary lookup + AI study draft (stable version)")

# -------------------------------------------------------
# 파일 경로
# -------------------------------------------------------
EN_PATH = os.path.join("data", "urantia_en.txt")
GLOSS_PATH = os.path.join("data", "English_Master_Glossary.xlsx")

# -------------------------------------------------------
# 영어 본문 로드
# -------------------------------------------------------
@st.cache_data
def load_text():
    encodings = ["utf-8", "utf-8-sig", "cp949", "latin-1"]
    for enc in encodings:
        try:
            with open(EN_PATH, "r", encoding=enc) as f:
                return [line.strip() for line in f if line.strip()]
        except Exception:
            continue
    return []

# -------------------------------------------------------
# 용어집 로드 (자동 컬럼 정리)
# -------------------------------------------------------
@st.cache_data
def load_glossary():
    try:
        df = pd.read_excel(GLOSS_PATH)
        raw_cols = list(df.columns)
        # 소문자+공백제거
        df.columns = [c.strip().lower() for c in df.columns]

        # 컬럼 자동 감지
        if "term" not in df.columns or "definition" not in df.columns:
            if len(df.columns) == 2:
                df.rename(columns={
                    df.columns[0]: "term",
                    df.columns[1]: "definition"
                }, inplace=True)
            else:
                for c in df.columns:
                    if "term" in c: df.rename(columns={c: "term"}, inplace=True)
                    if "def" in c or "desc" in c: df.rename(columns={c: "definition"}, inplace=True)

        df["term"] = df["term"].astype(str).str.strip().str.lower()
        df["definition"] = df["definition"].astype(str).str.strip()

        return df, raw_cols
    except Exception as e:
        st.error(f"⚠️ Glossary load error: {e}")
        return None, []

# -------------------------------------------------------
# 데이터 로드
# -------------------------------------------------------
text_lines = load_text()
glossary, raw_cols = load_glossary()

st.markdown("### 📦 Data Status")
st.write(f"📁 data/ folder exists: {os.path.exists('data')}")
st.write(f"📄 urantia_en.txt lines: {len(text_lines)}")
st.write(f"📄 glossary columns: {raw_cols if raw_cols else '❌ not loaded'}")

# -------------------------------------------------------
# 검색 입력
# -------------------------------------------------------
term = st.text_input("🔍 Enter keyword or theme (e.g., Thought Adjuster, faith, Michael)").strip()

# -------------------------------------------------------
# 검색 실행
# -------------------------------------------------------
if term:
    st.markdown("---")

    # 1️⃣ Glossary Lookup
    st.subheader("1. Glossary Lookup")
    if glossary is not None and len(glossary) > 0:
        found = glossary[glossary["term"].str.contains(term.lower(), case=False, na=False)]
        if len(found) > 0:
            for _, row in found.iterrows():
                st.markdown(f"**{row['term'].capitalize()}** — {row['definition']}")
        else:
            st.info("No glossary match found for this term.")
    else:
        st.warning("Glossary not loaded or invalid structure.")

    # 2️⃣ Urantia Book Search
    st.subheader("2. Passages in The Urantia Book")
    matches = [line for line in text_lines if term.lower() in line.lower()]
    if matches:
        for m in matches[:10]:
            st.markdown(f"🔹 {m}")
    else:
        st.info("No passages found in urantia_en.txt containing that keyword.")

    # 3️⃣ Topic importance
    st.subheader("3. Topic importance check")
    if len(matches) < 2 and len(term.split()) < 2:
        st.info("This topic seems too short or rare for an AI summary.")
    else:
        st.success("✅ Enough material for AI-based study expansion later.")

    # 4️⃣ AI Study (Placeholder)
    st.subheader("4. AI study material")
    st.info("AI explanation & PPT builder (GPT + Gamma) will appear here.")
else:
    st.info("Please enter a keyword above to begin searching.")












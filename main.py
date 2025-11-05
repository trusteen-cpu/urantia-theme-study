import streamlit as st
import pandas as pd
import os
from pathlib import Path

st.set_page_config(page_title="Urantia Theme Study (alpha)", layout="wide")

DATA_DIR = Path("data")
GLOSSARY_CANDIDATES = [
    DATA_DIR / "English_Master_Glossary.xlsx",
    DATA_DIR / "glossary.xlsx",
]
EN_PATH = DATA_DIR / "urantia_en.txt"

# ---------------------------
# 헬퍼: 텍스트 안전하게 읽기
# ---------------------------
def safe_read_text(path: Path):
    if not path.exists():
        return "", 0
    encodings = ["utf-8", "utf-8-sig", "cp949", "euc-kr", "latin-1"]
    for enc in encodings:
        try:
            text = path.read_text(encoding=enc)
            return text, len(text.splitlines())
        except Exception:
            continue
    # 마지막 수단
    text = path.read_text(encoding="utf-8", errors="replace")
    return text, len(text.splitlines())

# ---------------------------
# 헬퍼: glossary 읽기
# ---------------------------
@st.cache_data
def load_glossary():
    for cand in GLOSSARY_CANDIDATES:
        if cand.exists():
            try:
                df = pd.read_excel(cand)
                # 컬럼 이름을 소문자로
                df.columns = [str(c).strip().lower() for c in df.columns]
                return df, cand.name
            except Exception as e:
                return None, f"{cand.name} 읽기 실패: {e}"
    return None, "glossary 파일을 찾지 못했습니다."

# ---------------------------
# 실제 데이터 읽기
# ---------------------------
glossary_df, glossary_status = load_glossary()
en_text, en_lines = safe_read_text(EN_PATH)

st.title("📘 Urantia Theme Study (alpha)")
st.caption("Keyword → glossary → source passages → AI (나중에)")

# 디버그 정보 (지금은 보이게 해둠)
with st.expander("📦 Data status (이건 임시로 보이게 합니다)", expanded=True):
    st.write(f"📁 data/ 디렉토리 존재: {DATA_DIR.exists()}")
    st.write(f"📄 urantia_en.txt 존재: {EN_PATH.exists()} (lines: {en_lines})")
    st.write(f"📄 glossary 상태: {glossary_status}")

term = st.text_input("🔍 주제 / 용어를 입력하세요 (예: Thought Adjuster, faith, Michael)", "")

if term:
    term_low = term.lower().strip()

    # 1. Glossary lookup
    st.subheader("1. Glossary lookup")
term = st.text_input("찾고 싶은 용어 (영어 또는 한국어):", "", key="glossary_input").strip()

if glossary is not None and term:
    df = glossary.copy()
    # ✅ 컬럼 이름을 소문자, 공백 제거
    df.columns = [c.strip().lower() for c in df.columns]
    # ✅ term / definition 컬럼 강제 보정
    if "term" not in df.columns:
        for alt in ["word", "entry", "expression"]:
            if alt in df.columns:
                df.rename(columns={alt: "term"}, inplace=True)
    if "definition" not in df.columns:
        for alt in ["description", "meaning", "explanation"]:
            if alt in df.columns:
                df.rename(columns={alt: "definition"}, inplace=True)
    # ✅ 검색 처리
    df["term"] = df["term"].astype(str).str.strip().str.lower()
    df["definition"] = df["definition"].astype(str)
    found = df[df["term"].str.contains(term.lower(), case=False, na=False)]
    # ✅ 출력
    if len(found) > 0:
        for _, row in found.iterrows():
            st.markdown(f"**{row['term'].capitalize()}** — {row['definition']}")
    else:
        st.info("No glossary match found for this term.")

        else:
            for _, row in hits.iterrows():
                st.markdown("---")
                # 제목 후보
                title = None
                if possible_term_cols:
                    for c in possible_term_cols:
                        if c in row:
                            title = row[c]
                            break
                if not title:
                    title = term
                st.markdown(f"**🔹 {title}**")
                # 설명 후보
                body = None
                if possible_def_cols:
                    for c in possible_def_cols:
                        if c in row and row[c] not in ["", "nan", "None"]:
                            body = row[c]
                            break
                if not body:
                    # 남는 컬럼 합쳐서
                    body_parts = []
                    for c in df.columns:
                        val = row.get(c, "")
                        if isinstance(val, str) and val not in ["", "nan", "None"]:
                            body_parts.append(f"**{c}**: {val}")
                    body = "\n\n".join(body_parts)
                st.write(body)

    # 2. Passages in The Urantia Book
    st.subheader("2. Passages in The Urantia Book")
    if not en_text:
        st.warning("urantia_en.txt 를 읽지 못했습니다. data/ 안에 있고 UTF-8 또는 UTF-8-SIG 로 저장되었는지 확인해 주세요.")
    else:
        # 줄 단위로 검색
        lines = en_text.splitlines()
        hits = []
        for line in lines:
            if term_low in line.lower():
                hits.append(line.strip())
        if not hits:
            st.info("No passages found in urantia_en.txt containing that keyword.")
        else:
            st.markdown(f"**Found {len(hits)} passages containing '{term}':**")
            for h in hits[:50]:
                st.markdown(f"- {h}")

    # 3. Topic importance check (형식만)
    st.subheader("3. Topic importance check")
    st.write("이 주제가 너무 짧거나 애매하면 AI 설명을 건너뛰도록 할 수 있습니다. 지금은 수동 모드입니다.")

    # 4. AI study material (현재는 자리만)
    st.subheader("4. AI study material")
    st.write("현재는 OpenAI 호출 부분을 비워두었습니다. 위에서 본문이 1개 이상이라면 여기서 GPT 호출을 붙이면 됩니다.")
else:
    st.info("먼저 위 입력창에 찾고 싶은 주제나 단어를 넣어 주세요.")







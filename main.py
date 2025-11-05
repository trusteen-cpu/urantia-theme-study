import streamlit as st
import os
import re

# -----------------------
# 기본 설정
# -----------------------
st.set_page_config(page_title="Urantia Theme Study", layout="wide")
st.title("📘 Urantia Theme Study (GPT 5-slide generator)")
st.caption("Enter a Urantia-related theme/term → see matching passages → let GPT draft a 5-slide study outline.")

# -----------------------
# 데이터 경로
# -----------------------
DATA_DIR = "data"
EN_PATH = os.path.join(DATA_DIR, "urantia_en.txt")

# -----------------------
# 텍스트 안전하게 읽기
# -----------------------
def safe_read_text(path: str) -> list[str]:
    encodings = ["utf-8", "utf-8-sig", "cp949", "euc-kr", "latin-1"]
    last_err = None
    for enc in encodings:
        try:
            with open(path, "r", encoding=enc) as f:
                return f.readlines()
        except Exception as e:
            last_err = e
    # 최후 수단: 깨진 글자는 � 로라도
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.readlines()

@st.cache_data
def load_urantia_en():
    if not os.path.exists(EN_PATH):
        return []
    return safe_read_text(EN_PATH)

urantia_lines = load_urantia_en()

# -----------------------
# 본문 검색 함수
# -----------------------
def search_passages(keyword: str, lines: list[str], limit: int = 80):
    """키워드가 들어 있는 줄을 위에서부터 찾아서 반환"""
    if not keyword:
        return []
    keyword_lc = keyword.lower()
    results = []
    for line in lines:
        if keyword_lc in line.lower():
            results.append(line.strip())
            if len(results) >= limit:
                break
    return results

# -----------------------
# GPT 슬라이드 생성 함수
# -----------------------
def generate_slides_from_passages(term: str, passages: list[str]):
    """
    passages를 기반으로 5장짜리 슬라이드 + 발표 스크립트 생성
    OpenAI 최신 파이썬 SDK (from openai import OpenAI) 방식 사용
    """
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        return "**OPENAI_API_KEY가 설정되어 있지 않습니다. Render 환경 변수에 넣어주세요.**"

    # 최신 SDK 방식
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
    except Exception as e:
        return f"OpenAI 라이브러리를 불러오는 데 실패했습니다: {e}"

    # passages를 하나의 큰 블록으로
    source_block = "\n".join(passages) if passages else "No source passages found in the Urantia Book."

    prompt = f"""
You are helping to create a study presentation about a theme in The Urantia Book.

Theme: "{term}"

Below are source passages from the Urantia Book that mention or relate to this term:

--- SOURCE PASSAGES START ---
{source_block}
--- SOURCE PASSAGES END ---

Please do the following:

1. Read the passages and infer the Urantia-Book-specific meaning of this theme.
2. Produce **exactly 5 slides**.
3. Each slide must have:
   - Title
   - 3-5 bullet points (concise, but Urantia-ish in tone)
   - A short speaker notes section (2-4 sentences) explaining how to present this slide.
4. If the passages are few or incomplete, still infer the likely Urantia perspective and make the outline helpful for teaching.
5. Output in clean markdown with clear slide separation.

FORMAT STRICTLY LIKE THIS:

# Slide 1: <title>
- point
- point
Speaker notes: ...

# Slide 2: ...
...

Do not add extra commentary before or after.
"""

    try:
        # 모델은 사용 중인 계정에서 되는 걸로 바꾸세요
        # 온전히 지원되는 모델은 temperature 미지정이 안전
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert Urantia Book study assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        content = resp.choices[0].message.content
        return content
    except Exception as e:
        return f"⚠️ GPT 생성 중 오류가 발생했습니다:\n{e}"

# -----------------------
# UI
# -----------------------
st.subheader("1. Enter a theme / keyword")
term = st.text_input("예: Thought Adjuster, Supreme Being, Michael of Nebadon, faith, survival, morontia", "")

passages = []
if term:
    passages = search_passages(term, urantia_lines, limit=120)

st.subheader("2. Matching passages in The Urantia Book")
if not urantia_lines:
    st.error("data/urantia_en.txt 파일을 찾지 못했습니다. GitHub 저장소의 data 폴더에 이 파일을 올려주세요.")
elif term and passages:
    for i, p in enumerate(passages, start=1):
        st.markdown(f"**{i}.** {p}")
elif term and not passages:
    st.info("본문에서 이 단어를 찾지 못했습니다. 철자나 다른 표현을 시도해 보세요.")

st.subheader("3. Generate 5-slide study outline (GPT)")
st.caption("위에서 표시된 본문을 근거로 5장짜리 슬라이드 구조와 발표 스크립트를 만들어 줍니다.")

if st.button("✨ Generate 5-slide outline"):
    with st.spinner("GPT가 슬라이드 구조를 만드는 중입니다..."):
        slides_md = generate_slides_from_passages(term, passages)
    st.markdown("### 📑 Generated Slides (markdown)")
    st.markdown(slides_md)
else:
    st.info("위의 버튼을 누르면 GPT가 자동으로 5장짜리 발표안을 만들어 줍니다.")















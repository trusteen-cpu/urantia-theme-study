import streamlit as st
import os
import openai
import requests
import json

# ------------------------------------------------------------
# 기본 설정
# ------------------------------------------------------------
st.set_page_config(page_title="Urantia Theme Study", layout="wide")
st.title("📘 Urantia Theme Study")
st.caption("Keyword-based Urantia Book search, GPT-5 analysis, and Gamma PPT generation")

# ------------------------------------------------------------
# 파일 경로
# ------------------------------------------------------------
EN_PATH = os.path.join("data", "urantia_en.txt")

# ------------------------------------------------------------
# 영어 본문 로드
# ------------------------------------------------------------
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

text_lines = load_text()

# ------------------------------------------------------------
# API 키 확인
# ------------------------------------------------------------
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
GAMMA_KEY = os.getenv("GAMMA_API_KEY")  # 🔑 Gamma AI API 키

if not OPENAI_KEY:
    st.error("❌ OPENAI_API_KEY 환경변수가 없습니다. Render 환경 변수에 추가하세요.")
else:
    openai.api_key = OPENAI_KEY

# ------------------------------------------------------------
# 검색 입력
# ------------------------------------------------------------
term = st.text_input("🔍 Enter theme keyword (e.g., Thought Adjuster, Eternal Life, Michael)").strip()

# ------------------------------------------------------------
# 검색 실행
# ------------------------------------------------------------
if term:
    st.markdown("---")

    # 1️⃣ Urantia 본문 검색
    st.subheader("1. Relevant passages from The Urantia Book")
    matches = [line for line in text_lines if term.lower() in line.lower()]
    if matches:
        for m in matches[:20]:
            st.markdown(f"🔹 {m}")
    else:
        st.warning("No passages found containing that keyword.")

    # 2️⃣ GPT-5 분석 및 보고서 생성
    if OPENAI_KEY and matches:
        st.subheader("2. GPT-5 Thematic Analysis and Summary")
        with st.spinner("Analyzing theme..."):
            try:
                context = "\n".join(matches[:50])
                prompt = f"""
You are a theological researcher specializing in The Urantia Book.
Analyze the following excerpts that mention the keyword '{term}'.
Write a detailed academic report that includes:
- Summary of the main ideas
- Theological and cosmological meaning
- Connection to human spiritual growth
- Cross references and moral implications
Write clearly and elegantly in English.

Text excerpts:
{context}
                """

                response = openai.ChatCompletion.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                    max_tokens=1000
                )

                report = response.choices[0].message.content.strip()
                st.markdown(report)

                # 3️⃣ Gamma용 자료 생성
                st.subheader("3. PPT (Gamma) Export Material")
                st.markdown("The text below will be used to generate a 5-slide presentation in Gamma AI.")
                st.text_area("AI-generated Report", report, height=300)

                # 4️⃣ Gamma AI PPT 자동 생성
                if GAMMA_KEY:
                    st.subheader("4. Generate PPT via Gamma AI")
                    if st.button("🚀 Create 5-slide presentation in Gamma"):
                        try:
                            headers = {
                                "Authorization": f"Bearer {GAMMA_KEY}",
                                "Content-Type": "application/json"
                            }
                            gamma_prompt = {
                                "title": f"Urantia Theme Study — {term}",
                                "content": report,
                                "slides": 5
                            }
                            gamma_url = "https://api.gamma.app/v1/create"  # 실제 API 엔드포인트
                            r = requests.post(gamma_url, headers=headers, data=json.dumps(gamma_prompt))
                            if r.status_code == 200:
                                link = r.json().get("presentation_url", "No link returned")
                                st.success(f"✅ Gamma PPT created successfully! [Open Presentation]({link})")
                            else:
                                st.error(f"⚠️ Gamma API error: {r.status_code} — {r.text}")
                        except Exception as e:
                            st.error(f"Gamma API call failed: {e}")
                else:
                    st.info("To enable automatic PPT creation, add your `GAMMA_API_KEY` to environment variables.")

            except Exception as e:
                st.error(f"⚠️ GPT API error: {e}")

    elif not OPENAI_KEY:
        st.info("Enter your OpenAI API key to enable GPT-5 analysis.")

else:
    st.info("Please enter a keyword above to begin analysis.")













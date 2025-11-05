import streamlit as st
import os
import requests
import json
from openai import OpenAI

# ------------------------------------------------------------
# 기본 설정
# ------------------------------------------------------------
st.set_page_config(page_title="Urantia Theme Study", layout="wide")
st.title("📘 Urantia Theme Study")
st.caption("Comprehensive keyword-based Urantia Book search + GPT-5 analysis + Gamma PPT generation")

# ------------------------------------------------------------
# 파일 경로
# ------------------------------------------------------------
EN_PATH = os.path.join("data", "urantia_en.txt")

# ------------------------------------------------------------
# 본문 로드
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
GAMMA_KEY = os.getenv("GAMMA_API_KEY")

if not OPENAI_KEY:
    st.error("❌ OPENAI_API_KEY is missing. Please add it in Render → Environment Variables.")
    st.stop()

client = OpenAI(api_key=OPENAI_KEY)

# ------------------------------------------------------------
# 사용자 입력
# ------------------------------------------------------------
term = st.text_input("🔍 Enter a theme keyword (e.g., Thought Adjuster, Eternal Life, Michael)").strip()

# ------------------------------------------------------------
# 검색 및 분석
# ------------------------------------------------------------
if term:
    st.markdown("---")
    st.subheader("1️⃣ Relevant passages from The Urantia Book")

    matches = [line for line in text_lines if term.lower() in line.lower()]

    if matches:
        st.write(f"📖 Found {len(matches)} passages containing '{term}'.")
        for m in matches:
            st.markdown(f"🔹 {m}")
    else:
        st.warning("No passages found containing that keyword.")

    # --------------------------------------------------------
    # GPT 분석 보고서 생성
    # --------------------------------------------------------
    if matches:
        st.markdown("---")
        st.subheader("2️⃣ GPT-5 Thematic Analysis")

        # 긴 본문일 경우 일부만 요약에 사용
        full_context = "\n".join(matches)
        short_context = "\n".join(matches[:200])

        context_used = short_context if len(full_context) > 50000 else full_context

        with st.spinner("🧠 Analyzing with GPT-5... please wait"):
            try:
                prompt = f"""
You are an advanced Urantia Book scholar.
Analyze the following full set of passages that contain the term "{term}".

Your task:
1. Summarize all relevant teachings related to this keyword.
2. Explain its theological and cosmic meaning.
3. Show spiritual implications for human life.
4. Include relevant cross-references (if possible).
5. End with a reflective conclusion in the tone of Urantia scholarship.

Make sure your answer is faithful to the Urantia text and not distorted.

Text passages:
{context_used}
                """

                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are a Urantia scholar and researcher."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=1800,
                )

                report = response.choices[0].message.content.strip()
                st.markdown(report)

                # --------------------------------------------------------
                # PPT 내보내기
                # --------------------------------------------------------
                st.markdown("---")
                st.subheader("3️⃣ PPT Export Material")
                st.text_area("AI Study Report (for Gamma PPT generation)", report, height=300)

                # --------------------------------------------------------
                # Gamma PPT 자동 생성
                # --------------------------------------------------------
                if GAMMA_KEY:
                    st.subheader("4️⃣ Generate PPT in Gamma AI")
                    if st.button("🚀 Create 5-slide presentation in Gamma"):
                        try:
                            headers = {
                                "Authorization": f"Bearer {GAMMA_KEY}",
                                "Content-Type": "application/json"
                            }
                            payload = {
                                "title": f"Urantia Theme Study — {term}",
                                "content": report,
                                "slides": 5
                            }
                            url = "https://api.gamma.app/v1/create"
                            r = requests.post(url, headers=headers, data=json.dumps(payload))
                            if r.status_code == 200:
                                data = r.json()
                                link = data.get("presentation_url", "No link returned")
                                st.success(f"✅ PPT created successfully! [Open in Gamma]({link})")
                            else:
                                st.error(f"⚠️ Gamma API Error: {r.status_code} — {r.text}")
                        except Exception as e:
                            st.error(f"Gamma API failed: {e}")
                else:
                    st.info("To enable Gamma PPT creation, add `GAMMA_API_KEY` in your environment variables.")

            except Exception as e:
                st.error(f"⚠️ GPT-5 API Error: {e}")

else:
    st.info("Enter a keyword (e.g. 'Thought Adjuster', 'Supreme Being', 'Faith') to begin your study.")














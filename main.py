import os
import re
import streamlit as st
import pandas as pd

# ---------------------------------------------------------
# CONFIG
# ---------------------------------------------------------
st.set_page_config(page_title="Urantia Theme Study", layout="wide")

URANTIA_EN_PATH = os.path.join("data", "urantia_en.txt")
GLOSSARY_PATH = os.path.join("data", "glossary.xlsx")

# ---------------------------------------------------------
# SAFE LOADERS
# ---------------------------------------------------------
def safe_read_lines(path):
    encodings = ["utf-8", "utf-8-sig", "cp949", "euc-kr", "latin-1"]
    for enc in encodings:
        try:
            with open(path, "r", encoding=enc) as f:
                return f.readlines()
        except Exception:
            continue
    # 최후의 수단
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.readlines()

@st.cache_data
def load_urantia_en():
    lines = safe_read_lines(URANTIA_EN_PATH)
    data = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        # typical: "111:0.1 text..."
        m = re.match(r"^(\d+:\d+\.\d+)\s+(.*)$", line)
        if m:
            ref = m.group(1).strip()
            txt = m.group(2).strip()
            data.append({"ref": ref, "text": txt})
        else:
            # 라인 포맷이 다르면 그냥 텍스트만
            data.append({"ref": "", "text": line})
    return data

@st.cache_data
def load_glossary():
    if not os.path.exists(GLOSSARY_PATH):
        return pd.DataFrame(columns=["term", "definition"])
    df = pd.read_excel(GLOSSARY_PATH)
    df.columns = [c.strip().lower() for c in df.columns]
    # 기대하는 컬럼 이름: term, definition
    # 없는 경우 대비
    if "term" not in df.columns:
        df["term"] = ""
    if "definition" not in df.columns:
        df["definition"] = ""
    return df[["term", "definition"]]

urantia_en = load_urantia_en()
glossary_df = load_glossary()

# ---------------------------------------------------------
# OPTIONAL: OPENAI CLIENT
# ---------------------------------------------------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
have_openai = bool(OPENAI_API_KEY)
if have_openai:
    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_API_KEY)

# ---------------------------------------------------------
# UI - HEADER
# ---------------------------------------------------------
st.title("📘 Urantia Theme Study")
st.caption("Keyword → glossary → Urantia text → (optional) GPT analysis → 5-slide outline")

keyword = st.text_input("Enter a Urantia concept / keyword (e.g. 'Thought Adjuster', 'Supreme Being', 'Eternal Life', 'Enoch')", "")

if not keyword:
    st.info("Type a keyword above to start.")
    st.stop()

kw_lower = keyword.lower().strip()

# ---------------------------------------------------------
# 1) GLOSSARY LOOKUP
# ---------------------------------------------------------
st.subheader("1. Glossary lookup")

matched_gloss = glossary_df[glossary_df["term"].str.lower() == kw_lower]

if matched_gloss.empty:
    st.write("No glossary match found for this term.")
    glossary_def = ""
else:
    row = matched_gloss.iloc[0]
    glossary_def = row["definition"]
    st.success(f"**{row['term']}** – {row['definition']}")

# ---------------------------------------------------------
# 2) URANTIA TEXT SEARCH
# ---------------------------------------------------------
st.subheader("2. Passages in The Urantia Book")

matches = []
for entry in urantia_en:
    txt_lower = entry["text"].lower()
    if kw_lower in txt_lower:
        matches.append(entry)

if not matches:
    st.warning("No passages found in urantia_en.txt containing that keyword.")
else:
    st.write(f"Found **{len(matches)}** passage(s) containing **{keyword}**:")
    for m in matches[:100]:  # safety limit
        ref_show = m["ref"] if m["ref"] else "(no ref)"
        # highlight keyword
        highlighted = re.sub(f"(?i)({re.escape(keyword)})", r"**\1**", m["text"])
        st.markdown(f"- **{ref_show}** — {highlighted}")

# ---------------------------------------------------------
# 3) TOPIC IMPORTANCE CHECK (GPT)
# ---------------------------------------------------------
st.subheader("3. Topic importance check")

if not have_openai:
    st.info("OpenAI API key is not set. Add OPENAI_API_KEY in Render to enable GPT features.")
    st.stop()

check_btn = st.button("Check if this is a major Urantia topic")

is_major_topic = False
topic_reason = ""

if check_btn:
    # build a small context from matches (first few)
    sample_text = "\n".join([f"{m['ref']} {m['text']}" for m in matches[:5]])
    prompt = f"""
You are an expert on *The Urantia Book*.

Term: "{keyword}"

Here are some passages where it appears:
{sample_text}

Question: In the context of The Urantia Book, is this term a **major thematic / doctrinal topic** (like Trinity, Thought Adjusters, Universe Administration, Eternal Life), or is it just a **minor or incidental reference** (like a person's name that appears once)?

Answer ONLY in JSON with two fields:
{{
  "importance": "major" or "minor",
  "reason": "short explanation"
}}
"""
    try:
        resp = client.responses.create(
            model="gpt-4o-mini",  # 작은 모델로 판정만
            input=prompt
        )
        text = resp.output[0].content[0].text  # responses API 구조
        import json
        parsed = json.loads(text)
        importance = parsed.get("importance", "minor")
        topic_reason = parsed.get("reason", "")
        if importance == "major":
            is_major_topic = True
            st.success(f"Major topic ✅ — {topic_reason}")
        else:
            is_major_topic = False
            st.warning(f"Minor / incidental reference ⚠️ — {topic_reason}")
    except Exception as e:
        st.error(f"Error while checking topic importance: {e}")

# ---------------------------------------------------------
# 4) GPT ANALYSIS & 5-SLIDE OUTLINE (only for major topics)
# ---------------------------------------------------------
st.subheader("4. AI study material")

if not matches and not glossary_def:
    st.info("There is not enough source material to generate a good AI explanation.")
    st.stop()

if not is_major_topic:
    st.info("This term is not classified as a major Urantia topic. You can still force-generate analysis below.")
    force_generate = st.checkbox("Force generate anyway?")
    can_generate = force_generate
else:
    can_generate = True

if can_generate:
    gen_btn = st.button("Generate GPT analysis and 5-slide outline")
    if gen_btn:
        # build source text
        source_text = "\n".join([f"{m['ref']} {m['text']}" for m in matches[:15]])
        glossary_part = f"Glossary definition: {glossary_def}" if glossary_def else "No glossary definition available."

        analysis_prompt = f"""
You are a theologian and Urantia Book specialist.

User keyword: "{keyword}"

{glossary_part}

Below are relevant Urantia Book excerpts:
{source_text}

TASK 1 — EXPLANATION:
Write a clear, structured explanation of this concept *as it is used in The Urantia Book*: definition, cosmic context, related beings, spiritual significance. Keep it 4–6 paragraphs.

TASK 2 — SLIDE OUTLINE:
Then create a 5-slide outline for a presentation on this concept for Urantia readers. Use this JSON format:

{{
  "analysis": "...",
  "slides": [
    "Slide 1 title + bullet points",
    "Slide 2 ...",
    "Slide 3 ...",
    "Slide 4 ...",
    "Slide 5 ..."
  ]
}}
"""
        try:
            resp2 = client.responses.create(
                model="gpt-4.1-mini",
                input=analysis_prompt
            )
            raw = resp2.output[0].content[0].text
            # try to parse JSON; if fails, just show raw
            try:
                import json
                data = json.loads(raw)
                analysis = data.get("analysis", raw)
                slides = data.get("slides", [])
            except Exception:
                analysis = raw
                slides = []

            st.markdown("### 🔎 GPT Explanation")
            st.write(analysis)

            st.markdown("### 🖼 5-slide outline (for Gamma)")
            if slides:
                for i, s in enumerate(slides, start=1):
                    st.markdown(f"**Slide {i}** — {s}")
            else:
                st.write("Slides could not be parsed, but raw output is above.")
        except Exception as e:
            st.error(f"Error while generating analysis: {e}")
else:
    st.info("This term was judged minor. Nothing more to generate.")



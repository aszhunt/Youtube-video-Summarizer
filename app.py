import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs
from groq import Groq
from fpdf import FPDF

# =====================
# CONFIG
# =====================
st.set_page_config(page_title="ASZ AI Ultra V4", page_icon="🔥", layout="wide")

client = Groq(api_key="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")

# =====================
# UI
# =====================
st.markdown("""
<style>
body {background:#0a0a0a; color:white;}
.title {
    text-align:center;
    font-size:42px;
    background:linear-gradient(90deg, red, gold);
    -webkit-background-clip:text;
    -webkit-text-fill-color:transparent;
}
.box {
    background:#111;
    padding:20px;
    border-radius:12px;
    box-shadow:0 0 20px red;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">🔥 ASZ AI Video Intelligence V4</div>', unsafe_allow_html=True)

# =====================
# FUNCTIONS
# =====================

def get_video_id(url):
    try:
        return parse_qs(urlparse(url).query)["v"][0]
    except:
        return None

def get_transcript(video_id):
    try:
        data = YouTubeTranscriptApi.get_transcript(video_id)
        text = " ".join([x['text'] for x in data])
        timestamps = [(x['start'], x['text']) for x in data]
        return text, timestamps
    except:
        return None, None

def ai_main(text, duration, lang):
    prompt = f"""
You are a 20-year expert.

Provide:
1. Overview
2. Key Points
3. Insights
4. Action Steps
5. Most Important 20%

Language: {lang}
Length: {duration}

{text[:12000]}
"""
    res = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role":"user","content":prompt}]
    )
    return res.choices[0].message.content


def ai_timestamps(timestamps):
    sample = timestamps[:200]
    formatted = "\n".join([f"{int(t[0])} sec: {t[1]}" for t in sample])

    prompt = f"""
Summarize timeline into sections with timestamps.

{formatted}
"""
    res = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[{"role":"user","content":prompt}]
    )
    return res.choices[0].message.content


def ai_shorts(text):
    prompt = f"""
Find 5 viral short clips ideas from this content.

Give:
- Hook
- Clip idea
- Why viral

{text[:8000]}
"""
    res = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[{"role":"user","content":prompt}]
    )
    return res.choices[0].message.content


def ai_chat(text, question):
    prompt = f"""
Answer based ONLY on this video content:

{text[:10000]}

Question: {question}
"""
    res = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[{"role":"user","content":prompt}]
    )
    return res.choices[0].message.content


def create_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)
    for line in text.split("\n"):
        pdf.multi_cell(0, 8, line)
    return pdf.output(dest="S").encode("latin-1")

# =====================
# UI INPUT
# =====================

url = st.text_input("🔗 YouTube Link")

col1, col2 = st.columns(2)

with col1:
    duration = st.selectbox("⏱ Length", ["5 min","15 min","30 min"])

with col2:
    lang = st.selectbox("🌐 Language", ["English","Roman Urdu","Urdu"])

# =====================
# MAIN BUTTON
# =====================

if st.button("🚀 Analyze Video"):

    vid = get_video_id(url)

    if not vid:
        st.error("Invalid URL")
        st.stop()

    text, timestamps = get_transcript(vid)

    if not text:
        st.error("No captions available")
        st.stop()

    st.success("Processing...")

    main = ai_main(text, duration, lang)
    time_summary = ai_timestamps(timestamps)
    shorts = ai_shorts(text)

    st.markdown("## 📊 Main Analysis")
    st.markdown(f"<div class='box'>{main}</div>", unsafe_allow_html=True)

    st.markdown("## ⏱ Timeline Summary")
    st.write(time_summary)

    st.markdown("## 🎬 Shorts Ideas")
    st.write(shorts)

    # Chat
    st.markdown("## 💬 Ask Question from Video")
    q = st.text_input("Type your question")

    if q:
        ans = ai_chat(text, q)
        st.write(ans)

    # Download
    full = main + "\n\n" + time_summary + "\n\n" + shorts

    st.download_button("📥 TXT", full, "full_summary.txt")
    st.download_button("📄 PDF", create_pdf(full), "summary.pdf")

import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs
from groq import Groq
from fpdf import FPDF

# =====================
# CONFIG
# =====================
st.set_page_config(page_title="ASZ AI Ultra", page_icon="🔥", layout="wide")

# 🔴 PUT YOUR GROQ API KEY HERE
client = Groq(api_key="your_groq_api_key_here")

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

st.markdown('<div class="title">🔥 ASZ AI Video Intelligence</div>', unsafe_allow_html=True)

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
        return " ".join([x['text'] for x in data])
    except:
        return None

def ai_process(text, duration, lang):
    prompt = f"""
You are a 20-year expert analyst.

Analyze this YouTube transcript and give:

1. 📌 Overview
2. 🔥 Key Points
3. 🧠 Deep Insights
4. 🎯 Action Steps
5. ⚡ Most Important 20% (critical insight)
6. 🗂 Topic Breakdown
7. 💬 Key Quotes

Length: {duration}
Language: {lang}

{text[:12000]}
"""
    res = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[{"role": "user", "content": prompt}]
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
# TABS
# =====================

tab1, tab2 = st.tabs(["📄 Single Video", "📊 Compare Videos"])

# ========= SINGLE =========
with tab1:

    url = st.text_input("🔗 YouTube Link")

    col1, col2 = st.columns(2)

    with col1:
        duration = st.selectbox("⏱ Summary Length", ["5 min", "15 min", "30 min"])

    with col2:
        lang = st.selectbox("🌐 Language", ["English", "Roman Urdu", "Urdu"])

    if st.button("🚀 Generate"):

        vid = get_video_id(url)

        if not vid:
            st.error("Invalid URL")
            st.stop()

        text = get_transcript(vid)

        if not text:
            st.error("No captions available")
            st.stop()

        output = ai_process(text, duration, lang)

        st.markdown(f"<div class='box'>{output}</div>", unsafe_allow_html=True)

        # AUDIO
        st.audio(f"https://translate.google.com/translate_tts?ie=UTF-8&q={output[:200]}&tl=en&client=tw-ob")

        # DOWNLOAD
        st.download_button("📥 TXT", output, "summary.txt")

        pdf = create_pdf(output)
        st.download_button("📄 PDF", pdf, "summary.pdf")

# ========= COMPARE =========
with tab2:

    url1 = st.text_input("Video 1 Link")
    url2 = st.text_input("Video 2 Link")

    if st.button("⚔ Compare"):

        v1 = get_video_id(url1)
        v2 = get_video_id(url2)

        t1 = get_transcript(v1)
        t2 = get_transcript(v2)

        if not t1 or not t2:
            st.error("Missing captions in one video")
            st.stop()

        s1 = ai_process(t1, "15 min", "English")
        s2 = ai_process(t2, "15 min", "English")

        c1, c2 = st.columns(2)

        with c1:
            st.markdown("### 🎥 Video 1")
            st.write(s1)

        with c2:
            st.markdown("### 🎥 Video 2")
            st.write(s2)

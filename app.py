import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from urllib.parse import urlparse, parse_qs
from groq import Groq
from fpdf import FPDF

# =====================
# CONFIG
# =====================
st.set_page_config(page_title="ASZ AI Video Intelligence", page_icon="🔥", layout="wide")

# 🔴 PUT YOUR GROQ API KEY HERE
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

st.markdown('<div class="title">🔥 ASZ AI Video Intelligence (Final)</div>', unsafe_allow_html=True)

# =====================
# FUNCTIONS
# =====================

def get_video_id(url):
    try:
        parsed = urlparse(url)
        if parsed.hostname == "youtu.be":
            return parsed.path[1:]
        return parse_qs(parsed.query).get("v", [None])[0]
    except:
        return None


def get_transcript(video_id):
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

        try:
            transcript = transcript_list.find_manually_created_transcript(['en'])
        except:
            transcript = transcript_list.find_generated_transcript(['en'])

        data = transcript.fetch()

        text = " ".join([x['text'] for x in data])
        timestamps = [(x['start'], x['text']) for x in data]

        return text, timestamps

    except TranscriptsDisabled:
        return None, None
    except NoTranscriptFound:
        return None, None
    except Exception:
        return None, None


def ai_main(text, duration, lang):
    prompt = f"""
You are a 20-year expert.

Give:
1. Overview
2. Key Points
3. Insights
4. Action Steps
5. Most Important 20%
6. Topic Breakdown
7. Key Quotes

Length: {duration}
Language: {lang}

{text[:12000]}
"""
    res = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[{"role":"user","content":prompt}]
    )
    return res.choices[0].message.content


def ai_timeline(timestamps):
    sample = timestamps[:200]
    formatted = "\n".join([f"{int(t[0])} sec: {t[1]}" for t in sample])

    prompt = f"Summarize this into timeline sections:\n{formatted}"

    res = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[{"role":"user","content":prompt}]
    )
    return res.choices[0].message.content


def ai_shorts(text):
    prompt = f"""
Give 5 viral short clip ideas:
- Hook
- Idea
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
Answer ONLY from this content:

{text[:10000]}

Question: {question}
"""
    res = client.chat.completions.create(
        model="openai/gpt-oss-120b",
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
# INPUT
# =====================

url = st.text_input("🔗 Paste YouTube Link")

col1, col2 = st.columns(2)

with col1:
    duration = st.selectbox("⏱ Summary Length", ["5 min", "15 min", "30 min"])

with col2:
    lang = st.selectbox("🌐 Language", ["English", "Roman Urdu", "Urdu"])

# =====================
# MAIN BUTTON
# =====================

if st.button("🚀 Analyze Video"):

    if not url:
        st.warning("Enter a link")
        st.stop()

    if "live" in url:
        st.error("❌ Live videos not supported. Use normal YouTube video.")
        st.stop()

    video_id = get_video_id(url)

    if not video_id:
        st.error("Invalid URL")
        st.stop()

    text, timestamps = get_transcript(video_id)

    if not text:
        st.error("❌ No captions found on this video")
        st.stop()

    st.success("Processing...")

    main = ai_main(text, duration, lang)
    timeline = ai_timeline(timestamps)
    shorts = ai_shorts(text)

    st.markdown("## 📊 Main Summary")
    st.markdown(f"<div class='box'>{main}</div>", unsafe_allow_html=True)

    st.markdown("## ⏱ Timeline")
    st.write(timeline)

    st.markdown("## 🎬 Shorts Ideas")
    st.write(shorts)

    # Chat
    st.markdown("## 💬 Ask About Video")
    q = st.text_input("Ask question")

    if q:
        ans = ai_chat(text, q)
        st.write(ans)

    # Downloads
    full = main + "\n\n" + timeline + "\n\n" + shorts

    st.download_button("📥 Download TXT", full, "summary.txt")
    st.download_button("📄 Download PDF", create_pdf(full), "summary.pdf")

    # Audio preview
    st.audio(f"https://translate.google.com/translate_tts?ie=UTF-8&q={main[:200]}&tl=en&client=tw-ob")

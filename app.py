import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs
from groq import Groq

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="ASZ AI Video Intelligence", page_icon="🔥", layout="wide")

# 🔴 PUT YOUR GROQ API KEY HERE
GROQ_API_KEY = "your_groq_api_key_here"

client = Groq(api_key=GROQ_API_KEY)

# =========================
# UI STYLE
# =========================
st.markdown("""
<style>
body {
    background: #0a0a0a;
    color: white;
}
.title {
    font-size: 42px;
    font-weight: bold;
    text-align: center;
    background: linear-gradient(90deg, #ff0000, #ffcc00);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.box {
    padding: 20px;
    border-radius: 12px;
    background: #111;
    box-shadow: 0px 0px 15px rgba(255,0,0,0.3);
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">🔥 ASZ AI Video Intelligence</div>', unsafe_allow_html=True)

# =========================
# FUNCTIONS
# =========================

def extract_video_id(url):
    try:
        query = urlparse(url)
        if query.hostname == 'youtu.be':
            return query.path[1:]
        if query.hostname in ['www.youtube.com', 'youtube.com']:
            return parse_qs(query.query)['v'][0]
    except:
        return None


def get_transcript(video_id):
    try:
        data = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join([x['text'] for x in data])
    except:
        return None


def generate_summary(text, duration, language):
    prompt = f"""
You are a highly experienced expert (20+ years).

Analyze and summarize this YouTube video transcript.

Make output VERY structured and professional.

Sections:
1. 📌 Overview
2. 🔥 Key Points (bullets)
3. 🧠 Deep Insights
4. 🎯 Actionable Takeaways
5. ⚠️ Important Notes

Summary length target: {duration}

Language: {language}

Transcript:
{text[:12000]}
"""

    res = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[{"role": "user", "content": prompt}]
    )

    return res.choices[0].message.content


# =========================
# INPUT
# =========================

url = st.text_input("🔗 Paste YouTube Link")

col1, col2 = st.columns(2)

with col1:
    duration = st.selectbox("⏱ Summary Length", ["5 minutes", "15 minutes", "30 minutes"])

with col2:
    language = st.selectbox("🌐 Language", ["English", "Roman Urdu", "Urdu"])

# =========================
# BUTTON
# =========================

if st.button("🚀 Generate Intelligence"):

    if not url:
        st.warning("Please paste a link")
        st.stop()

    video_id = extract_video_id(url)

    if not video_id:
        st.error("Invalid YouTube link")
        st.stop()

    with st.spinner("📥 Getting transcript..."):
        transcript = get_transcript(video_id)

    if not transcript:
        st.error("❌ No captions available on this video")
        st.stop()

    with st.spinner("🧠 AI analyzing..."):
        output = generate_summary(transcript, duration, language)

    st.success("✅ Done")

    st.markdown("## 📊 AI Output")
    st.markdown(f"<div class='box'>{output}</div>", unsafe_allow_html=True)

    # DOWNLOAD
    st.download_button(
        label="📥 Download Summary",
        data=output,
        file_name="asz_summary.txt"
    )

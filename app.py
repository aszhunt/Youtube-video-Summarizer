import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs
from groq import Groq
from fpdf import FPDF

# CONFIG
st.set_page_config(page_title="ASZ AI FINAL", page_icon="🔥", layout="wide")

client = Groq(api_key="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")

# -------------------------
# FUNCTIONS
# -------------------------

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
        ytt = YouTubeTranscriptApi()
        transcript = ytt.fetch(video_id)

        data = transcript.to_raw_data()

        text = " ".join([x['text'] for x in data])
        return text

    except Exception as e:
        return None


def ai_summary(text):
    prompt = f"""
Summarize this video:

- Overview
- Key Points
- Insights

{text[:12000]}
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


# -------------------------
# UI
# -------------------------

st.title("🔥 ASZ FINAL VIDEO SUMMARIZER")

url = st.text_input("Paste YouTube Link")

if st.button("Generate"):

    if not url:
        st.error("Enter link")
        st.stop()

    if "live" in url:
        st.error("Live videos not supported")
        st.stop()

    video_id = get_video_id(url)

    if not video_id:
        st.error("Invalid link")
        st.stop()

    with st.spinner("Getting transcript..."):
        text = get_transcript(video_id)

    if not text:
        st.warning("⚠️ Transcript not available for this video")
        st.info("👉 Try another video with captions")
        st.stop()

    with st.spinner("AI analyzing..."):
        result = ai_summary(text)

    st.success("Done")
    st.write(result)

    st.download_button("Download TXT", result, "summary.txt")
    st.download_button("Download PDF", create_pdf(result), "summary.pdf")

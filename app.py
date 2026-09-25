import streamlit as st
import yt_dlp
from groq import Groq
from fpdf import FPDF

# CONFIG
st.set_page_config(page_title="ASZ FINAL AI", layout="wide")
client = Groq(api_key="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")

# -------------------
# GET TRANSCRIPT VIA yt-dlp
# -------------------
def get_transcript(url):
    try:
        ydl_opts = {
            'quiet': True,
            'skip_download': True,
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitlesformat': 'srt',
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

            subtitles = info.get("subtitles") or info.get("automatic_captions")

            if not subtitles:
                return None

            # pick English
            if "en" in subtitles:
                sub_url = subtitles["en"][0]["url"]
            else:
                lang = list(subtitles.keys())[0]
                sub_url = subtitles[lang][0]["url"]

        import requests
        r = requests.get(sub_url)
        return r.text

    except:
        return None


# -------------------
# AI SUMMARY
# -------------------
def ai_summary(text):
    prompt = f"""
Summarize this YouTube video:

- Overview
- Key points
- Insights

{text[:12000]}
"""
    res = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role":"user","content":prompt}]
    )
    return res.choices[0].message.content


# -------------------
# PDF
# -------------------
def create_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)
    for line in text.split("\n"):
        pdf.multi_cell(0, 8, line)
    return pdf.output(dest="S").encode("latin-1")


# -------------------
# UI
# -------------------
st.title("🔥 ASZ FINAL (NO ERROR VERSION)")

url = st.text_input("Paste YouTube Link")

if st.button("Generate"):

    if not url:
        st.error("Enter link")
        st.stop()

    with st.spinner("Getting transcript..."):
        transcript = get_transcript(url)

    if not transcript:
        st.error("❌ No captions available OR blocked video")
        st.stop()

    with st.spinner("AI analyzing..."):
        result = ai_summary(transcript)

    st.success("Done")
    st.write(result)

    st.download_button("Download TXT", result, "summary.txt")
    st.download_button("Download PDF", create_pdf(result), "summary.pdf")

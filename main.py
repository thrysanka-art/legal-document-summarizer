import streamlit as st
import nltk
import time
import textwrap
from PyPDF2 import PdfReader
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from io import BytesIO


# ------------------ NLTK ------------------
nltk.download("punkt", quiet=True)

# ------------------ PAGE CONFIG ------------------
st.set_page_config(
    page_title="Legal Document Summariser",
    page_icon="⚖️",
    layout="wide"
)

# ------------------ CSS (Glassmorphism + Animation) ------------------
def load_css(dark=True):
    if dark:
        #  DARK MODE (KEEP SAME)
        bg = "linear-gradient(135deg, #0f172a, #020617)"
        page_text = "#e5e7eb"
        card_bg = "rgba(30, 41, 59, 0.88)"
        card_text = "#e5e7eb"
        accent = "#facc15"
        shadow = "0 8px 32px rgba(0,0,0,0.45)"
    else:
        #  LIGHT MODE (WHITE + BLUE + READABLE)
        bg = "#ffffff"
        page_text = "#0f172a"
        card_bg = "#ffffff"
        card_text = "#111827"   #  THIS FIXES READABILITY
        accent = "#1e40af"
        shadow = "0 8px 20px rgba(30,64,175,0.18)"

    st.markdown(
        f"""
        <style>
        html, body {{
            background: {bg};
            color: {page_text};
            font-family: 'Segoe UI', sans-serif;
        }}

        .glass {{
            background: {card_bg};
            color: {card_text};              /*  FORCE TEXT COLOR */
            backdrop-filter: blur(14px);
            -webkit-backdrop-filter: blur(14px);
            border-radius: 18px;
            padding: 28px;
            margin-bottom: 22px;
            box-shadow: {shadow};
            animation: fadeIn 0.6s ease-in-out;
        }}

        .glass h1,
        .glass h2,
        .glass h3,
        .glass h4,
        .glass p,
        .glass li {{
            color: {card_text};              /*  HEADINGS & LISTS */
        }}

        .title {{
            text-align: center;
            font-size: 42px;
            font-weight: 700;
            color: {accent};
            margin-bottom: 14px;
            animation: slideDown 0.8s ease;
        }}

        ul {{
            padding-left: 20px;
        }}

        li {{
            margin-bottom: 8px;
        }}

        button {{
            border-radius: 10px !important;
            font-weight: 600 !important;
        }}

        @keyframes fadeIn {{
            from {{opacity:0; transform: translateY(14px);}}
            to {{opacity:1; transform: translateY(0);}}
        }}

        @keyframes slideDown {{
            from {{opacity:0; transform: translateY(-20px);}}
            to {{opacity:1; transform: translateY(0);}}
        }}

        .footer {{
            text-align: center;
            font-size: 13px;
            opacity: 0.65;
            margin-top: 45px;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )


# ------------------ SIDEBAR ------------------
st.sidebar.header("⚙️ Settings")

theme = st.sidebar.radio("🎨 Theme", [" Dark Mode", " Light Mode"])
dark_mode = theme == " Dark Mode"
load_css(dark_mode)

sentence_count = st.sidebar.slider("📝 Summary Length (Sentences)", 3, 15, 6)
uploaded_file = st.sidebar.file_uploader("📤 Upload Legal PDF", type=["pdf"])

# ------------------ FUNCTIONS ------------------
def read_pdf(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        try:
            content = page.extract_text()
            if content:
                text += content + " "
        except Exception:
            pass
    return text

def summarize_text(text, count):
    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    summarizer = LsaSummarizer()
    summary = summarizer(parser.document, count)
    return " ".join(str(sentence) for sentence in summary)

def create_pdf(summary_text):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    wrapped = textwrap.fill(summary_text, 90)
    story = [Paragraph(wrapped.replace("\n", "<br/>"), styles["Normal"])]
    doc.build(story)
    buffer.seek(0)
    return buffer

# ------------------ UI ------------------
st.markdown("<div class='title'>⚖️ Legal Document Summariser</div>", unsafe_allow_html=True)

st.markdown(
    """
    <div class="glass">
        <h3>📄 AI-powered legal document summarization</h3>
        <p>Upload a legal PDF and instantly generate a concise, readable summary.</p>
    </div>
    """,
    unsafe_allow_html=True
)

col1, col2 = st.columns(2)

with col1:
    st.markdown(
        """
        <div class="glass">
            <h3>📘 Instructions</h3>
            <ul>
                <li>Upload a legal PDF</li>
                <li>Select summary length</li>
                <li>View AI summary</li>
                <li>Download PDF summary</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        """
        <div class="glass">
            <h3>🚀 Features</h3>
            <ul>
                <li>NLP-based summarization</li>
                <li>Glassmorphism UI</li>
                <li>Dark / Light Mode</li>
                <li>PDF export</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True
    )

# ------------------ PROCESS FILE ------------------
if uploaded_file:
    progress = st.progress(0)
    status = st.empty()

    status.text("📄 Reading document...")
    text = read_pdf(uploaded_file)
    progress.progress(40)
    time.sleep(0.5)

    if not text.strip():
        st.error(" Unable to extract text. This may be a scanned PDF.")
        st.stop()

    status.text(" Generating summary...")
    summary = summarize_text(text, sentence_count)
    progress.progress(80)
    time.sleep(0.5)

    status.text(" Finalizing...")
    progress.progress(100)
    status.success("✅ Completed!")

    st.markdown("<div class='glass'><h3>📝 Summary Output</h3></div>", unsafe_allow_html=True)
    st.text_area("", summary, height=300)

    st.markdown(
        f"""
        <div class="glass">
            📄 Original Words: {len(text.split())}<br>
            📝 Summary Words: {len(summary.split())}
        </div>
        """,
        unsafe_allow_html=True
    )

    pdf_file = create_pdf(summary)

    if st.download_button(
            "⬇️ Download Summary as PDF",
            data=pdf_file,
            file_name="legal_summary.pdf",
            mime="application/pdf"
    ):
        st.success("✅ Summary PDF downloaded successfully.")

    with st.expander("📂 View Extracted Text"):
        st.write(text[:3000] + "...")

# ------------------ FOOTER ------------------
st.markdown(
    """
    <div class="footer">
        ⚠️ AI-generated summary — Not legal advice<br>
        Built by <b>Sankar</b> | AI & Robotics Diploma Project
    </div>
    """,
    unsafe_allow_html=True
)

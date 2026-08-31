import os
import re

import streamlit as st
from dotenv import load_dotenv
from pypdf import PdfReader
from docx import Document

from crewai import Crew, Task
from agent import resume_screener_agent


# =========================================================
# CONFIGURATION
# =========================================================

load_dotenv()

st.set_page_config(
    page_title="AI Resume Screener",
    page_icon="📄",
    layout="wide"
)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>

    .main-title {
        font-size: 42px;
        font-weight: 700;
        text-align: center;
        margin-bottom: 5px;
    }

    .subtitle {
        text-align: center;
        font-size: 18px;
        color: #666;
        margin-bottom: 30px;
    }

    .result-box {
        padding: 20px;
        border-radius: 12px;
        background-color: #f5f7fa;
        border: 1px solid #ddd;
        margin-top: 15px;
    }

    .score {
        font-size: 32px;
        font-weight: bold;
        text-align: center;
        padding: 15px;
    }

    .verdict {
        font-size: 26px;
        font-weight: bold;
        text-align: center;
        padding: 10px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# TITLE
# =========================================================

st.markdown(
    '<div class="main-title">🤖 AI Resume Screener</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Upload a Resume and Job Description to analyze candidate suitability'
    '</div>',
    unsafe_allow_html=True
)


# =========================================================
# FILE TEXT EXTRACTION
# =========================================================

def extract_pdf_text(uploaded_file):

    reader = PdfReader(uploaded_file)

    text = ""

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text


def extract_docx_text(uploaded_file):

    document = Document(uploaded_file)

    text = []

    for paragraph in document.paragraphs:
        if paragraph.text.strip():
            text.append(paragraph.text)

    return "\n".join(text)


def extract_text(uploaded_file):

    file_name = uploaded_file.name.lower()

    if file_name.endswith(".pdf"):
        return extract_pdf_text(uploaded_file)

    elif file_name.endswith(".docx"):
        return extract_docx_text(uploaded_file)

    elif file_name.endswith(".txt"):
        return uploaded_file.read().decode("utf-8")

    else:
        return ""


# =========================================================
# RESULT PARSING
# =========================================================

def extract_score(result):

    match = re.search(
        r"SCORE:\s*(\d{1,3})\s*/\s*100",
        result,
        re.IGNORECASE
    )

    if match:
        score = int(match.group(1))

        return min(max(score, 0), 100)

    return None


def extract_verdict(result):

    match = re.search(
        r"VERDICT:\s*(Strong|Moderate|Weak)",
        result,
        re.IGNORECASE
    )

    if match:
        return match.group(1).capitalize()

    return "Unknown"


# =========================================================
# FILE UPLOAD
# =========================================================

col1, col2 = st.columns(2)

with col1:

    st.subheader("📄 Upload Resume")

    resume_file = st.file_uploader(
        "Upload candidate resume",
        type=["pdf", "docx", "txt"],
        key="resume"
    )


with col2:

    st.subheader("💼 Upload Job Description")

    jd_file = st.file_uploader(
        "Upload job description",
        type=["pdf", "docx", "txt"],
        key="job"
    )


# =========================================================
# ANALYZE BUTTON
# =========================================================

st.markdown("---")

analyze_button = st.button(
    "🚀 Analyze Resume",
    use_container_width=True
)


# =========================================================
# ANALYSIS
# =========================================================

if analyze_button:

    if resume_file is None:

        st.error("❌ Please upload a resume.")

        st.stop()

    if jd_file is None:

        st.error("❌ Please upload a Job Description.")

        st.stop()


    # Check API key

    if not os.getenv("OPENROUTER_API_KEY"):

        st.error(
            "❌ OPENROUTER_API_KEY is missing. "
            "Please add it to your .env file."
        )

        st.stop()


    # Extract resume

    with st.spinner("📄 Reading resume..."):

        resume_text = extract_text(resume_file)


    # Extract job description

    with st.spinner("💼 Reading job description..."):

        job_description = extract_text(jd_file)


    # Validate extracted text

    if not resume_text.strip():

        st.error(
            "❌ Could not extract text from the resume. "
            "Please upload a text-based PDF, DOCX or TXT file."
        )

        st.stop()


    if not job_description.strip():

        st.error(
            "❌ Could not extract text from the Job Description."
        )

        st.stop()


    # =====================================================
    # CREATE CREWAI TASK
    # =====================================================

    screening_task = Task(
        description=f"""
Analyze this candidate resume against the provided job description.

================ RESUME ================

{resume_text}

================ JOB DESCRIPTION ================

{job_description}

==========================================

Analyze:

1. Overall resume-to-job match.
2. Technical skills.
3. Soft skills.
4. Education.
5. Work experience.
6. Certifications.
7. Missing important requirements.

Calculate a score from 0 to 100.

Then classify the candidate as:

Strong
Moderate
Weak

Use these general guidelines:

Strong:
The candidate meets most important requirements.

Moderate:
The candidate meets some important requirements but has noticeable gaps.

Weak:
The candidate does not meet many important requirements.

Do not invent information.

Return exactly:

SCORE: <number>/100

VERDICT: <Strong/Moderate/Weak>

MATCHING SKILLS:
- item
- item

MISSING OR WEAK SKILLS:
- item
- item

EXPERIENCE ANALYSIS:
text

EDUCATION ANALYSIS:
text

SUMMARY:
text

IMPROVEMENT SUGGESTIONS:
- suggestion
- suggestion
""",

        expected_output="A complete resume screening report.",
        agent=resume_screener_agent
    )


    # =====================================================
    # RUN CREWAI
    # =====================================================

    crew = Crew(
        agents=[resume_screener_agent],
        tasks=[screening_task],
        verbose=False
    )


    with st.spinner(
        "🤖 AI is comparing the resume with the Job Description..."
    ):

        try:

            result = crew.kickoff()

            result_text = str(result)

        except Exception as e:

            st.error(
                f"❌ Analysis failed: {str(e)}"
            )

            st.stop()


    # =====================================================
    # DISPLAY RESULT
    # =====================================================

    score = extract_score(result_text)

    verdict = extract_verdict(result_text)


    st.markdown("---")

    st.subheader("📊 Screening Result")


    # Score and verdict

    result_col1, result_col2 = st.columns(2)


    with result_col1:

        if score is not None:

            st.metric(
                "Resume Match Score",
                f"{score}/100"
            )

        else:

            st.metric(
                "Resume Match Score",
                "Not detected"
            )


    with result_col2:

        st.metric(
            "Final Verdict",
            verdict
        )


    # =====================================================
    # FULL AI REPORT
    # =====================================================

    st.markdown("### 🧠 AI Analysis")

    st.markdown(
        '<div class="result-box">',
        unsafe_allow_html=True
    )

    st.markdown(result_text)

    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )


    # =====================================================
    # DOWNLOAD REPORT
    # =====================================================

    st.download_button(
        label="📥 Download Screening Report",
        data=result_text,
        file_name="resume_screening_report.txt",
        mime="text/plain"
    )
"""app.py - Streamlit interface for the CV & Job Matcher (2 modes)."""
import json
import os

import streamlit as st
from pypdf import PdfReader

from demo_data import DEMO_RESULT, DEMO_REVIEW
from llm import call_llm, call_llm_json, LLMError, MODEL_NAME
from prompts import (
    EXTRACTION_SYSTEM, EXTRACTION_USER,
    MATCHING_SYSTEM, MATCHING_USER,
    COVER_LETTER_SYSTEM, COVER_LETTER_USER,
    REVIEW_SYSTEM, REVIEW_USER,
    fill,
)

MAX_CHARS = 6000  # limit the text size sent to the model


def read_pdf(file):
    """Extract the text of a PDF and handle unreadable or scanned files."""
    try:
        reader = PdfReader(file)
        text = "\n".join((page.extract_text() or "") for page in reader.pages)
    except Exception:
        raise LLMError("Could not read this PDF. Try another file.")
    if not text.strip():
        raise LLMError("No text found in the PDF (scanned image?). Try another file.")
    return text[:MAX_CHARS]


def run_pipeline(cv_text, job_text, tone, model, progress, api_key, demo):
    """Mode 1: extraction -> matching -> cover letter."""
    if demo:
        return DEMO_RESULT

    progress.progress(10, text="Step 1/3: extracting information (few-shot)...")
    cv = call_llm_json(EXTRACTION_SYSTEM, fill(EXTRACTION_USER, text=cv_text),
                       0.1, 2000, model, api_key=api_key)
    job = call_llm_json(EXTRACTION_SYSTEM, fill(EXTRACTION_USER, text=job_text),
                        0.1, 2000, model, api_key=api_key)

    progress.progress(40, text="Step 2/3: matching (persona + chain of thought)...")
    match = call_llm_json(
        MATCHING_SYSTEM,
        fill(MATCHING_USER, cv_json=json.dumps(cv), job_json=json.dumps(job)),
        0.3, 3000, model, api_key=api_key,
    )

    progress.progress(70, text="Step 3/3: writing the cover letter (persona)...")
    letter = call_llm(
        fill(COVER_LETTER_SYSTEM, tone=tone),
        fill(COVER_LETTER_USER, cv_json=json.dumps(cv), job_json=json.dumps(job),
             strengths=match.get("strengths", []), missing=match.get("missing_skills", [])),
        0.7, 2000, model, api_key=api_key,
    )
    progress.progress(100, text="Done")
    return {"match": match, "letter": letter}


def run_review(cv_text, target_role, model, progress, api_key, demo):
    """Mode 2: standalone CV review (persona + chain of thought)."""
    if demo:
        return DEMO_REVIEW

    progress.progress(30, text="Reviewing your CV (persona + chain of thought)...")
    review = call_llm_json(
        REVIEW_SYSTEM,
        fill(REVIEW_USER, cv_text=cv_text, target_role=target_role or "not specified"),
        0.3, 3000, model, api_key=api_key,
    )
    progress.progress(100, text="Done")
    return review


def safe_score(value):
    """Convert the model's score to an int between 0 and 100."""
    try:
        return max(0, min(100, int(value)))
    except (TypeError, ValueError):
        return 0


def show_list(title, items):
    st.markdown(title)
    for item in items or []:
        st.write("- " + str(item))


# ---------------- Interface ----------------
st.set_page_config(page_title="CV & Job Matcher", page_icon="🎯", layout="centered")

# Custom CSS: cleaner, more professional look
st.markdown("""
<style>
footer {visibility: hidden;}
.block-container {padding-top: 2rem; max-width: 900px;}
.app-title {font-size: 2.2rem; font-weight: 700; color: #0F172A; margin-bottom: 0;}
.app-sub {color: #64748B; margin-top: 0.2rem; margin-bottom: 1.5rem;}
div[data-testid="stMetric"] {
    background: #F1F5F9; border: 1px solid #E2E8F0;
    border-radius: 12px; padding: 16px;
}
.stButton > button {border-radius: 8px; font-weight: 600;}
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="app-title">CV &amp; Job Matcher</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="app-sub">Analyze your CV, match it with a job offer and generate a tailored cover letter.</p>',
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("Settings")

    # The key typed here stays in memory for the session only: it is never saved.
    user_key = st.text_input(
        "Groq API key", type="password",
        help="Free key from console.groq.com. Leave empty to use demo mode.",
    )
    api_key = user_key or os.getenv("GROQ_API_KEY", "")
    demo_mode = st.checkbox("Demo mode (no API key needed)", value=not api_key)
    if demo_mode:
        st.info("Demo mode: example results are shown. They are not generated "
                "from your CV. Enter an API key and untick this box for real analysis.")

    model = st.selectbox("Model", [MODEL_NAME, "openai/gpt-oss-20b"])
    tone = st.selectbox("Letter tone", ["professional and warm", "formal", "enthusiastic"])
    name = st.text_input("Your name (added at the end of the letter)")

cv_file = st.file_uploader("Your CV (PDF)", type="pdf")
tab_match, tab_review = st.tabs(["Match with a job", "CV review"])

# ----- Mode 1: matching -----
with tab_match:
    job_text = st.text_area("Job offer (paste the text)", height=200)
    if st.button("Analyze", type="primary"):
        if not demo_mode and cv_file is None:
            st.warning("Please upload your CV (PDF).")
        elif not demo_mode and not job_text.strip():
            st.warning("Please paste a job offer.")
        else:
            try:
                cv_text = "" if demo_mode else read_pdf(cv_file)
                progress = st.progress(0, text="Starting...")
                st.session_state["result"] = run_pipeline(
                    cv_text, job_text[:MAX_CHARS], tone, model, progress,
                    api_key, demo_mode)
                progress.empty()
            except LLMError as e:
                st.error(str(e))

    result = st.session_state.get("result")
    if result:
        match = result["match"]
        score = safe_score(match.get("score", 0))
        st.subheader("Match score")
        st.metric("Compatibility", f"{score} / 100")
        st.progress(score)
        col1, col2 = st.columns(2)
        with col1:
            show_list("**✅ Strengths**", match.get("strengths"))
        with col2:
            show_list("**⚠️ Missing skills**", match.get("missing_skills"))
        with st.expander("Recruiter's reasoning and advice"):
            st.write(match.get("reasoning", ""))
            for item in match.get("advice", []):
                st.write("- " + str(item))
        st.subheader("Cover letter")
        letter = result["letter"] + ("\n" + name if name else "")
        st.text_area("Letter", letter, height=350)
        st.download_button("Download (.txt)", letter, file_name="cover_letter.txt")

# ----- Mode 2: CV review -----
with tab_review:
    target_role = st.text_input("Target role (optional)", placeholder="e.g. Junior Python Developer")
    if st.button("Review my CV", type="primary"):
        if not demo_mode and cv_file is None:
            st.warning("Please upload your CV (PDF).")
        else:
            try:
                cv_text = "" if demo_mode else read_pdf(cv_file)
                progress = st.progress(0, text="Starting...")
                st.session_state["review"] = run_review(
                    cv_text, target_role, model, progress, api_key, demo_mode)
                progress.empty()
            except LLMError as e:
                st.error(str(e))

    review = st.session_state.get("review")
    if review:
        score = safe_score(review.get("overall_score", 0))
        st.subheader("CV quality")
        st.metric("Overall score", f"{score} / 100")
        st.progress(score)
        st.write(review.get("summary", ""))
        col1, col2 = st.columns(2)
        with col1:
            show_list("**✅ Sections present**", review.get("sections_present"))
            show_list("**💪 Strengths**", review.get("strengths"))
        with col2:
            show_list("**❌ Sections missing**", review.get("sections_missing"))
            show_list("**⚠️ Weaknesses**", review.get("weaknesses"))
        st.subheader("How to improve")
        for imp in review.get("improvements", []):
            if isinstance(imp, dict):
                st.markdown("**" + str(imp.get("issue", "")) + "**")
                st.write(str(imp.get("suggestion", "")))
                if imp.get("example"):
                    st.code(str(imp["example"]), language=None)
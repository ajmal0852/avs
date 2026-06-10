from __future__ import annotations

import html
from typing import Iterable

import streamlit as st

from analyzer import ResumeAnalysis, analyze_resume_vs_jd
from parser import extract_text


st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="AI",
    layout="wide",
    initial_sidebar_state="expanded",
)

MAX_ANALYSIS_CHARS = 30000


def inject_styles() -> None:
    st.markdown(
        """
        <style>
            :root {
                --bg: #f4efe6;
                --panel: #fffaf2;
                --panel-strong: #f6ead8;
                --text: #1f1b16;
                --muted: #6a5d50;
                --accent: #1f6f5b;
                --accent-2: #c76f2d;
                --border: rgba(31, 27, 22, 0.12);
            }

            .stApp {
                background:
                    radial-gradient(circle at top left, rgba(199, 111, 45, 0.12), transparent 32%),
                    radial-gradient(circle at top right, rgba(31, 111, 91, 0.10), transparent 28%),
                    linear-gradient(180deg, #fbf7f0 0%, #f4efe6 100%);
                color: var(--text);
            }

            .block-container {
                padding-top: 2rem;
                padding-bottom: 2rem;
            }

            .hero {
                padding: 1.25rem 1.4rem;
                border: 1px solid var(--border);
                border-radius: 24px;
                background: rgba(255, 250, 242, 0.85);
                backdrop-filter: blur(8px);
                box-shadow: 0 20px 50px rgba(31, 27, 22, 0.08);
            }

            .hero h1 {
                margin: 0 0 0.35rem 0;
                font-size: 2.1rem;
                line-height: 1.1;
            }

            .hero p {
                margin: 0;
                color: var(--muted);
                max-width: 70ch;
            }

            .section-card {
                padding: 1rem 1.05rem;
                border: 1px solid var(--border);
                border-radius: 18px;
                background: rgba(255, 250, 242, 0.88);
                box-shadow: 0 14px 32px rgba(31, 27, 22, 0.06);
            }

            .tag-row {
                display: flex;
                flex-wrap: wrap;
                gap: 0.55rem;
                margin-top: 0.5rem;
            }

            .tag {
                display: inline-flex;
                align-items: center;
                gap: 0.35rem;
                padding: 0.35rem 0.7rem;
                border-radius: 999px;
                border: 1px solid rgba(31, 111, 91, 0.18);
                background: rgba(31, 111, 91, 0.09);
                color: var(--accent);
                font-size: 0.9rem;
                line-height: 1;
                white-space: nowrap;
            }

            .tag.missing {
                border-color: rgba(199, 111, 45, 0.2);
                background: rgba(199, 111, 45, 0.11);
                color: #8b4a16;
            }

            .sidebar-note {
                color: var(--muted);
                font-size: 0.92rem;
                line-height: 1.45;
            }

            .stMetric {
                background: rgba(255, 250, 242, 0.90);
                border: 1px solid var(--border);
                border-radius: 18px;
                padding: 0.85rem 1rem;
                box-shadow: 0 12px 28px rgba(31, 27, 22, 0.05);
            }

            .stMarkdown ul {
                margin-top: 0.4rem;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_tag_group(items: Iterable[str], css_class: str = "") -> None:
    clean_items = [item.strip() for item in items if item and item.strip()]
    if not clean_items:
        st.caption("No items to display.")
        return

    tags = []
    for item in clean_items:
        safe_item = html.escape(item)
        tags.append(f'<span class="tag {css_class}">{safe_item}</span>')

    st.markdown('<div class="tag-row">' + "".join(tags) + "</div>", unsafe_allow_html=True)


def render_bullets(title: str, items: Iterable[str]) -> None:
    clean_items = [item.strip() for item in items if item and item.strip()]
    st.markdown(f"**{title}**")
    if not clean_items:
        st.caption("No items to display.")
        return

    st.markdown("\n".join(f"- {html.escape(item)}" for item in clean_items))


def clip_text(text: str, limit: int = MAX_ANALYSIS_CHARS) -> tuple[str, bool]:
    cleaned = text.strip()
    if len(cleaned) <= limit:
        return cleaned, False

    return cleaned[:limit], True


def main() -> None:
    inject_styles()

    st.sidebar.title("Resume Input")
    st.sidebar.markdown(
        "<div class='sidebar-note'>Upload a PDF or DOCX resume, paste the job description, then run the analysis.</div>",
        unsafe_allow_html=True,
    )

    uploaded_file = st.sidebar.file_uploader(
        "Resume file",
        type=["pdf", "docx"],
        accept_multiple_files=False,
        help="Supported formats: PDF and DOCX.",
    )
    job_description = st.sidebar.text_area(
        "Job description",
        height=320,
        placeholder="Paste the job description here...",
    )

    analyze_clicked = st.sidebar.button("Run Analysis", type="primary", use_container_width=True)

    st.markdown(
        """
        <div class="hero">
            <h1>AI Resume Analyzer</h1>
            <p>Upload a resume, compare it against the job description, and review the match score, skill gaps, and feedback in a compact dashboard.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("")

    if "analysis_result" not in st.session_state:
        st.session_state.analysis_result = None
    if "analysis_error" not in st.session_state:
        st.session_state.analysis_error = None
    if "resume_text" not in st.session_state:
        st.session_state.resume_text = ""

    if analyze_clicked:
        st.session_state.analysis_error = None
        st.session_state.analysis_result = None

        if uploaded_file is None:
            st.session_state.analysis_error = "Please upload a resume file before running the analysis."
        elif not job_description.strip():
            st.session_state.analysis_error = "Please enter a job description before running the analysis."
        else:
            try:
                with st.spinner("Extracting resume text and analyzing match..."):
                    resume_text = extract_text(uploaded_file)
                    clipped_resume_text, resume_was_clipped = clip_text(resume_text)
                    clipped_job_description, jd_was_clipped = clip_text(job_description.strip())
                    st.session_state.resume_text = clipped_resume_text
                    st.session_state.analysis_result = analyze_resume_vs_jd(
                        clipped_resume_text,
                        clipped_job_description,
                    )

                    if resume_was_clipped or jd_was_clipped:
                        st.info("Input text was trimmed to stay within a safer analysis size for Gemini.")
            except Exception as exc:
                st.session_state.analysis_error = str(exc)

    if st.session_state.analysis_error:
        st.error(st.session_state.analysis_error)

    result: ResumeAnalysis | None = st.session_state.analysis_result

    if result is None:
        st.info("Run an analysis to see the match score, matched skills, missing skills, and feedback.")
        return

    top_left, top_right, top_mid = st.columns([1.1, 1, 1])
    top_left.metric("Overall Match Score", f"{result.match_percentage}%")
    top_right.metric("Matched Skills", str(len(result.matched_skills)))
    top_mid.metric("Missing Skills", str(len(result.missing_skills)))

    middle_left, middle_right = st.columns(2)

    with middle_left:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("### Matched Skills")
        render_tag_group(result.matched_skills)
        st.markdown("</div>", unsafe_allow_html=True)

    with middle_right:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("### Missing Skills")
        render_tag_group(result.missing_skills, css_class="missing")
        st.markdown("</div>", unsafe_allow_html=True)

    st.write("")

    bottom_left, bottom_right = st.columns(2)

    with bottom_left:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        render_bullets("Strengths", result.strengths)
        st.markdown("</div>", unsafe_allow_html=True)

    with bottom_right:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        render_bullets("Improvements", result.improvements)
        st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
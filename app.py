from __future__ import annotations

import html
import os
from typing import Iterable

import streamlit as st

from analyzer import ResumeAnalysis, analyze_resume_vs_jd
from parser import extract_text
from i18n import translate as _
from providers import get_provider


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
        lang = st.session_state.get("language", "en")
        st.caption(_(lang, "no_items", "No items to display."))
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
        lang = st.session_state.get("language", "en")
        st.caption(_(lang, "no_items", "No items to display."))
        return

    st.markdown("\n".join(f"- {html.escape(item)}" for item in clean_items))


def clip_text(text: str, limit: int = MAX_ANALYSIS_CHARS) -> tuple[str, bool]:
    cleaned = text.strip()
    if len(cleaned) <= limit:
        return cleaned, False

    return cleaned[:limit], True


def main() -> None:
    # Set up session state language
    if "language" not in st.session_state:
        st.session_state.language = "en"

    # Define language selector dropdown in sidebar using native names
    lang_map = {
        "English": "en",
        "हिन्दी": "hi",
        "తెలుగు": "te"
    }

    current_lang_code = st.session_state.language
    current_lang_name = [name for name, code in lang_map.items() if code == current_lang_code][0]

    selected_lang_name = st.sidebar.selectbox(
        "Language / भाषा / భాష",
        options=list(lang_map.keys()),
        index=list(lang_map.keys()).index(current_lang_name)
    )

    selected_lang_code = lang_map[selected_lang_name]
    if selected_lang_code != st.session_state.language:
        st.session_state.language = selected_lang_code
        st.rerun()

    # Short utility helper for translated strings
    def t(key: str, default: str = "") -> str:
        return _(st.session_state.language, key, default)

    # ----------------------------------------------------
    # AI Provider Settings Section
    # ----------------------------------------------------
    st.sidebar.markdown("---")
    st.sidebar.subheader(t("provider_settings_title", "AI Provider Settings"))

    # Provider name selection
    if "provider_name" not in st.session_state:
        st.session_state.provider_name = "Gemini API"

    selected_provider = st.sidebar.selectbox(
        t("provider_label", "AI Provider"),
        options=["Gemini API", "Ollama"],
        index=0 if st.session_state.provider_name == "Gemini API" else 1
    )
    st.session_state.provider_name = selected_provider

    user_gemini_key = ""
    ollama_url = "http://localhost:11434"
    ollama_model = "llama3.2"

    if selected_provider == "Gemini API":
        user_gemini_key = st.sidebar.text_input(
            t("byok_label", "Gemini API Key (BYOK)"),
            value=st.session_state.get("user_gemini_key", ""),
            type="password",
            placeholder=t("byok_placeholder", "Enter your Gemini API key (optional)...")
        )
        st.session_state.user_gemini_key = user_gemini_key
    elif selected_provider == "Ollama":
        ollama_url = st.sidebar.text_input(
            t("ollama_url_label", "Ollama Base URL"),
            value=st.session_state.get("ollama_url", "http://localhost:11434")
        )
        st.session_state.ollama_url = ollama_url

        # Attempt to dynamically query installed models
        from providers.ollama_provider import OllamaProvider
        temp_prov = OllamaProvider(base_url=ollama_url)
        installed_models = temp_prov.get_installed_models()

        if installed_models:
            default_model = st.session_state.get("ollama_model", "llama3.2")
            default_idx = 0
            for idx, model_item in enumerate(installed_models):
                if model_item == default_model or model_item.startswith(f"{default_model}:"):
                    default_idx = idx
                    break

            ollama_model = st.sidebar.selectbox(
                t("ollama_model_label", "Ollama Model"),
                options=installed_models,
                index=default_idx
            )
        else:
            # Fallback warning if unreachable
            st.sidebar.warning(t("err_ollama_unavailable", "Ollama is currently unreachable. Please check your URL/service or switch providers."))
            ollama_model = st.sidebar.text_input(
                t("ollama_model_label", "Ollama Model"),
                value=st.session_state.get("ollama_model", "llama3.2")
            )
        st.session_state.ollama_model = ollama_model

    # Resolve active Gemini API key using priority order
    def get_resolved_gemini_key() -> str | None:
        if user_gemini_key.strip():
            return user_gemini_key.strip()
        try:
            secrets_val = (st.secrets.get("GEMINI_API_KEY") or st.secrets.get("GOOGLE_API_KEY") or "").strip()
            if secrets_val:
                return secrets_val
        except Exception:
            pass
        return (os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or "").strip()

    # Construct active provider using resolved parameters
    gemini_key = get_resolved_gemini_key() if selected_provider == "Gemini API" else None
    active_provider = get_provider(
        provider_name=selected_provider,
        gemini_key=gemini_key,
        ollama_url=ollama_url,
        ollama_model=ollama_model
    )

    # Test Connection mechanism
    if "conn_status" not in st.session_state:
        st.session_state.conn_status = None

    # Reset status if configurations change to require a fresh test
    config_fingerprint = f"{selected_provider}_{user_gemini_key}_{ollama_url}_{ollama_model}"
    if st.session_state.get("config_fingerprint") != config_fingerprint:
        st.session_state.config_fingerprint = config_fingerprint
        st.session_state.conn_status = None

    test_conn_clicked = st.sidebar.button(t("btn_test_connection", "Test Connection"), use_container_width=True)

    if test_conn_clicked:
        with st.sidebar.spinner(t("conn_testing", "Testing connection...")):
            st.session_state.conn_status = active_provider.verify_connection()

    # If connection has not been checked, perform a silent non-blocking check
    if st.session_state.conn_status is None:
        st.session_state.conn_status = active_provider.verify_connection()

    # Display status indicator
    status_label = t("status_label", "Connection Status")
    if st.session_state.conn_status is True:
        st.sidebar.markdown(f"**{status_label}:** :green[{t('status_connected', 'Connected')}]")
    else:
        st.sidebar.markdown(f"**{status_label}:** :red[{t('status_not_connected', 'Not Connected')}]")
        st.sidebar.error(t("conn_failed", "Connection failed. Please check credentials or URL."))

        # Manual fallback helper for Ollama unavailability
        if selected_provider == "Ollama":
            st.sidebar.warning(t("err_ollama_unavailable", "Ollama is currently unreachable. Please check your URL/service or switch providers."))
            if st.sidebar.button(t("btn_switch_to_gemini", "Switch to Gemini API"), use_container_width=True, key="switch_to_gemini_error"):
                st.session_state.provider_name = "Gemini API"
                st.session_state.conn_status = None
                st.rerun()

    # Disable analysis button if connection status is not verified
    is_disconnected = (st.session_state.conn_status is not True)

    # ----------------------------------------------------
    # Ingestion & Hero Title Section
    # ----------------------------------------------------
    st.sidebar.markdown("---")
    st.sidebar.title(t("sidebar_title", "Resume Input"))
    sidebar_note_text = t("sidebar_note", "Upload a PDF or DOCX resume, paste the job description, then run the analysis.")
    st.sidebar.markdown(
        f"<div class='sidebar-note'>{html.escape(sidebar_note_text)}</div>",
        unsafe_allow_html=True,
    )

    uploaded_file = st.sidebar.file_uploader(
        t("resume_file_label", "Resume file"),
        type=["pdf", "docx"],
        accept_multiple_files=False,
        help=t("resume_file_help", "Supported formats: PDF and DOCX."),
    )
    job_description = st.sidebar.text_area(
        t("jd_label", "Job description"),
        height=320,
        placeholder=t("jd_placeholder", "Paste the job description here..."),
    )

    analyze_clicked = st.sidebar.button(
        t("run_analysis_btn", "Run Analysis"),
        type="primary",
        use_container_width=True,
        disabled=is_disconnected
    )

    inject_styles()

    hero_title = t("hero_title", "AI Resume Analyzer")
    hero_desc = t("hero_desc", "Upload a resume, compare it against the job description, and review the match score, skill gaps, and feedback in a compact dashboard.")
    st.markdown(
        f"""
        <div class="hero">
            <h1>{html.escape(hero_title)}</h1>
            <p>{html.escape(hero_desc)}</p>
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
    if "analysis_metadata" not in st.session_state:
        st.session_state.analysis_metadata = None

    if analyze_clicked:
        st.session_state.analysis_error = None
        st.session_state.analysis_result = None
        st.session_state.analysis_metadata = None

        if uploaded_file is None:
            st.session_state.analysis_error = t("err_no_resume", "Please upload a resume file before running the analysis.")
        elif not job_description.strip():
            st.session_state.analysis_error = t("err_no_jd", "Please enter a job description before running the analysis.")
        else:
            try:
                with st.spinner(t("spinner_text", "Extracting resume text and analyzing match...")):
                    resume_text = extract_text(uploaded_file)
                    clipped_resume_text, resume_was_clipped = clip_text(resume_text)
                    clipped_job_description, jd_was_clipped = clip_text(job_description.strip())
                    st.session_state.resume_text = clipped_resume_text

                    st.session_state.analysis_result = active_provider.analyze_resume(
                        clipped_resume_text,
                        clipped_job_description,
                        language=st.session_state.language,
                    )

                    st.session_state.analysis_metadata = {
                        "provider": active_provider.name,
                        "model": active_provider.model_name,
                        "inference_type": active_provider.inference_type
                    }

                    if resume_was_clipped or jd_was_clipped:
                        st.info(t("trim_info", "Input text was trimmed to stay within a safer analysis size for Gemini."))
            except Exception as exc:
                st.session_state.analysis_error = str(exc)

    if st.session_state.analysis_error:
        st.error(st.session_state.analysis_error)

    result: ResumeAnalysis | None = st.session_state.analysis_result

    if result is None:
        st.info(t("info_run_analysis", "Run an analysis to see the match score, matched skills, missing skills, and feedback."))
        return

    top_left, top_right, top_mid = st.columns([1.1, 1, 1])
    top_left.metric(t("metric_match_score", "Overall Match Score"), f"{result.match_percentage}%")
    top_right.metric(t("metric_matched_skills", "Matched Skills"), str(len(result.matched_skills)))
    top_mid.metric(t("metric_missing_skills", "Missing Skills"), str(len(result.missing_skills)))

    # Display active provider metadata block prominently in results
    metadata = st.session_state.get("analysis_metadata")
    if metadata:
        st.markdown(
            f"""
            <div style="background: rgba(31, 111, 91, 0.06); border: 1px solid rgba(31, 111, 91, 0.15); border-radius: 12px; padding: 0.65rem 1rem; margin-top: 1rem; margin-bottom: 1rem; font-size: 0.9rem;">
                <strong>{html.escape(t('provider_metadata_label', 'AI Engine Info'))}:</strong> 
                {html.escape(t('provider_name_label', 'Provider'))}: <code>{html.escape(metadata['provider'])}</code> | 
                {html.escape(t('model_name_label', 'Model'))}: <code>{html.escape(metadata['model'])}</code> | 
                {html.escape(t('inference_type_label', 'Inference Type'))}: <code>{html.escape(metadata['inference_type'])}</code>
            </div>
            """,
            unsafe_allow_html=True
        )

    middle_left, middle_right = st.columns(2)

    with middle_left:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown(f"### {html.escape(t('section_matched_skills', 'Matched Skills'))}")
        render_tag_group(result.matched_skills)
        st.markdown("</div>", unsafe_allow_html=True)

    with middle_right:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown(f"### {html.escape(t('section_missing_skills', 'Missing Skills'))}")
        render_tag_group(result.missing_skills, css_class="missing")
        st.markdown("</div>", unsafe_allow_html=True)

    st.write("")

    bottom_left, bottom_right = st.columns(2)

    with bottom_left:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        render_bullets(t("strengths_title", "Strengths"), result.strengths)
        st.markdown("</div>", unsafe_allow_html=True)

    with bottom_right:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        render_bullets(t("improvements_title", "Improvements"), result.improvements)
        st.markdown("</div>", unsafe_allow_html=True)




if __name__ == "__main__":
    main()
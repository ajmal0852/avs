from __future__ import annotations

import os
from pathlib import Path
from pydantic import BaseModel, Field

DOTENV_PATH = Path(__file__).resolve().with_name(".env")
ENV_VAR_CANDIDATES = ("GEMINI_API_KEY", "GOOGLE_API_KEY")


class ResumeAnalysis(BaseModel):
    match_percentage: int = Field(ge=0, le=100)
    matched_skills: list[str]
    missing_skills: list[str]
    strengths: list[str]
    improvements: list[str]


def _resolve_api_key() -> tuple[str, str]:
    # 1) Streamlit secrets (deployed environment)
    try:
        import streamlit as st  # imported lazily so analyzer can be imported in non-Streamlit tests

        secret_val = (st.secrets.get("GEMINI_API_KEY") or st.secrets.get("GOOGLE_API_KEY") or "").strip()
        if secret_val:
            return secret_val, "st.secrets"
    except Exception:
        # Not running inside Streamlit or st.secrets not available
        pass

    # 2) Environment variables (recommended for most CI/CD and cloud deployments)
    for env_name in ENV_VAR_CANDIDATES:
        env_value = (os.getenv(env_name) or "").strip()
        if env_value:
            return env_value, f"{env_name} in process environment"

    # 3) Fallback: local .env file via python-dotenv if present (development only)
    try:
        from dotenv import dotenv_values  # type: ignore
    except Exception:
        dotenv_values = lambda _path: {}

    file_values = dotenv_values(DOTENV_PATH) if DOTENV_PATH.exists() else {}
    for env_name in ENV_VAR_CANDIDATES:
        file_value = (file_values.get(env_name) or "").strip()
        if file_value:
            return file_value, f"{env_name} in {DOTENV_PATH.name}"

    dotenv_hint = f"Add GEMINI_API_KEY=... to {DOTENV_PATH}" if DOTENV_PATH.exists() else f"Create {DOTENV_PATH} with GEMINI_API_KEY=..."
    raise RuntimeError(
        "Gemini API key is not set. "
        f"Checked {', '.join(ENV_VAR_CANDIDATES)}. {dotenv_hint}."
    )


def _mask_api_key(api_key: str) -> str:
    if len(api_key) < 10:
        return "<too-short-to-mask>"
    return f"{api_key[:6]}...{api_key[-4:]}"



def analyze_resume_vs_jd(resume_text: str, job_description: str, language: str = "en") -> ResumeAnalysis:
    """Analyze a resume against a job description and return a structured result using GeminiProvider."""
    from providers.gemini_provider import GeminiProvider
    provider = GeminiProvider()
    return provider.analyze_resume(resume_text, job_description, language=language)

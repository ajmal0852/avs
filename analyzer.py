from __future__ import annotations

import logging
import os
from functools import lru_cache
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from google import genai
from google.genai import errors, types
from pydantic import BaseModel, Field

MODEL_NAME = "gemini-2.5-flash"
DOTENV_PATH = Path(__file__).resolve().with_name(".env")
ENV_VAR_CANDIDATES = ("GEMINI_API_KEY", "GOOGLE_API_KEY")
MIN_GEMINI_API_KEY_LENGTH = 35

logger = logging.getLogger(__name__)


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


def _validate_api_key(api_key: str, source: str) -> str:
    cleaned_key = api_key.strip()
    key_length = len(cleaned_key)

    logger.warning("Gemini API key preview: %s", _mask_api_key(cleaned_key))
    logger.warning("Gemini API key starts with AIza: %s", cleaned_key.startswith("AIza"))

    if key_length < MIN_GEMINI_API_KEY_LENGTH:
        raise RuntimeError(
            f"Gemini API key from {source} is too short ({key_length} characters). "
            f"A Google Gemini API key is typically around 39 characters and must be at least {MIN_GEMINI_API_KEY_LENGTH} characters here."
        )

    if cleaned_key.upper().startswith("YOUR_"):
        raise RuntimeError(
            f"Gemini API key from {source} still looks like a placeholder value: {_mask_api_key(cleaned_key)}"
        )

    return cleaned_key


def _install_request_logging(client: genai.Client) -> None:
    api_client = getattr(client, "_api_client", None)
    httpx_client = getattr(api_client, "_httpx_client", None)
    if httpx_client is None:
        logger.warning("Gemini request logging could not be installed: missing httpx client")
        return

    original_send = getattr(httpx_client, "send", None)
    if original_send is None or getattr(original_send, "__wrapped_by_hackathon2__", False):
        return

    def logged_send(request: Any, *args: Any, **kwargs: Any):
        request_url = str(getattr(request, "url", ""))
        parsed_url = urlparse(request_url)
        logger.warning(
            "Gemini network request: method=%s hostname=%s url=%s path=%s",
            getattr(request, "method", "<unknown>") ,
            parsed_url.hostname,
            request_url,
            parsed_url.path,
        )
        return original_send(request, *args, **kwargs)

    logged_send.__wrapped_by_hackathon2__ = True  # type: ignore[attr-defined]
    httpx_client.send = logged_send  # type: ignore[assignment]


@lru_cache(maxsize=1)
def _get_client() -> genai.Client:
    api_key, source = _resolve_api_key()
    api_key = _validate_api_key(api_key, source)
    logger.warning("Gemini API key loaded from %s (length=%d)", source, len(api_key))
    logger.warning("Using Google GenAI SDK with model=%s", MODEL_NAME)

    client = genai.Client(api_key=api_key)
    _install_request_logging(client)
    return client


def _analysis_prompt(resume_text: str, job_description: str) -> str:
    return (
        "Compare the resume against the job description and return only structured JSON. "
        "Use the provided schema exactly.\n\n"
        f"Resume:\n{resume_text}\n\n"
        f"Job Description:\n{job_description}"
    )


def _coerce_analysis(response: Any) -> ResumeAnalysis:
    parsed = getattr(response, "parsed", None)
    if parsed is not None:
        if isinstance(parsed, ResumeAnalysis):
            return parsed
        if isinstance(parsed, dict):
            return ResumeAnalysis.model_validate(parsed)

    text = getattr(response, "text", "") or ""
    if not text:
        raise ValueError("Gemini returned an empty response.")

    return ResumeAnalysis.model_validate_json(text)


def analyze_resume_vs_jd(resume_text: str, job_description: str) -> ResumeAnalysis:
    """Analyze a resume against a job description and return a structured result."""
    try:
        client = _get_client()
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=_analysis_prompt(resume_text, job_description),
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ResumeAnalysis,
                temperature=0.2,
            ),
        )
        return _coerce_analysis(response)
    except (RuntimeError, ValueError):
        raise
    except errors.APIError as exc:
        raise RuntimeError(f"Gemini API error: {exc}") from exc
    except Exception as exc:
        raise RuntimeError(f"Failed to analyze resume: {exc}") from exc
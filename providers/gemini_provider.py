from __future__ import annotations

import os
from typing import Any

from google import genai
from google.genai import errors, types

from analyzer import ResumeAnalysis
from providers.base import AIProvider


class GeminiProvider(AIProvider):
    def __init__(self, api_key: str | None = None, model_name: str = "gemini-2.5-flash"):
        self._api_key = (api_key or "").strip()
        self._model_name = model_name

    @property
    def name(self) -> str:
        return "Gemini API"

    @property
    def model_name(self) -> str:
        return self._model_name

    @property
    def inference_type(self) -> str:
        return "Cloud"

    def _get_client(self) -> genai.Client:
        key = self._api_key
        if not key:
            # Re-use resolution helper to resolve from secrets/env/.env files
            from analyzer import _resolve_api_key
            try:
                key, _source = _resolve_api_key()
            except Exception:
                pass

        if not key:
            raise RuntimeError(
                "Gemini API key is not set. Please enter a key in the UI settings, "
                "configure Streamlit Secrets, or set the GEMINI_API_KEY environment variable."
            )


        if len(key) < 35:
            raise RuntimeError(
                f"Gemini API key is too short ({len(key)} characters). "
                "A standard key must be at least 35 characters."
            )

        if key.upper().startswith("YOUR_"):
            raise RuntimeError(
                "Gemini API key still looks like a placeholder value."
            )

        return genai.Client(api_key=key)

    def verify_connection(self) -> bool:
        try:
            client = self._get_client()
            # Lightweight ping request
            client.models.generate_content(
                model=self._model_name,
                contents="ping",
                config=types.GenerateContentConfig(
                    temperature=0.0,
                    max_output_tokens=1
                ),
            )
            return True
        except Exception:
            return False

    def _coerce_analysis(self, response: Any) -> ResumeAnalysis:
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

    def analyze_resume(
        self, resume_text: str, job_description: str, language: str = "en"
    ) -> ResumeAnalysis:
        try:
            client = self._get_client()

            target_language = "English (US)"
            if language == "te":
                target_language = "Telugu (తెలుగు)"
            elif language == "hi":
                target_language = "Hindi (हिन्दी)"

            system_instruction = (
                "You are a Senior Talent Acquisition Manager, Technical Recruiter, and Applicant Tracking System (ATS) compatibility engineer. "
                "Your task is to analyze the user's resume text relative to the target Job Description (JD). "
                "Evaluate candidate credentials, structural layout, experience hierarchy, actionable gaps, skill keyword match, and ATS optimization elements. "
                "Provide constructive, objective, and highly professional advice. "
                "You must respond strictly with a valid JSON object matching the requested schema.\n"
                f"CRITICAL: You must write all textual content within 'strengths' and 'improvements' arrays entirely in the selected language: {target_language}. "
                f"Ensure all feedback, descriptions, and suggestions are written in fluent, grammatically correct {target_language}. "
                "Use the native script where appropriate (e.g., Hindi/Devanagari letters for Hindi, Telugu letters for Telugu)."
            )

            prompt = (
                "Compare the resume against the job description and return only structured JSON. "
                "Use the provided schema exactly.\n\n"
                f"Resume:\n{resume_text}\n\n"
                f"Job Description:\n{job_description}"
            )

            response = client.models.generate_content(
                model=self._model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    response_mime_type="application/json",
                    response_schema=ResumeAnalysis,
                    temperature=0.2,
                ),
            )
            return self._coerce_analysis(response)
        except (RuntimeError, ValueError):
            raise
        except errors.APIError as exc:
            raise RuntimeError(f"Gemini API error: {exc}") from exc
        except Exception as exc:
            raise RuntimeError(f"Failed to analyze resume: {exc}") from exc

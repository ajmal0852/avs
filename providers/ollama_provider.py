from __future__ import annotations

import json
import urllib.request
import urllib.error
from typing import Any

from analyzer import ResumeAnalysis
from providers.base import AIProvider


class OllamaProvider(AIProvider):
    def __init__(self, base_url: str = "http://localhost:11434", model_name: str = "llama3.2"):
        self._base_url = base_url.rstrip("/")
        self._model_name = model_name

    @property
    def name(self) -> str:
        return "Ollama"

    @property
    def model_name(self) -> str:
        return self._model_name

    @property
    def inference_type(self) -> str:
        return "Local"

    def get_installed_models(self) -> list[str]:
        """Fetch the list of model names currently installed in Ollama."""
        try:
            req = urllib.request.Request(f"{self._base_url}/api/tags")
            with urllib.request.urlopen(req, timeout=3) as response:
                if response.status != 200:
                    return []
                data = json.loads(response.read().decode("utf-8"))
                return [m["name"] for m in data.get("models", [])]
        except Exception:
            return []

    def verify_connection(self) -> bool:
        """Returns True if Ollama is running and the selected model is installed."""
        try:
            models = self.get_installed_models()
            if not models:
                return False

            # Normalize names to check if the target model matches
            # e.g., 'llama3.2' matches 'llama3.2:latest' or 'llama3.2:latest' matches 'llama3.2'
            def normalize(name: str) -> str:
                if ":" in name:
                    parts = name.split(":")
                    if parts[1] == "latest":
                        return parts[0]
                return name

            normalized_models = {normalize(m) for m in models}
            normalized_target = normalize(self._model_name)

            return (
                self._model_name in models
                or normalized_target in normalized_models
                or any(m.startswith(f"{self._model_name}:") for m in models)
            )
        except Exception:
            return False

    def analyze_resume(
        self, resume_text: str, job_description: str, language: str = "en"
    ) -> ResumeAnalysis:
        try:
            target_language = "English (US)"
            if language == "te":
                target_language = "Telugu (తెలుగు)"
            elif language == "hi":
                target_language = "Hindi (हिन्दी)"

            # Construct system-like guidelines and formatting inside the prompt
            prompt = (
                "You are a Senior Talent Acquisition Manager, Technical Recruiter, and Applicant Tracking System (ATS) compatibility engineer. "
                "Your task is to analyze the user's resume text relative to the target Job Description (JD). "
                "Evaluate candidate credentials, structural layout, experience hierarchy, actionable gaps, skill keyword match, and ATS optimization elements. "
                "Provide constructive, objective, and highly professional advice. "
                "You must respond with a JSON object strictly matching the following schema:\n"
                "{\n"
                "  \"match_percentage\": <integer 0-100>,\n"
                "  \"matched_skills\": [<string>, ...],\n"
                "  \"missing_skills\": [<string>, ...],\n"
                "  \"strengths\": [<string>, ...],\n"
                "  \"improvements\": [<string>, ...]\n"
                "}\n\n"
                f"CRITICAL: You must write all textual content within 'strengths' and 'improvements' arrays entirely in the selected language: {target_language}. "
                f"Ensure all feedback, descriptions, and suggestions are written in fluent, grammatically correct {target_language}. "
                "Use the native script where appropriate.\n\n"
                f"Resume:\n{resume_text}\n\n"
                f"Job Description:\n{job_description}\n\n"
                "Return ONLY the raw JSON object. Do not include any explanation, markdown styling, or text outside the JSON."
            )

            payload = {
                "model": self._model_name,
                "prompt": prompt,
                "format": "json",
                "stream": False,
                "options": {
                    "temperature": 0.2
                }
            }

            req = urllib.request.Request(
                f"{self._base_url}/api/generate",
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )

            with urllib.request.urlopen(req, timeout=60) as response:
                if response.status != 200:
                    raise RuntimeError(f"Ollama server returned status code {response.status}")
                res_data = json.loads(response.read().decode("utf-8"))
                raw_response = res_data.get("response", "").strip()
                if not raw_response:
                    raise ValueError("Ollama returned an empty response.")

                return ResumeAnalysis.model_validate_json(raw_response)
        except urllib.error.URLError as exc:
            raise RuntimeError(f"Failed to connect to Ollama at {self._base_url}: {exc.reason}")
        except Exception as exc:
            raise RuntimeError(f"Ollama analysis failed: {exc}")

from __future__ import annotations

from abc import ABC, abstractmethod
from analyzer import ResumeAnalysis


class AIProvider(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the provider (e.g. 'Gemini API' or 'Ollama')."""
        pass

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Name of the active model."""
        pass

    @property
    @abstractmethod
    def inference_type(self) -> str:
        """Type of inference: 'Cloud' or 'Local'."""
        pass

    @abstractmethod
    def verify_connection(self) -> bool:
        """Returns True if the provider is reachable and active."""
        pass

    @abstractmethod
    def analyze_resume(
        self, resume_text: str, job_description: str, language: str = "en"
    ) -> ResumeAnalysis:
        """Perform resume analysis against a job description in the target language."""
        pass

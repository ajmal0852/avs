# Changelog

All notable changes to the AI Resume Analyzer project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-06-11
### Added
- Core Streamlit application supporting fast resume comparisons.
- Parser module integrating `pypdf` and `python-docx` for native `.pdf` and `.docx` extraction.
- Interactive user interface built using Streamlit.
- Google GenAI SDK integration executing `gemini-3.5-flash` content generation with strict JSON schema outputs.
- Comprehensive compliance setup using Ruff, Gitleaks, Mypy, and automated pipeline specifications.

### Changed
- Migrated legacy layout to secure and lazy-initialized Gemini API interfaces.

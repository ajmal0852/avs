# AI Resume Analyzer - User Manual

Welcome to the AI Resume Analyzer! This manual describes the features, configuration, and interface details for candidates and recruiters.

## Overview
The AI Resume Analyzer evaluates resumes against target job descriptions using Google Gemini AI, offering immediate feedback on keyword alignment, structural layout, ATS score estimates, and direct formatting suggestions.

## Features

1. **Resume File Parser**:
   - Supports uploading `.pdf`, `.docx`, and `.txt` resumes.
   - Decodes structural layouts and renders plain test output for review.
2. **Interactive Comparative Grid**:
   - Allows side-by-side editing of both the resume copy and target Job Description.
3. **ATS Match Score Dial**:
   - Real-time gauge reflecting calculated ATS compatibility.
4. **Keyword Tag Board**:
   - Compares list of present (Matched) and absent (Missing) skillsets.
5. **Actionable Recommendations**:
   - Clear indicators outlining key strengths and direct layout issues of your document.

## How to Run locally

### Requirements
- Python 3.10+
- A valid `GEMINI_API_KEY` configured in secrets.

### Operations
```bash
# 1. Install packages
pip install -r requirements.txt

# 2. Boot up the Streamlit application
streamlit run app.py

# 3. Access in your browser at:
http://localhost:8501
```

## How to Optimize Your Score

1. Review the **Gaps / Missing Skills** tags generated in the analysis panel.
2. Incorporate missing keywords and tools into your resume description organically.
3. Fix visual or structural alerts shown under the **ATS Fixes Required** section.
4. Re-upload or re-analyze the updated resume to verify score increases!

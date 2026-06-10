# Technical Specifications: AI Resume Analyzer

## 1. System Architecture
The application runs as a single-page web application. The backend handles document ingestion, text normalization, API orchestration with Gemini, and parsing logic.

## 2. File Ingestion & Parsing Specs
* **Supported Formats:** `.pdf`, `.docx`
* **Libraries:** `pypdf` for PDFs, `python-docx` for Word files.
* **Constraints:** Max file size 5MB. Text must be stripped of anomalous whitespace and normalized to UTF-8 before sending to the AI model.

## 3. Gemini AI Analysis Specification
* **SDK:** `google-genai`
* **Model:** `gemini-1.5-flash` (for fast, cost-effective analysis) or `gemini-1.5-pro` (for deeper reasoning).
* **Output Strategy:** Use Gemini's `response_schema` in `GenerateContentConfig` to force a strict, guaranteed JSON output without relying on manual markdown parsing.
* **Expected JSON Schema:**
    1.  `match_percentage`: Integer (0 to 100).
    2.  `matched_skills`: List of strings.
    3.  `missing_skills`: List of critical keywords/skills present in the JD but missing in the resume.
    4.  `strengths`: List of bullet points.
    5.  `improvements`: List of actionable formatting or content suggestions.

## 4. UI / UX Design Specs
* **Sidebar:** File upload widget for the resume, text area input for the Job Description, and a "Run Analysis" button.
* **Main Panel:**
    * **Top Row:** Metric cards showing the Overall Match Score.
    * **Middle Row:** Column layouts comparing Matched vs. Missing skills (using visual tags or progress bars).
    * **Bottom Row:** Markdown text area displaying the detailed AI feedback and formatting advice.
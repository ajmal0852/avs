# Todo Task List: AI Resume Analyzer

## Phase 1: Environment Setup & Document Parsing
- [ ] Initialize git repository and create virtual environment (`venv`).
- [ ] Install base dependencies (`streamlit`, `pypdf`, `python-docx`, `google-genai`, `python-dotenv`, `pydantic`).
- [ ] Create `.env` file to securely store the `GEMINI_API_KEY`.
- [ ] Implement `parser.py` with helper functions to extract raw text from PDF and DOCX files.
- [ ] Test the parser locally with a sample resume to ensure text outputs correctly in terminal.

## Phase 2: Gemini AI Integration
- [ ] Create `analyzer.py` and initialize the Gemini client using `from google import genai`.
- [ ] Define a Pydantic class to represent the desired JSON output structure for the resume analysis.
- [ ] Set up the `client.models.generate_content` call with `response_mime_type="application/json"` and pass the Pydantic schema into `response_schema`.
- [ ] Implement error handling for Gemini API exceptions, quota limits, or network timeouts.
- [ ] Verify the scoring logic by feeding it a mock resume and job description via a local script.

## Phase 3: Frontend Development (Streamlit)
- [ ] Create `app.py` and set up the basic page layout (sidebar config, title, headers).
- [ ] Integrate the file upload component and string input for the job description.
- [ ] Link the UI "Run Analysis" button to call the parser and Gemini analysis functions.
- [ ] Add a loading spinner (`st.spinner`) to manage UX while Gemini processes the data.
- [ ] Render the JSON response into organized components (e.g., `st.metric`, `st.pills` or tags, and clean bullet points).

## Phase 4: Refinement & Testing
- [ ] Test behavior when a user clicks "Analyze" without uploading a file or entering a JD.
- [ ] Optimize the input text length to stay well within Gemini's context window.
- [ ] Add formatting tips to the output panel (e.g., advising against complex multi-column resume tables for ATS systems).
# Project Plan: AI Resume Analyzer

## 1. Vision & Objective
The goal is to build an intelligent AI Resume Analyzer that allows users to upload a resume (PDF/DOCX) and a job description. The application will parse the resume, evaluate how well it matches the job description, and provide actionable feedback using Google's Gemini API.

## 2. Core Features
* **Resume Parsing:** Extract text and structured metadata (Skills, Experience, Education) from PDF/DOCX files.
* **Job Description Matching:** Compare the parsed resume against a user-provided job description.
* **Gemini AI Analysis & Scoring:** Generate a match percentage score, highlight keyword gaps, and provide restructuring suggestions using Gemini 1.5 Flash / Pro.
* **Dashboard UI:** A clean interface to upload files, view scores via interactive charts, and read feedback.

## 3. Tech Stack
* **Frontend:** Streamlit (recommended for rapid prototyping with Python).
* **Backend / Processing:** Python.
* **PDF Parsing:** `pypdf` or `pdfplumber`.
* **AI Integration:** Google GenAI SDK (`google-genai`).
* **Environment:** VS Code with ChatGPT Codex/Copilot.

## 4. Milestone Timeline
* **Milestone 1:** Setup & Document Parsing (Local text extraction).
* **Milestone 2:** Gemini API Integration & Structured JSON Prompts.
* **Milestone 3:** UI Development & Data Visualization.
* **Milestone 4:** Testing, Optimization, and Edge-Case Handling.
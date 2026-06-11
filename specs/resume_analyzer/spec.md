# Feature Spec: AI Resume Analyzer

## 1. Overview & Context
This feature allows job applicants and recruiters to match their resumes instantly against target Job Descriptions using Google's generative AI, diagnosing missing skills, strengths, layout bugs, and providing score improvements.

## 2. User Experience & Design Specs
- **Font Stack**: Inter (for clean reading) paired with JetBrains Mono (for raw data tags).
- **Layout**: Two-panel dynamic dashboard. Input controllers on the left; metrics, gauges, dynamic comparative tag boards, and detailed markdown advice on the right.
- **Themes**: Soft crisp off-white background with professional indigo, emerald, amber, and slate gradients.
- **Animations**: Entrance and fade transitions implemented using `motion/react`.

## 3. Systems & Storage
- **Backend Service**: Express server running on port 3000.
- **Model Ingestion**: Google GenAI `gemini-3.5-flash` model utilizing exact JSON `response_schema` parameters.
- **File Parsing**: Server-side parsing of base64 document files using `pdf-parse` (PDF) and `mammoth` (Word .docx).

## 4. Expected Behaviors & Constraints
- Empty state: Explainer card outlining privacy structures and directions.
- Loading state: Custom list checklists indicating parsing state progress.
- Results: Visual match circular indicator gauge, comparative matched/missing tag bubbles, and deep advice text.

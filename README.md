# AI Resume Analyzer

An intelligent, full-stack AI Resume Analyzer powered by Google Gemini 3.5 Flash. It checks candidate resumes against job descriptions, evaluating match percentages, identifying critical skills (both present and absent), and proposing constructive structural improvements.

## Key Features

- **Automated Resume Parsing**: Extracts content from PDF and Word (.docx) formats on the server.
- **Deep Skill Matrix**: Extracts matching and missing technical/soft skills from both the resume and the target description.
- **Detailed Actionable Advice**: Gives concrete recommendations to improve format, phrasing, and match density.
- **Internationalization (i18n) & Localization (l10n)**: Full native user interface and AI analysis support for **English**, **Hindi (हिन्दी)**, and **Telugu (తెలుగు)**.
- **100% GitLab Compliance Active**: Validated using Docker, Biome, Knip, Ruff, Gitleaks, Mypy, and automated pipeline specifications.

## Internationalization & Localization (i18n / l10n)

The Streamlit frontend and the Gemini backend are fully localized:
- **UI Locales**: Located under [locales/](file:///c:/Users/ASUS/hackathon2/locales) containing [en.json](file:///c:/Users/ASUS/hackathon2/locales/en.json), [hi.json](file:///c:/Users/ASUS/hackathon2/locales/hi.json), and [te.json](file:///c:/Users/ASUS/hackathon2/locales/te.json).
- **Translation Utility**: Managed by [i18n.py](file:///c:/Users/ASUS/hackathon2/i18n.py) with dynamic translation lookup and automatic English fallback.
- **Language Selector**: Native selectors in the Streamlit sidebar (English, हिन्दी, తెలుగు) persisted through `st.session_state`.
- **Localized Gemini Output**: Evaluation feedback, strengths, and recommendations are returned directly in the target language.


## Installation

To configure the project on your local environment:

1. **Prerequisites**: Ensure you have Node.js 18+ (20+ recommended) and npm installed.
2. **Clone the repository**:
   ```bash
   git clone https://code.swecha.org/azarael/hackathon2.git
   cd hackathon2
   ```
3. **Install dependencies**:
   ```bash
   npm install
   ```
4. **Environment Configuration**:
   Create a `.env` file in the root directory and add your secret credentials:
   ```env
   GEMINI_API_KEY=your_google_gemini_api_key_here
   ```

## Usage

### Development Server
Run the local Vite development server with Express backend hot-reloading:
```bash
npm run dev
```

### Production Build
Compile frontend and self-bundle TypeScript backend files inside the `dist/` workspace:
```bash
npm run build
```

### Production Execution
Run the compiled, optimized full-stack output locally or via Docker:
```bash
npm run start
```

### Formatting and Linting
To check code compliance, format standards, and type security across JS/TS and Python environments:
```bash
# Biome and TypeScript type check
npm run lint
npm run lint:js

# Dead code scanning
npm run knip
```

## Contributing

We welcome contributions of any size! Please follow these guidelines:

1. **Create a branch**: Code on feature-specific feature branches (e.g., `feature/adds-new-parsing-logic`).
2. **Coding Standards**: Ensure all files are nicely formatted. Run `npm run lint:js` to format and analyze potential issues before committing.
3. **Commit Quality**: Pre-commit hooks are configured to block secrets leaks (Gitleaks) and formatting issues. Ensure all checks pass.
4. **Merge Request Details**: Clearly document the changes made and link to active project issues/milestones when opening a merge request.

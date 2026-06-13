# Contributing to AI Resume Analyzer

We welcome contributions from the community! To ensure high quality, secure code, and a smooth setup process, please adhere to the following guidelines.

## Code of Conduct
By participating in this project, you agree to abide by our Code of Conduct. Please review the `CODE_OF_CONDUCT.md` file for more details.

## Getting Started

1. **Fork the Repository**: Create your own copy of this repository on GitLab or GitHub.
2. **Setup Development Dependencies**:
   ```bash
   # Install dependencies
   pip install -r requirements.txt
   # Run the Streamlit application
   streamlit run app.py
   ```
3. **Draft your feature / patch**: Ensure to write a clean specification inside the `specs/` folder if you are adding new features, respecting our Spec-driven development philosophy.

## Standard Style Guides

- **Format and Lint Checks**:
  Before committing your code, always make sure to run:
  ```bash
  ruff format --check .
  ruff check .
  mypy .
  ```
- **Tests**:
  Ensure coverage remains above 90%. Run your tests and verify coverage reports:
  ```bash
  pytest
  ```

## Making a Pull / Merge Request

1. Create a descriptive feature branch (e.g., `feat/add-ats-analyzer-layout`).
2. Implement your updates, keeping changes self-contained.
3. Commit using conventional commit standards (e.g., `feat: integrate gemini model parser`).
4. Submit your Merge Request to the `main` branch. Ensure the GitLab CI pipeline passes all tests and linter stages.

Thank you for helping us build better ATS tools!

# Gemini Development Guidelines

This file defines the principles and workflow for the AI assistant (Gemini) when performing development tasks in this project.

## 1. General Principles
- **Small, Atomic Changes:** Keep changes small and focused on a single concern. Do not bundle multiple refactorings or features into one large change.
- **No Test-Specific Code Modification:** Do not temporarily modify application source code or hardcode values for testing purposes. Use environment files (`.env`), configuration files, or command-line arguments.

## 2. Development Workflow
1.  **Implement:** Apply the code changes.
2.  **Test:** **Always** run tests before committing to ensure the changes work correctly and do not break existing functionality.
3.  **Update Changelog:** For every user-facing change (features, fixes, breaking changes), you must update `CHANGELOG.md`.
    - Discuss the versioning impact (Major, Minor, Patch) and use the correct version number and date.
4.  **Commit & Push:** Commit all related changes (source code, `CHANGELOG.md`, etc.) together and push them.

## 3. Environment & Execution
- **Use Virtual Environment Interpreter:** Always use the full path to the virtual environment's interpreter (e.g., `./.venv/bin/python3 ...`) for all script executions to avoid ambiguity and dependency on shell `PATH` settings.
- **Install Dependencies:** If a new dependency is added to `requirements.txt`, run `uv pip install -r requirements.txt` to install it before modifying the code that uses it.

## 4. Error Handling
- **Ensure Non-Zero Exit Codes:** For all code paths where an error can occur, ensure exceptions are handled properly and that the script exits with a non-zero status code.
- **No Silent Failures:** Do not omit error handling. If an error occurs, halt the process and clearly notify the user instead of printing a warning and continuing.
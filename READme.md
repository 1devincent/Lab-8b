# Task Management API

A small FastAPI + SQLite backend for managing tasks. Uses parameterized SQL throughout and exposes a `create_app(database_path)` factory so each test run can target its own SQLite file.

## Tool Versions

- **Python:** 3.10+ (tested on 3.11 / 3.12)
- **FastAPI:** 0.115.6
- **Uvicorn:** 0.34.0
- **Pytest:** 8.3.4
- **Httpx:** 0.28.1
- **Ruff:** 0.8.4
- **Bandit:** 1.8.0
- **pip-audit:** 2.7.3

## Project Layout

```text
app/
  __init__.py
  main.py
tests/
  test_tasks.py
evidence/           # Stores output logs for security and linting checks
requirements.txt
requirements-dev.txt
README.md
1. Virtual Environment Setup
It is highly recommended to use a virtual environment to isolate dependencies.

Windows (PowerShell):

powershell
python -m venv .venv
.\.venv\Scripts\activate
macOS / Linux:

bash
python3 -m venv .venv
source .venv/bin/activate
2. Installation Steps
Once the virtual environment is activated, install the development requirements (this automatically includes the runtime requirements).

bash
pip install -r requirements-dev.txt
3. Start the API
Run the server with Uvicorn. The --reload flag automatically restarts the server if you make code changes (it is configured to only watch the app folder so it doesn't restart when you save test files).

bash
uvicorn app.main:app --reload --reload-dir app
API Base URL: http://127.0.0.1:8000

Interactive Docs (Swagger UI): http://127.0.0.1:8000/docs

(Note: By default, the database is saved as tasks.db in the project root. You can override this by setting the TASKS_DB_PATH environment variable before starting the server.)

4. Run Checks (Linting, Security, and Tests)
To satisfy the lab's evidence requirements, run the following commands and redirect their outputs to the evidence/ folder.

Run Integration Tests
Executes the 6 test cases in tests/test_tasks.py.

bash
python -m pytest -q
(To save output: python -m pytest -q > evidence/pytest_final.txt)

Run Ruff (Linting & Style)
Checks the code for syntax errors, unused imports, and style violations.

bash
ruff check app
(To save output: ruff check app > evidence/ruff_final.txt)

Run Bandit (Security Static Analysis)
Scans the code for common security vulnerabilities (e.g., SQL injection, hardcoded passwords).

bash
bandit -r app
(To save output: bandit -r app > evidence/bandit_final.txt)

Run pip-audit (Dependency Vulnerabilities)
Checks your installed Python packages against known vulnerability databases.

bash
pip-audit -r requirements-dev.txt
(To save output: pip-audit -r requirements-dev.txt > evidence/pip_audit_final.txt)

Endpoints Overview
Method	Path	Description
POST	/tasks	Creates a task. Body: {"title": str, "completed": bool?}. Title is trimmed, 1–120 chars. Extras rejected (422). Returns 201.
GET	/tasks/{id}	Returns the task. Returns 200 or 404 (if missing). Non-positive/non-integer IDs return 422.
PATCH	/tasks/{id}	Updates completed. Body: {"completed": bool}. Returns 200, 404 (missing), or 422 (invalid).
Notes
No secrets or credentials are used; data is synthetic.

All SQL uses parameterized queries (? placeholders) to prevent SQL injection.

One SQLite connection is opened per request and closed when the request ends.

The database schema is created automatically on app startup via lifespan.


prompt convo on https://chat.deepseek.com/share/bcr7144zwofybpmxe4
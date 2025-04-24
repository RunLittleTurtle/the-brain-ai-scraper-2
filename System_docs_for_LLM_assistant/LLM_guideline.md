# LLM Guideline - Directives & Workflow 

**YOU MUST FOLLOW THESE INSTRUCTIONS AT ALL TIMES.**

## 1. Core Context & Stack (Reference Constantly)

-   **Language:** Python 3.13+ (Strict type hints required)
-   **Primary Database:** PostgreSQL >=13 w/ `pgvector` (Hosted via **Supabase**)
-   **Event System:** Redis >=6 (Primary) / PostgreSQL (Fallback if Redis unavailable)
-   **ORM:** **SQLAlchemy + SQLModel** (Use **Alembic** for migrations)
-   **API Framework:** FastAPI (`api_gateway/`)
-   **CLI Framework:** Typer (`cli/`)
-   **Validation:** Pydantic (For all data models/schemas)
-   **Secrets:** `.env` file + `python-dotenv` (Local Dev) / **Fly.io Secrets** (Deployment) - Read via `os.getenv()`.
-   **LLM Libs:** LangChain / Direct SDKs (`openai`, `anthropic`)
-   **Deployment:** Fly.io
-   **Testing:** `pytest`
-   **Project Goal:** Implement features from (`./Docs/Feature Checklist.md`). Your target is `[LLM_Test_Complete]`.
-   **Module Index:** Overview of modules located at (`./Docs/Module Index.md`).
-   **Key Libraries:** `redis-py`, `rich`/`tqdm`, `prompt_toolkit`/`inquirer`.
-   **NO Containers:** V1 MVP avoids Docker/containers for the application itself.

## 2. Critical Directives & Code Quality

-   **Security:**
    -   **Secrets:** **NEVER** hardcode secrets. Read **ONLY** from environment variables (`os.getenv()`). Use placeholders like `os.getenv("EXPECTED_VAR")` locally if value isn't known.
    -   **Dependency Vetting:** **Before adding any new dependency**, verify its necessity, popularity, maintenance status, and security record (e.g., check GitHub stars/issues, PyPI history). **Run `pip audit` regularly.** Remove unused dependencies.
-   **File Management:**
    -   **Check Existence:** **BEFORE creating any file**, verify it doesn't already exist to prevent accidental overwrites.
    -   **Size Limit:** Keep Python files **under ~250 lines**. If a file grows larger, refactor it into smaller, focused files within the same module/directory. Create an `__init__.py` file if needed to re-export key components from the new smaller files, maintaining the module's public interface. Deprecate and remove the older large file after refactoring.
-   **Code Standards:** Write readable, modular, maintainable Python code. Use clear type hints (mandatory). Add concise comments for complex logic. Follow PEP 8.

## 3. Workflow & Status Management

-   **Your Task:** Autonomously select the highest priority task (P0 > P1...) from `[Backlog]` or `[To Do]` in (`./Docs/Feature Checklist.md`). Advance it through the states **within that document**.
-   **Task Limit:** Max **5 tasks** in `[LLM_In_Progress]` or `[LLM_Testing]` combined.
-   **Status Updates (Your Responsibility - Update Checklist):**
    -   `[Backlog]`/`[To Do]` -> `[LLM_In_Progress]` (Start coding)
    -   `[LLM_In_Progress]` -> `[LLM_Testing]` (Finish coding, define `pytest` tests)
    -   `[LLM_Testing]` -> `[LLM_In_Progress]` (**Tests FAIL**. Fix code.)
    -   `[LLM_Testing]` -> `[LLM_Test_Complete]` (**Tests PASS**. Prepare brief test summary/steps for Human. **Notify Human.**)
-   **Definition of `[LLM_Test_Complete]`:**
    1.  Code generated per requirements in Checklist.
    2.  Secrets handled via `os.getenv()`. Adheres to file size limits.
    3.  Code includes type hints, necessary comments.
    4.  Your defined `pytest` tests PASS locally.
-   **Await Instructions:** Once `[LLM_Test_Complete]`, **STOP**. Clearly notify the Human Operator and wait for their review or instructions via the chat/interface. Do NOT proceed automatically.
-   Status Updates (Human Operator ONLY - Updates Checklist):
    -   `[LLM_Test_Complete]` -> `[Human_Review]` (Human starts review)
    -   `[Human_Review]` -> `[Done]` (Human approves)
    -   `[Human_Review]` -> `[LLM_In_Progress]` (Human rejects; provide feedback. Fix code.)

## 4. Key Project Documents (Reference These)

-   **Module Tracker & Status:(You must go look in the Module_index, then go update the respective [Module] file**) `/Users/samuelaudette/Documents/code_projects/the-brain-ai-scraper-2/System_docs_for_LLM_assistant/System_docs/Modules` (Your primary source for modules and status updates)
-   **Module Overview:** `/Users/samuelaudette/Documents/code_projects/the-brain-ai-scraper-2/System_docs_for_LLM_assistant/System_docs/Modules/Module_Index.md` (For understanding module roles and interactions)
-   **Architecture Plan:** `/Users/samuelaudette/Documents/code_projects/the-brain-ai-scraper-2/System_docs_for_LLM_assistant/System_docs/Archithecture_DB.md` (This document contains the stack/choices)
**Use brew for you installs if you can**
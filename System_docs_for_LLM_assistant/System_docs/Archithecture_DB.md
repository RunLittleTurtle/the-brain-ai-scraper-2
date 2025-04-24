# Architecture and Technology Stack Plan 

## 1. Introduction & Goal

This document outlines the core technologies, data storage strategy, key frameworks, and deployment approach for the V1 implementation of "The Brain". The goal is a **robust, scalable foundation simple enough for LLM development**, prioritizing standard Python practices and minimizing complex dependencies for the V1 MVP.

**Key Principles:**

1. **Scalable Core:** Use PostgreSQL (Supabase + pgvector) and Redis as primary data stores.
2. **Developer Experience:** Use `.env` locally (via `python-dotenv`) Prefer services with generous free tiers (like Supabase, Fly.io, cloud Redis providers) and well-supported Python libraries. Always use latest stable version for installation.
5. **LLM Programmability:** Avoid containers for V1 MVP; use standard Python libraries (SQLAlchemy, SQLModel, Pydantic, FastAPI, Typer).
6. **Consistent Environments:** Local development connects directly to hosted DB/Redis services (configured via `.env`) to ensure parity with deployment.

## 2. Core Technology Choices (V1 Summary)

-   **Programming Language:** Python (latest version 3.13+)
-   **Primary Database (Knowledge Base & Fallback Event Log):** PostgreSQL (>=13) with `pgvector` enabled.
    -   **Provider:** **Supabase** (Handles hosting, backups, extensions).
-   **Primary Event/Log Storage (Progress Tracking):** Redis (>=6)
    -   **Provider:** e.g., Upstash, Fly.io Redis, other hosted providers.
-   **Tool Definitions Storage:** JSON file (`tools.json`)
-   **Configuration & Secrets Storage:**
    -   **Method:** `.env` file loaded by `python-dotenv` library.
    -   **Usage:** Stores `DATABASE_URL` (Supabase), `REDIS_URL`, and all API keys (LLM, tools) for **local development**.
    -   **Deployment:** Use **Fly.io Secrets** for all URLs and API keys.
-   **Web API Framework:** FastAPI
-   **CLI Framework:** Typer
-   **Data Validation/Schema:** Pydantic
-   **Database Interaction ORM:** **SQLAlchemy + SQLModel** (with **Alembic** for migrations).
-   **LLM Interaction:** LangChain / Direct SDKs.
-   **CLI Enhancement Libraries:** `rich`/`tqdm`, `prompt_toolkit`/`inquirer`.
-   **Target Deployment Platform:** Fly.io

## 3. Data Storage & Persistence Architecture (V1)

### a. PostgreSQL Database (via Supabase)

-   **Purpose:** Primary store for `knowledge_base` (`runs` table) and **fallback** for `progress_tracker` (`events` table).
-   **Technology:** PostgreSQL >=13 with `pgvector`.
-   **Setup:** Connect using `DATABASE_URL` obtained from Supabase.
-   **Rationale:** Single, scalable relational database leveraging Supabase's management and `pgvector` for future semantic search. JSONB handles flexible data. Using it as a fallback simplifies dependencies compared to adding SQLite.
-   **Key Tables (Managed via SQLAlchemy/SQLModel & Alembic):**
    -   `runs`: Stores run history (specs, status, results, feedback, embeddings). Managed by `knowledge_base`.
    -   `events`: Stores detailed step/log events (timestamp, type, message). Managed by `progress_tracker` (only written to if Redis is unavailable). Consider partitioning if volume grows.
-   **Interacting Modules:** `knowledge_base`, `pipeline_builder`, `cli`, `evaluator`, `aggregator`, and `progress_tracker` (for fallback).

### b. Redis (Primary for `progress_tracker` Events)

-   **Purpose:** High-frequency event publishing and real-time status updates.
-   **Technology:** Redis >=6.
-   **Setup:** Connect using `REDIS_URL` from a hosted provider (e.g., Upstash, Fly Redis).
-   **Rationale:** Optimal performance for real-time messaging (Pub/Sub) and quick status lookups.
-   **Usage Pattern (Managed by `progress_tracker`):**
    -   Check if `REDIS_URL` is present and connection is successful.
    -   **If Yes (Primary Path):** Use Redis `PUBLISH` for events, `SET` for latest status (with optional TTL), `SUBSCRIBE` for real-time listeners.
    -   **If No (Fallback Path):** Log events by inserting into the `events` table in PostgreSQL. Listeners must poll this table.
-   **Interacting Modules:** `progress_tracker` (Owner), `executor` (Publisher), `cli` / `api_gateway` (Subscribers/Readers).

### c. PostgreSQL Fallback (`progress_tracker` Events - Fallback)

- **Technology:** PostgreSQL (Leveraging Supabase or local instance, using `events` table).
- **Rationale:** Provides a **minimal fallback** only if Redis is not configured or available, consolidating dependencies to the existing PostgreSQL service (via Supabase or local). Less optimal than Redis for real-time updates (requires polling instead of Pub/Sub), but sufficient for basic logging and avoids additional database types like SQLite for simplicity.
- **Usage Pattern (Managed by `progress_tracker`):**
  - `progress_tracker` detects if `REDIS_URL` is configured. If not, it falls back to using the existing PostgreSQL connection (via `DATABASE_URL`).
  - An `events` table (`id`, `run_id`, `timestamp`, `event_type`, `message`, `progress_percentage`) is used.
  - Publishing inserts rows. Reading involves polling (`SELECT ... WHERE run_id = ? ORDER BY timestamp DESC LIMIT ...`).
- **Interacting Modules:** Same as Redis, but the underlying mechanism within `progress_tracker` changes. `cli`/`api_gateway` would need to poll the `progress_tracker` functions instead of subscribing.

### d. JSON File (`tool_registry`)

-   **Purpose:** Store tool definitions.
-   **Technology:** `tools.json` file.
-   **Rationale:** Simple, version-controlled. Parsed on startup by `tool_registry`.
-   **Modules:** `tool_registry/` **Owner**.

### e. Configuration & Secrets Storage (Simplified)

-   **Technology:** `.env` file + `python-dotenv` library.
-   **Local Development:**
    -   Create a `.env` file in the project root (add `.env` to `.gitignore`).
    -   Add `DATABASE_URL`, `REDIS_URL`, and all necessary API Keys (e.g., `OPENAI_API_KEY`, `SCRAPERAPI_KEY`) directly into this file.
    -   The `config_secrets` module uses `python-dotenv`'s `load_dotenv()` function and then reads values using `os.getenv()`.
-   **Deployment (Fly.io):**
    -   Do **not** deploy the `.env` file.
    -   Use `fly secrets set KEY=VALUE` to securely provide `DATABASE_URL`, `REDIS_URL`, and all API keys to the deployed application as environment variables.
    -   The application code (`config_secrets`) reads these secrets the same way (`os.getenv()`), requiring no code changes between local and deployed environments.
-   **Rationale:** Extremely simple for local setup (single `.env` file). Leverages standard library (`os`) and a common utility (`python-dotenv`). Uses the deployment platform's native, secure secret management for production.

## 4. Key Frameworks & Libraries (V1)

- **SQLAlchemy + SQLModel:**

  - Used by `knowledge_base/`, `tool_registry/` (backup), optionally `progress_tracker/` (PostgreSQL fallback).

  - SQLModel defines data models using Python type hints (inheriting from Pydantic `BaseModel` and SQLAlchemy base), providing automatic schema generation hints.

  - SQLAlchemy Core/ORM handles database communication, connection pooling, and session management.

- **Alembic:** **Required** alongside SQLAlchemy/SQLModel for managing database schema migrations (creating/altering tables like `runs`, `events`). **Alembic** is essential for managing changes to the PostgreSQL schema (`runs`, `tools_backup`, `secrets`, `events` tables) in a controlled, versioned way. Initialize Alembic early but limit its use to initial schema setup for V1 MVP simplicity.
- **DB Sessions:** Use SQLAlchemy's session management patterns. For FastAPI, dependency injection provides sessions per request. For CLI commands or background tasks, ensure sessions are created and closed correctly (e.g., using context managers).
- **FastAPI:** For `api_gateway/`. Leverages SQLModel/Pydantic for automatic request/response validation.
- **Typer (or Click):** For `cli/`.
- **Pydantic:** Core for data validation across all modules.
- **LangChain / SDKs:** For `intent_inference/`, `aggregator/`.
- **Tool Libraries:** `requests`, `playwright`, etc., for `executor/`.
- **CLI Enhancements:** `prompt_toolkit`/`inquirer`, `rich`/`tqdm` for `cli/`.
- **Redis Client:** `redis-py` (or `aredis` for async) used by `progress_tracker/`.
- **Python-Dotenv:** For loading `.env` file secrets and configuration in local development.

## 6. External Services (V1 Summary)

-   **Required Hosted:** Supabase (PostgreSQL), Redis Provider (e.g., Upstash), LLM API Provider.
-   **Optional:** Tool-specific APIs (e.g., ScraperAPI).

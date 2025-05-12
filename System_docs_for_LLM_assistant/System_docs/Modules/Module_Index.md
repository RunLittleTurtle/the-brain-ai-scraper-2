# Module Index & Development Priority

> Modular roadmap for the "The Brain" project. Each module is designed to be independent and testable in isolation, with a focus on components necessary for the defined scraping flow (from user intent to execution and feedback). Modules are completed one by one in the specified order, yet coexist in the same codebase if needed for interactions or cross-testing.

## General Approach for LLM and Program Autonomy

- Each module must have well-defined inputs and outputs (preferably in JSON format via Pydantic schemas) to avoid ambiguity and ease integration.
- Interactions between modules must be limited to simple function calls or data exchanges via files or a shared database, reducing complex dependencies.
- Provide concrete examples and regression tests in each module's specification (expected inputs/outputs, error cases) to guide LLM-driven development and ensure consistency.
- **Sequential Completion:** Each module must be fully implemented and tested before proceeding to the next in the development order, although minor adjustments or integrations might require revisiting earlier modules. All modules reside in the same codebase, enabling interactions as needed (e.g., `cli/` calling `tool_registry/` for early testing).

## Summary with Development Order

1. **tool_registry/** — Plug-and-play catalogue of scraping tools with metadata, CRUD operations, and compatibility validation. **Status:** Human_Done
2. **config_secrets/** — Centralized secrets management via local .env loader and secure retrieval helpers. **Status:** LLM_In_Progress
3. **cli/** — Thin command-line interface supporting structured flags, free-text commands, and interactive prompts. **Status:** LLM_In_Progress
4. **intent_inference/** — LLM-driven conversion of raw user input into validated IntentSpec JSON. **Status:** Backlog
5. **progress_tracker/** — Publish/subscribe event bus and real-time CLI progress indicators for run status and logs. **Status:** Backlog
6. **api_gateway/** — FastAPI-based REST/MCP entrypoint exposing core functions and SSE status updates. **Status:** Backlog
7. **pipeline_builder/** — Dynamic construction of PipelineSpec JSON from IntentSpec, selecting compatible tools. **Status:** Backlog
8. **executor/** — Local execution engine for pipelines with error handling and result extraction. **Status:** Backlog
9. **evaluator/** — Automated error analysis, output cleaning, quality scoring, and feedback suggestion loops. **Status:** Backlog
10. **knowledge_base/** — Storage and similarity-based retrieval of past runs for learning and reuse. **Status:** Backlog
11. **output_processor/** — Merging and LLM-driven normalization of multiple JSON run outputs into a consolidated result. **Status:** Backlog
12. **scout/** — Analyze websites to determine technical requirements and structure. **Status:** Backlog
13. **orchestrator/** —  Coordinate flow between modules and manage execution state. **Status:** Backlog

## Development and Priority by Order

### 1. tool_registry/ (P0 - Core Foundations)

- **One-Line Goal:** Plug-and-play catalogue of scraping tools.
- Encapsulated Features:
  - `tools.json` manifest schema with metadata for each tool, including fields like `name`, `tool_type`, `capabilities` (e.g., `javascript_rendering`, `html_parsing`), `compatibilities` (compatible tool types or names), and `incompatible_with` (incompatible tools).
  - CRUD operations: `add_tool(metadata)`, `list_tools()`, `remove_tool(name)` for managing tool registry.
  - Compatibility validation via `check_compatibility(tool_list)` to ensure tools can be stacked in pipelines.
- Key CLI Regression Tests:
  - `brain tools add playwright` (add a tool with metadata, verify storage).
  - `brain tools list` (list all tools and their metadata, verify output format).
  - `brain tools check-compat playwright beautifulsoup4` (verify if tools are compatible, expect success or failure message).
- **Status:**  `[Human_Done]`
- **Priority Rationale:** First module to develop (P0, Order 1) as it forms the foundation for cataloging tools and their compatibilities, critical for the "Lego" logic of dynamic selection by `pipeline_builder`.
- **Development Completion Note:** Must be fully implemented (schema, CRUD operations, compatibility checks) and tested before moving to `config_secrets/`. Tests must confirm that tool metadata is correctly stored, retrievable, and compatibility logic works as expected.
- **Dependencies:** None (standalone module, serves as foundation for others).
- Input/Output Specifications:
  - **Input Example (CLI Command):** `brain tools add --name "playwright" --type "browser" --capabilities "javascript_rendering,http_request" --compatibilities "parser" --incompatible_with "selenium"`.
  - **Input Example (Internal JSON after Parsing):** `{"name": "playwright", "tool_type": "browser", "capabilities": ["javascript_rendering", "http_request"], "compatibilities": ["parser"], "incompatible_with": ["selenium"]}` (parsed by CLI or API before storage in `tools.json`).
  - **Output Example (List Tools):** JSON array like `[{"name": "playwright", "tool_type": "browser", "capabilities": ["javascript_rendering", "http_request"], "compatibilities": ["parser"], "incompatible_with": ["selenium"]}, ...]` (returned with `--json` flag or via API).
- Additional Test Cases:
  - Edge Case: Attempt to add a duplicate tool (expect error or overwrite option).
  - Error Case: Check compatibility with non-existent tool (expect error message).
- Notes:
  - Initial Toolset (10 tools): Limit initial complexity by focusing on a core set of tools covering key scraping needs:
    1. **Playwright (Browser Automation):** Versatile, supports async/sync.
    2. **Selenium (Browser Automation):** Industry standard, wide compatibility.
    3. **Scrapy (Crawling Framework):** For large-scale scraping tasks.
    4. **cloudscraper (Anti-blocking):** Bypasses Cloudflare/DDoS protections.
    5. **ScraperAPI (Proxy/Anti-bot Service):** Turnkey solution for blocking issues.
    6. **undetected-chromedriver (Stealth):** Avoids anti-bot detection.
    7. **Requests (HTTP Client):** Simple, for basic requests.
    8. **HTTPX (HTTP Client):** Modern, async, FastAPI-compatible.
    9. **BeautifulSoup4 (Parsing):** Essential for HTML data extraction.
    10. **Parsel (Parsing):** Strong selector support, pairs with Scrapy.
  - Ensure metadata documents compatibilities (e.g., "Playwright + ScraperAPI = OK", "Scrapy + Selenium = KO") in JSON format.
  - Outputs must be JSON-structured for easy parsing by other modules like `pipeline_builder`.

### 2. config_secrets/ (P0 - Core Foundations)

- **One-Line Goal:** Centralised secrets & runtime switches.
- Encapsulated Features:
  - `.env` loader for local secret storage (e.g., API keys, passwords).
  - Prisma `Secret` table for hosted environments (optional in V1, can be deferred).
  - `get_secret(name)` helper function to access secrets securely in code.
- Key CLI Regression Tests:
  - `brain config set OPENAI_KEY sk-xxx` (set a secret value, verify storage).
  - `brain config list` (list configured secrets, masked for security, verify output).
- **Status:** `[LLM_In_Progress]`
- **Priority Rationale:** Second module (P0, Order 2) as it provides a secure mechanism to manage secrets (e.g., API keys for ScraperAPI), necessary for certain tools in `tool_registry`. Follows directly after `tool_registry` to prepare configurations before user interaction via `cli/`.
- **Development Completion Note:** Must be fully implemented (local `.env` loading, basic getter function) and tested before moving to `cli/`. Tests must confirm that secrets can be set and retrieved correctly.
- **Dependencies:** None directly, but supports `tool_registry` if tools have `required_config` tied to secrets.
- Input/Output Specifications:
  - **Input Example (CLI Command):** `brain config set SCRAPERAPI_KEY abc123xyz` (stores key in `.env` or local storage).
  - **Input Example (Internal JSON after Parsing):** `{"key_name": "SCRAPERAPI_KEY", "value": "abc123xyz"}` (parsed internally for storage).
  - **Output Example (List Secrets):** JSON or text like `{"keys": ["SCRAPERAPI_KEY", "OPENAI_KEY"], "values": ["****", "****"]}` (values masked, returned with `--json` flag).
  - **Code Usage Example:** `api_key = get_secret("SCRAPERAPI_KEY")` returns `abc123xyz` if set.
- Additional Test Cases:
  - Edge Case: Attempt to retrieve a non-existent secret (expect default or error handling).
  - Error Case: Set invalid secret format (expect validation error).
- Notes:
  - Focus on local `.env` support in V1 to simplify implementation. Hosted secret storage can be a V2 enhancement.
  - Integration with `tool_registry` may be needed if tools reference `required_config` fields tied to secrets.

### 3. cli/ (P0 - Core Foundations)

- **One-Line Goal:** Thin CLI wrapper for user interaction & testing.
- Encapsulated Features:
  - Global flags: `--json` (for machine-readable output), `--verbose` (for debugging logs).
  - Sub-commands for core modules: `scrape` (submit scraping request), `tools` (manage registry), `infer` (test intent parsing), `dryrun` (preview pipeline), `retry` (retry with feedback adjustments).
  - Basic output formatting for human readability or JSON for automation.
  - **Dynamic Interaction:** Interactive terminal prompts or menus using libraries like `prompt_toolkit` or `inquirer` to guide users through commands and options, eliminating the need to remember exact syntax (e.g., menu to select scraping options after typing `brain scrape`).
  - **Context-Aware Verbose Output:** Adaptive messaging based on the current process state (e.g., after a failed scrape, suggest `retry` with specific hints like "adjust selector for price"), enhancing terminal UX for flow navigation.
- Key CLI Regression Tests:
  - `brain scrape --url <URL> --extract price,title` (structured input for scraping, verify intent submission).
  - `brain scrape "Get price from Amazon product page <URL>"` (free-text input, verify parsing).
  - `brain tools list` (list tools in registry, verify integration with `tool_registry`).
- **Status:**  `[LLM_In_Progress]`
- **Priority Rationale:** Third module (P0, Order 3) as it provides the primary interface for users to interact with `tool_registry`, submit scraping intents, and manually test other modules. Follows `config_secrets` to allow secured configurations if needed.
- **Development Completion Note:** Must be fully implemented (basic commands, support for structured and free-text inputs) and tested before moving to `progress_tracker/`. Tests must confirm that CLI can interact with `tool_registry` and accept diverse input formats.
- **Dependencies:** Relies on `tool_registry/` for tool management commands and `config_secrets/` for secure configurations if applicable.
- Input/Output Specifications:
  - **Input Example (Structured):** `brain scrape --url https://amazon.ca/dp/B08WRBGSL2 --extract price,title --jscan true`.
  - **Input Example (Free-text):** `brain scrape "I want the price and title from this Amazon product: https://amazon.ca/dp/B08WRBGSL2"`.
  - **Input Example (Interactive Prompt):** Typing `brain scrape` triggers a menu like `1. Enter URL manually, 2. Extract specific fields, 3. Use free-text description` for user selection.
  - **Output Example (JSON Flag):** `brain tools list --json` returns `[{"name": "playwright", "tool_type": "browser", ...}, ...]`.
  - **Output Example (Context-Aware Verbose):** After a failed scrape, `brain --verbose` outputs "Scrape failed: selector 'price' not found. Try 'brain retry --adjust-selector price' to fix."
- Additional Test Cases:
  - Edge Case: Invalid input format (expect helpful error message or prompt for correction via interactive menu).
  - Error Case: Command without required arguments (expect usage hint or guided prompt to fill missing data).
  - Interaction Case: Test interactive menu navigation (simulate user selecting options, expect correct command execution).
- Notes:
  - Must support both structured commands and free-text input to align with the permissive `intent_inference` module.
  - Output should be JSON-parseable (with `--json` flag) for scripting and integration.
  - **Dynamic Interaction:** Implement terminal menus or prompts to guide users through the scraping flow (e.g., after `brain scrape`, offer choices for URL input or field selection), reducing the cognitive load of remembering commands.
  - **Context-Aware UX:** Ensure verbose output adapts to the process state, providing relevant next steps or error-specific suggestions (e.g., after a timeout, suggest `brain retry --increase-timeout`), making terminal flow intuitive.
  - Lives in the same codebase as prior modules, enabling early testing of `tool_registry` and `config_secrets`.

### 4. intent_inference/ (P1 - High Priority)

- **One-Line Goal:** Iteratively transform raw user input (text-based) into a robust, validated, and human-approved structured `IntentSpec` JSON, capable of self-correction and incorporating feedback.

- **Encapsulated Features:**

  - LLM-Powered Intent Generation:
    - Parses natural language user requests into an initial `IntentSpec` using an LLM (e.g., `chains/intent_chain.py`).
    - Processes user feedback on existing `IntentSpec`s to produce revised versions using an LLM (e.g., `chains/feedback_chain.py`).
  - **Contextual Processing:** Maintains conversation state (`models/context.py:ContextStore`) including the last generated spec, user query, and critique hints to inform subsequent processing.
  - Iterative Self-Correction (LLM-as-a-Judge):
    - Employs an LLM-based validation chain (`chains/validation_chain.py`) to critically evaluate the generated `IntentSpec` for clarity, completeness, and actionability against the original user query.
    - Includes basic URL health checks (`utils/url_validator.py`) as part of the validation.
    - If issues are found, critique hints are fed back into the context for retrying the intent/feedback generation LLM calls, enabling self-improvement.
  - Human-in-the-Loop (HITL) for Clarification & Final Approval:
    - If the LLM-as-a-Judge determines the intent is too ambiguous or requires further details, it can generate clarification questions for the user.
    - The final `IntentSpec` produced by the LLM loop (even if deemed valid by the judge) is presented to a human operator via a CLI (`cli.py`) for explicit review and approval.
    - The human operator can approve, or reject and provide feedback, which then re-initiates the processing loop.
  - **Strict Pydantic Schema Validation:** The `IntentSpec` (`models/intent_spec.py`) is defined using Pydantic V2, ensuring a machine-readable format and validating data integrity at each stage.

- **Key CLI Regression Tests (Illustrative examples, actual tests will cover more scenarios):**

  - `brain infer "scrape price and title on Amazon product page https://amazon.ca/dp/B08WRBGSL2"` (Initial free-text intent, verify `IntentSpec` creation, self-correction, and successful human approval).
  - `brain infer "Get stock prices from Yahoo"` (Vague initial intent, verify system identifies ambiguity, generates clarification questions, and awaits human feedback/clarification before proceeding to approval).
  - (In interactive mode) User provides initial intent -> System outputs spec & clarification -> User provides feedback like "Actually, just for Apple stock" -> System processes feedback, re-validates, and presents for approval.

- **Status:** Backlog.

- **Priority Rationale:** Sixth module (P1, Order 6). This module is critical as it's the primary engine translating diverse user inputs and feedback into a reliable, validated `IntentSpec` required by `pipeline_builder/`. Its sophisticated feedback and validation mechanisms ensure higher quality inputs downstream.

- **Development Completion Note:**

  - Must be fully implemented according to the graph (including context management, new intent path, feedback path, LLM-as-a-Judge validation loop with URL checks, and human approval CLI).
  - All Pydantic models (`ContextStore`, `IntentSpec`, etc.) must be finalized.
  - Core LLM chains (`intent_chain`, `feedback_chain`, `validation_chain`) must be robust.
  - The orchestration logic in `main.py:IntentInferenceAgent` must correctly manage the state, loops, and human interaction.
  - Thorough testing is required to confirm that a variety of inputs lead to correctly structured, validated, and (simulated) human-approved `IntentSpec` outputs, including scenarios requiring self-correction and human feedback.

- **Dependencies:**

  - Takes textual input, which could originate from `cli/` or `api_gateway/`.
  - Output (`IntentSpec`) is consumed by `pipeline_builder/`.

- **Input/Output Specifications:**

  - **Input (User Text):** Natural language string, e.g., `"I want the price, title, and reviews from this Amazon page: https://amazon.ca/dp/B08WRBGSL2 for the last month"` or feedback like `"No, change the site to bestbuy.com and also get the stock availability"`.

  - Output Example (`IntentSpec` JSON after successful processing and human approval):

    json

    

    ```json
    {
      "spec_id": "intent_78532_rev1", // Example, may include revisions
      "original_user_query": "I want the price, title, and reviews from this Amazon page: https://amazon.ca/dp/B08WRBGSL2 for the last month",
      "target_urls_or_sites": ["https://amazon.ca/dp/B08WRBGSL2"],
      "data_to_extract": [
        {"field_name": "price", "description": "The current selling price of the product"},
        {"field_name": "title", "description": "The full title of the product"},
        {"field_name": "customer_reviews_text", "description": "Text content of customer reviews"}
      ],
      "constraints": {
        "time_period": "last month" // Extracted from query
      },
      "url_health_status": {"https://amazon.ca/dp/B08WRBGSL2": "healthy"},
      "validation_status": "user_approved", // Final status
      "critique_history": ["Initial LLM thought reviews might need specific date filtering, but clarified it means recent reviews."], // Example of internal critique
      "clarification_questions_for_user": [], // Empty after successful clarification/validation
      "human_approval_notes": "Approved after confirming 'last month' review scope." // Human note
    }
    ```

- **Additional Test Cases:**

  - **Multi-turn Feedback:** Test multiple rounds of human feedback leading to a final approved spec.
  - **LLM Self-Correction:** Input that initially generates a flawed spec which is then corrected by the LLM-as-a-Judge *before* human review.
  - **URL Health Failure:** Test scenario where a provided URL is unhealthy and this is caught, leading to `needs_user_clarification` or being flagged to the human.
  - **Conflicting Constraints:** User provides conflicting information – how does the LLM handle it, and how clearly is this presented for resolution?

- **Notes:**

  - **Permissivity & Refinement:** The system uses LLMs to interpret diverse inputs. The iterative refinement (LLM-as-Judge + Human Feedback) is key to handling ambiguities and improving accuracy. It does not *make assumptions* about technical details like JavaScript requirements (that's for Scout); it focuses on capturing the *user's intent* regarding *what data* from *what sources* under *what conditions*.
  - **Schema Focus:** The `IntentSpec` JSON schema is the contract. Its primary purpose is to define *what* the user wants, not *how* to get it.
  - **Autonomy (within its scope):** Operates by taking text and context, producing a refined `IntentSpec`.

- **Implementation Options (as per your detailed Python plan):**

  - Primarily **LangChain (MIT-licensed)** for orchestrating LLM calls (`intent_chain`, `feedback_chain`, `validation_chain`) with `PydanticOutputParser` for schema enforcement (or direct LLM JSON mode if preferred).
  - **Pydantic V2** for defining all data models (`IntentSpec`, `ContextStore`, etc.) and performing data validation.
  - **`httpx`** for asynchronous URL health checks.
  - Python's built-in `argparse` and `asyncio` for the `cli.py`.
  - LLM provider: **OpenAI GPT models** (e.g., `gpt-4-turbo-preview`, `gpt-3.5-turbo`) are used in the example code. This is configurable.

- **Pydantic Role:** Enforces the `IntentSpec` and intermediate schemas. Catches structural errors in LLM outputs if `PydanticOutputParser` is used. The structure of `IntentSpec` (e.g., `validation_status`, `clarification_questions_for_user`, `critique_history`) is designed to support the iterative refinement and HITL process.

- **Recommendation:** The detailed Python-based implementation plan you've drafted, using LangChain, Pydantic, and a clear agent-based orchestration, is the direct path forward for V1. This aligns with building a robust, self-correcting, and human-in-the-loop system.



### 5. progress_tracker/ (P0 - Core Foundations)

- **One-Line Goal:** Publish/subscribe run status & logs.
- Encapsulated Features:
  - Redis (hosted) or SQLite (local) event bus for tracking run progress and logging status updates.
  - `publish(event)` function for modules to log execution steps or errors (e.g., "Pipeline started", "Step 1 completed").
  - SSE (Server-Sent Events) consumer for real-time updates accessible via CLI or API.
  - **Progress Indicators:** For processes longer than 1 second, display a dynamic progress status bar, percentage, or step indicator in the terminal (using libraries like `tqdm` or `rich`) to visually inform users about ongoing operations and avoid confusion between bugs and long-running tasks.
  - **User Control Commands:** Provide commands like `diagnostic <run_id>` (to inspect detailed logs or state), `kill <run_id>` (to terminate a stuck process), and `retry <run_id>` (to restart a failed run with optional adjustments), preventing zombie modes, infinite loops, or stuck processes.
- Key CLI Regression Tests:
  - Simulated-events unit test (mock events like "Pipeline started" and verify receipt in CLI or log).
- **Status:** Backlog.
- **Priority Rationale:** Fourth module (P0, Order 4) as requested, placed directly after `cli/` to enable tracking of operations initiated via CLI. Essential for providing visibility into ongoing processes even in V1.
- **Development Completion Note:** Must be fully implemented (local SQLite event bus, basic publishing mechanism, progress indicators, user control commands) and tested before moving to `api_gateway/`. Tests must confirm that status events are published, progress is displayed dynamically, and control commands work as expected.
- **Dependencies:** Integrates with `cli/` for displaying real-time status and progress to users, and later with `executor/` for run-specific events.
- Input/Output Specifications:
  - **Input Example (Publish):** `publish({"run_id": "123", "status": "started", "message": "Pipeline initiated", "progress_percentage": 0})` (logged by a module like `executor`).
  - **Output Example (CLI View):** `brain status 123` returns stream or log like "Run 123: started - Pipeline initiated at 10:00 [Progress: 0% - Step 1/3]".
  - **Progress Indicator Example:** During a scrape, terminal shows `[██████████          ] 50% - Fetching page content...` updated every second.
  - **Control Command Example:** `brain diagnostic 123` returns "Run 123: Last update 30s ago, Status: Fetching, Possible delay in network response", while `brain kill 123` terminates with "Run 123 terminated by user".
- Additional Test Cases:
  - Edge Case: Multiple simultaneous runs (ensure event isolation by `run_id` and correct progress bars for each).
  - Error Case: Publishing with missing `run_id` (expect fallback or error handling).
  - Progress Case: Long process (>1s) without updates (ensure progress bar shows "stalled" or similar warning).
  - Control Case: Test `kill` on non-existent run (expect error message).
- Notes:
  - Focus on local SQLite in V1 for simplicity, deferring Redis to a later phase for hosted scalability.
  - Integration with `cli/` for real-time status display during testing.
  - **Progress Indicators:** Implement dynamic terminal progress bars/percentages/steps updating every second for processes over 1 second, ensuring users understand if a delay is normal or indicative of a bug.
  - **User Control:** Commands like `diagnostic`, `kill`, and `retry` give users visibility and control over runs, preventing zombie processes or infinite loops by allowing inspection (detailed logs), termination, or restart with adjustments, enhancing trust in the system’s state.

### 6. api_gateway/ (P0 - Core Foundations)

- **One-Line Goal:** Single REST / MCP entrypoint.
- Encapsulated Features:
  - FastAPI base app for REST API access to core functions of other modules.
  - Routes: `/build` (pipeline creation endpoint), `/run` (execution trigger), `/status` (run status retrieval), `/tools` (registry access for listing tools).
  - SSE endpoint: `/events/{run}` for real-time status updates linked to `progress_tracker`.
- Key CLI Regression Tests:
  - `curl /healthz` (check API health, expect 200 OK response).
  - `brain --api ping` (CLI-to-API connectivity test, expect confirmation).
- **Status:** Backlog.
- **Priority Rationale:** Fifth module (P0, Order 5) as it provides an alternative interface to CLI for automated or remote interactions, complementing the initial flow. Follows `progress_tracker/` to enable integration with status tracking.
- **Development Completion Note:** Must be fully implemented (basic FastAPI app with core routes) and tested before moving to `intent_inference/`. Tests must confirm that the API can interact with `tool_registry` and `cli/`.
- **Dependencies:** Relies on `tool_registry/` for tool data access, `progress_tracker/` for SSE status updates, and eventually other modules for pipeline building/execution.
- Input/Output Specifications:
  - **Input Example (API Call):** `POST /tools {"name": "playwright", "tool_type": "browser"}` (add tool via API).
  - **Output Example (API Response):** `GET /tools` returns `[{"name": "playwright", "tool_type": "browser", ...}, ...]` with HTTP 200 status.
- Additional Test Cases:
  - Edge Case: API request with malformed JSON (expect 400 Bad Request).
  - Error Case: Access non-existent endpoint (expect 404 Not Found).
- Notes:
  - While CLI suffices for V1 testing, `api_gateway` supports broader integrations and automation in future iterations.
  - Lives in the same codebase, allowing parallel access to shared modules like `tool_registry`.

### 7. pipeline_builder/ (P1 - High Priority)

- **One-Line Goal:** Dynamically build `PipelineSpec` JSON from `IntentSpec` for scraping tasks.
- Encapsulated Features:
  - Functions: `propose_pipeline(intent_spec) -> PipelineSpec` for creating initial pipeline specifications.
  - `modify_pipeline(pipeline_spec, feedback) -> PipelineSpec` for adjustments based on execution feedback or errors.
  - Integration with `tool_registry` for selecting tools and validating compatibilities during pipeline construction.
- Key CLI Regression Tests:
  - `brain dryrun --intent-spec <json_file> --show-spec` (preview pipeline spec from intent, verify structure and tool selection).
- **Status:** Backlog.
- **Priority Rationale:** Seventh module (P1, Order 7) as it dynamically constructs pipelines from `IntentSpec`, a key step in the flow following intent interpretation.
- **Development Completion Note:** Must be fully implemented (tool selection, pipeline generation, feedback adjustments) and tested before moving to `executor/`. Tests must confirm that `IntentSpec` inputs produce valid `PipelineSpec` outputs respecting compatibility rules.
- **Dependencies:** Relies heavily on `tool_registry/` for tool metadata and compatibility data; takes input from `intent_inference/`.
- Input/Output Specifications:
  - **Input Example (`IntentSpec` JSON):** `{"target": {"type": "url", "value": "https://amazon.ca/dp/B08WRBGSL2"}, "requirements": {"technical": ["javascript_rendering"]}, "data_to_extract": ["price", "title"]}`.
  - **Output Example (`PipelineSpec` JSON):** `[{"step": 1, "tool": "Playwright", "config": {"url": "https://amazon.ca/dp/B08WRBGSL2", "wait_selector": "span.a-price-whole"}}, {"step": 2, "tool": "BeautifulSoup4", "config": {"selectors": {"price": "span.a-price-whole", "title": "#productTitle"}}}]`.
- Additional Test Cases:
  - Edge Case: `IntentSpec` with conflicting requirements (e.g., no tools match all needs) – expect fallback tool selection or error.
  - Error Case: Tools incompatible for pipeline (expect alternative tool suggestion or failure report).
- Notes:
  - **Complexity Management:** Uses `compatibility_matrix.json` from `tool_registry` for explicit tool pairings (e.g., "Playwright + BeautifulSoup4 = OK").
  - **Simplification:** Limit pipeline complexity (e.g., max 3 tools initially). Separate initial generation from feedback-based optimization to avoid confusion.
  - **Output:** Rigid `PipelineSpec` JSON (steps, tools, configurations) validated via Pydantic schema.

### 8. executor/ (P2 - Medium Priority)

- **One-Line Goal:** Execute pipelines defined in `PipelineSpec` and return scraped results.
- Encapsulated Features:
  - Local execution of pipelines using hardcoded logic in V1 (e.g., `if/elif` conditional blocks for known tools like Playwright, BeautifulSoup4).
  - Basic error handling for common issues (timeouts, selector not found) and result passing between pipeline steps.
  - Initial output cleaning (e.g., strip HTML tags, basic field validation before return).
- Key CLI Regression Tests:
  - `brain runlocal <spec_id>` (execute a pipeline spec and return results, verify data scraping).
- **Status:** Backlog.
- **Priority Rationale:** Eighth module (P2, Order 8) as it completes the base flow by executing generated pipelines, a testable step after validating construction logic via `pipeline_builder`.
- **Development Completion Note:** Must be fully implemented (V1 hardcoded logic for key tools, error handling) and tested before moving to `evaluator/`. Tests must confirm successful execution of a simple pipeline and proper result return.
- **Dependencies:** Takes input from `pipeline_builder/` (`PipelineSpec` JSON), may log status via `progress_tracker/`.
- Input/Output Specifications:
  - **Input Example (`PipelineSpec` JSON):** `[{"step": 1, "tool": "Playwright", "config": {"url": "https://amazon.ca/dp/B08WRBGSL2"}}, {"step": 2, "tool": "BeautifulSoup4", "config": {"selectors": {"price": "span.a-price-whole"}}}]`.
  - **Output Example (Raw Result):** `{"price": "123.00", "title": "Mon Produit Incroyable"}` (post minimal cleaning).
- Additional Test Cases:
  - Edge Case: Pipeline with unsupported tool (expect graceful failure or skip).
  - Error Case: Webpage timeout or selector not found (expect detailed error log and status update via `progress_tracker`).
- Notes:
  - **Simplification for V1:** Restrict to local execution (Python subprocess) without Docker/K8s complexity. Hardcode logic for a limited set of tools (e.g., Playwright, BeautifulSoup4).
  - **Autonomy:** Takes `PipelineSpec` as input, executes independently, outputs raw or minimally cleaned results.
  - **Evolution:** V2 introduces dynamic adaptors to replace hardcoded logic.



### 9. evaluator/ (P2 - Medium Priority)

- **One-Line Goal:** Analyze execution results, diagnose errors, perform basic cleaning for analysis, and trigger intelligent feedback loops.
- Encapsulated Features:
  - **Error Analysis:** Identify specific failure types (selector not found, anti-bot detection, timeouts) and map them to potential causes.
  - **Page Structure Analysis:** Examine HTML to find alternative selectors or extraction patterns when standard approaches fail.
  - **Fix Suggestion:** Generate actionable recommendations for pipeline adjustments, selector modifications, or tool changes.
  - **Output Validation:** Ensure extracted fields match `IntentSpec` requirements (e.g., all requested fields present).
  - **Basic Cleaning:** Perform minimal cleaning necessary for proper analysis (remove basic HTML tags, normalize whitespace).
  - **Quality Scoring:** Evaluate completeness and accuracy based on predefined or dynamic criteria.
  - **Feedback Routing:** Direct issues to appropriate modules (e.g., `pipeline_builder` for pipeline flaws, `intent_inference` for intent misinterpretation).
- Input/Output Specifications:
  - **Input Example (Success Case):** `{"price": "123.00<br>", "title": "<b>Mon Produit Incroyable</b>"}`, with associated `IntentSpec` and `run_id`.
  - **Input Example (Error Case):** `{"error": {"type": "selector_not_found", "selector": ".price-whole", "page_content": "<!DOCTYPE html>..."}}`, with associated `IntentSpec` and `run_id`.
  - **Output Example (Analyzed & Basic Cleaned):** `{"basic_cleaned_result": {"price": "123.00", "title": "Mon Produit Incroyable"}, "quality_score": 0.9, "feedback": "All requested fields present"}`.
  - **Output Example (Error Analysis):** `{"analysis": {"error_type": "selector_not_found", "possible_causes": ["Site layout change"], "suggested_selectors": [".s-item__price"]}, "recommendations": [{"action": "update_selector", "target": "price", "new_value": ".s-item__price"}]}`.
- Notes:
  - **Focused Role:** Primarily concerned with validating extraction success and diagnosing failures
  - **Basic Cleaning Only:** Performs minimal cleaning necessary for analysis (removing obvious HTML tags)
  - **Semantic Validation:** Checks if the data makes sense given the intent (e.g., price is present for product intent)

### 10. knowledge_base/ (P3 - Low Priority)

- **One-Line Goal:** Store past pipelines for learning and reuse in future runs.
- Encapsulated Features:
  - Storage of pipeline runs with associated data (`IntentSpec`, `PipelineSpec`, execution results, user feedback).
  - Simple similarity search to retrieve successful past pipelines for reuse by `pipeline_builder`.
- Key CLI Regression Tests:
  - `brain kb stats` (show stats on stored runs, verify storage and count).
- **Status:** Backlog.
- **Priority Rationale:** Tenth module (P3, Order 10) as it is not essential for the initial scraping flow but enhances `pipeline_builder` by learning from past runs, an optimization for post-V1.
- **Development Completion Note:** Must be fully implemented (local storage, basic similarity search) and tested before moving to `aggregator/`. Tests must confirm storage and retrieval of past runs.
- **Dependencies:** Stores data from `intent_inference/` (`IntentSpec`), `pipeline_builder/` (`PipelineSpec`), `executor/` (results), and `evaluator/` (feedback/quality scores).
- Input/Output Specifications:
  - **Input Example (Store Run):** `save_run({"run_id": "123", "intent_spec": {...}, "pipeline_spec": {...}, "result": {...}, "feedback": "Success", "quality_score": 0.9})`.
  - **Output Example (Search Similar):** `find_similar_successful_runs(intent_spec)` returns `[ {"run_id": "456", "pipeline_spec": {...}, "quality_score": 0.95}, ... ]`.
- Additional Test Cases:
  - Edge Case: Search with no similar runs (expect empty result or fallback suggestion).
  - Error Case: Corrupted stored data (expect graceful handling or skip).
- Notes:
  - **Simplification:** Use PostgreSQL for structured storage (JSONB for specs). Defer vector search (e.g., Chroma) for semantic similarity to later phases.
  - **Autonomy:** Passive store/retrieve system, providing raw data to `pipeline_builder` without decision-making logic.
  - **Feedback Storage:** Stores all runs (success/failure) for long-term learning, supporting feedback loops.

### 11. output_processor/ (Renamed from aggregator/) (P4 - Medium Priority)

- **One-Line Goal:** Apply deep cleaning to individual results and merge multiple JSON runs when needed.

- Encapsulated Features:

  - Deep Data Cleaning:

    Apply comprehensive cleaning and normalization to single run data:

    - Remove all HTML artifacts
    - Format field values according to semantic type (prices, dates, etc.)
    - Standardize field names and structure
    - Apply data transformations based on IntentSpec

  - **Schema Normalization:** Ensure consistent formatting across results, leveraging an LLM to intelligently map fields (e.g., aligning "price" and "cost" to a unified key).

  - **Multi-Run Merging:** Combine multiple runs into a consolidated output when needed.

  - **Type Conversion:** Apply appropriate type conversions (string to number, date parsing, etc.) based on field semantics.

  - **Consistent Structure:** Ensure output JSON matches expected structure defined in IntentSpec.

- Input/Output Specifications:

  - **Input Example (Single Run):** `{"basic_cleaned_result": {"price": "123.00", "title": "Mon Produit Incroyable"}, "quality_score": 0.9}`.
  - **Input Example (Multiple Runs):** Multiple results with tag "jobs".
  - **Output Example (Single Deep Cleaned):** `{"processed_result": {"price": 123.00, "title": "Mon Produit Incroyable"}, "processing_notes": ["Converted price to number", "Fixed capitalization"]}`.
  - **Output Example (Merged Result):** `{"tag": "jobs", "merged_data": [{"price": 123.00, "title": "Product A"}, {"price": 456.00, "title": "Product B"}]}`.

- Notes:

  - **Dual Functions:** Handles both deep cleaning of individual results and merging of multiple results
  - **Always Cleans:** Every successful run passes through output_processor for consistent formatting
  - **LLM Integration:** Uses LLM for complex normalization decisions and field mapping
  - **IntentSpec Driven:** Uses intent specifications to determine appropriate formatting
  - **User-Ready Output:** This module is responsible for the final polish on the data before it's stored permanently or presented to the user.
  - LLM Mapping Case: Test field renaming and restructuring for both single (if target schema differs from raw) and multi-run scenarios.

### 12. scout/ (P1 - High Priority)
- One-Line Goal: Analyze websites to determine technical requirements and structure
- Encapsulated Features:
  - Check URL validity and accessibility
  - Detect JavaScript requirements and page rendering needs
  - Identify anti-bot measures, login walls, or proxy blocks
  - Map available data fields and their selectors
  - Determine site navigation patterns (pagination, detail pages)

### 13. orchestrator/ (P1 - High Priority)
- One-Line Goal: Coordinate flow between modules and manage execution state
- Encapsulated Features:
  - Run ID generation and context tracking
  - Sequential invocation of modules with proper error handling
  - Status updates via progress_tracker
  - Decision-making for retries or fallbacks
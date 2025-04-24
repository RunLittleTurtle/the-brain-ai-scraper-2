# Module Index & Development Priority

> Modular roadmap for the "The Brain" project. Each module is designed to be independent and testable in isolation, with a focus on components necessary for the defined scraping flow (from user intent to execution and feedback). Modules are completed one by one in the specified order, yet coexist in the same codebase if needed for interactions or cross-testing.

## General Approach for LLM and Program Autonomy

- Each module must have well-defined inputs and outputs (preferably in JSON format via Pydantic schemas) to avoid ambiguity and ease integration.
- Interactions between modules must be limited to simple function calls or data exchanges via files or a shared database, reducing complex dependencies.
- Provide concrete examples and regression tests in each module's specification (expected inputs/outputs, error cases) to guide LLM-driven development and ensure consistency.
- **Sequential Completion:** Each module must be fully implemented and tested before proceeding to the next in the development order, although minor adjustments or integrations might require revisiting earlier modules. All modules reside in the same codebase, enabling interactions as needed (e.g., `cli/` calling `tool_registry/` for early testing).

## Summary with Development Order

1. **Priority P0: tool_registry/** - Plug-and-play catalogue of scraping tools. CLI Tests: `brain tools add playwright`, `brain tools list`. Status: `[Human_Review]`

2. **Priority P0: config_secrets/** - Centralised secrets & runtime switches. CLI Tests: `brain config set OPENAI_KEY`, `brain config list`. Status: `[Human_Review]`

3. **Priority P0: cli/** - Thin CLI wrapper for user interaction & testing. CLI Tests: `brain scrape`, `brain tools list`. Status: `Backlog`

4. **Priority P0: progress_tracker/** - Publish/subscribe run status & logs. CLI Tests: Simulated-events unit test. Status: `Backlog`

5. **Priority P0: api_gateway/** - Single REST / MCP entrypoint. CLI Tests: `curl /healthz`, `brain --api ping`. Status: `Backlog`

6. **Priority P1: intent_inference/** - Turn raw user input into structured `IntentSpec` JSON. CLI Tests: `brain infer "scrape price on Amazon"`. Status: `Backlog`

7. **Priority P1: pipeline_builder/** - Dynamically build `PipelineSpec` JSON from `IntentSpec`. CLI Tests: `brain dryrun --show-spec`. Status: `Backlog`

8. **Priority P2: executor/** - Execute pipelines and return results. CLI Tests: `brain runlocal <spec_id>`. Status: `Backlog`

9. **Priority P3: evaluator/** - Score output quality and clean results. CLI Tests: `brain evaluate <run_id>`. Status: `Backlog`

10. **Priority P3: knowledge_base/** - Store past pipelines for learning and reuse. CLI Tests: `brain kb stats`. Status: `Backlog`

11. **Priority P3: aggregator/** - Merge multiple JSON runs. CLI Tests: `brain merge tag=jobs`. Status: `Backlog`

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
- **Status:** `[Human_Review]`
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
- **Status:** Backlog.
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
- **Status:** Backlog.
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

### 4. progress_tracker/ (P0 - Core Foundations)

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

### 5. api_gateway/ (P0 - Core Foundations)

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

### 6. intent_inference/ (P1 - High Priority)

- **One-Line Goal:** Transform raw user input (structured or free-text) into structured `IntentSpec` JSON.

- Encapsulated Features:

  - LLM-based function: `infer_intent(input: str) -> IntentSpec` for parsing diverse user requests.
  - Support for structured input (e.g., CLI flags like `--url`) and free-text natural language input (e.g., "Get price from Amazon").
  - Output validation using a strict Pydantic schema for `IntentSpec` to ensure machine-readable format with error detection for malformed or incomplete intents.

- Key CLI Regression Tests:

  - `brain infer "scrape price on Amazon product page https://amazon.ca/dp/B08WRBGSL2"` (free-text input, verify `IntentSpec` creation).
  - `brain infer --url https://amazon.ca/dp/B08WRBGSL2 --extract price,title` (structured input, verify `IntentSpec` creation).

- **Status:** Backlog.

- **Priority Rationale:** Sixth module (P1, Order 6) as it translates user inputs into a usable format (`IntentSpec`) for `pipeline_builder`. Follows the foundational P0 modules to ensure robust user interfaces before tackling processing logic.

- **Development Completion Note:** Must be fully implemented (LLM parsing, schema validation) and tested before moving to `pipeline_builder/`. Tests must confirm that varied inputs (structured or free-text) produce valid `IntentSpec` outputs.

- **Dependencies:** Relies on `cli/` for receiving user input and may integrate with `api_gateway/` for API-driven requests.

- Input/Output Specifications:

  - **Input Example (Free-text):** `"I want the price and title from this Amazon page: https://amazon.ca/dp/B08WRBGSL2"`.
  - **Input Example (Structured):** `--url https://amazon.ca/dp/B08WRBGSL2 --extract price,title --jscan true`.
  - **Output Example (`IntentSpec` JSON):** `{"target": {"type": "url", "value": "https://amazon.ca/dp/B08WRBGSL2"}, "requirements": {"technical": ["javascript_rendering", "html_parsing"]}, "data_to_extract": ["price", "title"]}`.

- Additional Test Cases:

  - Edge Case: Ambiguous input (e.g., "Get product info from Amazon") – expect LLM to prompt for URL or make reasonable assumptions.
  - Error Case: Invalid URL format (expect Pydantic validation error or correction suggestion logged for feedback).

- Notes:

  - **Permissivity:** Highly flexible, using an LLM to interpret diverse formulations. Makes assumptions if needed (e.g., JavaScript for Amazon domains) and requests clarification for ambiguities via CLI prompts.

  - **Simplification:** Rigid `IntentSpec` JSON schema with mandatory fields (`target`, `requirements`, `data_to_extract`) and defaults. Include input-output examples in specs to guide LLM coding.

  - **Autonomy:** Operates independently, producing `IntentSpec` from text input without initial reliance on other modules beyond user input delivery.

  - Implementation Options:

     

    Several libraries and services can aid development, offering varied approaches for intent parsing:

    - **LangChain (MIT-licensed):** Easy orchestration of LLM calls with Pydantic OutputParsers to enforce `IntentSpec` schema. Vendor-agnostic, works with any LLM (OpenAI, Anthropic, local). Example: `parser = PydanticOutputParser(pydantic_object=IntentSpec); chain.run_and_parse(input=user_text)`.
    - **OpenAI Python SDK Function Calling:** Defines `IntentSpec` as a JSON schema for direct structured output. Tied to OpenAI but minimizes prompt engineering. Example: Define `infer_intent` function schema and parse response with `function_call.arguments`.
    - **Rasa NLU (Apache-2.0):** Intent classification and entity extraction via trainable models for offline use. Requires annotation but offers high accuracy.
    - **spaCy + spaCy-Transformer (MIT-licensed):** Token-level NER and custom rules for URL/entity extraction before/after LLM. Lightweight but manual setup.
    - **Typer (MIT-licensed):** CLI parsing for structured inputs (`--url`, `--extract`) directly into Pydantic models. Complements LLM for free-text. Example: `app.command()(flags: Flags = typer.Argument(...))`.
    - **Commercial NLU Services (Google Dialogflow, Microsoft LUIS, Amazon Lex):** Outsourced intent detection and slot filling via API, mappable to `IntentSpec`.

  - **Pydantic Role:** Pydantic enforces `IntentSpec` schema, ensuring consistent output and catching malformed intents (e.g., missing URL) via validation errors, which can be logged as feedback for refinement. In the long run, feedback from `evaluator/` (e.g., failed runs due to poor intent parsing) stored in `knowledge_base/` can inform `intent_inference/` improvements or redirect `pipeline_builder` with adjusted strategies (e.g., alternative tools if intent was misparsed as not needing JavaScript).

  - **Recommendation:** A hybrid stack of Typer (CLI parsing), Pydantic (schema/validation), and LangChain/OpenAI SDK (LLM parsing) balances flexibility, control, and error detection for V1, with feedback loops enhancing accuracy over time.

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

### 9. evaluator/ (P3 - Low Priority)

- **One-Line Goal:** Score output quality, clean results, and trigger feedback loops.
- Encapsulated Features:
  - Output validation to ensure extracted fields match `IntentSpec` requirements (e.g., all requested fields present).
  - Advanced cleaning of results (e.g., remove HTML artifacts like `<br>`, format numbers for "price").
  - Quality scoring (e.g., completeness, accuracy based on predefined or dynamic criteria).
  - Feedback triggering to suggest retry or adjustment, routing issues to `pipeline_builder` (pipeline flaws) or `intent_inference` (intent misinterpretation).
- Key CLI Regression Tests:
  - `brain evaluate <run_id>` (assess output quality and cleanliness, verify cleaned JSON and feedback suggestions).
- **Status:** Backlog.
- **Priority Rationale:** Ninth module (P3, Order 9) as it enhances the flow by validating and cleaning outputs after execution, a valuable but non-critical step for initial V1 testing of the core scraping flow.
- **Development Completion Note:** Must be fully implemented (validation, advanced cleaning, feedback logic) and tested before moving to `knowledge_base/`. Tests must confirm outputs are cleaned (no HTML tags) and appropriate feedback is suggested for errors or poor quality.
- **Dependencies:** Takes output from `executor/`, references `IntentSpec` from `intent_inference/` for validation, integrates with `progress_tracker/` for status logging.
- Input/Output Specifications:
  - **Input Example (Raw Output from Executor):** `{"price": "123.00<br>", "title": "<b>Mon Produit Incroyable</b>"}`, with associated `IntentSpec` and `run_id`.
  - **Output Example (Cleaned & Scored):** `{"cleaned_result": {"price": "123.00", "title": "Mon Produit Incroyable"}, "quality_score": 0.9, "feedback": "All requested fields present and clean"}`.
  - **Feedback Trigger Example:** If "price" is missing, output `{"feedback": "Missing field 'price', suggest adjusting selector in pipeline", "target_module": "pipeline_builder"}`.
- Additional Test Cases:
  - Edge Case: Output with mixed HTML and text (expect full cleanup to plain text).
  - Error Case: Missing mandatory fields per `IntentSpec` (expect low score and feedback to adjust pipeline or intent).
- Notes:
  - **Output Cleaning:** Ensures JSON output matches user intent (e.g., "price" as numeric, no HTML in "title"). Basic cleaning initially in `executor`, advanced validation and scoring here.
  - **Feedback Loop:** Determines if issues stem from intent misinterpretation (returns to `intent_inference`) or pipeline flaws (returns to `pipeline_builder`), with clear triggers based on error type or quality score.

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

### 11. aggregator/ (P4 - Very Low Priority)

- **One-Line Goal:** Merge multiple JSON runs into consolidated output.
- Encapsulated Features:
  - `merge(tag)` command to combine results from multiple scraping runs under a shared tag or identifier.
  - Schema normalization to ensure consistent formatting across merged results, leveraging an LLM to intelligently map fields (e.g., aligning "price" and "cost" to a unified key), rename columns, and restructure data dynamically for coherence.
  - Consolidated JSON output aggregating data from multiple runs into a unified structure.
  - **Staging Mechanism:** Use a secondary database or in-memory staging structure to temporarily hold data during manipulation, ensuring original scraped results remain untouched until the aggregated output is finalized and validated.
- Key CLI Regression Tests:
  - `brain merge tag=jobs` (merge results tagged with a specific identifier, verify consolidated output).
- **Status:** Backlog.
- **Priority Rationale:** Eleventh and final module (P4, Order 11) as it provides an advanced feature for merging results, outside the scope of the basic V1 scraping flow but useful for broader use cases (e.g., combining multiple scrapes).
- **Development Completion Note:** Last module to complete, after all others are fully implemented and tested. Tests must confirm multiple results can be merged into a coherent JSON output.
- **Dependencies:** Takes outputs from `executor/` or `evaluator/` (scraped results with tags), may store staging data temporarily.
- Input/Output Specifications:
  - **Input Example (Run Results):** Multiple JSON files or DB entries tagged with "jobs", e.g., `{"tag": "jobs", "data": {"price": "123.00", "item_name": "Product A"}}, {"tag": "jobs", "data": {"cost": "456.00", "title": "Product B"}}`.
  - **Intermediate Mapping (LLM Output):** LLM processes to map fields, e.g., `{"normalized_data": [{"price": "123.00", "title": "Product A"}, {"price": "456.00", "title": "Product B"}]}` (stored in staging DB/structure).
  - **Output Example (Merged Result):** `{"tag": "jobs", "merged_data": [{"price": "123.00", "title": "Product A"}, {"price": "456.00", "title": "Product B"}]}` (finalized post-LLM normalization).
- Additional Test Cases:
  - Edge Case: Merging runs with conflicting schemas (expect LLM-driven normalization or detailed error report if unmappable).
  - Error Case: No runs found for tag (expect empty result or user notification).
  - LLM Mapping Case: Test field renaming (e.g., "cost" to "price") and restructuring (expect consistent unified schema).
- Notes:
  - **LLM Integration:** Utilize an LLM to intelligently aggregate and normalize data, mapping disparate fields (e.g., "price" and "cost" to "price") and restructuring inconsistent JSON outputs into a unified schema. This reduces manual rule-coding and adapts to varied data formats dynamically.
  - **Staging Mechanism:** Implement a secondary database (e.g., temporary SQLite table) or in-memory structure to stage data during LLM processing, preserving original results until the aggregated output is validated and confirmed correct. This ensures data integrity and allows rollback if mapping fails.
  - Focus on simple merging logic in V1 with basic LLM mapping, deferring complex normalization or large-scale DB setups to later phases.
  - Enhances usability for users running multiple scrapes but not critical for initial flow.

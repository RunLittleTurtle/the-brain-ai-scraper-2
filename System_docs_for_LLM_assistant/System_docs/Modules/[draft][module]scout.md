# [draft] [module] Scout

12. scout/ (P1 - High Priority)
- One-Line Goal: Analyze websites to determine technical requirements and structure
- Encapsulated Features:
  - Check URL validity and accessibility
  - Detect JavaScript requirements and page rendering needs
  - Identify anti-bot measures, login walls, or proxy blocks
  - Map available data fields and their selectors
  - Determine site navigation patterns (pagination, detail pages)



## The "Scout" Functionality for `intent_inference` and `evaluator`

You've hit on a very important point. Simply translating NLP to `IntentSpec` might not be enough. The `IntentSpec` needs to be *grounded* in the reality of the target website.

**My thoughts on the "Scout":**

*   **A Dedicated `ScoutAgent` or `WebsiteProfiler` Module:** I lean towards creating a new, distinct module for this.
    *   **Goal:** To perform preliminary analysis of a target (URL, website) to gather metadata crucial for both robust intent inference and effective evaluation/error diagnosis.
    *   **Responsibilities:**
        *   Basic connectivity checks (is the URL live?).
        *   Detecting JavaScript-heavy rendering needs.
        *   Initial assessment of anti-bot measures (Cloudflare, captchas observed on a quick pass).
        *   Checking for common pagination patterns or if content is loaded dynamically.
        *   For tasks like "get job details," it might try to identify if the URL is a list page or a detail page.
        *   **Crucially for `intent_inference`:** If the user says "extract field X," the scout could do a quick check to see if something resembling "X" is even present on the page, potentially prompting the user for clarification earlier.
        *   **Crucially for `evaluator`:** When a scrape fails (e.g., "selector not found"), the `evaluator` can call the `ScoutAgent` to re-analyze the page *as it is now* to understand if the structure changed, if new anti-bot measures are up, etc.
    *   **Implementation:** This `ScoutAgent` could itself be a Langchain chain or a small, focused LangGraph. It might use tools like:
        *   A simple `requests.get()`.
        *   A headless browser (Playwright/Selenium) for a quick JS render and DOM snapshot.
        *   Lightweight HTML parsing (BeautifulSoup) to look for specific tags/patterns.
        *   Potentially a very focused LLM call to summarize page characteristics based on its DOM/content.
    *   **Output:** A `ScoutReport` (Pydantic model) detailing its findings.
        `{"url_is_live": true, "requires_javascript": true, "detected_anti_bot": "Cloudflare (challenge observed)", "initial_field_check": {"price": "likely_present", "reviews": "not_obvious"}, "page_type_guess": "product_detail"}`.

*   **Why a separate module?**
    *   **SRP (Single Responsibility Principle):** `intent_inference` focuses on understanding user language. `evaluator` focuses on results and errors. The "Scout" focuses on understanding the target website's raw characteristics.
    *   **Reusability:** Both `intent_inference` and `evaluator` (and potentially `pipeline_builder` if it wants to proactively choose tools based on scouted info) can use it.
    *   **Testability:** The `ScoutAgent` can be tested in isolation.

*   **Integration:**
    *   `intent_inference` calls `ScoutAgent` -> receives `ScoutReport` -> uses report to refine `IntentSpec` (e.g., adds `javascript_rendering: true` to requirements) or even prompt the user for more info if the scout finds discrepancies.
    *   `evaluator` calls `ScoutAgent` when an error occurs -> uses `ScoutReport` to diagnose and suggest fixes.

So, yes, great instinct! Adding a `WebsiteProfilerAgent` (or similar name) to your module index seems like a smart move.
# Google Infer_intent langchain plan

```markdown
# Module Development Plan: intent_inference

**Module Index:** #4
**Priority:** P1 (High Priority)
**Development Order:** 6
**Status:** `[Backlog]`

## I. Core Purpose & Context

### Description

The `intent_inference` module is responsible for transforming raw user input—provided either as structured data (primarily for development/API use) or, more commonly, **free-text natural language via the CLI**—into one or more standardized, machine-readable JSON objects called `IntentSpec`. This structured specification defines the user's scraping or information retrieval goal (what to retrieve, from where, relevant parameters, and specific requirements).

This module acts as a crucial translator between the user's request (via `cli` or potentially `api_gateway`) and the downstream `pipeline_builder` module. Its primary implementation will leverage the **LangChain** framework to orchestrate interactions with a Large Language Model (LLM) for understanding natural language input.

**LangSmith** will be integrated for observability, enabling tracing, debugging, and evaluation of the LLM interactions and parsing steps. **Langflow** can be used during development for visual prototyping and understanding of the LangChain flows before implementation in code.

The module should adhere to a microservice mindset: well-defined inputs/outputs, clear dependencies managed via LangChain, and independently testable units, facilitated by LangSmith evaluation. **It must handle a variety of user intents**, from simple URL scraping to complex searches like finding job postings, local businesses, or monitoring online discussions.

### Main Objective (for Implementing LLM Coder)

Your primary goal is to implement the Python functions necessary to:
1.  Accept user input (`str` or `Dict`). Prioritize robust handling of **free-text `str` input**.
2.  **Utilize LangChain:** Construct a chain (potentially using a **RouterChain** approach for different intent types) involving `PromptTemplate`(s), an LLM (e.g., `ChatOpenAI`), and a `PydanticOutputParser` configured for `IntentOutput` (containing `List[IntentSpec]`).
3.  **Handle Diverse Intents:** The system must parse varied requests:
    *   Simple URL scraping (`"Get price from URL"`)
    *   Complex entity searches (`"Find product manager jobs on Indeed/LinkedIn last month"`)
    *   Filtered product searches (`"best-selling wireless headphones on Amazon, 4+ stars, under $100, available in Montreal"`)
    *   Local searches (`"nearby coffee shops over 4 stars open now"`)
    *   Marketplace searches (`"used baseball bats on Facebook Marketplace"`)
    *   Content monitoring (`"Reddit posts about Gymshark competitors in last 24h"`)
4.  **Suggest Relevant Fields:** The LLM should be prompted to suggest appropriate `data_to_extract` fields based on the inferred task type (e.g., suggest `job_title`, `salary` for job searches), *in addition to* any fields explicitly requested by the user.
5.  **Output Structure:** Ensure the output is a `List[IntentSpec]` containing one or more validated Pydantic V2 objects.
6.  **Integrate LangSmith:** Configure automatic tracing via environment variables.
7.  **Error Handling:** Gracefully handle LLM errors, parsing failures, and validation issues.

### Dependencies

*   **Internal Modules:**
    *   `config_secrets`: To retrieve API keys (e.g., `OPENAI_API_KEY`, `LANGCHAIN_API_KEY`).
*   **External Libraries:**
    *   `pydantic` (>= V2): For `IntentSpec` schema (using V2 features).
    *   `langchain`: Core framework.
    *   `langchain-openai`: (Or other provider).
    *   `langsmith`: SDK for observability.
    *   `python-dotenv`: For loading `.env`.
    *   `tiktoken`: For OpenAI token counting.

### Suggested File Structure

```
intent_inference/
├── __init__.py
├── models/
│   ├── __init__.py
│   └── specs.py           # Defines IntentSpec Pydantic V2 model
├── chains/
│   ├── __init__.py
│   ├── intent_router.py   # Optional: Logic for routing to different chains
│   ├── generic_parser_chain.py # Or specific chains (job_parser_chain.py, etc.)
│   └── chain_factory.py   # Function to build the appropriate chain
├── core.py                # Main infer_intent function calling the chain factory/chain
├── exceptions.py          # Custom exceptions
├── utils.py               # Helper functions
├── prompts/               # Store prompt templates
│   ├── generic_intent_prompt.txt
│   ├── job_search_prompt.txt # Example specific prompt if using router
│   └── product_search_prompt.txt # Example specific prompt
└── tests/
    # ... testing files ...
```

## II. Technical Design & Interfaces

### Inputs & Outputs

*   **Primary Input:** `Union[str, Dict]` (Focus on `str`)
    *   *Example 1 (Job Search):* `"I want to retrieve all the job posting of the last month from indeed and linkedin for product manager positions"`
    *   *Example 2 (Amazon Search):* `"Find me the best-selling wireless headphones on Amazon with 4+ stars and price under $100 available in a Montreal store"`
*   **Primary Output:** `List[IntentSpec]` (Validated Pydantic V2 Objects)
    *   **Output Example 1 (Job Search):**
        ```json
        [
          {
            "target": {
              "type": "search_query",
              "source_platform": "Indeed",
              "search_keywords": ["product manager"],
              "time_filter": "last_month",
              "estimated_query": "q=product+manager&fromage=30&sort=date"
            },
            "data_to_extract": [ // Fields suggested by LLM based on context + any user fields
              "job_title",
              "company_name",
              "location",
              "salary_range", // Suggested
              "job_description",
              "posted_date", // Suggested
              "apply_url", // Suggested
              "employment_type" // Suggested
            ],
            "requirements": {
              "technical": ["requires_search_capability", "handle_pagination", "date_parsing"],
              "performance": {"timeout_seconds": 60, "max_retries": 2 }
            },
            "metadata": {
              "original_input": "I want to retrieve all the job posting of the last month from indeed and linkedin for product manager positions",
              "inferred_task_type": "job_search",
              "source": "cli_free_text",
              "confidence_score": 0.90
            }
          },
          {
            "target": {
              "type": "search_query",
              "source_platform": "LinkedIn",
              "search_keywords": ["product manager"],
              "time_filter": "last_month",
              "estimated_query": "keywords=product%20manager&f_TPR=r2592000&sortBy=DD"
            },
            "data_to_extract": [ // Same suggested fields for consistency
              "job_title",
              "company_name",
              "location",
              "salary_range",
              "job_description",
              "posted_date",
              "apply_url",
              "employment_type"
            ],
            "requirements": {
              "technical": ["requires_search_capability", "handle_pagination", "requires_login", "date_parsing"],
              "performance": {"timeout_seconds": 90, "max_retries": 1 }
            },
            "metadata": {
               "original_input": "...",
               "inferred_task_type": "job_search",
               "source": "cli_free_text",
               "confidence_score": 0.90
            }
          }
        ]
```
    *   **Output Example 2 (Amazon Search):**
        ```json
        [
          {
            "target": {
              "type": "search_query",
              "source_platform": "Amazon", // Identified platform
              "search_keywords": ["best-selling wireless headphones"], // Main query terms
              "filters": { // Extracted constraints
                "min_rating": 4.0,
                "max_price": 100.0,
                "price_currency": "USD", // LLM might infer or default
                "availability_location": "Montreal store" // Captured location constraint
              },
              "estimated_query": "k=best-selling+wireless+headphones&rh=p_72%3A4-star-up%2Cp_36%3A-10000" // Note: Location filter hard to map to URL param directly
            },
            "data_to_extract": [ // Suggested relevant fields for product search
              "product_title",
              "price",
              "currency",
              "rating_value",
              "review_count",
              "image_url", // Suggested
              "product_url", // Suggested
              "is_bestseller", // Suggested based on query
              "availability_status", // Suggested based on query constraint
              "features" // Suggested
            ],
            "requirements": {
              "technical": ["javascript_rendering", "requires_search_capability", "handle_pagination", "filter_application"], // Filter application is key
              "performance": { "timeout_seconds": 60, "max_retries": 1 }
            },
            "metadata": {
              "original_input": "Find me the best-selling wireless headphones on Amazon with 4+ stars and price under $100 available in a Montreal store",
              "inferred_task_type": "product_search_with_filters",
              "source": "cli_free_text",
              "confidence_score": 0.88
            }
          }
        ]
        ```

### Exposed Interface

*   **Primary Function:**
    ```python
    from typing import Union, Dict, List, Optional
    from .models.specs import IntentSpec
    from .exceptions import IntentParseError
    
    def infer_intent(user_input: Union[str, Dict], trace_name: Optional[str] = None) -> List[IntentSpec]:
        """
        Parses user input into a list of validated IntentSpec objects using LangChain.
    
        Args:
            user_input: The raw request from the user.
            trace_name: Optional name for the LangSmith trace.
    
        Returns:
            A list containing one or more validated IntentSpec objects.
        """
        # ... implementation using LangChain with LangSmith configuration ...
        pass
    ```
    *(Added `trace_name` for better LangSmith organization)*

### Core Logic / Encapsulated Features

1.  **Configuration & Tracing:** Load keys, set up LangSmith env vars. Use `trace_name` if provided.
2.  **LangChain Chain Strategy:**
    *   **Option A (Recommended Start): Generic Chain.** Use a single, powerful prompt template (`generic_intent_prompt.txt`) that guides the LLM to identify task type, extract parameters (URLs, keywords, platforms, filters), suggest fields based on type, handle multiple sources, and structure the output as `List[IntentSpec]` (wrapped in `IntentOutput`).
    *   **Option B (If A struggles only): Router Chain.** Use an `LLMRouterChain` or `MultiPromptChain`. A first LLM call classifies the intent type (job search, product search, local, etc.). Based on the classification, it routes the original input to a *specialized* chain with a prompt tailored for that specific task (e.g., `job_search_prompt.txt`). This improves reliability for distinct task types but adds complexity.
3.  **Chain Definition (`chain_factory.py` or specific files):** Define the chosen chain(s) - Prompt(s), LLM, PydanticOutputParser(`IntentOutput`).
4.  **Core Function (`core.py`):** Invoke the appropriate chain (either the generic one or via the router). Handle parsing errors. Return the validated list.

### Data Structures/Models (`models/specs.py` - Pydantic V2)

*   **Further Refinements for Diversity:**
    *   Add `LocalSearchTargetSpec`, `ContentMonitoringTargetSpec`, etc., to the `TargetSpec = Union[...]` definition.
    *   `LocalSearchTargetSpec` might include fields like `business_type`, `location_query` ("near me", "Montreal"), `required_features` ("open now", "wifi").
    *   `ContentMonitoringTargetSpec` might include `platform` ("Reddit", "Twitter"), `query`, `time_filter`.
    *   Add more potential values to `requirements.technical` like `"local_geo_search"`, `"social_media_api"`.
    *   Ensure the `IntentSpec` can capture the nuances (like filters in the Amazon example) either in `target` or `metadata`.

### Example LangChain Chain Steps (Conceptual - Generic Approach)

1.  **Input:** User query `str`: `"Find pm jobs on indeed last month"`
2.  **Prepare Prompt:** Combine the user query with instructions from `generic_intent_prompt.txt` and the Pydantic format instructions for `IntentOutput`.
3.  **LLM Call:** Send the complete prompt to the configured LLM (e.g., `ChatOpenAI`).
4.  **LLM Response:** Receive a JSON string attempting to match the `IntentOutput` structure.
    ```json
    // LLM attempts to generate this based on prompt
    {
      "intents": [
        {
          "target": {
            "type": "search_query",
            "source_platform": "Indeed",
            "search_keywords": ["product manager"],
            "time_filter": "last_month"
          },
          "data_to_extract": ["job_title", "company_name", "location", "salary_range", "posted_date", "description"], // Suggested
          "requirements": { "technical": ["requires_search_capability", "handle_pagination", "date_parsing"] },
          "metadata": { "inferred_task_type": "job_search" }
        }
      ]
    }
    ```
5.  **Parse Output:** Use `PydanticOutputParser(pydantic_object=IntentOutput).parse(llm_response_string)`
6.  **Validation:** Pydantic automatically validates the parsed `IntentOutput` object and its nested `IntentSpec` list against the schemas.
7.  **Return:** Extract and return the validated `intent_output.intents` list.
8.  **(Parallel) Trace:** LangSmith automatically captures the prompt, response, parsing step, latency, etc., if configured.

### Langflow and Dynamic Connection / Hot Reload

*   **Langflow's Role:** Langflow is primarily a **visual prototyping and design tool**. You build, test, and iterate on chains *within the Langflow UI*.
*   **No Direct Hot Reload:** Langflow **does not** dynamically connect to or hot-reload with your external Python application code (`intent_inference` module). Changes made in your `.py` files won't automatically update a running Langflow graph, and changes in Langflow need to be *exported* (as JSON or Python code snippets) and then *integrated* into your application code manually.
*   **Workflow:**
    1.  Design and rapidly test chain ideas (prompts, models, parsers) in Langflow.
    2.  Once satisfied, export the flow's structure or copy the relevant component configurations (like the prompt template).
    3.  Implement this structure in your Python code within the `chains/` directory.
    4.  Run and test your Python application code, using LangSmith to observe the execution that happens within your *actual application*, not Langflow.

### SequentialChain vs. RouterChain in LangChain

*   **SequentialChain:** Executes a series of chains or steps in a predefined linear order. The output of one step becomes the input for the next.
    *   **Use Case:** Simple, multi-step processes where the order is fixed.
    *   **Example (Not ideal for `intent_inference` itself, but illustrative):**
        1.  `Chain 1 (LLM)`: Extract keywords from user query. -> Output: `{"keywords": ["produtc manager", "indeed", "last month"]}`
        2.  `Chain 2 (Function Call)`: Take `keywords` and format them into a specific Indeed URL structure. -> Output: `{"search_url": "https://indeed.com/..."}`
        *This isn't how `intent_inference` should work (it outputs `IntentSpec`, not just a URL), but demonstrates the linear flow.*
*   **RouterChain:** Dynamically selects the *next* chain to execute based on the input or the result of a preliminary step. Useful for conditional logic or handling different types of input.
    *   **Use Case:** Handling diverse user intents where different processing logic is needed. **This is relevant for `intent_inference` if a single generic prompt proves unreliable.**
    *   **Example (`intent_inference` Router):**
        1.  `Routing Step (LLMRouterChain)`: Analyze user input (`"Find pm jobs..."` vs. `"Get price from URL..."`). -> Output: The *name* of the next chain to run (e.g., `"job_search_chain"` or `"url_analysis_chain"`).
        2.  `Destination Chains`: Have separate chains defined:
            *   `job_search_chain`: Specialized prompt and logic for job searches.
            *   `url_analysis_chain`: Specialized prompt for simple URL scraping intent.
            *   `product_search_chain`: Specialized prompt for product searches.
        3.  The `RouterChain` executes the specific destination chain chosen in Step 1, passing the original user input to it. -> Output: `List[IntentSpec]` from the executed destination chain.

### Generalized Prompts Strategy

*   **Challenge:** Creating a single prompt that reliably handles jobs, products, local search, URLs, monitoring, etc., and outputs the *correct* `TargetSpec` variant and relevant suggested fields is difficult.
*   **Approach 1: Start with a Rich Generic Prompt:**
    *   Design `generic_intent_prompt.txt` with detailed instructions.
    *   Emphasize identifying the **task type**.
    *   Provide examples within the prompt covering different scenarios (few-shot learning).
    *   Instruct the LLM to choose the appropriate `target.type` (`url`, `search_query`, `local_search`, etc.) and populate corresponding fields.
    *   Explicitly ask it to suggest relevant `data_to_extract` fields based on the detected task type.
    *   Use a powerful LLM (like GPT-4).
    *   **Monitor closely with LangSmith.**
*   **Approach 2: Implement Sequential Chain or Router Chain if Needed:**
    *   If the generic prompt struggles with accuracy or mixes up output formats for different tasks (observed via LangSmith evaluation), switch to a `RouterChain` (like `LLMRouterChain` or `MultiPromptChain`).
    *   We will need to go do a first scrape of the website in order to retrive data that will help us analyse the suggested fields and the possible limitation or website spec we need in order to give as an output to the pipeline_builder module.
    *   Create specific prompt templates (`job_search_prompt.txt`, `product_search_prompt.txt`, etc.) tailored to each intent type.
    *   The router first classifies the input, then directs it to the specialized prompt/chain. This generally yields higher accuracy for distinct tasks.

## IV. Implementation Guidance & Roadmap

### Notes for Implementing LLM Coder

*   **Prioritize Free-Text:** Design the core flow around `str` input, as this is the primary user interface. Structured `Dict` input can be handled as a secondary path or converted to a descriptive string for the LLM.
*   **Prompt Engineering (Crucial):** Invest significant effort here. Use the strategies above (generic or router). Provide clear instructions, examples, and specify the *exact* desired output structure (including the `IntentOutput` wrapper and `List[IntentSpec]`). Reference the Pydantic models. Use `output_parser.get_format_instructions()`.
*   **Suggested Fields Logic:** Prompt the LLM: "Based on the inferred task type (e.g., job search, product listing), suggest a comprehensive list of relevant data fields a user would likely want, such as [...examples...]. Include these in the 'data_to_extract' list along with any fields the user explicitly mentioned." **Clarification:** This module *suggests* fields based on context. It does *not* scrape the target page to *find* available fields. That happens later in the workflow.
*   **Pydantic V2 & Unions:** Use the `discriminator` field in the `Union` definition for `TargetSpec` to help Pydantic correctly parse the different target types based on the `type` field generated by the LLM.
*   **Router vs. Generic Prompt Decision:** Start with the generic prompt approach. If testing and LangSmith evaluation reveal frequent errors or inability to handle specific query types correctly, pivot to implementing a `RouterChain`.
*   **LangSmith Utilisation:** Actively use LangSmith. Set meaningful `trace_name`s. Create datasets for evaluation (especially for regression testing prompt changes). Monitor cost, latency, and success rates.

### Task Breakdown / Features to Develop

*   **Phase 1: Setup & Core Components (Generic Approach First)**
    *   `[To_Do_Next]` Setup Env, Pydantic V2 Models (include `SearchTargetSpec`, `URLTargetSpec`, `IntentOutput`), Config Secrets.
    *   `[To_Do]` Implement `chain_factory.py` to build a *generic* chain using `generic_intent_prompt.txt`, `ChatOpenAI`, `PydanticOutputParser(IntentOutput)`.
    *   `[To_Do]` Implement `core.py::infer_intent` calling the generic chain, include `trace_name` pass-through.
    *   `[To_Do]` Implement basic error handling.
    *   `[To_Do]` Write initial tests (Pydantic models, chain structure with mock LLM).
*   **Phase 2: Prompt Refinement & Basic Testing**
    *   `[To_Do]` Develop `generic_intent_prompt.txt` with detailed instructions for handling diverse types (URL, job, product) and field suggestion. Include Pydantic format guidance.
    *   `[To_Do]` Test manually with simple URL, job search, and product search queries via `core.py`.
    *   `[To_Do]` **Observe in LangSmith:** Verify traces, check if LLM follows instructions, identify initial issues.
    *   `[To_Do]` Write integration tests with mocked LLM responses for these core cases.
*   **Phase 3: Handling Diverse Inputs & Robustness**
    *   `[To_Do]` Refine the generic prompt further based on LangSmith observations to handle local search, competitor monitoring, marketplace examples.
    *   `[To_Do]` Add Pydantic models for other target types (`LocalSearchTargetSpec`, etc.) as needed.
    *   `[To_Do]` Implement handling for structured `Dict` input (e.g., convert to string or bypass LLM if simple).
    *   `[To_Do]` **Evaluation:** Create LangSmith datasets with diverse inputs and expected outputs. Run evaluations.
    *   `[To_Do / Decision Point]` **Assess Generic Prompt:** If evaluation shows poor performance on specific intent types, implement **Phase 3B: Router Chain**. Otherwise, continue refining the generic prompt.
    *   `[To_Do]` Add integration tests (including real LLM calls, marked) covering the full range of intended query types.
*   **Phase 3B: Router Chain Implementation (If Needed)**
    *   `[To_Do]` Design the routing logic (`LLMRouterChain` or custom).
    *   `[To_Do]` Create specific prompt templates for each major intent type (`job_search_prompt.txt`, etc.).
    *   `[To_Do]` Update `chain_factory.py` to build the router and destination chains.
    *   `[To_Do]` Update tests and LangSmith evaluations for the router architecture.

### Module-Specific Rules

*   Output **Must** be `List[IntentSpec]` Pydantic V2 objects.
*   LangChain is mandatory; LangSmith tracing must be enabled.
*   The system must attempt to suggest relevant `data_to_extract` fields based on context.
*   Handle a diverse range of user intents beyond simple URL scraping.

### Development Workflow

1.  Configure Env Vars (APIs, LangSmith).
2.  (Optional) Prototype chain ideas in Langflow.
3.  Implement Pydantic V2 models.
4.  Implement generic LangChain pipeline (`chain_factory.py`, `core.py`).
5.  Develop and refine the generic prompt (`prompts/`).
6.  Test with `pytest` (mocked LLM). Observe in LangSmith.
7.  Iteratively improve prompt based on results.
8.  Test with real LLM integration tests.
9.  Create LangSmith datasets and run evaluations.
10. **Decide:** Stick with generic prompt or implement RouterChain based on evaluation results.
11. Finalize implementation based on chosen strategy.

```
```



# Claude Infer_intent langchain plan


When at this module, I will need to prompt for the plan following this recommendation: Use this scraper analyser draft, with the Evaluator in module index, combine both goal into one evaluotor development plan. Also use these possible file strcuture and goals:

## I. Core Purpose & Context

### Description

The `evaluator/` module serves a dual role in "The Brain" project: it assesses and cleans successful scraping outputs while also diagnosing failures and providing intelligent remediation recommendations. Acting as both quality controller and scraping diagnostician, it creates feedback loops that continuously improve the system's extraction capabilities.

### Main Objective

Create a unified evaluation system that validates output quality, cleans and normalizes data, diagnoses failures through page structure analysis, and generates actionable recommendations, enabling a self-improving scraping system that learns from both successes and failures.

### Dependencies

- **Core Dependencies**:
  - `executor/`: For accessing raw scraping results or error details
  - `intent_inference/`: For retrieving the original intent specification to validate against
  - `pipeline_builder/`: For providing pipeline adjustment recommendations
  - `knowledge_base/`: For retrieving and storing learned patterns (optional in V1)
  - `progress_tracker/`: For logging evaluation status and progress
- **External Libraries**:
  - `beautifulsoup4`: For HTML analysis and selector testing
  - `pydantic`: For schema validation of outputs
  - `rich`: For progress visualization in CLI
  - `regex`: For pattern matching in error analysis
  - `lxml`: For advanced HTML/XML parsing

evaluator/
├── __init__.py                     # Public exports
├── data_cleaning/                  # Output cleaning functionality
│   ├── __init__.py
│   ├── html_cleaner.py             # HTML tag removal
│   ├── field_formatter.py          # Type conversion and formatting
│   └── transformers/               # Field-specific transformers
│       ├── __init__.py
│       ├── price_transformer.py    # Price-specific formatting
│       └── text_transformer.py     # Text content cleaning
├── quality/                        # Output quality assessment
│   ├── __init__.py
│   ├── validators.py               # Field validation functions
│   ├── completeness.py             # Checks for missing fields
│   └── scoring.py                  # Overall quality scoring
├── diagnostics/                    # Error analysis functionality
│   ├── __init__.py
│   ├── error_analyzer.py           # Error type identification
│   ├── page_analyzer.py            # HTML structure analysis
│   ├── recommender.py              # Fix recommendation generation
│   └── patterns/                   # Common error patterns
│       ├── __init__.py
│       ├── selector_errors.py      # Selector-related error patterns
│       └── anti_bot_patterns.py    # Anti-bot detection patterns
├── feedback/                       # Feedback loop management
│   ├── __init__.py
│   ├── router.py                   # Routes feedback to appropriate modules
│   └── triggers.py                 # Defines when to trigger feedback
├── models/                         # Data models
│   ├── __init__.py
│   ├── evaluation_result.py        # Output schema for evaluation results
│   ├── analysis_result.py          # Output schema for error analysis
│   └── recommendation.py           # Schema for recommendations
└── utils/                          # Helper utilities
    ├── __init__.py
    ├── html_utils.py               # HTML manipulation helpers
    └── schema_utils.py             # Schema validation helpers

# Module: scrape_analyzer/ - Adding Intelligent Analysis to "The Brain"

## Incorporating the Scrape Analyzer Module

Looking at the CLI user flows, I've identified the need for a module that provides intelligent analysis of scraping errors, page structures, and output quality. This module would be responsible for the diagnostic capabilities demonstrated in user flows like error recovery, selector recommendations, and data cleaning.

### Proposed Position in Module Order

I recommend placing `scrape_analyzer/` as module #9 between `executor/` and `evaluator/`:

```
8. executor/ (P2)
9. scrape_analyzer/ (P2)
10. evaluator/ (P3)
11. knowledge_base/ (P3)
12. aggregator/ (P4)
```

This position makes sense because:
1. It analyzes problems after execution attempts
2. It provides inputs to improve evaluation quality
3. It's more critical than lower-priority modules for user experience

## Module Definition: scrape_analyzer/

- **One-Line Goal:** Diagnose scraping errors, analyze page structures, and suggest intelligent fixes.

- **Encapsulated Features:**
  - **Error Analysis:** Identify specific error types (selector not found, anti-bot detection, timeout) and map them to potential causes.
  - **Page Structure Analysis:** Examine HTML structures to find alternative selectors or extract page patterns.
  - **Fix Suggestion:** Generate actionable recommendations for pipeline adjustments or tool changes.
  - **Output Cleaning Rules:** Create transformation rules for cleaning HTML or reformatting data.
  - **Knowledge Integration:** Reference and update a knowledge base of common errors and solutions.

- **Key CLI Regression Tests:**
  - `brain analyze run_123` (analyze a failed run and suggest fixes)
  - `brain analyze --url https://example.com --target price` (analyze a page to find potential selectors)
  - `brain analyze --output run_123 --check-quality` (check output quality and suggest cleaning rules)

- **Status:** Backlog.

- **Priority Rationale:** Medium Priority (P2) because it significantly improves user experience by making error recovery and debugging accessible to non-technical users, a key differentiator of the platform.

- **Development Completion Note:** Must be fully implemented (error analysis, structure analysis, fix suggestion) and tested before relying on it in higher-level modules. Tests must confirm accurate error diagnosis and actionable recommendations.

- **Dependencies:**
  - Takes input from `executor/` (error reports, page content)
  - May use data from `progress_tracker/` (execution logs)
  - Updates and references `knowledge_base/` for learned patterns
  - Provides recommendations to `pipeline_builder/` for pipeline adjustments

- **Input/Output Specifications:**
  - **Input Example (Error Analysis):** 
    ```json
    {
      "run_id": "123",
      "error": {
        "type": "selector_not_found",
        "selector": ".price-whole",
        "page_url": "https://ebay.com/itm/123456789",
        "page_content": "<!DOCTYPE html>..."
      }
    }
    ```
  
  - **Output Example (Analysis Result):** 
    ```json
    {
      "analysis": {
        "error_type": "selector_not_found",
        "possible_causes": ["Site layout change", "A/B testing variant", "Region-specific layout"],
        "knowledge_base_matches": ["eBay 2023 Q2 layout update"],
        "suggested_selectors": [".s-item__price", ".ux-textspans--BOLD"],
        "confidence": 0.85
      },
      "recommendations": [
        {
          "action": "update_selector",
          "target": "price",
          "new_value": ".s-item__price",
          "command": "brain retry run_123 --adjust-selector price=.s-item__price"
        },
        {
          "action": "change_browser",
          "current": "playwright",
          "suggested": "selenium",
          "command": "brain retry run_123 --browser selenium"
        }
      ]
    }
    ```

- **Additional Test Cases:**
  - Edge Case: Analysis with minimal information (e.g., error but no page content)
  - Error Case: Undefined error type (expect generic troubleshooting steps)
  - Integration Case: Test feedback loop where analysis improves knowledge base

## How Scrape Analyzer Would Work with the Project

### 1. Integration with Executor

When the `executor/` module encounters an error during pipeline execution:

```
❌ Error: Selector '.prcIsum' not found on page
```

It would capture:
- The error type and details
- The pipeline configuration that failed
- The page content at the time of error
- The run context (user intent, site type)

This information would then be passed to `scrape_analyzer/` for diagnosis.

### 2. Analysis Process

The `scrape_analyzer/` would:

1. **Categorize the Error:** Identify it as a selector error, anti-bot measure, timeout, etc.

2. **Query Knowledge Base:** Check for known issues with this site or similar errors:
   ```
   🔍 Knowledge base match: "eBay 2023 Q2 layout update"
   ```

3. **Analyze Page Structure:** Examine the HTML to find potential alternatives:
   ```
   🔄 [####----------] 20% Capturing page snapshot
   🔄 [########------] 40% Identifying page elements
   🔄 [############--] 60% Mapping element hierarchy
   🔄 [################] 80% Searching for price patterns
   🔄 [####################] 100% Generating recommendations
   ```

4. **Generate Recommendations:** Create actionable suggestions with:
   - Clear explanations of what went wrong
   - Specific fixes to try
   - Confidence levels for each suggestion
   - CLI commands for easy implementation

### 3. User Interaction Through CLI

The `cli/` module would present these recommendations to users:

```
💡 Available actions:
  1. analyze - Use scrape_analyzer to analyze page structure and find selectors
  2. retry - Retry with different selector
  3. browser - Try a different browser tool
  4. abort - Cancel this scrape

Choose an action [1-4]: 1
```

When the user chooses "analyze", `scrape_analyzer/` provides detailed insights:

```
ℹ️ Analysis complete:
  - Found potential price selector: '.s-item__price'
  - Detected layout: "New eBay listing page format"
  - Knowledge base match: "eBay 2023 Q2 layout update"
  - Recommendation: Update selector for price
```

### 4. Pipeline Rebuilding

Based on analysis, `scrape_analyzer/` would feed recommendations to `pipeline_builder/` to adjust the pipeline:

```
⚙️ Rebuilding pipeline with updated selectors...
🔄 [########------] 40% Updating extraction parameters
🔄 [################] 80% Reconfiguring parser settings
🔄 [####################] 100% Finalizing updated pipeline
```

### 5. Learning Loop with Knowledge Base

After successful execution, `scrape_analyzer/` would update the knowledge base:

```
💡 The system has learned from this interaction and updated its eBay price selectors for future use.
```

This creates a feedback loop where:
1. Errors trigger analysis
2. Analysis generates fixes
3. Successful fixes update the knowledge base
4. Future pipelines benefit from learned patterns

### 6. Data Quality Enhancement

Beyond error fixing, `scrape_analyzer/` would also help clean and improve output data:

```
📋 What issues do you see with the results?
> The location still has HTML tags and the amenities have some HTML tags too

ℹ️ Analyzing issues with scrape_analyzer...
🔄 [########------] 40% Detecting HTML artifacts
🔄 [############--] 60% Creating cleaning rules
🔄 [################] 80% Generating transformations
🔄 [####################] 100% Validating clean output
```

These cleaning rules would be applied to the current results and stored for future use.

## Implementation Approach

The `scrape_analyzer/` module would leverage:

1. **Pattern Recognition:** Identify common error patterns and site structures

2. **Heuristic Rules:** Apply logic-based approaches for common issues (e.g., try variations of selectors like `.price`, `#price`, `[data-price]`)

3. **LLM Integration:** For complex cases, use LLMs to interpret errors and generate fixes by analyzing HTML structures

4. **Knowledge Management:** Maintain a database of site-specific information, common error patterns, and successful solutions

5. **Transformation Rules:** Define and apply rules for data cleaning and normalization

By adding this intelligent analysis layer between execution and evaluation, "The Brain" would gain the ability to diagnose and self-heal issues, dramatically improving the user experience for non-technical users.

## Conclusion

The `scrape_analyzer/` module would serve as the "diagnostic expert" in "The Brain" ecosystem, providing intelligent analysis that bridges the gap between raw errors and actionable solutions. It would work closely with the `executor/`, `pipeline_builder/`, and `knowledge_base/` modules to create a self-improving scraping system capable of learning from failures and adapting to changing websites.

This capability is demonstrated throughout the user flows where errors don't just fail but lead to intelligent suggestions and automated fixes, creating a much more robust and user-friendly scraping experience.
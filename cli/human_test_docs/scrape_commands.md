# The Brain CLI - Scraping Commands

This document provides step-by-step instructions for testing the scraping functionality, with expected outputs for each command.

## Scraping Commands

### Basic Scraping

Execute a scraping operation with structured arguments:

```bash
python -m cli.app scrape --url https://example.com --extract price,title
```

**Expected Output:**
```
Structured request:
  • Target URL: https://example.com
  • Fields to extract: price, title
  • Technical requirements: html_parsing

⚙️ Building scraping pipeline with pipeline_builder...
🔄 [####----------] 20% Analyzing page requirements
🔄 [########------] 40% Selecting appropriate tools
🔄 [############--] 60% Determining tool compatibility
🔄 [################] 80% Configuring tool parameters
🔄 [####################] 100% Finalizing pipeline

ℹ️ Proposed pipeline:
  • Pipeline ID: pipe_xxxxxxxx
  • Tools:
    1. requests (Reason: Required for content fetching)
    2. beautifulsoup4 (Reason: HTML extraction for specified fields)

Does this pipeline look correct? [Y/n]: Y

🔄 Executing scrape with executor...
🔄 [####----------] 20% Initializing tools
🔄 [########------] 40% Fetching content with requests
🔄 [############--] 60% Processing content with beautifulsoup4
🔄 [################] 80% Extracting data
🔄 [####################] 100% Generating results

✓ Scraping completed successfully
Run ID: run_xxxxxxxx
Execution time: x.xx seconds

Extracted data:
  • price: $49.99
  • title: Sample Product Title
```

### Scraping with JavaScript Support

Execute a scraping operation that requires JavaScript rendering:

```bash
python -m cli.app scrape --url https://amazon.com/some-product --extract price,title --javascript
```

**Expected Output:**
```
Structured request:
  • Target URL: https://amazon.com/some-product
  • Fields to extract: price, title
  • Technical requirements: html_parsing, javascript_rendering

⚙️ Building scraping pipeline with pipeline_builder...
🔄 [####----------] 20% Analyzing page requirements
🔄 [########------] 40% Selecting appropriate tools
🔄 [############--] 60% Determining tool compatibility
🔄 [################] 80% Configuring tool parameters
🔄 [####################] 100% Finalizing pipeline

ℹ️ Proposed pipeline:
  • Pipeline ID: pipe_xxxxxxxx
  • Tools:
    1. playwright (Reason: JavaScript rendering needed)
    2. beautifulsoup4 (Reason: HTML extraction for specified fields)

Does this pipeline look correct? [Y/n]: Y

🔄 Executing scrape with executor...
🔄 [####----------] 20% Initializing tools
🔄 [########------] 40% Fetching content with playwright
🔄 [############--] 60% Processing content with beautifulsoup4
🔄 [################] 80% Extracting data
🔄 [####################] 100% Generating results

✓ Scraping completed successfully
Run ID: run_xxxxxxxx
Execution time: x.xx seconds

Extracted data:
  • price: $49.99
  • title: Sample Product Title
```

### Natural Language Scraping

Execute a scraping operation with a natural language description:

```bash
python -m cli.app scrape "Get the price and title from https://example.com"
```

**Expected Output:**
```
Processing request: Get the price and title from https://example.com
Using intent inference to analyze request...

Inferred intent:
  • Target URL: https://example.com
  • Fields to extract: price, title
  • Technical requirements: html_parsing

⚙️ Building scraping pipeline with pipeline_builder...
🔄 [####----------] 20% Analyzing page requirements
🔄 [########------] 40% Selecting appropriate tools
🔄 [############--] 60% Determining tool compatibility
🔄 [################] 80% Configuring tool parameters
🔄 [####################] 100% Finalizing pipeline

ℹ️ Proposed pipeline:
  • Pipeline ID: pipe_xxxxxxxx
  • Tools:
    1. requests (Reason: Required for content fetching)
    2. beautifulsoup4 (Reason: HTML extraction for specified fields)

Does this pipeline look correct? [Y/n]: Y

🔄 Executing scrape with executor...
🔄 [####----------] 20% Initializing tools
🔄 [########------] 40% Fetching content with requests
🔄 [############--] 60% Processing content with beautifulsoup4
🔄 [################] 80% Extracting data
🔄 [####################] 100% Generating results

✓ Scraping completed successfully
Run ID: run_xxxxxxxx
Execution time: x.xx seconds

Extracted data:
  • price: $49.99
  • title: Sample Product Title
```

### Verbose Output

Get detailed output with --verbose flag:

```bash
python -m cli.app --verbose scrape --url https://example.com --extract title
```

**Expected Output:**
```
Verbose mode enabled
Structured request:
  • Target URL: https://example.com
  • Fields to extract: title
  • Technical requirements: html_parsing

⚙️ Building scraping pipeline with pipeline_builder...
🔄 [####----------] 20% Analyzing page requirements
🔄 [########------] 40% Selecting appropriate tools
🔄 [############--] 60% Determining tool compatibility
🔄 [################] 80% Configuring tool parameters
🔄 [####################] 100% Finalizing pipeline

ℹ️ Proposed pipeline:
  • Pipeline ID: pipe_xxxxxxxx
  • Tools:
    1. requests (Reason: Required for content fetching)
      Config: {'timeout': 10, 'headers': {'User-Agent': 'Mozilla/5.0...'}}
    2. beautifulsoup4 (Reason: HTML extraction for specified fields)
      Config: {'parser': 'html.parser'}
      Selectors:
      • title: title, h1.product-title, h1.title, h1

Does this pipeline look correct? [Y/n]: Y

🔄 Executing scrape with executor...
🔄 [####----------] 20% Initializing tools
🔄 [########------] 40% Fetching content with requests
🔄 [############--] 60% Processing content with beautifulsoup4
🔄 [################] 80% Extracting data
🔄 [####################] 100% Generating results

✓ Scraping completed successfully
Run ID: run_xxxxxxxx
Execution time: x.xx seconds

Extracted data:
  • title: Sample Product Title
```

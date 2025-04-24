# Tool Registry CLI Test Guide

This document provides a comprehensive guide for testing the Tool Registry CLI commands with examples and expected outputs.

## Prerequisites

Before running these commands, ensure that:

1. You're in the project root directory (`/Users/samuelaudette/Documents/code_projects/the-brain-ai-scraper-2`)
2. The virtual environment is activated (`source venv/bin/activate`)
3. The tool definitions have been loaded (if not, run the first command below)

## Available Commands

### 1. Adding Tool Definitions

Load all tool definitions from the `tool_registry/tools` directory:

```bash
find tool_registry/tools -name "*.json" | xargs -I{} python -m tool_registry.cli add {}
```

Expected output:
```
✅ Tool 'beautifulsoup4' added successfully to the registry
✅ Tool 'scraperapi' added successfully to the registry
✅ Tool 'scrapy' added successfully to the registry
✅ Tool 'selenium' added successfully to the registry
✅ Tool 'cloudscraper' added successfully to the registry
✅ Tool 'playwright' added successfully to the registry
✅ Tool 'requests' added successfully to the registry
✅ Tool 'parsel' added successfully to the registry
✅ Tool 'undetected-chromedriver' added successfully to the registry
✅ Tool 'httpx' added successfully to the registry
```

### 2. Listing All Tools

Display all registered tools:

```bash
python -m tool_registry.cli list
```

Expected output:
```
                                                         Tool Registry                                                          
┏━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Name                    ┃ Type             ┃ Execution Mode ┃ Capabilities                                                   ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ beautifulsoup4          │ parser           │ sync           │ html_parsing, xml_parsing, malformed_markup_handling ...       │
│ scraperapi              │ anti_bot_service │ sync           │ proxy_rotation, browser_fingerprinting, cloudflare_bypass ...  │
│ scrapy                  │ framework        │ async          │ crawling, request_management, response_parsing ...             │
│ selenium                │ browser          │ sync           │ javascript_rendering, spa_support, headless_mode ...           │
│ cloudscraper            │ anti_bot_service │ sync           │ cloudflare_bypass, browser_fingerprinting, anti_bot_bypass ... │
│ playwright              │ browser          │ async          │ javascript_rendering, spa_support, headless_mode ...           │
│ requests                │ http_client      │ sync           │ http_request, https_support, cookie_management ...             │
│ parsel                  │ parser           │ sync           │ html_parsing, xml_parsing, css_selectors ...                   │
│ undetected-chromedriver │ browser          │ sync           │ anti_detection, javascript_rendering, headless_mode ...        │
│ httpx                   │ http_client      │ async          │ http_request, https_support, http2_support ...                 │
└─────────────────────────┴──────────────────┴────────────────┴────────────────────────────────────────────────────────────────┘

Total tools: 10
```

### 3. Filtering Tools by Type

Display only tools of a specific type:

```bash
python -m tool_registry.cli list --type browser
```

Expected output:
```
                                                 Tool Registry                                                  
┏━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Name                    ┃ Type    ┃ Execution Mode ┃ Capabilities                                            ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ selenium                │ browser │ sync           │ javascript_rendering, spa_support, headless_mode ...    │
│ playwright              │ browser │ async          │ javascript_rendering, spa_support, headless_mode ...    │
│ undetected-chromedriver │ browser │ sync           │ anti_detection, javascript_rendering, headless_mode ... │
└─────────────────────────┴─────────┴────────────────┴─────────────────────────────────────────────────────────┘

Total tools: 3
```

### 4. Filtering Tools by Capability

Display only tools that have a specific capability:

```bash
python -m tool_registry.cli list --capability javascript_rendering
```

Expected output:
```
                                                 Tool Registry                                                 
┏━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Name                    ┃ Type       ┃ Execution Mode ┃ Capabilities                                        ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ selenium                │ browser    │ sync           │ javascript_rendering, spa_support, headless_mode ... │
│ playwright              │ browser    │ async          │ javascript_rendering, spa_support, headless_mode ... │
│ scrapy                  │ framework  │ async          │ crawling, request_management, javascript_rendering ...│
│ undetected-chromedriver │ browser    │ sync           │ anti_detection, javascript_rendering, headless ...   │
└─────────────────────────┴────────────┴────────────────┴──────────────────────────────────────────────────────┘

Total tools: 4
```

### 5. Checking Compatibility Between Tools

Check if two tools can work together:

```bash
python -m tool_registry.cli check-compat playwright beautifulsoup4
```

Expected output:
```
✅ Compatible: The specified tools can work together in a pipeline
```

Check tools that are not compatible:

```bash
python -m tool_registry.cli check-compat playwright selenium
```

Expected output:
```
❌ Not Compatible: The specified tools cannot work together in a pipeline
```

### 6. Finding Compatible Tools

Find tools of a specific type that are compatible with a given tool:

```bash
python -m tool_registry.cli find-compatible beautifulsoup4 --type browser
```

Expected output:
```
         Tools Compatible with beautifulsoup4         
┏━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━━━┓
┃ Name                    ┃ Type    ┃ Execution Mode ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━━━┩
│ selenium                │ browser │ sync           │
│ playwright              │ browser │ async          │
│ undetected-chromedriver │ browser │ sync           │
└─────────────────────────┴─────────┴────────────────┘

Total compatible tools: 3
```

### 7. Adding a Custom Tool

Create a sample test tool definition:

```bash
echo '{
  "name": "test-tool",
  "description": "A test tool for demonstration purposes",
  "tool_type": "utility",
  "package_name": "test-tool",
  "execution_mode": "sync",
  "capabilities": ["testing"]
}' > test-tool.json

python -m tool_registry.cli add test-tool.json
```

Expected output:
```
✅ Tool 'test-tool' added successfully to the registry
```

### 8. Removing a Tool

Remove a tool from the registry:

```bash
python -m tool_registry.cli remove test-tool
```

Expected output:
```
✅ Tool 'test-tool' removed successfully from the registry
```

### 9. Help Commands

Get general help:

```bash
python -m tool_registry.cli --help
```

Get help for a specific command:

```bash
python -m tool_registry.cli list --help
```

## Troubleshooting

- If you see "No tools found matching the criteria", you need to add tools to the registry first (see step 1)
- The registry stores tools in a persistent file (typically `~/.thebrain/tools.json`), so tools will remain between sessions
- If you need to reset the registry, you can delete the storage file and re-add the tools

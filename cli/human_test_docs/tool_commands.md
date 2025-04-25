# The Brain CLI - Tool Management Commands

This document provides step-by-step instructions for testing the tool management functionality, with expected outputs for each command.

## Tool Management Commands

### List Tools

List all registered tools:

```bash
python -m cli.app tools list
```

**Expected Output:**
```
Found X tools
                                                                      Registered Tools                                                                        
┏━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Name                    ┃ Type             ┃ Capabilities                                           ┃ Compatible With                                       ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ beautifulsoup4          │ parser           │ html_parsing, xml_parsing, malformed_markup_handling,  │ type:browser, type:http_client                        │
│                         │                  │ css_selectors, tag_navigation, attribute_extraction,   │                                                       │
│                         │                  │ text_extraction, encoding_detection                    │                                                       │
└─────────────────────────┴──────────────────┴───────────────────────────────────────────────────────┴───────────────────────────────────────────────────────┘
```

Filter tools by type:

```bash
python -m cli.app tools list --type browser
```

**Expected Output:**
```
Found X browser tools
                                                                      Registered Tools                                                                        
┏━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Name                    ┃ Type             ┃ Capabilities                                           ┃ Compatible With                                       ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ selenium                │ browser          │ javascript_rendering, spa_support, headless_mode,      │ type:parser, type:captcha_solver, type:proxy_manager, │
│                         │                  │ headed_mode, screenshot, network_interception,         │ type:anti_bot_service, undetected-chromedriver        │
│                         │                  │ user_input_simulation, form_submission,                │                                                       │
│                         │                  │ iframe_handling, wait_conditions                       │                                                       │
└─────────────────────────┴──────────────────┴───────────────────────────────────────────────────────┴───────────────────────────────────────────────────────┘
```

### Add Tool

Add a new tool to the registry:

```bash
python -m cli.app tools add \
  --name "test-tool" \
  --description "Test tool for CLI testing" \
  --type "parser" \
  --package "test-package" \
  --capability "html_parsing" \
  --capability "css_selectors"
```

**Expected Output:**
```
✓ Tool 'test-tool' added successfully to registry
```

### Remove Tool

Remove a tool from the registry (with confirmation):

```bash
python -m cli.app tools remove test-tool
```

**Expected Output:**
```
Are you sure you want to remove tool 'test-tool'? [y/N]: y
✓ Tool 'test-tool' removed successfully from registry
```

Force remove without confirmation:

```bash
python -m cli.app tools remove test-tool --force
```

**Expected Output:**
```
✓ Tool 'test-tool' removed successfully from registry
```

### Check Tool Compatibility

Check compatibility between tools:

```bash
python -m cli.app tools check-compat beautifulsoup4 selenium
```

**Expected Output:**
```
✓ Tools 'beautifulsoup4' and 'selenium' are compatible
Compatible because: 
  • 'beautifulsoup4' is compatible with type:browser
  • 'selenium' is of type browser
```

### JSON Output

Get tool list in JSON format:

```bash
python -m cli.app tools list --json
```

**Expected Output:**
```json
[
  {
    "name": "beautifulsoup4",
    "description": "HTML/XML parsing library",
    "tool_type": "parser",
    "package_name": "beautifulsoup4",
    "capabilities": ["html_parsing", "xml_parsing", "css_selectors"],
    "compatibilities": ["type:browser", "type:http_client"]
  },
  ...
]
```

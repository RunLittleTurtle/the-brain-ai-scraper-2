#  Module CLI

# Module Development Plan: cli/

## Status: Backlog - Ready for Implementation

## I. Core Purpose & Context

### Description

The `cli/` module provides a rich, interactive command-line interface for "The Brain" project, acting as the primary interaction point for users to access the system's scraping capabilities. It emphasizes user guidance, context awareness, and visual feedback to make complex scraping tasks accessible.

### Main Objective

Create a sophisticated CLI that provides seamless access to all system functionalities through multiple input styles (structured commands, free-text natural language, and interactive prompts), while maintaining consistent, visually appealing output with strong contextual awareness to guide users throughout their workflow.

### Dependencies

- **Core Dependencies**:
  - `tool_registry/`: For tool management commands and tool information retrieval (AVAILABLE)
  - `config_secrets/`: For secure configuration management and access (AVAILABLE)
  - `progress_tracker/`: For tracking operations status (FUTURE MODULE - REQUIRE MOCKING)
  - `intent_inference/`: For natural language processing (FUTURE MODULE - REQUIRE MOCKING)
  - `pipeline_builder/`: For pipeline creation (FUTURE MODULE - REQUIRE MOCKING)
  - `executor/`: For pipeline execution (FUTURE MODULE - REQUIRE MOCKING)

- **External Libraries**:
  - `typer`: For CLI framework and command routing
  - `rich`: For terminal formatting, progress bars, and tables
  - `prompt_toolkit`/`inquirer`: For interactive prompts and menus
  - `pydantic`: For input validation and schema definitions

### Suggested File Structure

```
cli/
├── __init__.py                # Public exports
├── app.py                     # Main CLI application (Typer app)
├── commands/                  # Command implementations by module
│   ├── __init__.py
│   ├── tool/                  # Tool registry commands
│   │   ├── __init__.py
│   │   ├── list.py
│   │   ├── add.py
│   │   └── check_compat.py
│   ├── config/                # Configuration commands
│   │   ├── __init__.py
│   │   ├── set.py
│   │   └── list.py
│   ├── scrape/                # Scraping commands
│   │   ├── __init__.py
│   │   ├── execute.py
│   │   └── retry.py
│   └── pipeline/              # Pipeline commands
│       ├── __init__.py
│       ├── status.py
│       └── diagnostic.py
├── formatters/                # Output formatting utilities
│   ├── __init__.py
│   ├── json_formatter.py      # JSON output formatting
│   ├── table_formatter.py     # Table formatting for terminal
│   └── progress.py            # Progress indicators
├── interactive/               # Interactive UI components
│   ├── __init__.py
│   ├── prompts.py             # Basic interactive prompts
│   └── menus.py               # Simple menu systems
├── context/                   # Command context tracking
│   ├── __init__.py
│   └── state.py               # Basic state tracking
└── mocks/                     # Mock implementations of future modules
    ├── __init__.py
    ├── mock_intent_inference.py
    ├── mock_pipeline_builder.py
    └── mock_executor.py
```

#### Explanation of each files :File Structure Analysis for CLI Module

##### Critical Components (Must Implement for Phase 1)

1. **`app.py`**
   - **Purpose:** Main entry point and Typer application setup
   - **Criticality:** CRITICAL - This is the foundation of the entire CLI
   - **Implementation:** Sets up the core command structure, global flags, and routing
2. **`__init__.py` (root)**
   - **Purpose:** Module exports and version information
   - **Criticality:** CRITICAL - Required for proper Python module behavior
   - **Implementation:** Exposes key functions and constants for external use
3. **`formatters/json_formatter.py` and `formatters/table_formatter.py`**
   - **Purpose:** Output formatting for structured data
   - **Criticality:** CRITICAL - Required for all command outputs
   - **Implementation:** Converts internal data structures to user-facing outputs
4. **`commands/tool/list.py` and `commands/tool/add.py`**
   - **Purpose:** Core tool management commands
   - **Criticality:** CRITICAL - Required for integration with existing `tool_registry`
   - **Implementation:** Thin wrappers around `tool_registry` functionality
5. **`commands/config/set.py` and `commands/config/list.py`**
   - **Purpose:** Core configuration management commands
   - **Criticality:** CRITICAL - Required for integration with existing `config_secrets`
   - **Implementation:** Thin wrappers around `config_secrets` functionality
6. **`mocks/mock_intent_inference.py`**
   - **Purpose:** Temporary stand-in for future modules
   - **Criticality:** CRITICAL - Enables end-to-end testing from day one
   - **Implementation:** Simple functions that mimic expected behavior of future modules

##### Important Components (Should Implement for Phase 1)

1. **`formatters/progress.py`**
   - **Purpose:** Progress indicators for long-running operations
   - **Criticality:** IMPORTANT - Significantly enhances user experience
   - **Implementation:** Uses `rich.progress` to show dynamic progress bars
2. **`commands/tool/check_compat.py`**
   - **Purpose:** Check compatibility between tools
   - **Criticality:** IMPORTANT - Useful for pipeline planning
   - **Implementation:** Wrapper around `tool_registry` compatibility checking
3. **`commands/config/unset.py`**
   - **Purpose:** Remove configuration values
   - **Criticality:** IMPORTANT - Completes the config management functionality
   - **Implementation:** Wrapper around `config_secrets` unset functionality
4. **`commands/scrape/execute.py`**
   - **Purpose:** Basic scraping command with structured arguments
   - **Criticality:** IMPORTANT - Enables core scraping functionality
   - **Implementation:** Uses mocks for unavailable modules to demonstrate flow
5. **`interactive/prompts.py` (basic version)**
   - **Purpose:** Simple interactive prompts for missing parameters
   - **Criticality:** IMPORTANT - Improves usability when parameters are missing
   - **Implementation:** Simple input prompts for required arguments
6. **`mocks/mock_pipeline_builder.py` and `mocks/mock_executor.py`**
   - **Purpose:** Temporary stand-ins for future scraping modules
   - **Criticality:** IMPORTANT - Enables scraping command testing
   - **Implementation:** Simple mocks returning predefined results

#### Nice-to-Have Components (Can Defer to Later Phases)

1. **`context/state.py`**
   - **Purpose:** Track command state between invocations
   - **Criticality:** NICE-TO-HAVE - Enhances UX but not critical for initial functionality
   - **Implementation:** Simple singleton for tracking last run ID and command history
2. **`commands/pipeline/status.py`**
   - **Purpose:** Check status of running operations
   - **Criticality:** NICE-TO-HAVE - Requires `progress_tracker` module
   - **Implementation:** Will need to integrate with `progress_tracker` when available
3. **`commands/scrape/retry.py`**
   - **Purpose:** Retry failed scrape operations
   - **Criticality:** NICE-TO-HAVE - Requires context tracking
   - **Implementation:** Uses context to find last run ID and retries with adjustments
4. **`interactive/menus.py`**
   - **Purpose:** Advanced multi-option menus
   - **Criticality:** NICE-TO-HAVE - Basic prompts are sufficient for Phase 1
   - **Implementation:** More complex menu system using `prompt_toolkit`
5. **`commands/pipeline/diagnostic.py`**
   - **Purpose:** Advanced troubleshooting for pipelines
   - **Criticality:** NICE-TO-HAVE - Requires integration with multiple future modules
   - **Implementation:** Detailed error analysis and suggestions





## II. Technical Design & Interfaces

### Inputs & Outputs

#### Input Types (Implemented in Phases)

1. **Structured Commands** (Phase 1 - Immediate Implementation)
   ```bash
   brain scrape --url https://amazon.ca/dp/B08WRBGSL2 --extract price,title
   ```

2. **Free-Text Natural Language** (Phase 2 - After `intent_inference` module is available)
   ```bash
   brain scrape "Get price and title from Amazon product page at https://amazon.ca/dp/B08WRBGSL2"
   ```

3. **Interactive Prompts** (Phase 1 for basic prompts, Phase 3 for advanced workflows)
   ```bash
   brain scrape  # Triggers interactive workflow to collect missing parameters
   ```

#### Output Formats

Output is displayed in two possible formats, determined by the `--json` global flag:

1. **Human-Readable Format** (default): Rich, colorful terminal output with tables, progress bars, and emojis
   ```
   ✅ Found 3 tools in registry:
   ┌─────────────┬────────────┬─────────────────────────────┐
   │ Name        │ Type       │ Capabilities                │
   ├─────────────┼────────────┼─────────────────────────────┤
   │ playwright  │ browser    │ javascript_rendering, ...   │
   │ beautifulsoup│ parser    │ html_parsing, ...           │
   │ scrapy      │ crawler    │ pagination, ...             │
   └─────────────┴────────────┴─────────────────────────────┘
   ```

2. **Machine-Readable Format** (with `--json`): Structured JSON for automation
   ```json
   {
     "status": "success",
     "tools": [
       {"name": "playwright", "type": "browser", "capabilities": ["javascript_rendering", "..."]},
       {"name": "beautifulsoup", "type": "parser", "capabilities": ["html_parsing", "..."]},
       {"name": "scrapy", "type": "crawler", "capabilities": ["pagination", "..."]}
     ]
   }
   ```

### Exposed Interface

#### Global Commands and Flags

```
brain [--json] [--verbose] [--help] [--version] <command> [OPTIONS]
```

- `--json`: Output in JSON format for machine readability
- `--verbose`: Enable detailed output and contextual suggestions
- `--help`: Display help information
- `--version`: Show version information

#### Core Subcommands (Implemented in Phases)

1. **Tool Management** (Phase 1 - Immediate Implementation)
   ```
   brain tools list [--json]
   brain tools add <tool_name> [--type=<type>] [--capabilities=<cap1,cap2>] [--compatibilities=<comp1,comp2>]
   brain tools remove <tool_name>
   brain tools check-compat <tool1> <tool2> [<tool3> ...]
   ```

2. **Configuration Management** (Phase 1 - Immediate Implementation)
   ```
   brain config set <key> <value>
   brain config unset <key>
   brain config list [--show-secrets]
   ```

3. **Scraping Operations** (Phase 1 with mocks, Phase 2 with real modules)
   ```
   brain scrape [--url=<url>] [--extract=<fields>] [--jscan=<true|false>] ["free text description"]
   brain retry <run_id> [--adjust-selector=<selector>] [--increase-timeout]
   ```

4. **Pipeline Management** (Phase 2 - After `progress_tracker` is available)
   ```
   brain status <run_id>
   brain diagnostic <run_id>
   brain kill <run_id>
   ```

5. **Advanced Testing Commands** (Phase 3 - After all dependent modules are available)
   ```
   brain infer "free text description" [--json]
   brain dryrun --intent-spec=<json_file> [--show-spec]
   ```

### Core Logic / Encapsulated Features

#### 1. Command Routing and Integration (Phase 1)

The CLI implements thin wrappers around module functionality, making minimal assumptions about internal implementation details. For modules that aren't yet available, mocks provide the necessary behavior to enable end-to-end testing.

```python
# Example thin wrapper for tool_registry
def list_tools(json_output: bool = False) -> str:
    """List all available tools in the registry."""
    try:
        # Call the actual module function - available module
        from tool_registry import ToolRegistry
        registry = ToolRegistry()
        tools = registry.list_tools()
        
        # Format and return results
        if json_output:
            return format_json({"status": "success", "tools": tools})
        else:
            return format_table(tools, title="Available Tools")
    except Exception as e:
        return format_error(str(e), json_output)

# Example with mock for unavailable module
def scrape(url: str, fields: List[str], json_output: bool = False) -> str:
    """Execute a scraping operation with mocked components."""
    try:
        # For now, use mock implementations
        from cli.mocks.mock_pipeline_builder import mock_build_pipeline
        from cli.mocks.mock_executor import mock_execute_pipeline
        
        # Show progress for operations taking > 1 second
        with create_progress_bar("Scraping", 3) as progress:
            # Step 1: Build pipeline (will be real in Phase 2)
            progress.update("Building pipeline...")
            pipeline = mock_build_pipeline(url, fields)
            
            # Step 2: Execute pipeline (will be real in Phase 2)
            progress.update("Executing pipeline...")
            results = mock_execute_pipeline(pipeline)
            
            # Step 3: Format results
            progress.update("Processing results...")
            
        # Format and return results
        if json_output:
            return format_json({"status": "success", "data": results})
        else:
            return format_results(results, title="Scraping Results")
    except Exception as e:
        return format_error(str(e), json_output)
```

#### 2. Progress Indicators (Phase 1)

For any operation taking more than 1 second, the CLI provides visual feedback using progress bars:

```python
# Example progress indicator implementation
def create_progress_bar(task_name, total_steps=1):
    """Create a progress bar for long-running operations."""
    progress = rich.progress.Progress(
        "[progress.description]{task.description}",
        rich.progress.BarColumn(),
        "[progress.percentage]{task.percentage:>3.0f}%",
        " - ",
        "[progress.state]{task.fields[state]}"
    )
    
    task_id = progress.add_task(
        f"🔄 {task_name} in progress...", 
        total=total_steps,
        state="Initializing"
    )
    
    return ProgressContext(progress, task_id)

class ProgressContext:
    """Context manager for progress bars."""
    def __init__(self, progress, task_id):
        self.progress = progress
        self.task_id = task_id
        
    def __enter__(self):
        self.progress.start()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.progress.stop()
        
    def update(self, state, advance=1):
        """Update progress bar state and advance if specified."""
        self.progress.update(self.task_id, advance=advance, state=state)
```

#### 3. Error Handling (Phase 1)

Central error handling with consistent formatting and actionable suggestions:

```python
def format_error(message, json_output=False, suggestions=None):
    """Format error messages with suggested actions."""
    if json_output:
        return json.dumps({
            "status": "error",
            "message": message,
            "suggestions": suggestions or []
        })
    else:
        console = rich.console.Console()
        console.print(f"[bold red]❌ Error:[/] {message}")
        
        if suggestions:
            console.print("\n[bold yellow]💡 Suggested actions:[/]")
            for suggestion in suggestions:
                console.print(f"  - {suggestion}")
        
        return ""  # Console output already handled
```

#### 4. Basic Interactive Elements (Phase 1)

Simple interactive prompts for missing parameters:

```python
def prompt_for_url():
    """Prompt user to enter a URL."""
    return input("📝 Enter URL to scrape: ")

def prompt_for_fields():
    """Prompt user to enter fields to extract."""
    fields_input = input("📋 Enter fields to extract (comma-separated): ")
    return [field.strip() for field in fields_input.split(",") if field.strip()]
```

#### 5. Context Tracking (Phase 2)

Simple state tracking for command history and run IDs:

```python
class CommandContext:
    """Track command state and history."""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CommandContext, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        self.last_run_id = None
        self.command_history = []
        self.verbose = False
        self.json_output = False
    
    def update_run_id(self, run_id):
        """Update the last run ID."""
        self.last_run_id = run_id
    
    def add_command(self, command):
        """Add a command to history."""
        self.command_history.append({
            "command": command,
            "timestamp": datetime.now()
        })
        # Keep only recent history
        if len(self.command_history) > 10:
            self.command_history.pop(0)
```

#### 6. Advanced Natural Language Processing (Phase 2 - After `intent_inference` is available)

Process free-text input by calling the `intent_inference` module:

```python
def process_free_text(text, json_output=False):
    """Process free-text input using intent_inference module."""
    try:
        # This will be mocked initially, then use the real module when available
        from intent_inference import infer_intent
        
        # Show analyzing message
        if not json_output:
            console = rich.console.Console()
            console.print("🧠 Analyzing request...")
        
        # Get intent specification
        intent_spec = infer_intent(text)
        
        # Execute scraping with the inferred intent
        return execute_scrape(
            url=intent_spec.get("target", {}).get("value"),
            fields=intent_spec.get("data_to_extract", []),
            json_output=json_output
        )
    except Exception as e:
        return format_error(str(e), json_output)
```

### Data Structures/Models

#### Core Data Models (Phase 1)

1. **CommandContext**
   ```python
   class CommandContext:
       """Track command state for context-aware features."""
       def __init__(self):
           self.last_run_id = None
           self.verbose = False
           self.json_output = False
           # Limited history in Phase 1
           self.command_history = []
   ```

2. **CommandResult**
   ```python
   class CommandResult:
       """Standardized result structure for all commands."""
       def __init__(self, status, message, data=None, errors=None, suggestions=None):
           self.status = status  # "success", "error", "warning", "info"
           self.message = message
           self.data = data
           self.errors = errors
           self.suggestions = suggestions
   ```

## III. Development & Testing Strategy

### Developer Interaction

#### Adding New Commands

```python
# cli/commands/example/new_command.py
import typer
from typing import Optional
from cli.formatters import format_output

def new_command(
    param: str = typer.Argument(..., help="Description of parameter"),
    json_output: bool = typer.Option(False, "--json", help="Output in JSON format")
):
    """
    Command help text that describes what this command does.
    
    Example usage:
      brain example new-command myvalue
    """
    # Command implementation
    result = {
        "status": "success",
        "message": f"Command executed with {param}",
        "data": {"param": param}
    }
    
    # Format and return output
    return format_output(result, json_output=json_output)

# Register in app.py
from cli.commands.example.new_command import new_command
app.command()(new_command)
```

#### Mocking Future Modules

```python
# cli/mocks/mock_intent_inference.py
def mock_infer_intent(text):
    """Simple mock for the intent_inference module."""
    import re
    
    # Extract URL using regex
    url_match = re.search(r'https?://[^\s]+', text)
    url = url_match.group(0) if url_match else None
    
    # Extract fields based on common terms
    fields = []
    if "price" in text.lower():
        fields.append("price")
    if "title" in text.lower():
        fields.append("title")
    if "description" in text.lower():
        fields.append("description")
    
    # Return mocked intent spec
    return {
        "target": {"type": "url", "value": url},
        "data_to_extract": fields,
        "requirements": {"technical": ["javascript_rendering"]}
    }
```

### Testing Strategy

#### Unit Tests for Core Functionality (Phase 1)

```python
# Test command parsing
def test_parse_structured_command():
    result = parse_command(["scrape", "--url", "https://example.com", "--extract", "price,title"])
    assert result["command"] == "scrape"
    assert result["args"]["url"] == "https://example.com"
    assert result["args"]["extract"] == ["price", "title"]

# Test output formatting
def test_json_output_formatting():
    data = {"status": "success", "data": {"price": "10.99"}}
    result = format_output(data, json_output=True)
    assert '"status": "success"' in result
    assert '"price": "10.99"' in result
```

#### Integration Tests with Available Modules (Phase 1)

```python
# Test tool_registry integration
def test_tools_list_command():
    runner = CliRunner()
    result = runner.invoke(app, ["tools", "list"])
    assert result.exit_code == 0
    assert "Found" in result.stdout

# Test config_secrets integration
def test_config_set_command():
    runner = CliRunner()
    result = runner.invoke(app, ["config", "set", "TEST_KEY", "test_value"])
    assert result.exit_code == 0
    assert "Configuration set" in result.stdout
```

#### Mocked End-to-End Tests (Phase 1)

```python
# Test scraping with mocked components
def test_scrape_command_mocked():
    runner = CliRunner()
    result = runner.invoke(app, ["scrape", "--url", "https://example.com", "--extract", "title"])
    assert result.exit_code == 0
    assert "Scraping in progress" in result.stdout
    assert "Scraping complete" in result.stdout
```

#### Key Regression Tests (All Phases)

1. **Core Command Tests**
   - `brain tools list` returns all registered tools with correct formatting
   - `brain config set TEST_KEY test_value` followed by `brain config list` shows the new key
   - `brain scrape --url https://example.com --extract title` extracts and returns the page title

2. **Input Processing Tests**
   - `brain scrape` without arguments triggers interactive prompts
   - (Phase 2) `brain scrape "Get price from example.com"` correctly processes free-text input

3. **Output Format Tests**
   - `brain tools list` returns human-readable table
   - `brain tools list --json` returns valid, parseable JSON
   - `brain --verbose scrape --url https://example.com` shows detailed progress information

## IV. Implementation Guidance & Roadmap

### Notes for Implementing LLM

1. **Phased Implementation Approach**

   > **IMPORTANT:** Implement the CLI in phases, focusing first on the core functionality with structured commands before adding more advanced features.

   - **Phase 1 (Initial Implementation):** 
     - Set up the basic command structure with Typer
     - Implement thin wrappers around available modules (`tool_registry`, `config_secrets`)
     - Create mocks for unavailable modules
     - Add basic progress indicators and error handling
     - Implement simple interactive prompts for missing parameters
     - Focus on clear, consistent output formatting (both human-readable and JSON)

   - **Phase 2 (After `intent_inference` and other modules are available):**
     - Integrate with real modules as they become available, replacing mocks
     - Implement free-text natural language processing by calling `intent_inference`
     - Add more sophisticated context tracking
     - Enhance error handling with more specific suggestions

   - **Phase 3 (Full Feature Implementation):**
     - Add advanced interactive workflows
     - Implement sophisticated context-aware suggestions
     - Create rich diagnostic and troubleshooting commands
     - Add multi-level menus and detailed progress tracking

2. **Mocking Strategy for Unavailable Modules**

   > **IMPORTANT:** Create simple mock implementations for modules that aren't yet available.

   ```python
   # Example of creating a mock for intent_inference
   def mock_infer_intent(text):
       """Mock implementation of intent_inference module."""
       import re
       
       # Extract URL with regex
       url_match = re.search(r'https?://[^\s]+', text)
       url = url_match.group(0) if url_match else None
       
       # Simple extraction of fields from text
       fields = []
       for field in ["price", "title", "description", "rating"]:
           if field in text.lower():
               fields.append(field)
       
       # Return a structured mock intent
       return {
           "target": {"type": "url", "value": url},
           "data_to_extract": fields,
           "requirements": {"technical": ["javascript_rendering"]}
       }
   ```

3. **Progress Indicators for Operations > 1 Second**

   > **IMPORTANT:** Always show progress indicators for operations that take more than one second.

   ```python
   def long_running_operation():
       """Example of showing progress for long operations."""
       with create_progress_bar("Operation", total_steps=3) as progress:
           # Step 1
           time.sleep(1)  # Simulate work
           progress.update("Processing step 1...")
           
           # Step 2
           time.sleep(1)  # Simulate work
           progress.update("Processing step 2...")
           
           # Step 3
           time.sleep(1)  # Simulate work
           progress.update("Finalizing...")
       
       # Operation complete
       console = rich.console.Console()
       console.print("[bold green]✅ Operation complete![/]")
   ```

4. **Thin Wrapper Pattern**

   > **IMPORTANT:** Implement commands as thin wrappers around module functionality, don't duplicate logic.

   ```python
   def list_tools_wrapper(json_output=False):
       """Thin wrapper around tool_registry.list_tools."""
       try:
           # Call the actual module function
           from tool_registry import ToolRegistry
           registry = ToolRegistry()
           tools = registry.list_tools()
           
           # Format the output appropriately
           result = {
               "status": "success",
               "message": f"Found {len(tools)} tools in registry",
               "data": {"tools": tools}
           }
           
           return format_output(result, json_output=json_output)
       except Exception as e:
           return format_error(str(e), json_output)
   ```

5. **Output Formatting Consistency**

   > **IMPORTANT:** Maintain consistent output formatting across all commands.

   ```python
   def format_output(result, json_output=False):
       """Format command output consistently."""
       if json_output:
           return json.dumps(result)
       else:
           console = rich.console.Console()
           
           # Display status-appropriate message
           if result["status"] == "success":
               console.print(f"[bold green]✅ {result['message']}[/]")
           elif result["status"] == "error":
               console.print(f"[bold red]❌ {result['message']}[/]")
           elif result["status"] == "warning":
               console.print(f"[bold yellow]⚠️ {result['message']}[/]")
           else:
               console.print(f"[bold blue]ℹ️ {result['message']}[/]")
           
           # Display data if available
           if "data" in result and result["data"]:
               if isinstance(result["data"], list):
                   # Display as table if it's a list of dicts
                   if result["data"] and isinstance(result["data"][0], dict):
                       table = format_table(result["data"])
                       console.print(table)
                   else:
                       # Display as simple list
                       for item in result["data"]:
                           console.print(f"  - {item}")
               elif isinstance(result["data"], dict):
                   # Display key-value pairs
                   for key, value in result["data"].items():
                       console.print(f"  - {key}: {value}")
           
           return ""  # Console output already handled
   ```

### Task Breakdown / Features to Develop

#### 1. Core Framework `[Human_Review]`

- ✅ Set up Typer application with global flags (--json, --verbose, --version)
- ✅ Create standard output formatters (human-readable and JSON)
- ✅ Implement basic error handling
- ✅ Set up module directory structure

#### 2. Tool Commands `[Human_Review]`

- ✅ Implement `brain tools list` wrapper around `tool_registry`
- ✅ Implement `brain tools add` wrapper
- ✅ Implement `brain tools remove` wrapper
- ✅ Implement `brain tools check-compat` wrapper

#### 3. Config Commands `[Human_Review]`

- ✅ Implement `brain config set` wrapper around `config_secrets`
- ✅ Implement `brain config list` wrapper
- ✅ Implement `brain config unset` wrapper

#### 4. Basic Scraping `[Human_Review]`

- ✅ Implement `brain scrape` with structured arguments
- ✅ Create mock implementations for future modules (intent_inference, pipeline_builder, executor)
- ✅ Add progress indicator for scraping
- ✅ Implement basic prompts for missing parameters

#### 5. Status Commands [Backlog - After progress_tracker module is available]

- Implement `brain status` with integration to `progress_tracker`
- Implement simple `brain retry` command

#### 6. Natural Language Support [Backlog - After intent_inference module is available]

- Integrate with `intent_inference` module
- Implement free-text processing for scrape command
- Add confirmation prompts for inferred intentions

#### 7. Context Tracking [Backlog]

- Implement command history tracking
- Add run ID tracking for reference in subsequent commands
- Create context-aware command suggestions

#### 8. Advanced Interactive Features [Backlog - After all core modules are available]

- Implement rich interactive menus for complex workflows
- Add detailed diagnostics and error recovery
- Implement advanced progress visualization

### Module-Specific Rules

1. **Mock Management Rules**
   - Create mocks in a dedicated `mocks/` directory
   - Make mocks easily replaceable when real modules become available
   - Document mock limitations clearly

2. **Command Implementation Rules**
   - All commands must support both human-readable and JSON output
   - Long-running operations (>1 second) must show progress indicators
   - All error messages must be actionable
   - Keep commands as thin wrappers around module functionality

3. **Output Formatting Rules**
   - Use consistent styling across all commands
   - Tables must have clear headers and proper alignment
   - Progress indicators should include percentage and status
   - Error messages should be concise and include suggestions when possible

4. **Progressive Enhancement Rules**
   - Start with simple implementations and add complexity later
   - Free-text support depends on `intent_inference` module availability
   - Advanced interactive features depend on all core modules being available

### Development Workflow

1. Begin with the core framework and tool/config commands that can be fully implemented
2. Add basic scraping support with mock implementations
3. Implement simple progress tracking for long-running operations
4. Add basic interactive prompts for missing parameters
5. As other modules become available, replace mocks with real implementations
6. Add more sophisticated features after the core functionality is working reliably
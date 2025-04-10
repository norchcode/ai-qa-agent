# AI QA Agent Repository Structure

This document describes the organization of the AI QA Agent repository.

## Directory Structure

```
ai-qa-agent/
├── config/                 # Configuration files
│   └── default_config.json # Default configuration
├── docs/                   # Documentation
│   ├── api.md              # API documentation
│   ├── file_processing_design.md
│   └── ...
├── src/                    # Source code
│   ├── core/               # Core components
│   ├── tools/              # Testing and analysis tools
│   ├── ui/                 # User interface components
│   └── utils/              # Utility functions and helpers
├── tests/                  # Test files
│   ├── sample_files/       # Sample files for testing
│   └── ...
├── LICENSE                 # License file
├── README.md               # Main documentation
└── requirements.txt        # Project dependencies
```

## Directory Descriptions

### `config/`
Contains configuration files for the application. The `default_config.json` file provides default settings that can be overridden by environment variables or user-specific configurations.

### `docs/`
Contains detailed documentation for the project, including API specifications, design documents, and usage guides.

### `src/`
Contains all source code for the application, organized into subdirectories:

#### `src/core/`
Core components that form the foundation of the application:
- `agent.py` - Main agent implementation
- `controller.py` - Central controller that integrates all tools
- `history_manager.py` - Manages test history and session data
- `llm_integration.py` - Integration with LLM providers

#### `src/tools/`
Testing and analysis tools:
- `android_device.py` - Android device interaction
- `gherkin_translator.py` - Translates between natural language and Gherkin
- `qa_tools_database.py` - Database of QA tools and recommendations
- `report_generator.py` - Generates test reports
- `scrcpy_controller.py` - Controls scrcpy for mobile testing
- `tool_recommender.py` - Recommends appropriate testing tools
- `visual_testing.py` - Visual testing and screenshot analysis

#### `src/ui/`
User interface components:
- `webui_enhanced.py` - Enhanced web UI with unified interface

#### `src/utils/`
Utility functions and helpers:
- `api.py` - API utilities
- `logger.py` - Logging utilities

### `tests/`
Contains test files for the application, including unit tests, integration tests, and sample files for testing.

#### `tests/sample_files/`
Sample files used for testing file upload and processing functionality:
- `natural_language_steps.txt` - Example natural language test steps
- `sample_test_case.feature` - Example Gherkin feature file

## Import Structure

When importing modules in the new structure, use the following pattern:

```python
# Core components
from src.core.controller import AIQAAgentController
from src.core.llm_integration import LLMProvider

# Tools
from src.tools.gherkin_translator import GherkinTranslator
from src.tools.visual_testing import VisualTesting

# UI components
from src.ui.webui_enhanced import start_webui

# Utilities
from src.utils.logger import setup_logging
from src.utils.api import APIClient
```

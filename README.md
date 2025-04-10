# AI QA Agent

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An AI-powered QA automation agent that combines LLM capabilities with traditional testing tools to create, execute, and analyze tests.

## 📋 Table of Contents

- [Features](#-features)
- [Repository Structure](#-repository-structure)
- [Installation](#-installation)
- [Configuration](#-configuration)
  - [Environment Variables](#environment-variables)
  - [Configuration File](#configuration-file)
- [Usage](#-usage)
  - [Web UI](#web-ui)
  - [Unified Interface](#unified-interface)
  - [API Usage](#api-usage)
- [File and Image Processing](#-file-and-image-processing)
- [Mobile Testing](#-mobile-testing)
- [Reporting](#-reporting)
- [LLM Provider Configuration](#-llm-provider-configuration)
- [Development](#-development)
- [License](#-license)
- [Acknowledgements](#-acknowledgements)

## ✨ Features

- 🧠 **LLM Integration**: Support for multiple LLM providers (Groq, OpenAI, Anthropic, Ollama)
- 🤖 **Unified Interface**: Single input prompt to access all tools and functionalities
- 📁 **File Upload**: Support for uploading and processing various file types (images, PDFs, text files)
- 📱 **Mobile Testing**: Appium integration with scrcpy for Android device testing
- 📊 **Visual Testing**: Screenshot comparison, OCR, and UI/UX analysis
- 📝 **Test Generation**: Create test cases from requirements or user stories
- 📂 **File Processing**: Analyze code, extract test cases from documentation
- 🖼️ **Image Analysis**: Compare UI designs with actual implementations
- 📈 **Reporting**: Detailed PDF, interactive HTML, and executive summary reports
- 🔄 **History Tracking**: Persistent storage of test execution history

## 🗂️ Repository Structure

The repository is organized into the following structure:

```
ai-qa-agent/
├── config/                 # Configuration files
│   └── default_config.json # Default configuration
├── docs/                   # Documentation
│   ├── api.md              # API documentation
│   ├── repository_structure.md # File structure documentation
│   └── ...
├── src/                    # Source code
│   ├── core/               # Core components
│   │   ├── agent.py
│   │   ├── controller.py
│   │   ├── history_manager.py
│   │   └── llm_integration.py
│   ├── tools/              # Testing and analysis tools
│   │   ├── android_device.py
│   │   ├── gherkin_translator.py
│   │   ├── qa_tools_database.py
│   │   ├── report_generator.py
│   │   ├── scrcpy_controller.py
│   │   ├── tool_recommender.py
│   │   └── visual_testing.py
│   ├── ui/                 # User interface components
│   │   └── webui_enhanced.py
│   └── utils/              # Utility functions and helpers
│       ├── api.py
│       └── logger.py
├── tests/                  # Test files
│   ├── sample_files/       # Sample files for testing
│   └── ...
├── LICENSE
├── README.md
└── requirements.txt
```

For more details on the repository structure, see [Repository Structure Documentation](docs/repository_structure.md).

## 🚀 Installation

### Prerequisites

- Python 3.10 or higher
- pip (Python package installer)
- For image processing: Tesseract OCR
- For mobile testing: Appium and Android SDK

### Steps

1. Clone the repository:

```bash
git clone https://github.com/norchcode/ai-qa-agent.git
cd ai-qa-agent
```

2. Create and activate a virtual environment (recommended):

```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create a `.env` file (see [Configuration](#-configuration) section)

5. Run the application:

```bash
python -m src.main
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
# LLM Provider Configuration
LLM_PROVIDER=groq  # Options: groq, openai, anthropic, ollama
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=llama3-70b-8192
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4
ANTHROPIC_API_KEY=your_anthropic_api_key
ANTHROPIC_MODEL=claude-3-opus-20240229

# Web UI Configuration
WEBUI_HOST=127.0.0.1
WEBUI_PORT=7788
WEBUI_THEME=Ocean  # Options: Ocean, Soft, Glass, Default

# Browser Configuration
BROWSER_TYPE=chromium  # Options: chromium, firefox, webkit
HEADLESS=false
BROWSER_RESOLUTION=1920,1080

# Report Configuration
REPORT_FORMAT=pdf  # Options: pdf, html, json
REPORT_INCLUDE_SCREENSHOTS=true
REPORT_INCLUDE_VIDEOS=true

# Logging Configuration
LOG_LEVEL=INFO  # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FILE=./logs/ai_qa_agent.log

# Database Configuration
DATABASE_PATH=./data/history.db
```

### Configuration File

Alternatively, you can use the configuration file at `config/default_config.json`:

```json
{
    "llm_provider": "groq",
    "groq_api_key": "",
    "groq_model": "llama3-70b-8192",
    "browser_type": "chromium",
    "headless": false,
    "browser_resolution": "1920,1080",
    "report_format": "pdf",
    "include_screenshots": true,
    "include_videos": true,
    "log_level": "INFO",
    "log_file": "./logs/ai_qa_agent.log",
    "database_path": "./data/history.db"
}
```

Environment variables take precedence over the configuration file.

## 🖥️ Usage

### Web UI

Start the web UI with:

```bash
python -m src.ui.webui_enhanced
```

This will start the Gradio-based web interface at http://127.0.0.1:7788 (or the configured host/port).

### Unified Interface

The AI QA Agent features a unified interface that allows you to interact with all tools through a single input prompt. You can:

- Ask questions about testing
- Analyze test cases by pasting them or uploading files
- Generate tests from requirements descriptions
- Process and analyze images/screenshots
- Compare visual elements

Example prompts:
- "Analyze this test case for quality and coverage"
- "Generate test cases for a user registration form"
- "Compare these two screenshots and highlight the differences"
- "Convert these steps to Gherkin format"

### API Usage

```python
from src.utils.api import aiqa

# Analyze a test case
test_case = """
Feature: Login Functionality
  Scenario: Successful login
    Given I am on the login page
    When I enter valid credentials
    And I click the login button
    Then I should be redirected to the dashboard
"""
analysis = aiqa.analyze_test_case(test_case)
print(f"Quality score: {analysis['quality_score']}")

# Process a file
result = aiqa.process_file("/path/to/requirements.md")
print(result)

# Analyze an image
analysis = aiqa.analyze_image("/path/to/screenshot.png")
print(analysis)

# Use the unified interface
response = aiqa.process_unified_request(
    "Generate test cases for a login form",
    files=[]
)
print(response)
```

## 📊 File and Image Processing

The AI QA Agent supports processing and analyzing various file types and images:

```python
# Analyze a code file
analysis = aiqa.analyze_code_file("/path/to/code.py")

# Extract test cases from a file
test_cases = aiqa.extract_test_cases_from_file("/path/to/requirements.md")

# Compare UI design with actual implementation
comparison = aiqa.compare_ui_with_design(
    "/path/to/design.png",
    "/path/to/screenshot.png"
)
```

See [File and Image Processing Documentation](docs/file_image_processing.md) for more details.

## 📱 Mobile Testing

The AI QA Agent integrates with Appium and scrcpy for mobile testing:

```python
from src.tools.android_device import AndroidDevice

# Initialize device
device = AndroidDevice()

# Start Appium session
device.start_session()

# Perform test actions
device.tap_element("id:login_button")
device.input_text("id:username_field", "testuser")

# Take screenshot
device.take_screenshot("/path/to/screenshot.png")

# End session
device.end_session()
```

## 📈 Reporting

Generate comprehensive test reports:

```python
from src.tools.report_generator import ReportGenerator

# Initialize report generator
report_gen = ReportGenerator()

# Generate PDF report
report_gen.generate_pdf_report(
    test_results,
    "/path/to/report.pdf",
    template="detailed"
)

# Generate HTML report
report_gen.generate_html_report(
    test_results,
    "/path/to/report.html"
)
```

## 🧠 LLM Provider Configuration

Configure different LLM providers:

```python
# Change LLM provider
aiqa.change_llm_provider("openai", api_key="your-api-key")

# Get available providers
providers = aiqa.get_available_providers()
print(f"Available providers: {providers}")

# Get current provider
current = aiqa.get_current_provider()
print(f"Current provider: {current}")
```

## 🛠️ Development

### Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_file_image_processing.py

# Run with coverage
pytest tests/ --cov=src/ --cov-report=term
```

### Building Documentation

```bash
# Install documentation dependencies
pip install mkdocs mkdocs-material

# Build documentation
mkdocs build

# Serve documentation locally
mkdocs serve
```

### Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgements

- [Groq](https://groq.com/) for their LLM API
- [OpenAI](https://openai.com/) for their GPT models
- [Anthropic](https://www.anthropic.com/) for their Claude models
- [Gradio](https://gradio.app/) for the web UI framework
- [Appium](https://appium.io/) for mobile testing capabilities
- [scrcpy](https://github.com/Genymobile/scrcpy) for Android device mirroring
- [OpenCV](https://opencv.org/) for image processing capabilities
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) for text extraction from images

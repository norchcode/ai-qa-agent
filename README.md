# AI QA Agent

[![CI Status](https://github.com/norchcode/ai-qa-agent/workflows/AI%20QA%20Agent%20CI/badge.svg)](https://github.com/yourusername/ai-qa-agent/actions)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An AI-powered QA automation agent that combines LLM capabilities with traditional testing tools to create, execute, and analyze tests.

## ✨ Features

- 🧠 **LLM Integration**: Support for multiple LLM providers (Groq, Hyperbolic.xyz, Ollama, LM Studio)
- 📱 **Mobile Testing**: Appium integration with scrcpy for Android device testing
- 📊 **Visual Testing**: Screenshot comparison, OCR, and UI/UX analysis
- 📝 **Test Generation**: Create test cases from requirements or user stories
- 📂 **File Processing**: Analyze code, extract test cases from documentation
- 🖼️ **Image Analysis**: Compare UI designs with actual implementations
- 📈 **Reporting**: Detailed PDF, interactive HTML, and executive summary reports
- 🔄 **History Tracking**: Persistent storage of test execution history

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/ai-qa-agent.git
cd ai-qa-agent

# Install dependencies
pip install -r requirements.txt

# Install additional dependencies for image processing
pip install pillow opencv-python-headless pytesseract
```

### Basic Usage

```python
from src.api import aiqa

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

# Start the web UI
aiqa.start_webui()
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
from src.appium_device import AppiumDevice

# Initialize device
device = AppiumDevice()

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
from src.report_generator import ReportGenerator

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
aiqa.change_llm_provider("hyperbolic", api_key="your-api-key")

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

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgements

- [Groq](https://groq.com/) for their LLM API
- [Appium](https://appium.io/) for mobile testing capabilities
- [scrcpy](https://github.com/Genymobile/scrcpy) for Android device mirroring
- [OpenCV](https://opencv.org/) for image processing capabilities
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) for text extraction from images

---
title: API Documentation
---

# AI QA Agent API Reference

This document provides detailed information about the AI QA Agent's API, including classes, methods, and usage examples.

## Core Modules

### TestSession

The `TestSession` class is the main entry point for using the AI QA Agent. It manages test execution, history tracking, and reporting.

```python
class TestSession:
    def __init__(self, name, config=None):
        """
        Initialize a new test session.
        
        Args:
            name (str): Name of the test session
            config (dict, optional): Configuration dictionary
        """
        
    def run_tests(self, test_path, test_type=None):
        """
        Run tests from the specified path.
        
        Args:
            test_path (str): Path to test files or directory
            test_type (str, optional): Test type (unit, integration, visual, mobile)
        
        Returns:
            TestResult: Object containing test results
        """
        
    def compare_with_previous(self, previous_session_id):
        """
        Compare current test session with a previous one.
        
        Args:
            previous_session_id (str): ID of the previous session to compare with
            
        Returns:
            ComparisonResult: Object containing comparison results
        """
        
    def generate_report(self, output_path, report_type="pdf"):
        """
        Generate a report for the test session.
        
        Args:
            output_path (str): Path to save the report
            report_type (str): Type of report (pdf, html, executive)
            
        Returns:
            str: Path to the generated report
        """
        
    def export_data(self, output_path, format="json"):
        """
        Export test session data.
        
        Args:
            output_path (str): Path to save the exported data
            format (str): Export format (json, csv)
            
        Returns:
            str: Path to the exported data
        """
```

### HistoryManager

The `HistoryManager` class provides functionality for managing test execution history.

```python
class HistoryManager:
    def __init__(self, db_path=None):
        """
        Initialize the history manager.
        
        Args:
            db_path (str, optional): Path to the SQLite database
        """
        
    def save_session(self, session):
        """
        Save a test session to the history database.
        
        Args:
            session (TestSession): The test session to save
            
        Returns:
            str: ID of the saved session
        """
        
    def get_session(self, session_id):
        """
        Retrieve a test session from the history database.
        
        Args:
            session_id (str): ID of the session to retrieve
            
        Returns:
            TestSession: The retrieved test session
        """
        
    def list_sessions(self, filters=None):
        """
        List test sessions matching the specified filters.
        
        Args:
            filters (dict, optional): Filters to apply
            
        Returns:
            list: List of matching test sessions
        """
        
    def delete_session(self, session_id):
        """
        Delete a test session from the history database.
        
        Args:
            session_id (str): ID of the session to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        
    def cleanup_old_sessions(self, days=30):
        """
        Delete sessions older than the specified number of days.
        
        Args:
            days (int): Number of days
            
        Returns:
            int: Number of deleted sessions
        """
```

### AndroidDevice

The `AndroidDevice` class provides functionality for interacting with Android devices.

```python
class AndroidDevice:
    def __init__(self, device_id=None):
        """
        Initialize a new Android device.
        
        Args:
            device_id (str, optional): Device ID (uses first available device if None)
        """
        
    def start_app(self, package_name, activity_name=None):
        """
        Start an app on the device.
        
        Args:
            package_name (str): Package name of the app
            activity_name (str, optional): Activity name to start
        """
        
    def stop_app(self, package_name):
        """
        Stop an app on the device.
        
        Args:
            package_name (str): Package name of the app
        """
        
    def take_screenshot(self, output_path):
        """
        Take a screenshot of the device.
        
        Args:
            output_path (str): Path to save the screenshot
            
        Returns:
            str: Path to the saved screenshot
        """
        
    def start_recording(self, output_path):
        """
        Start screen recording.
        
        Args:
            output_path (str): Path to save the recording
        """
        
    def stop_recording(self):
        """
        Stop screen recording.
        
        Returns:
            str: Path to the saved recording
        """
        
    def execute_adb_command(self, command):
        """
        Execute an ADB command on the device.
        
        Args:
            command (str): ADB command to execute
            
        Returns:
            str: Command output
        """
```

### AppiumDevice

The `AppiumDevice` class extends `AndroidDevice` with Appium-specific functionality.

```python
class AppiumDevice(AndroidDevice):
    def __init__(self, device_id=None, appium_server_url=None):
        """
        Initialize a new Appium device.
        
        Args:
            device_id (str, optional): Device ID
            appium_server_url (str, optional): URL of the Appium server
        """
        
    def find_element(self, locator_type, locator_value):
        """
        Find an element on the screen.
        
        Args:
            locator_type (str): Type of locator (id, xpath, etc.)
            locator_value (str): Value of the locator
            
        Returns:
            Element: The found element
        """
        
    def tap(self, x, y):
        """
        Tap at the specified coordinates.
        
        Args:
            x (int): X coordinate
            y (int): Y coordinate
        """
        
    def swipe(self, start_x, start_y, end_x, end_y, duration=None):
        """
        Swipe from one point to another.
        
        Args:
            start_x (int): Starting X coordinate
            start_y (int): Starting Y coordinate
            end_x (int): Ending X coordinate
            end_y (int): Ending Y coordinate
            duration (int, optional): Duration of the swipe in milliseconds
        """
        
    def input_text(self, element, text):
        """
        Input text into an element.
        
        Args:
            element (Element): The element to input text into
            text (str): The text to input
        """
        
    def wait_for_element(self, locator_type, locator_value, timeout=30):
        """
        Wait for an element to be visible.
        
        Args:
            locator_type (str): Type of locator
            locator_value (str): Value of the locator
            timeout (int, optional): Timeout in seconds
            
        Returns:
            Element: The found element
        """
```

### VisualTesting

The `VisualTesting` class provides functionality for visual testing.

```python
class VisualTesting:
    def __init__(self, config=None):
        """
        Initialize the visual testing module.
        
        Args:
            config (dict, optional): Configuration dictionary
        """
        
    def compare_screenshots(self, baseline_path, current_path, diff_output_path=None):
        """
        Compare two screenshots and generate a diff image.
        
        Args:
            baseline_path (str): Path to the baseline screenshot
            current_path (str): Path to the current screenshot
            diff_output_path (str, optional): Path to save the diff image
            
        Returns:
            dict: Comparison results including similarity score
        """
        
    def extract_text(self, image_path, lang='eng'):
        """
        Extract text from an image using OCR.
        
        Args:
            image_path (str): Path to the image
            lang (str, optional): Language code for OCR
            
        Returns:
            str: Extracted text
        """
        
    def generate_heatmap(self, interaction_data, screenshot_path, output_path):
        """
        Generate a heatmap visualization of user interactions.
        
        Args:
            interaction_data (dict or str): User interaction data or path to JSON file
            screenshot_path (str): Path to the screenshot
            output_path (str): Path to save the heatmap
            
        Returns:
            str: Path to the generated heatmap
        """
        
    def detect_ui_elements(self, image_path):
        """
        Detect UI elements in an image.
        
        Args:
            image_path (str): Path to the image
            
        Returns:
            list: Detected UI elements with coordinates and types
        """
```

### EnhancedTestCaseAnalyzer

The `EnhancedTestCaseAnalyzer` class provides functionality for analyzing test cases.

```python
class EnhancedTestCaseAnalyzer:
    def __init__(self, llm_provider="groq"):
        """
        Initialize the enhanced test case analyzer.
        
        Args:
            llm_provider (str): The LLM provider to use for analysis
        """
        
    def parse_gherkin(self, gherkin_text):
        """
        Parse Gherkin text into a structured format.
        
        Args:
            gherkin_text (str): The Gherkin text to parse
            
        Returns:
            dict: Parsed Gherkin structure
        """
        
    def analyze_test_case(self, test_case, coverage_data=None, 
                         execution_history=None, code_changes=None):
        """
        Analyze a test case with enhanced metrics and risk assessment.
        
        Args:
            test_case (str): The test case to analyze, in Gherkin format
            coverage_data (dict, optional): Code coverage data
            execution_history (list, optional): Previous execution results
            code_changes (dict, optional): Information about recent code changes
            
        Returns:
            dict: Comprehensive analysis results
        """
        
    def suggest_improvements(self, test_case, execution_results=None,
                            coverage_data=None):
        """
        Suggest comprehensive improvements for a test case.
        
        Args:
            test_case (str): The test case in Gherkin format
            execution_results (dict, optional): Test execution results
            coverage_data (dict, optional): Code coverage data
            
        Returns:
            dict: Suggested improvements
        """
        
    def optimize_test_case(self, test_case, improvement_suggestions=None):
        """
        Optimize a test case based on analysis and suggestions.
        
        Args:
            test_case (str): The test case in Gherkin format
            improvement_suggestions (dict, optional): Improvement suggestions
            
        Returns:
            str: Optimized test case in Gherkin format
        """
        
    def analyze_error(self, error_message, test_step, screenshot_path=None,
                     execution_context=None):
        """
        Analyze an error that occurred during test execution.
        
        Args:
            error_message (str): The error message
            test_step (str): The test step that failed
            screenshot_path (str, optional): Path to a screenshot
            execution_context (dict, optional): Additional context
            
        Returns:
            dict: Error analysis and suggested fixes
        """
```

### ReportGenerator

The `ReportGenerator` class provides functionality for generating test reports.

```python
class ReportGenerator:
    def __init__(self, config=None):
        """
        Initialize the report generator.
        
        Args:
            config (dict, optional): Configuration dictionary
        """
        
    def generate_pdf_report(self, test_results, output_path, template="detailed"):
        """
        Generate a PDF report.
        
        Args:
            test_results (TestResult): Test results to include in the report
            output_path (str): Path to save the report
            template (str, optional): Template to use (detailed, summary, executive)
            
        Returns:
            str: Path to the generated report
        """
        
    def generate_html_report(self, test_results, output_path):
        """
        Generate an interactive HTML report.
        
        Args:
            test_results (TestResult): Test results to include in the report
            output_path (str): Path to save the report
            
        Returns:
            str: Path to the generated report
        """
        
    def generate_executive_report(self, test_results, output_path):
        """
        Generate an executive summary report.
        
        Args:
            test_results (TestResult): Test results to include in the report
            output_path (str): Path to save the report
            
        Returns:
            str: Path to the generated report
        """
```

### LLMIntegration

The `LLMIntegration` class provides functionality for integrating with LLM providers.

```python
class LLMIntegration:
    def __init__(self, provider="groq", api_key=None, config=None):
        """
        Initialize the LLM integration.
        
        Args:
            provider (str): LLM provider name
            api_key (str, optional): API key for the provider
            config (dict, optional): Additional configuration
        """
        
    def analyze_test_case(self, test_case):
        """
        Analyze a test case using the LLM.
        
        Args:
            test_case (str): The test case to analyze
            
        Returns:
            dict: Analysis results
        """
        
    def generate_completion(self, prompt, system_prompt=None):
        """
        Generate a completion using the LLM.
        
        Args:
            prompt (str): The prompt to send to the LLM
            system_prompt (str, optional): System prompt for context
            
        Returns:
            str: Generated completion
        """
        
    def analyze_error(self, error_message, test_step, screenshot_path=None):
        """
        Analyze an error using the LLM.
        
        Args:
            error_message (str): The error message
            test_step (str): The test step that failed
            screenshot_path (str, optional): Path to a screenshot
            
        Returns:
            dict: Error analysis
        """
        
    def suggest_test_improvements(self, test_case, execution_results):
        """
        Suggest improvements for a test case using the LLM.
        
        Args:
            test_case (str): The test case to improve
            execution_results (dict): Results from test execution
            
        Returns:
            list: Suggested improvements
        """
```

## Utility Modules

### CodeCoverageAnalyzer

The `CodeCoverageAnalyzer` class provides functionality for analyzing code coverage data.

```python
class CodeCoverageAnalyzer:
    def parse_coverage_xml(self, xml_path):
        """
        Parse code coverage data from a Cobertura XML file.
        
        Args:
            xml_path (str): Path to the Cobertura XML file
            
        Returns:
            dict: Parsed coverage data
        """
        
    def parse_coverage_json(self, json_path):
        """
        Parse code coverage data from a JSON file.
        
        Args:
            json_path (str): Path to the JSON coverage file
            
        Returns:
            dict: Parsed coverage data
        """
        
    def analyze_coverage(self, coverage_data):
        """
        Analyze code coverage data to identify areas for improvement.
        
        Args:
            coverage_data (dict): Parsed coverage data
            
        Returns:
            dict: Analysis results
        """
        
    def suggest_test_cases(self, coverage_data, source_code=None):
        """
        Suggest test cases to improve code coverage.
        
        Args:
            coverage_data (dict): Parsed coverage data
            source_code (str, optional): Source code to analyze
            
        Returns:
            list: Suggested test cases
        """
```

### RiskAssessment

The `RiskAssessment` class provides functionality for assessing risk and prioritizing test cases.

```python
class RiskAssessment:
    def assess_risk(self, test_case, execution_history=None, code_changes=None):
        """
        Assess the risk level of a test case.
        
        Args:
            test_case (dict): The test case data
            execution_history (list, optional): Previous execution results
            code_changes (dict, optional): Information about recent code changes
            
        Returns:
            dict: Risk assessment results
        """
        
    def prioritize_test_cases(self, test_cases):
        """
        Prioritize test cases based on risk assessment.
        
        Args:
            test_cases (list): List of test cases with risk assessments
            
        Returns:
            list: Prioritized list of test cases
        """
        
    def generate_test_plan(self, prioritized_test_cases, time_budget=None):
        """
        Generate a test execution plan based on prioritized test cases.
        
        Args:
            prioritized_test_cases (list): Prioritized list of test cases
            time_budget (int, optional): Time budget in minutes
            
        Returns:
            dict: Test execution plan
        """
```

## Configuration

### Environment Variables

The AI QA Agent supports the following environment variables:

- `AI_QA_AGENT_CONFIG_PATH`: Path to the configuration file
- `AI_QA_AGENT_DB_PATH`: Path to the SQLite database
- `AI_QA_AGENT_LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)
- `AI_QA_AGENT_LLM_PROVIDER`: Default LLM provider
- `AI_QA_AGENT_LLM_API_KEY`: API key for the LLM provider
- `AI_QA_AGENT_APPIUM_URL`: URL of the Appium server

### Configuration File

The AI QA Agent can be configured using a YAML configuration file. Example:

```yaml
# General configuration
general:
  log_level: INFO
  db_path: /path/to/database.db
  
# LLM configuration
llm:
  provider: groq
  api_key: your-api-key
  
# Appium configuration
appium:
  server_url: http://localhost:4723
  
# Visual testing configuration
visual:
  similarity_threshold: 0.95
  
# Reporting configuration
reporting:
  default_format: pdf
  logo_path: /path/to/logo.png
```

## Advanced Usage

### Custom Test Runners

You can create custom test runners by extending the `TestRunner` class:

```python
from ai_qa_agent import TestRunner

class CustomTestRunner(TestRunner):
    def __init__(self, config=None):
        super().__init__(config)
        # Custom initialization
        
    def setup(self):
        # Custom setup logic
        
    def run(self, test_path):
        # Custom test execution logic
        
    def teardown(self):
        # Custom teardown logic
```

### Custom Report Templates

You can create custom report templates by extending the `ReportTemplate` class:

```python
from ai_qa_agent import ReportTemplate

class CustomReportTemplate(ReportTemplate):
    def __init__(self, config=None):
        super().__init__(config)
        # Custom initialization
        
    def generate(self, test_results, output_path):
        # Custom report generation logic
```

### Integration with External Systems

The AI QA Agent can be integrated with external systems using the provided APIs:

```python
from ai_qa_agent import TestSession, HistoryManager

# Initialize components
history_manager = HistoryManager()
session = TestSession("Integration Test")

# Run tests
results = session.run_tests("tests/")

# Save results to history
session_id = history_manager.save_session(session)

# Generate report
report_path = session.generate_report("report.pdf")

# Export results to external system
import requests

response = requests.post(
    "https://your-external-system.com/api/test-results",
    json={
        "session_id": session_id,
        "results": results.to_dict(),
        "report_url": f"file://{report_path}"
    }
)
```

## Error Handling

The AI QA Agent provides several exception classes for error handling:

- `AIQAAgentError`: Base exception class
- `ConfigurationError`: Error in configuration
- `TestExecutionError`: Error during test execution
- `DeviceConnectionError`: Error connecting to a device
- `LLMProviderError`: Error communicating with an LLM provider
- `ReportGenerationError`: Error generating a report

Example error handling:

```python
from ai_qa_agent import TestSession, TestExecutionError, DeviceConnectionError

try:
    session = TestSession("Error Handling Test")
    session.run_tests("tests/")
except DeviceConnectionError as e:
    print(f"Device connection error: {e}")
    # Attempt to reconnect or use a different device
except TestExecutionError as e:
    print(f"Test execution error: {e}")
    # Log the error and continue with other tests
except Exception as e:
    print(f"Unexpected error: {e}")
    # Log the error and abort
```

## Performance Considerations

For optimal performance, consider the following:

- Use the `parallel` option to run tests in parallel when possible
- Use the `headless` option for UI tests when visual verification is not needed
- Use the `skip_screenshots` option to disable automatic screenshots during test execution
- Use the `minimal_logging` option to reduce log output
- Use the `cache_results` option to cache test results for faster reporting

Example:

```python
session = TestSession(
    "Performance Test",
    config={
        "parallel": True,
        "headless": True,
        "skip_screenshots": True,
        "minimal_logging": True,
        "cache_results": True
    }
)
```

## Security Considerations

When using the AI QA Agent, consider the following security best practices:

- Store API keys in environment variables or a secure vault, not in code
- Use the `sanitize_logs` option to remove sensitive information from logs
- Use the `secure_storage` option to encrypt stored test results
- Use the `secure_reports` option to password-protect generated reports
- Regularly update dependencies to address security vulnerabilities

Example:

```python
session = TestSession(
    "Secure Test",
    config={
        "sanitize_logs": True,
        "secure_storage": True,
        "secure_reports": True,
        "report_password": "your-secure-password"
    }
)
```

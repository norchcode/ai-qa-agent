# AI QA Agent Documentation

## Overview

The AI QA Agent is an advanced automated testing framework that leverages Large Language Models (LLMs) to enhance the quality assurance process. This tool combines traditional testing methodologies with AI capabilities to provide intelligent test generation, execution, analysis, and reporting.

## Features

### QA Tools Integration
- Comprehensive database of QA tools with detailed information
- Intelligent tool recommendation system based on test requirements
- Links to documentation and resources for each tool

### Memory and History Saving
- Persistent storage system for test execution history
- Session tracking for test runs
- Query interface for retrieving historical test data
- Comparison functionality between test runs
- Data retention policies and cleanup
- Data export functionality (CSV, JSON)
- Visualization for test history trends
- User interface for history browsing

### Appium Integration with scrcpy
- Appium server management
- Appium driver integration with AndroidDevice class
- scrcpy module for Android device mirroring
- Device management functionality
- Screenshot and recording capabilities for mobile tests
- Touch action simulation for Android testing
- Appium-specific test helpers and utilities
- Element identification and interaction via Appium
- Mobile-specific test reporting
- Sample Appium test templates

### Visual Testing Enhancements
- Screenshot comparison functionality using structural similarity index (SSIM)
- OCR capabilities for text extraction from screenshots
- Visual heatmaps for UI/UX analysis
- Enhanced UI element detection with computer vision techniques

### Reporting Enhancements
- Detailed PDF report templates
- Interactive HTML reports with drill-down capabilities
- Executive summary reports for management
- Support for charts, tables, and embedded screenshots

### LLM Provider Extensions
- Support for multiple LLM providers (Groq, Hyperbolic.xyz, Ollama, LM Studio)
- Provider selection UI in the web interface
- Performance comparison between different LLM providers
- Abstraction layer for provider switching

### Test Case Analysis Improvements
- Enhanced test case analysis with detailed metrics
- Code coverage analysis integration
- Test case prioritization based on risk assessment

### CI/CD Integration
- GitHub Actions integration
- Jenkins pipeline support
- Docker container for easy deployment

## Installation

### Prerequisites
- Python 3.10 or higher
- Node.js 18 or higher (for Appium)
- Docker (optional, for containerized deployment)

### Standard Installation
```bash
# Clone the repository
git clone https://github.com/yourusername/ai-qa-agent.git
cd ai-qa-agent

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Appium (optional, for mobile testing)
npm install -g appium
npm install -g appium-uiautomator2-driver
```

### Docker Installation
```bash
# Build the Docker image
docker build -t ai-qa-agent .

# Run the container
docker run -p 5000:5000 -p 4723:4723 ai-qa-agent
```

## Usage

### Basic Usage
```python
from ai_qa_agent import TestSession

# Create a new test session
session = TestSession(name="Example Test Run")

# Run tests
session.run_tests("path/to/tests")

# Generate report
session.generate_report("report.pdf")
```

### Using the Web Interface
```bash
# Start the web server
python app.py

# Access the web interface at http://localhost:5000
```

### Using with CI/CD
The AI QA Agent includes ready-to-use configurations for GitHub Actions and Jenkins:

- GitHub Actions: `.github/workflows/ci.yml`
- Jenkins: `Jenkinsfile`

## API Reference

### TestSession

```python
class TestSession:
    """Manages a test execution session."""
    
    def __init__(self, name, config=None):
        """
        Initialize a new test session.
        
        Args:
            name: Name of the test session
            config: Optional configuration dictionary
        """
        pass
    
    def run_tests(self, test_path, test_type=None):
        """
        Run tests from the specified path.
        
        Args:
            test_path: Path to test files or directory
            test_type: Optional test type (unit, integration, visual, mobile)
        
        Returns:
            TestResult object
        """
        pass
    
    def generate_report(self, output_path, report_type="pdf"):
        """
        Generate a report for the test session.
        
        Args:
            output_path: Path to save the report
            report_type: Type of report (pdf, html, executive)
        
        Returns:
            Path to the generated report
        """
        pass
```

### AndroidDevice

```python
class AndroidDevice:
    """Manages an Android device for testing."""
    
    def __init__(self, device_id=None):
        """
        Initialize a new Android device.
        
        Args:
            device_id: Optional device ID (uses first available device if None)
        """
        pass
    
    def start_app(self, package_name, activity_name=None):
        """
        Start an app on the device.
        
        Args:
            package_name: Package name of the app
            activity_name: Optional activity name to start
        """
        pass
    
    def take_screenshot(self, output_path):
        """
        Take a screenshot of the device.
        
        Args:
            output_path: Path to save the screenshot
        
        Returns:
            Path to the saved screenshot
        """
        pass
    
    def start_recording(self, output_path):
        """
        Start screen recording.
        
        Args:
            output_path: Path to save the recording
        """
        pass
    
    def stop_recording(self):
        """
        Stop screen recording.
        
        Returns:
            Path to the saved recording
        """
        pass
```

### EnhancedTestCaseAnalyzer

```python
class EnhancedTestCaseAnalyzer:
    """Analyzer for test cases with advanced metrics and risk assessment."""
    
    def __init__(self, llm_provider="groq"):
        """
        Initialize the Enhanced Test Case Analyzer.
        
        Args:
            llm_provider: The LLM provider to use for analysis
        """
        pass
    
    def analyze_test_case(self, test_case, coverage_data=None, 
                         execution_history=None, code_changes=None):
        """
        Analyze a test case with enhanced metrics and risk assessment.
        
        Args:
            test_case: The test case to analyze, in Gherkin format
            coverage_data: Optional code coverage data
            execution_history: Optional list of previous execution results
            code_changes: Optional information about recent code changes
        
        Returns:
            Dictionary containing comprehensive analysis results
        """
        pass
    
    def suggest_improvements(self, test_case, execution_results=None,
                            coverage_data=None):
        """
        Suggest comprehensive improvements for a test case.
        
        Args:
            test_case: The test case in Gherkin format
            execution_results: Optional dictionary containing test execution results
            coverage_data: Optional code coverage data
        
        Returns:
            Dictionary containing suggested improvements
        """
        pass
```

## Examples

### Basic Test Execution

```python
from ai_qa_agent import TestSession

# Create a new test session
session = TestSession(name="Basic Test Run")

# Run unit tests
session.run_tests("tests/unit/")

# Generate PDF report
session.generate_report("reports/basic_test_report.pdf")
```

### Mobile Testing with Appium

```python
from ai_qa_agent import TestSession, AndroidDevice

# Initialize Android device
device = AndroidDevice()

# Start the app
device.start_app("com.example.app")

# Create a test session with the device
session = TestSession(name="Mobile Test Run", config={"device": device})

# Run mobile tests
session.run_tests("tests/mobile/", test_type="mobile")

# Take a screenshot
device.take_screenshot("screenshots/home_screen.png")

# Start recording
device.start_recording("recordings/test_flow.mp4")

# Run a specific test
session.run_tests("tests/mobile/test_login.py")

# Stop recording
device.stop_recording()

# Generate HTML report
session.generate_report("reports/mobile_test_report.html", report_type="html")
```

### Visual Testing

```python
from ai_qa_agent import TestSession, VisualTesting

# Initialize visual testing
visual = VisualTesting()

# Create a test session with visual testing
session = TestSession(name="Visual Test Run", config={"visual": visual})

# Run visual tests
session.run_tests("tests/visual/", test_type="visual")

# Compare screenshots
diff_result = visual.compare_screenshots(
    "baseline/home_screen.png",
    "current/home_screen.png",
    "diffs/home_screen_diff.png"
)

# Extract text from screenshot
text = visual.extract_text("screenshots/error_message.png")

# Generate heatmap
visual.generate_heatmap(
    "interactions.json",
    "screenshots/home_screen.png",
    "heatmaps/home_screen_heatmap.png"
)

# Generate executive report
session.generate_report("reports/visual_test_report.pdf", report_type="executive")
```

### Test Case Analysis

```python
from ai_qa_agent import EnhancedTestCaseAnalyzer

# Initialize the analyzer
analyzer = EnhancedTestCaseAnalyzer()

# Test case in Gherkin format
test_case = """
Feature: User Authentication

Scenario: Successful login
  Given I am on the login page
  When I enter valid credentials
  And I click the login button
  Then I should be redirected to the dashboard
  And I should see a welcome message
"""

# Analyze the test case
analysis = analyzer.analyze_test_case(test_case)

# Get suggestions for improvement
suggestions = analyzer.suggest_improvements(test_case)

# Optimize the test case
optimized_test_case = analyzer.optimize_test_case(test_case)

# Print the results
print("Analysis:", analysis)
print("Suggestions:", suggestions)
print("Optimized Test Case:", optimized_test_case)
```

## Troubleshooting

### Common Issues

#### Appium Connection Issues
If you're having trouble connecting to Appium:
1. Ensure Appium server is running: `appium`
2. Check device is connected: `adb devices`
3. Verify Appium driver is installed: `npm list -g appium-uiautomator2-driver`

#### Docker Permission Issues
If you encounter permission issues with Docker:
1. Ensure your user is in the docker group: `sudo usermod -aG docker $USER`
2. Restart your session or system
3. Try running with sudo if necessary

#### LLM Provider Connection Issues
If you're having trouble connecting to LLM providers:
1. Check your API keys are correctly set in the configuration
2. Verify network connectivity to the provider
3. Check provider status on their status page

## Contributing

We welcome contributions to the AI QA Agent! Please follow these steps:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin feature/your-feature-name`
5. Submit a pull request

Please ensure your code passes all tests and linting checks before submitting a pull request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

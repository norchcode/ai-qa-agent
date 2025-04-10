"""
Central controller for the AI QA Agent that integrates all tools into a unified interface.
"""
import os
import logging
from typing import Dict, List, Any, Optional, Union
import json
import tempfile
from pathlib import Path

# Import all tool modules
from test_case_analyzer import TestCaseAnalyzer
from gherkin_translator import GherkinTranslator
from test_executor import TestExecutor
from visual_testing import VisualTesting
from history_manager import HistoryManager
from report_generator import ReportGenerator
from appium_manager import AppiumManager
from llm_integration import LLMProvider

logger = logging.getLogger(__name__)

class AIQAAgentController:
    """
    Central controller for the AI QA Agent that integrates all tools into a unified interface.
    
    This class serves as the main integration point for all AI QA Agent tools and features.
    It initializes and manages all components, provides a unified API for the web UI,
    handles communication between components, and coordinates workflows that span multiple tools.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the AI QA Agent Controller with the given configuration.
        
        Args:
            config: Optional configuration dictionary. If not provided, default configuration will be used.
        """
        self.config = config or {}
        self._load_config()
        
        # Initialize all tool components
        self.llm_provider = self._init_llm_provider()
        self.test_analyzer = self._init_test_analyzer()
        self.gherkin_translator = self._init_gherkin_translator()
        self.test_executor = self._init_test_executor()
        self.visual_testing = self._init_visual_testing()
        self.history_manager = self._init_history_manager()
        self.report_generator = self._init_report_generator()
        self.appium_manager = self._init_appium_manager()
        
        logger.info("AI QA Agent Controller initialized")
    
    def _load_config(self):
        """Load configuration from environment variables and config file."""
        # Load from environment variables
        env_config = {
            "llm_provider": os.getenv("LLM_PROVIDER", "groq"),
            "groq_api_key": os.getenv("GROQ_API_KEY", ""),
            "groq_model": os.getenv("GROQ_MODEL", "llama3-70b-8192"),
            "browser_type": os.getenv("BROWSER_TYPE", "chromium"),
            "headless": os.getenv("HEADLESS", "false").lower() == "true",
            "browser_resolution": os.getenv("BROWSER_RESOLUTION", "1920,1080"),
            "report_format": os.getenv("REPORT_FORMAT", "pdf"),
            "include_screenshots": os.getenv("REPORT_INCLUDE_SCREENSHOTS", "true").lower() == "true",
            "include_videos": os.getenv("REPORT_INCLUDE_VIDEOS", "true").lower() == "true",
            "log_level": os.getenv("LOG_LEVEL", "INFO"),
            "log_file": os.getenv("LOG_FILE", "./logs/ai_qa_agent.log"),
            "database_path": os.getenv("DATABASE_PATH", "./data/history.db"),
        }
        
        # Update with provided config
        self.config.update(env_config)
        
        # Load from config file if specified
        config_file = self.config.get("config_file") or os.getenv("CONFIG_FILE")
        if config_file and os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    file_config = json.load(f)
                self.config.update(file_config)
                logger.info(f"Loaded configuration from {config_file}")
            except Exception as e:
                logger.error(f"Error loading configuration from {config_file}: {e}")
    
    def _init_llm_provider(self) -> LLMProvider:
        """Initialize the LLM provider based on configuration."""
        provider_name = self.config.get("llm_provider", "groq")
        provider_config = {
            "api_key": self.config.get(f"{provider_name}_api_key", ""),
            "model": self.config.get(f"{provider_name}_model", "")
        }
        return LLMProvider(provider_name, provider_config)
    
    def _init_test_analyzer(self) -> TestCaseAnalyzer:
        """Initialize the test case analyzer."""
        return TestCaseAnalyzer(self.llm_provider)
    
    def _init_gherkin_translator(self) -> GherkinTranslator:
        """Initialize the Gherkin translator."""
        return GherkinTranslator(self.llm_provider)
    
    def _init_test_executor(self) -> TestExecutor:
        """Initialize the test executor."""
        return TestExecutor(self.config)
    
    def _init_visual_testing(self) -> VisualTesting:
        """Initialize the visual testing component."""
        return VisualTesting(self.config)
    
    def _init_history_manager(self) -> HistoryManager:
        """Initialize the history manager."""
        return HistoryManager(self.config.get("database_path", "./data/history.db"))
    
    def _init_report_generator(self) -> ReportGenerator:
        """Initialize the report generator."""
        return ReportGenerator(self.config)
    
    def _init_appium_manager(self) -> AppiumManager:
        """Initialize the Appium manager."""
        return AppiumManager(self.config)
    
    # Test Case Analysis Methods
    
    def analyze_test_case(self, test_case: str) -> Dict[str, Any]:
        """
        Analyze a test case and return detailed metrics and insights.
        
        Args:
            test_case: The test case in Gherkin format.
            
        Returns:
            Dictionary containing analysis results.
        """
        logger.info("Analyzing test case")
        analysis = self.test_analyzer.analyze(test_case)
        return analysis
    
    def optimize_test_case(self, test_case: str) -> str:
        """
        Optimize a test case to improve quality, readability, and effectiveness.
        
        Args:
            test_case: The test case in Gherkin format.
            
        Returns:
            Optimized test case in Gherkin format.
        """
        logger.info("Optimizing test case")
        optimized = self.test_analyzer.optimize(test_case)
        return optimized
    
    # Gherkin Translation Methods
    
    def translate_to_gherkin(self, natural_language: str) -> str:
        """
        Translate natural language test steps to Gherkin format.
        
        Args:
            natural_language: Test steps in natural language.
            
        Returns:
            Test steps in Gherkin format.
        """
        logger.info("Translating to Gherkin")
        gherkin = self.gherkin_translator.to_gherkin(natural_language)
        return gherkin
    
    def translate_from_gherkin(self, gherkin: str) -> str:
        """
        Translate Gherkin format to natural language test steps.
        
        Args:
            gherkin: Test steps in Gherkin format.
            
        Returns:
            Test steps in natural language.
        """
        logger.info("Translating from Gherkin")
        natural_language = self.gherkin_translator.from_gherkin(gherkin)
        return natural_language
    
    def generate_gherkin_from_description(self, description: str) -> str:
        """
        Generate Gherkin scenarios from a test description.
        
        Args:
            description: Description of the test requirements.
            
        Returns:
            Generated Gherkin scenarios.
        """
        logger.info("Generating Gherkin from description")
        gherkin = self.gherkin_translator.generate_from_description(description)
        return gherkin
    
    def suggest_gherkin_improvements(self, gherkin: str) -> Dict[str, Any]:
        """
        Suggest improvements for Gherkin scenarios.
        
        Args:
            gherkin: Test steps in Gherkin format.
            
        Returns:
            Dictionary containing suggested improvements.
        """
        logger.info("Suggesting Gherkin improvements")
        suggestions = self.gherkin_translator.suggest_improvements(gherkin)
        return suggestions
    
    # Test Execution Methods
    
    def run_tests(self, test_path: str) -> Dict[str, Any]:
        """
        Run tests from the specified path and return results.
        
        Args:
            test_path: Path to test file or directory.
            
        Returns:
            Dictionary containing test results.
        """
        logger.info(f"Running tests from {test_path}")
        results = self.test_executor.run(test_path)
        
        # Save results to history
        session_id = self.history_manager.create_session(
            name=f"Test run: {Path(test_path).name}",
            test_path=test_path,
            results=results
        )
        
        return results
    
    def generate_report(self, results: Dict[str, Any], format: str = None) -> str:
        """
        Generate a report from test results.
        
        Args:
            results: Test results dictionary.
            format: Report format (pdf, html, json). If None, uses default from config.
            
        Returns:
            Path to the generated report.
        """
        format = format or self.config.get("report_format", "pdf")
        logger.info(f"Generating {format} report")
        report_path = self.report_generator.generate(results, format)
        return report_path
    
    # Visual Testing Methods
    
    def analyze_screenshot(self, screenshot_path: str) -> Dict[str, Any]:
        """
        Analyze a screenshot and return insights.
        
        Args:
            screenshot_path: Path to the screenshot file.
            
        Returns:
            Dictionary containing analysis results.
        """
        logger.info(f"Analyzing screenshot: {screenshot_path}")
        analysis = self.visual_testing.analyze_screenshot(screenshot_path)
        return analysis
    
    def compare_screenshots(self, baseline_path: str, current_path: str, diff_path: str = None) -> Dict[str, Any]:
        """
        Compare two screenshots and generate a difference image.
        
        Args:
            baseline_path: Path to the baseline screenshot.
            current_path: Path to the current screenshot.
            diff_path: Path to save the difference image. If None, a temporary file is used.
            
        Returns:
            Dictionary containing comparison results.
        """
        logger.info(f"Comparing screenshots: {baseline_path} vs {current_path}")
        results = self.visual_testing.compare_screenshots(baseline_path, current_path, diff_path)
        return results
    
    def extract_text_from_screenshot(self, screenshot_path: str) -> str:
        """
        Extract text from a screenshot using OCR.
        
        Args:
            screenshot_path: Path to the screenshot file.
            
        Returns:
            Extracted text.
        """
        logger.info(f"Extracting text from screenshot: {screenshot_path}")
        text = self.visual_testing.extract_text(screenshot_path)
        return text
    
    def generate_heatmap(self, interaction_data: Dict[str, Any], screenshot_path: str, output_path: str = None) -> str:
        """
        Generate a heatmap visualization of user interactions.
        
        Args:
            interaction_data: Dictionary containing interaction data.
            screenshot_path: Path to the screenshot file.
            output_path: Path to save the heatmap image. If None, a temporary file is used.
            
        Returns:
            Path to the generated heatmap image.
        """
        logger.info(f"Generating heatmap for screenshot: {screenshot_path}")
        heatmap_path = self.visual_testing.generate_heatmap(interaction_data, screenshot_path, output_path)
        return heatmap_path
    
    # Mobile Testing Methods
    
    def start_appium_server(self) -> bool:
        """
        Start the Appium server.
        
        Returns:
            True if server started successfully, False otherwise.
        """
        logger.info("Starting Appium server")
        success = self.appium_manager.start_server()
        return success
    
    def stop_appium_server(self) -> bool:
        """
        Stop the Appium server.
        
        Returns:
            True if server stopped successfully, False otherwise.
        """
        logger.info("Stopping Appium server")
        success = self.appium_manager.stop_server()
        return success
    
    def connect_to_device(self, device_id: str = None) -> Dict[str, Any]:
        """
        Connect to an Android device.
        
        Args:
            device_id: Device ID. If None, connects to the first available device.
            
        Returns:
            Dictionary containing device information.
        """
        logger.info(f"Connecting to device: {device_id or 'first available'}")
        device_info = self.appium_manager.connect_to_device(device_id)
        return device_info
    
    def start_app(self, package_name: str, activity_name: str = None) -> bool:
        """
        Start an app on the connected device.
        
        Args:
            package_name: Package name of the app.
            activity_name: Activity name to start. If None, the main activity is started.
            
        Returns:
            True if app started successfully, False otherwise.
        """
        logger.info(f"Starting app: {package_name}")
        success = self.appium_manager.start_app(package_name, activity_name)
        return success
    
    def take_screenshot(self, output_path: str = None) -> str:
        """
        Take a screenshot of the connected device.
        
        Args:
            output_path: Path to save the screenshot. If None, a temporary file is used.
            
        Returns:
            Path to the saved screenshot.
        """
        logger.info("Taking screenshot")
        screenshot_path = self.appium_manager.take_screenshot(output_path)
        return screenshot_path
    
    # History Management Methods
    
    def get_test_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get the test execution history.
        
        Args:
            limit: Maximum number of history entries to return.
            
        Returns:
            List of dictionaries containing history entries.
        """
        logger.info(f"Getting test history (limit: {limit})")
        history = self.history_manager.get_sessions(limit)
        return history
    
    def get_session_details(self, session_id: str) -> Dict[str, Any]:
        """
        Get details for a specific test session.
        
        Args:
            session_id: ID of the test session.
            
        Returns:
            Dictionary containing session details.
        """
        logger.info(f"Getting session details: {session_id}")
        details = self.history_manager.get_session(session_id)
        return details
    
    def compare_sessions(self, session_id1: str, session_id2: str) -> Dict[str, Any]:
        """
        Compare two test sessions.
        
        Args:
            session_id1: ID of the first test session.
            session_id2: ID of the second test session.
            
        Returns:
            Dictionary containing comparison results.
        """
        logger.info(f"Comparing sessions: {session_id1} vs {session_id2}")
        comparison = self.history_manager.compare_sessions(session_id1, session_id2)
        return comparison
    
    def export_history(self, format: str = "json", output_path: str = None) -> str:
        """
        Export test history to a file.
        
        Args:
            format: Export format (json, csv).
            output_path: Path to save the export file. If None, a temporary file is used.
            
        Returns:
            Path to the export file.
        """
        logger.info(f"Exporting history to {format}")
        export_path = self.history_manager.export(format, output_path)
        return export_path
    
    # Configuration Methods
    
    def update_config(self, new_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update the configuration.
        
        Args:
            new_config: Dictionary containing new configuration values.
            
        Returns:
            Updated configuration dictionary.
        """
        logger.info("Updating configuration")
        self.config.update(new_config)
        
        # Update environment variables
        for key, value in new_config.items():
            if isinstance(value, bool):
                os.environ[key.upper()] = str(value).lower()
            else:
                os.environ[key.upper()] = str(value)
        
        return self.config
    
    def save_config(self, config_path: str = None) -> str:
        """
        Save the current configuration to a file.
        
        Args:
            config_path: Path to save the configuration file. If None, uses the path from config.
            
        Returns:
            Path to the saved configuration file.
        """
        config_path = config_path or self.config.get("config_file") or "./config/ai_qa_agent.json"
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        
        logger.info(f"Saving configuration to {config_path}")
        with open(config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
        
        return config_path
    
    # Workflow Methods
    
    def execute_test_workflow(self, test_description: str) -> Dict[str, Any]:
        """
        Execute a complete test workflow from description to results.
        
        This workflow:
        1. Generates Gherkin from the description
        2. Optimizes the Gherkin
        3. Runs the tests
        4. Generates a report
        
        Args:
            test_description: Description of the test requirements.
            
        Returns:
            Dictionary containing workflow results.
        """
        logger.info("Executing test workflow")
        
        # Generate Gherkin from description
        gherkin = self.generate_gherkin_from_description(test_description)
        
        # Optimize the Gherkin
        optimized_gherkin = self.optimize_test_case(gherkin)
        
        # Save Gherkin to a temporary file
        temp_dir = tempfile.mkdtemp()
        temp_file = os.path.join(temp_dir, "test.feature")
        
        with open(temp_file, "w") as f:
            f.write(optimized_gherkin)
        
        # Run the tests
        results = self.run_tests(temp_file)
        
        # Generate a report
        report_path = self.generate_report(results)
        
        # Return workflow results
        workflow_results = {
            "gherkin": gherkin,
            "optimized_gherkin": optimized_gherkin,
            "test_results": results,
            "report_path": report_path
        }
        
        return workflow_results
    
    def execute_visual_workflow(self, baseline_path: str, current_path: str) -> Dict[str, Any]:
        """
        Execute a complete visual testing workflow.
        
        This workflow:
        1. Compares the screenshots
        2. Extracts text from both screenshots
        3. Analyzes the current screenshot
        4. Generates a report
        
        Args:
            baseline_path: Path to the baseline screenshot.
            current_path: Path to the current screenshot.
            
        Returns:
            Dictionary containing workflow results.
        """
        logger.info("Executing visual workflow")
        
        # Compare screenshots
        temp_dir = tempfile.mkdtemp()
        diff_path = os.path.join(temp_dir, "diff.png")
        comparison = self.compare_screenshots(baseline_path, current_path, diff_path)
        
        # Extract text from both screenshots
        baseline_text = self.extract_text_from_screenshot(baseline_path)
        current_text = self.extract_text_from_screenshot(current_path)
        
        # Analyze the current screenshot
        analysis = self.analyze_screenshot(current_path)
        
        # Generate a report
        results = {
            "comparison": comparison,
            "baseline_text": baseline_text,
            "current_text": current_text,
            "analysis": analysis,
            "diff_path": diff_path
        }
        
        report_path = self.generate_report(results)
        
        # Return workflow results
        workflow_results = {
            **results,
            "report_path": report_path
        }
        
        return workflow_results
    
    def execute_mobile_workflow(self, package_name: str, test_path: str) -> Dict[str, Any]:
        """
        Execute a complete mobile testing workflow.
        
        This workflow:
        1. Starts the Appium server
        2. Connects to a device
        3. Starts the app
        4. Takes a screenshot
        5. Runs the tests
        6. Generates a report
        7. Stops the Appium server
        
        Args:
            package_name: Package name of the app to test.
            test_path: Path to test file or directory.
            
        Returns:
            Dictionary containing workflow results.
        """
        logger.info("Executing mobile workflow")
        
        # Start the Appium server
        server_started = self.start_appium_server()
        
        if not server_started:
            return {"error": "Failed to start Appium server"}
        
        try:
            # Connect to a device
            device_info = self.connect_to_device()
            
            if "error" in device_info:
                return {"error": f"Failed to connect to device: {device_info['error']}"}
            
            # Start the app
            app_started = self.start_app(package_name)
            
            if not app_started:
                return {"error": f"Failed to start app: {package_name}"}
            
            # Take a screenshot
            screenshot_path = self.take_screenshot()
            
            # Run the tests
            results = self.run_tests(test_path)
            
            # Generate a report
            report_path = self.generate_report(results)
            
            # Return workflow results
            workflow_results = {
                "device_info": device_info,
                "screenshot_path": screenshot_path,
                "test_results": results,
                "report_path": report_path
            }
            
            return workflow_results
        
        finally:
            # Stop the Appium server
            self.stop_appium_server()

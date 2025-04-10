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
    
    # Unified Interface Method
    
    def process_unified_request(self, prompt: str, files: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Process a unified request that can handle any type of testing task.
        
        This method serves as the main entry point for the unified interface, routing
        requests to the appropriate tools based on the content of the prompt and any
        attached files.
        
        Args:
            prompt: The user's prompt/request text
            files: Optional list of file paths that were uploaded with the prompt
            
        Returns:
            Dictionary containing the response and any additional data
        """
        logger.info(f"Processing unified request: {prompt[:100]}...")
        
        # Use the LLM to analyze the request and determine the appropriate action
        analysis = self.llm_provider.process_unified_prompt(prompt, files)
        action = analysis.get("action_taken", "unknown")
        
        # Based on the determined action, call the appropriate method
        result = {
            "analysis": analysis,
            "action": action,
            "response": "",
            "data": {},
            "files": []
        }
        
        try:
            # Route to the appropriate handler based on the action
            if action == "test_case_analysis":
                # Extract test case from prompt or files
                test_case = self._extract_test_case_from_request(prompt, files)
                analysis_result = self.analyze_test_case(test_case)
                result["response"] = "Test case analysis completed"
                result["data"] = analysis_result
                
            elif action == "test_case_optimization":
                test_case = self._extract_test_case_from_request(prompt, files)
                optimized = self.optimize_test_case(test_case)
                result["response"] = "Test case optimization completed"
                result["data"] = {"optimized_test_case": optimized}
                
            elif action == "gherkin_translation":
                if "to_gherkin" in analysis.get("sub_task", ""):
                    nl_text = prompt  # Simplified; in reality would extract the relevant part
                    gherkin = self.translate_to_gherkin(nl_text)
                    result["response"] = "Translated to Gherkin format"
                    result["data"] = {"gherkin": gherkin}
                else:
                    gherkin = self._extract_test_case_from_request(prompt, files)
                    nl_text = self.translate_from_gherkin(gherkin)
                    result["response"] = "Translated from Gherkin format"
                    result["data"] = {"natural_language": nl_text}
                    
            elif action == "visual_testing":
                if files and len(files) > 0:
                    if len(files) == 1:
                        # Single screenshot analysis
                        analysis_result = self.analyze_screenshot(files[0])
                        result["response"] = "Screenshot analysis completed"
                        result["data"] = analysis_result
                    elif len(files) >= 2:
                        # Compare two screenshots
                        temp_dir = tempfile.mkdtemp()
                        diff_path = os.path.join(temp_dir, "diff.png")
                        comparison = self.compare_screenshots(files[0], files[1], diff_path)
                        result["response"] = "Screenshot comparison completed"
                        result["data"] = comparison
                        result["files"] = [diff_path]
                else:
                    result["response"] = "Error: No screenshots provided for visual testing"
                    
            elif action == "mobile_testing":
                # Mobile testing would require more complex handling
                result["response"] = "Mobile testing request received"
                result["data"] = {"status": "Mobile testing functionality requires specific setup"}
                
            elif action == "test_generation":
                description = prompt  # Simplified
                gherkin = self.generate_gherkin_from_description(description)
                result["response"] = "Test cases generated from description"
                result["data"] = {"generated_tests": gherkin}
                
            else:  # general_question or unknown
                # For general questions, we'll just return the LLM's response
                result["response"] = analysis.get("response", "I processed your request but couldn't determine a specific action.")
        
        except Exception as e:
            logger.error(f"Error processing unified request: {e}")
            result["response"] = f"Error processing request: {str(e)}"
            result["error"] = str(e)
        
        # Log the action taken
        self.history_manager.log_action(action, prompt, result)
        
        return result
    
    def _extract_test_case_from_request(self, prompt: str, files: Optional[List[str]] = None) -> str:
        """
        Extract test case content from the request.
        
        Args:
            prompt: The user's prompt text
            files: Optional list of file paths
            
        Returns:
            Extracted test case as a string
        """
        # First check if there's a file with test case content
        if files and len(files) > 0:
            for file_path in files:
                ext = os.path.splitext(file_path)[1].lower()
                if ext in ['.feature', '.txt', '.md']:
                    try:
                        with open(file_path, 'r') as f:
                            return f.read()
                    except Exception as e:
                        logger.error(f"Error reading file {file_path}: {e}")
        
        # If no suitable file found, extract from the prompt
        # This is a simplified version; in reality, would use more sophisticated extraction
        return prompt
    
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
            screenshot_path: Path to the screenshot to overlay the heatmap on.
            output_path: Path to save the heatmap image. If None, a temporary file is used.
            
        Returns:
            Path to the generated heatmap image.
        """
        logger.info("Generating interaction heatmap")
        heatmap_path = self.visual_testing.generate_heatmap(interaction_data, screenshot_path, output_path)
        return heatmap_path
    
    # Mobile Testing Methods
    
    def start_appium_server(self) -> bool:
        """
        Start the Appium server.
        
        Returns:
            True if the server was started successfully, False otherwise.
        """
        logger.info("Starting Appium server")
        success = self.appium_manager.start_server()
        return success
    
    def stop_appium_server(self) -> bool:
        """
        Stop the Appium server.
        
        Returns:
            True if the server was stopped successfully, False otherwise.
        """
        logger.info("Stopping Appium server")
        success = self.appium_manager.stop_server()
        return success
    
    def connect_to_device(self, device_id: str = None) -> Dict[str, Any]:
        """
        Connect to a mobile device.
        
        Args:
            device_id: Optional device ID. If not provided, connects to the first available device.
            
        Returns:
            Dictionary containing device information.
        """
        logger.info(f"Connecting to device: {device_id or 'first available'}")
        device_info = self.appium_manager.connect_to_device(device_id)
        return device_info
    
    def install_app(self, app_path: str) -> bool:
        """
        Install an app on the connected device.
        
        Args:
            app_path: Path to the app file.
            
        Returns:
            True if the app was installed successfully, False otherwise.
        """
        logger.info(f"Installing app: {app_path}")
        success = self.appium_manager.install_app(app_path)
        return success
    
    def launch_app(self, package_name: str, activity_name: str = None) -> bool:
        """
        Launch an app on the connected device.
        
        Args:
            package_name: Package name of the app.
            activity_name: Optional activity name to launch.
            
        Returns:
            True if the app was launched successfully, False otherwise.
        """
        logger.info(f"Launching app: {package_name}")
        success = self.appium_manager.launch_app(package_name, activity_name)
        return success
    
    def take_screenshot(self, output_path: str = None) -> str:
        """
        Take a screenshot of the connected device.
        
        Args:
            output_path: Path to save the screenshot. If None, a temporary file is used.
            
        Returns:
            Path to the screenshot file.
        """
        logger.info("Taking device screenshot")
        screenshot_path = self.appium_manager.take_screenshot(output_path)
        return screenshot_path
    
    def start_recording(self, output_path: str = None) -> str:
        """
        Start recording the connected device screen.
        
        Args:
            output_path: Path to save the recording. If None, a temporary file is used.
            
        Returns:
            Path where the recording will be saved.
        """
        logger.info("Starting screen recording")
        recording_path = self.appium_manager.start_recording(output_path)
        return recording_path
    
    def stop_recording(self) -> str:
        """
        Stop recording the connected device screen.
        
        Returns:
            Path to the recorded video file.
        """
        logger.info("Stopping screen recording")
        recording_path = self.appium_manager.stop_recording()
        return recording_path
    
    # History Management Methods
    
    def get_test_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent test history.
        
        Args:
            limit: Maximum number of history items to return.
            
        Returns:
            List of dictionaries containing history items.
        """
        logger.info(f"Getting test history (limit: {limit})")
        history = self.history_manager.get_history(limit)
        return history
    
    def get_session_details(self, session_id: str) -> Dict[str, Any]:
        """
        Get details for a specific test session.
        
        Args:
            session_id: ID of the session to get details for.
            
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
            session_id1: ID of the first session.
            session_id2: ID of the second session.
            
        Returns:
            Dictionary containing comparison results.
        """
        logger.info(f"Comparing sessions: {session_id1} vs {session_id2}")
        comparison = self.history_manager.compare_sessions(session_id1, session_id2)
        return comparison
    
    def export_history(self, format: str = "json") -> str:
        """
        Export test history to a file.
        
        Args:
            format: Export format (json, csv).
            
        Returns:
            Path to the exported file.
        """
        logger.info(f"Exporting history to {format}")
        export_path = self.history_manager.export(format)
        return export_path

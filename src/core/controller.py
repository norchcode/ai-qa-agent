"""
Central controller for the AI QA Agent that integrates all tools into a unified interface.
"""
import os
import logging
import re
from typing import Dict, List, Any, Optional, Union
import json
import tempfile
from pathlib import Path

# Import all tool modules
from src.core.test_case_analyzer import TestCaseAnalyzer
from src.tools.gherkin_translator import GherkinTranslator
from src.tools.test_executor import TestExecutor
from src.tools.visual_testing import VisualTesting
from src.utils.history_manager import HistoryManager
from src.tools.report_generator import ReportGenerator
from src.utils.appium_manager import AppiumManager
from src.core.llm_integration import LLMProvider

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
        
        # Check if this is a browser automation command before using LLM
        if self._is_browser_automation_command(prompt):
            return self._handle_browser_automation(prompt)
        
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
                
            elif action == "browser_automation":
                # This is a fallback in case the LLM identifies it as browser automation
                # but it wasn't caught by our pattern matching
                result = self._handle_browser_automation(prompt)
                
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
    
    def _is_browser_automation_command(self, prompt: str) -> bool:
        """
        Determine if the prompt is a browser automation command.
        
        Args:
            prompt: The user's prompt text
            
        Returns:
            True if the prompt is a browser automation command, False otherwise
        """
        # Define patterns that indicate browser automation commands
        browser_patterns = [
            r"open\s+[a-zA-Z0-9]+\.[a-zA-Z]+",  # open website.com
            r"search\s+for\s+.+",  # search for something
            r"click\s+on\s+.+",  # click on something
            r"navigate\s+to\s+.+",  # navigate to something
            r"sort\s+(?:by|the)\s+.+",  # sort by something
            r"fill\s+(?:in|out)\s+.+",  # fill in something
            r"select\s+.+",  # select something
            r"submit\s+.+",  # submit something
        ]
        
        # Check if the prompt contains any of the patterns
        for pattern in browser_patterns:
            if re.search(pattern, prompt, re.IGNORECASE):
                return True
        
        # Check if the prompt contains multiple commands separated by commas
        # which is a common pattern for browser automation
        if "," in prompt and len(prompt.split(",")) >= 2:
            command_parts = [part.strip() for part in prompt.split(",")]
            # Check if at least two parts match browser patterns
            matches = 0
            for part in command_parts:
                for pattern in browser_patterns:
                    if re.search(pattern, part, re.IGNORECASE):
                        matches += 1
                        break
            if matches >= 2:
                return True
        
        return False
    
    def _handle_browser_automation(self, prompt: str) -> Dict[str, Any]:
        """
        Handle a browser automation command.
        
        Args:
            prompt: The user's prompt text containing browser automation commands
            
        Returns:
            Dictionary containing the response and any additional data
        """
        logger.info(f"Handling browser automation command: {prompt}")
        
        try:
            # Execute the browser automation command using the test executor
            test_results = self.test_executor.run(prompt)
            
            # Create a temporary directory for screenshots
            temp_dir = tempfile.mkdtemp()
            screenshot_files = []
            
            # Copy screenshots to the temporary directory if they exist
            if "screenshots" in test_results:
                for i, screenshot_path in enumerate(test_results["screenshots"]):
                    if os.path.exists(screenshot_path):
                        new_path = os.path.join(temp_dir, f"step_{i+1}_screenshot.png")
                        try:
                            import shutil
                            shutil.copy(screenshot_path, new_path)
                            screenshot_files.append(new_path)
                        except Exception as e:
                            logger.error(f"Error copying screenshot: {e}")
            
            # Generate a response based on the test results
            steps_summary = ""
            if "steps" in test_results:
                for step in test_results["steps"]:
                    status_emoji = "✅" if step.get("status") == "passed" else "⚠️" if step.get("status") == "warning" else "❌"
                    steps_summary += f"{status_emoji} Step {step.get('step', '')}: {step.get('command', '')}\n"
                    if "details" in step:
                        steps_summary += f"   {step['details']}\n"
            
            # Create the result dictionary
            result = {
                "action": "browser_automation",
                "response": f"Browser automation test executed successfully.\n\n{steps_summary}",
                "data": test_results,
                "files": screenshot_files
            }
            
            # Log the action
            self.history_manager.log_action("browser_automation", prompt, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error handling browser automation command: {e}")
            result = {
                "action": "browser_automation",
                "response": f"Error executing browser automation command: {str(e)}",
                "error": str(e),
                "data": {},
                "files": []
            }
            
            # Log the action
            self.history_manager.log_action("browser_automation", prompt, result)
            
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
        if files:
            for file_path in files:
                if file_path.endswith(('.feature', '.txt', '.md')):
                    try:
                        with open(file_path, 'r') as f:
                            return f.read()
                    except Exception as e:
                        logger.error(f"Error reading file {file_path}: {e}")
        
        # If no file or couldn't read file, extract from prompt
        # This is a simplified implementation; in reality would use more sophisticated extraction
        return prompt
    
    # Public API Methods
    
    def analyze_test_case(self, test_case: str) -> Dict[str, Any]:
        """
        Analyze a test case and return detailed metrics and insights.
        
        Args:
            test_case: The test case to analyze
            
        Returns:
            Dictionary containing analysis results
        """
        return self.test_analyzer.analyze(test_case)
    
    def optimize_test_case(self, test_case: str) -> str:
        """
        Optimize a test case to improve quality, readability, and effectiveness.
        
        Args:
            test_case: The test case to optimize
            
        Returns:
            Optimized test case
        """
        return self.test_analyzer.optimize(test_case)
    
    def translate_to_gherkin(self, natural_language: str) -> str:
        """
        Translate natural language test steps to Gherkin format.
        
        Args:
            natural_language: Natural language test steps
            
        Returns:
            Gherkin format test case
        """
        return self.gherkin_translator.translate_to_gherkin(natural_language)
    
    def translate_from_gherkin(self, gherkin: str) -> str:
        """
        Translate Gherkin format test case to natural language.
        
        Args:
            gherkin: Gherkin format test case
            
        Returns:
            Natural language test steps
        """
        return self.gherkin_translator.translate_from_gherkin(gherkin)
    
    def generate_gherkin_from_description(self, description: str) -> str:
        """
        Generate Gherkin test cases from a feature description.
        
        Args:
            description: Feature description
            
        Returns:
            Gherkin format test cases
        """
        return self.gherkin_translator.generate_from_description(description)
    
    def analyze_screenshot(self, screenshot_path: str) -> Dict[str, Any]:
        """
        Analyze a screenshot and return insights.
        
        Args:
            screenshot_path: Path to the screenshot file
            
        Returns:
            Dictionary containing analysis results
        """
        return self.visual_testing.analyze_screenshot(screenshot_path)
    
    def compare_screenshots(self, screenshot1_path: str, screenshot2_path: str, diff_path: str) -> Dict[str, Any]:
        """
        Compare two screenshots and generate a diff image.
        
        Args:
            screenshot1_path: Path to the first screenshot
            screenshot2_path: Path to the second screenshot
            diff_path: Path to save the diff image
            
        Returns:
            Dictionary containing comparison results
        """
        return self.visual_testing.compare_screenshots(screenshot1_path, screenshot2_path, diff_path)
    
    def run_tests(self, test_path: str) -> Dict[str, Any]:
        """
        Run tests from a test file.
        
        Args:
            test_path: Path to the test file
            
        Returns:
            Dictionary containing test results
        """
        return self.test_executor.run_tests(test_path)
    
    def generate_report(self, test_results: Dict[str, Any], format: str = None) -> str:
        """
        Generate a report from test results.
        
        Args:
            test_results: Test results
            format: Report format (pdf, html, json)
            
        Returns:
            Path to the generated report
        """
        format = format or self.config.get("report_format", "pdf")
        return self.report_generator.generate(test_results, format)
    
    def get_test_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get test execution history.
        
        Args:
            limit: Maximum number of history entries to return
            
        Returns:
            List of history entries
        """
        return self.history_manager.get_history(limit)

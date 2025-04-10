"""
AI QA Agent module for test automation and quality assurance.
"""
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class AIQAAgent:
    """
    AI-powered QA Agent for test automation and quality assurance.
    
    This class serves as the main entry point for the AI QA Agent functionality.
    It provides a high-level API for interacting with the agent and accessing
    its various capabilities.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the AI QA Agent with the given configuration.
        
        Args:
            config: Optional configuration dictionary. If not provided, default configuration will be used.
        """
        from ..core.controller import AIQAAgentController
        
        self.config = config or {}
        self.controller = AIQAAgentController(self.config)
        logger.info("AI QA Agent initialized")
    
    def analyze_test_case(self, test_case: str) -> Dict[str, Any]:
        """
        Analyze a test case and return detailed metrics and insights.
        
        Args:
            test_case: The test case in Gherkin format.
            
        Returns:
            Dictionary containing analysis results.
        """
        return self.controller.analyze_test_case(test_case)
    
    def optimize_test_case(self, test_case: str) -> str:
        """
        Optimize a test case to improve quality, readability, and effectiveness.
        
        Args:
            test_case: The test case in Gherkin format.
            
        Returns:
            Optimized test case in Gherkin format.
        """
        return self.controller.optimize_test_case(test_case)
    
    def translate_to_gherkin(self, natural_language: str) -> str:
        """
        Translate natural language test steps to Gherkin format.
        
        Args:
            natural_language: Test steps in natural language.
            
        Returns:
            Test steps in Gherkin format.
        """
        return self.controller.translate_to_gherkin(natural_language)
    
    def translate_from_gherkin(self, gherkin: str) -> str:
        """
        Translate Gherkin format to natural language test steps.
        
        Args:
            gherkin: Test steps in Gherkin format.
            
        Returns:
            Test steps in natural language.
        """
        return self.controller.translate_from_gherkin(gherkin)
    
    def generate_gherkin_from_description(self, description: str) -> str:
        """
        Generate Gherkin scenarios from a test description.
        
        Args:
            description: Description of the test requirements.
            
        Returns:
            Generated Gherkin scenarios.
        """
        return self.controller.generate_gherkin_from_description(description)
    
    def suggest_gherkin_improvements(self, gherkin: str) -> Dict[str, Any]:
        """
        Suggest improvements for Gherkin scenarios.
        
        Args:
            gherkin: Test steps in Gherkin format.
            
        Returns:
            Dictionary containing suggested improvements.
        """
        return self.controller.suggest_gherkin_improvements(gherkin)
    
    def run_tests(self, test_path: str) -> Dict[str, Any]:
        """
        Run tests from the specified path and return results.
        
        Args:
            test_path: Path to test file or directory.
            
        Returns:
            Dictionary containing test results.
        """
        return self.controller.run_tests(test_path)
    
    def generate_report(self, results: Dict[str, Any], format: str = None) -> str:
        """
        Generate a report from test results.
        
        Args:
            results: Test results dictionary.
            format: Report format (pdf, html, json). If None, uses default from config.
            
        Returns:
            Path to the generated report.
        """
        return self.controller.generate_report(results, format)
    
    def analyze_screenshot(self, screenshot_path: str) -> Dict[str, Any]:
        """
        Analyze a screenshot and return insights.
        
        Args:
            screenshot_path: Path to the screenshot file.
            
        Returns:
            Dictionary containing analysis results.
        """
        return self.controller.analyze_screenshot(screenshot_path)
    
    def compare_screenshots(self, baseline_path: str, current_path: str, diff_path: str = None) -> Dict[str, Any]:
        """
        Compare two screenshots and return differences.
        
        Args:
            baseline_path: Path to the baseline screenshot.
            current_path: Path to the current screenshot.
            diff_path: Optional path to save the difference image.
            
        Returns:
            Dictionary containing comparison results.
        """
        return self.controller.compare_screenshots(baseline_path, current_path, diff_path)
    
    def extract_text_from_screenshot(self, screenshot_path: str) -> str:
        """
        Extract text from a screenshot using OCR.
        
        Args:
            screenshot_path: Path to the screenshot file.
            
        Returns:
            Extracted text.
        """
        return self.controller.extract_text_from_screenshot(screenshot_path)
    
    def process_unified_request(self, prompt: str, files: Optional[list] = None) -> Dict[str, Any]:
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
        return self.controller.process_unified_request(prompt, files)

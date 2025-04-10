"""
Test integration module for AI QA Agent.
This module provides functionality for testing the integration of all components.
"""
import os
import logging
import asyncio
import json
from typing import Dict, Any, Optional
from datetime import datetime

from src.core.controller import AIQAAgentController
from src.tools.browser_automation import BrowserAutomation
from src.tools.gherkin_executor import GherkinExecutor
from src.tools.report_generator import ReportGenerator

logger = logging.getLogger(__name__)

class IntegrationTester:
    """
    Tests the integration of all AI QA Agent components.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the integration tester.
        
        Args:
            config: Configuration dictionary.
        """
        self.config = config or {}
        self.controller = AIQAAgentController(self.config)
        self.gherkin_executor = GherkinExecutor(self.config)
        self.report_generator = ReportGenerator(self.config)
        self.test_results_dir = self.config.get("test_results_dir", "./test_results")
        os.makedirs(self.test_results_dir, exist_ok=True)
        logger.info("Integration tester initialized")
    
    async def test_browser_automation(self, command: str) -> Dict[str, Any]:
        """
        Test browser automation functionality.
        
        Args:
            command: Browser automation command to test.
            
        Returns:
            Dictionary containing test results.
        """
        logger.info(f"Testing browser automation with command: {command}")
        
        # Process the command through the controller
        result = self.controller.process_unified_request(command)
        
        # Save the result to a file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        result_path = os.path.join(self.test_results_dir, f"browser_test_{timestamp}.json")
        with open(result_path, "w") as f:
            json.dump(result, f, indent=2)
        
        # Generate a report
        report_path = self.report_generator.generate(result.get("data", {}), "html")
        
        # Add the report path to the result
        result["report_path"] = report_path
        
        return result
    
    async def test_gherkin_integration(self, command: str) -> Dict[str, Any]:
        """
        Test Gherkin integration functionality.
        
        Args:
            command: Browser automation command to convert to Gherkin and execute.
            
        Returns:
            Dictionary containing test results.
        """
        logger.info(f"Testing Gherkin integration with command: {command}")
        
        # Convert the command to Gherkin
        gherkin_text = self.gherkin_executor.convert_browser_command_to_gherkin(command)
        
        # Execute the Gherkin scenario
        result = await self.gherkin_executor.execute_gherkin(gherkin_text)
        
        # Save the result to a file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        result_path = os.path.join(self.test_results_dir, f"gherkin_test_{timestamp}.json")
        with open(result_path, "w") as f:
            json.dump(result, f, indent=2)
        
        # Generate a report
        report_path = self.report_generator.generate(result, "html")
        
        # Add the report path and Gherkin text to the result
        result["report_path"] = report_path
        result["gherkin_text"] = gherkin_text
        
        return result
    
    async def test_error_handling(self, command: str) -> Dict[str, Any]:
        """
        Test error handling functionality by executing a command that will likely fail.
        
        Args:
            command: Browser automation command that will likely fail.
            
        Returns:
            Dictionary containing test results.
        """
        logger.info(f"Testing error handling with command: {command}")
        
        # Process the command through the controller
        result = self.controller.process_unified_request(command)
        
        # Save the result to a file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        result_path = os.path.join(self.test_results_dir, f"error_test_{timestamp}.json")
        with open(result_path, "w") as f:
            json.dump(result, f, indent=2)
        
        # Generate a report
        report_path = self.report_generator.generate(result.get("data", {}), "html")
        
        # Add the report path to the result
        result["report_path"] = report_path
        
        return result
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """
        Run all integration tests.
        
        Returns:
            Dictionary containing all test results.
        """
        logger.info("Running all integration tests")
        
        results = {
            "browser_automation": None,
            "gherkin_integration": None,
            "error_handling": None,
            "timestamp": datetime.now().isoformat(),
            "status": "passed"
        }
        
        try:
            # Test browser automation
            browser_command = "open tokopedia.com, search for shokz headset, sort the price to lowest/cheapest"
            results["browser_automation"] = await self.test_browser_automation(browser_command)
            
            # Test Gherkin integration
            results["gherkin_integration"] = await self.test_gherkin_integration(browser_command)
            
            # Test error handling
            error_command = "open nonexistentwebsite123456.com, search for something"
            results["error_handling"] = await self.test_error_handling(error_command)
            
        except Exception as e:
            logger.error(f"Error running integration tests: {e}")
            results["status"] = "failed"
            results["error"] = str(e)
        
        # Save the overall results to a file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        result_path = os.path.join(self.test_results_dir, f"all_tests_{timestamp}.json")
        with open(result_path, "w") as f:
            json.dump(results, f, indent=2)
        
        return results

# Run the integration tests if this module is executed directly
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Create a new event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # Run the integration tests
    tester = IntegrationTester()
    results = loop.run_until_complete(tester.run_all_tests())
    
    # Print the results
    print(json.dumps(results, indent=2))

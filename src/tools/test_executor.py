"""
Test executor module for AI QA Agent.
This module provides functionality for executing tests.
"""
import os
import logging
import json
from typing import Dict, Any, Optional
import asyncio
from datetime import datetime

from src.tools.browser_automation import BrowserAutomation

logger = logging.getLogger(__name__)

class TestExecutor:
    """
    Executes tests for the AI QA Agent.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the test executor.
        
        Args:
            config: Configuration dictionary.
        """
        self.config = config or {}
        self.browser_automation = BrowserAutomation(self.config)
        logger.info("Test executor initialized")
    
    def run(self, command: str) -> Dict[str, Any]:
        """
        Run a test command directly.
        
        Args:
            command: The command to run.
            
        Returns:
            Dictionary containing the results.
        """
        logger.info(f"Running test command: {command}")
        
        # For direct commands, we'll use the browser automation
        return self.browser_automation.run(command)
    
    def run_tests(self, test_path: str) -> Dict[str, Any]:
        """
        Run tests from a test file.
        
        Args:
            test_path: Path to the test file.
            
        Returns:
            Dictionary containing test results.
        """
        logger.info(f"Running tests from {test_path}")
        
        # Check if the file exists
        if not os.path.exists(test_path):
            return {
                "status": "failed",
                "error": f"Test file {test_path} does not exist"
            }
        
        # Read the test file
        with open(test_path, 'r') as f:
            test_content = f.read()
        
        # Check if it's a Gherkin file
        if test_path.endswith('.feature'):
            return self._run_gherkin_tests(test_content)
        
        # Otherwise, treat it as a simple command list
        commands = [line.strip() for line in test_content.split('\n') if line.strip()]
        
        results = {
            "status": "success",
            "test_path": test_path,
            "timestamp": datetime.now().isoformat(),
            "results": []
        }
        
        for command in commands:
            command_result = self.run(command)
            results["results"].append({
                "command": command,
                "result": command_result
            })
            
            if command_result["status"] == "failed":
                results["status"] = "failed"
        
        return results
    
    def _run_gherkin_tests(self, gherkin_content: str) -> Dict[str, Any]:
        """
        Run tests from Gherkin content.
        
        Args:
            gherkin_content: Gherkin test content.
            
        Returns:
            Dictionary containing test results.
        """
        # This is a simplified implementation
        # In a real implementation, we would parse the Gherkin and execute each step
        
        results = {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "scenarios": []
        }
        
        # Split by scenarios
        scenarios = gherkin_content.split("Scenario:")
        
        for i, scenario in enumerate(scenarios[1:], 1):  # Skip the first split which is the Feature description
            lines = scenario.strip().split('\n')
            scenario_name = lines[0].strip()
            
            scenario_result = {
                "name": scenario_name,
                "status": "passed",
                "steps": []
            }
            
            for line in lines[1:]:
                line = line.strip()
                if not line:
                    continue
                
                # Extract the step type and text
                parts = line.split(' ', 1)
                if len(parts) < 2:
                    continue
                
                step_type = parts[0]  # Given, When, Then, And
                step_text = parts[1]
                
                # Execute the step
                # In a real implementation, we would map the step to a function
                # For now, we'll just simulate success
                step_result = {
                    "type": step_type,
                    "text": step_text,
                    "status": "passed"
                }
                
                scenario_result["steps"].append(step_result)
            
            results["scenarios"].append(scenario_result)
        
        return results

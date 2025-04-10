"""
Browser automation integration with Gherkin for AI QA Agent.
This module provides functionality for executing Gherkin scenarios using browser automation.
"""
import os
import logging
import asyncio
import json
import re
from typing import Dict, List, Any, Optional, Union
from datetime import datetime

from src.browser_automation import BrowserAutomation
from src.gherkin_translator import GherkinTranslator

logger = logging.getLogger(__name__)

class GherkinExecutor:
    """
    Executes Gherkin scenarios using browser automation.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the Gherkin executor.
        
        Args:
            config: Configuration dictionary.
        """
        self.config = config or {}
        self.browser_automation = None
        self.gherkin_translator = GherkinTranslator()
        self.screenshots_dir = self.config.get("screenshots_dir", "/tmp/gherkin_screenshots")
        os.makedirs(self.screenshots_dir, exist_ok=True)
        logger.info("Gherkin executor initialized")
    
    async def execute_gherkin(self, gherkin_text: str) -> Dict[str, Any]:
        """
        Execute a Gherkin scenario using browser automation.
        
        Args:
            gherkin_text: Gherkin scenario text.
            
        Returns:
            Dictionary containing execution results.
        """
        logger.info("Executing Gherkin scenario")
        
        # Parse the Gherkin text
        scenarios = self._parse_gherkin(gherkin_text)
        
        # Initialize browser automation
        self.browser_automation = BrowserAutomation(self.config)
        await self.browser_automation.start()
        
        results = {
            "feature": self._extract_feature_name(gherkin_text),
            "scenarios": [],
            "status": "passed",
            "timestamp": datetime.now().isoformat(),
            "screenshots": []
        }
        
        try:
            # Execute each scenario
            for scenario in scenarios:
                scenario_result = await self._execute_scenario(scenario)
                results["scenarios"].append(scenario_result)
                
                # Update overall status
                if scenario_result["status"] == "failed":
                    results["status"] = "failed"
                elif scenario_result["status"] == "warning" and results["status"] != "failed":
                    results["status"] = "warning"
                
                # Add screenshots to overall results
                results["screenshots"].extend(scenario_result.get("screenshots", []))
        finally:
            # Stop the browser
            await self.browser_automation.stop()
        
        return results
    
    def _parse_gherkin(self, gherkin_text: str) -> List[Dict[str, Any]]:
        """
        Parse Gherkin text into a structured format.
        
        Args:
            gherkin_text: Gherkin scenario text.
            
        Returns:
            List of dictionaries representing scenarios.
        """
        scenarios = []
        current_scenario = None
        current_step_type = None
        
        for line in gherkin_text.split('\n'):
            line = line.strip()
            
            if not line or line.startswith('#'):
                continue
                
            if line.startswith('Feature:'):
                continue
                
            if line.startswith('Scenario:') or line.startswith('Scenario Outline:'):
                if current_scenario:
                    scenarios.append(current_scenario)
                
                scenario_name = line.split(':', 1)[1].strip()
                current_scenario = {
                    "name": scenario_name,
                    "steps": []
                }
                current_step_type = None
                
            elif line.startswith('Given '):
                current_step_type = "Given"
                step_text = line[6:].strip()
                if current_scenario:
                    current_scenario["steps"].append({
                        "type": "Given",
                        "text": step_text
                    })
                    
            elif line.startswith('When '):
                current_step_type = "When"
                step_text = line[5:].strip()
                if current_scenario:
                    current_scenario["steps"].append({
                        "type": "When",
                        "text": step_text
                    })
                    
            elif line.startswith('Then '):
                current_step_type = "Then"
                step_text = line[5:].strip()
                if current_scenario:
                    current_scenario["steps"].append({
                        "type": "Then",
                        "text": step_text
                    })
                    
            elif line.startswith('And ') or line.startswith('But '):
                step_text = line[4:].strip()
                if current_scenario and current_step_type:
                    current_scenario["steps"].append({
                        "type": current_step_type,
                        "text": step_text
                    })
        
        # Add the last scenario
        if current_scenario:
            scenarios.append(current_scenario)
        
        return scenarios
    
    def _extract_feature_name(self, gherkin_text: str) -> str:
        """
        Extract the feature name from Gherkin text.
        
        Args:
            gherkin_text: Gherkin scenario text.
            
        Returns:
            Feature name.
        """
        for line in gherkin_text.split('\n'):
            line = line.strip()
            if line.startswith('Feature:'):
                return line.split(':', 1)[1].strip()
        
        return "Unnamed Feature"
    
    async def _execute_scenario(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a single Gherkin scenario.
        
        Args:
            scenario: Dictionary representing a Gherkin scenario.
            
        Returns:
            Dictionary containing execution results.
        """
        logger.info(f"Executing scenario: {scenario['name']}")
        
        scenario_result = {
            "name": scenario["name"],
            "steps": [],
            "status": "passed",
            "screenshots": []
        }
        
        for i, step in enumerate(scenario["steps"]):
            step_result = await self._execute_step(step, i)
            scenario_result["steps"].append(step_result)
            
            # Update scenario status based on step status
            if step_result["status"] == "failed":
                scenario_result["status"] = "failed"
                # Don't break here, continue executing steps for better reporting
            elif step_result["status"] == "warning" and scenario_result["status"] != "failed":
                scenario_result["status"] = "warning"
            
            # Add screenshot to scenario results
            if "screenshot" in step_result:
                scenario_result["screenshots"].append(step_result["screenshot"])
        
        return scenario_result
    
    async def _execute_step(self, step: Dict[str, Any], step_index: int) -> Dict[str, Any]:
        """
        Execute a single Gherkin step.
        
        Args:
            step: Dictionary representing a Gherkin step.
            step_index: Index of the step in the scenario.
            
        Returns:
            Dictionary containing execution results.
        """
        step_type = step["type"]
        step_text = step["text"]
        
        logger.info(f"Executing {step_type} step: {step_text}")
        
        step_result = {
            "type": step_type,
            "text": step_text,
            "status": "passed"
        }
        
        try:
            # Execute the step based on its type and text
            if step_type == "Given":
                await self._execute_given_step(step_text)
            elif step_type == "When":
                await self._execute_when_step(step_text)
            elif step_type == "Then":
                await self._execute_then_step(step_text)
            
            # Take a screenshot after the step
            screenshot_path = os.path.join(self.screenshots_dir, f"step_{step_index+1}.png")
            await self.browser_automation.take_screenshot(screenshot_path)
            step_result["screenshot"] = screenshot_path
            
        except Exception as e:
            logger.error(f"Error executing step: {e}")
            step_result["status"] = "failed"
            step_result["error"] = str(e)
            
            # Take a screenshot of the error
            screenshot_path = os.path.join(self.screenshots_dir, f"step_{step_index+1}_error.png")
            await self.browser_automation.take_screenshot(screenshot_path)
            step_result["screenshot"] = screenshot_path
            
            # Try to recover from the error
            error_type = self._determine_error_type(str(e))
            recovery_successful = await self.browser_automation.recover_from_error(error_type)
            
            if recovery_successful:
                step_result["recovery"] = "Automatic recovery was successful"
                step_result["status"] = "warning"
            else:
                step_result["recovery"] = "Automatic recovery failed"
        
        return step_result
    
    async def _execute_given_step(self, step_text: str):
        """
        Execute a Given step.
        
        Args:
            step_text: Text of the Given step.
        """
        # Handle common Given patterns
        if "I am on" in step_text or "I navigate to" in step_text or "I open" in step_text:
            # Extract URL
            url_match = re.search(r'(?:I am on|I navigate to|I open) (?:the )?(.*?)(?:page|website|site)?$', step_text)
            if url_match:
                url = url_match.group(1).strip()
                # Add https:// if not present
                if not url.startswith(('http://', 'https://')):
                    url = f"https://{url}"
                await self.browser_automation.navigate(url)
            else:
                raise ValueError(f"Could not extract URL from step: {step_text}")
        else:
            # Default handling for other Given steps
            logger.warning(f"No specific implementation for Given step: {step_text}")
    
    async def _execute_when_step(self, step_text: str):
        """
        Execute a When step.
        
        Args:
            step_text: Text of the When step.
        """
        # Handle common When patterns
        if "I search for" in step_text:
            # Extract search term
            search_match = re.search(r'I search for "(.*?)"', step_text)
            if search_match:
                search_term = search_match.group(1)
                # Determine search engine based on current URL
                if self.browser_automation.page and "tokopedia.com" in self.browser_automation.page.url:
                    await self.browser_automation.search(search_term, "tokopedia")
                else:
                    await self.browser_automation.search(search_term)
            else:
                raise ValueError(f"Could not extract search term from step: {step_text}")
                
        elif "I sort" in step_text and "price" in step_text:
            # Extract sort order
            if "lowest" in step_text or "ascending" in step_text:
                await self.browser_automation.sort_by_price("lowest")
            elif "highest" in step_text or "descending" in step_text:
                await self.browser_automation.sort_by_price("highest")
            else:
                raise ValueError(f"Could not determine sort order from step: {step_text}")
                
        elif "I click" in step_text:
            # This would require more sophisticated element selection
            # For now, just log a warning
            logger.warning(f"Click action not fully implemented for step: {step_text}")
            
        else:
            # Default handling for other When steps
            logger.warning(f"No specific implementation for When step: {step_text}")
    
    async def _execute_then_step(self, step_text: str):
        """
        Execute a Then step.
        
        Args:
            step_text: Text of the Then step.
        """
        # Handle common Then patterns
        if "I should see" in step_text:
            # Extract expected text
            text_match = re.search(r'I should see "(.*?)"', step_text)
            if text_match:
                expected_text = text_match.group(1)
                # Check if the text is present on the page
                page_content = await self.browser_automation.page.content()
                if expected_text not in page_content:
                    raise AssertionError(f"Expected text '{expected_text}' not found on page")
            else:
                raise ValueError(f"Could not extract expected text from step: {step_text}")
                
        else:
            # Default handling for other Then steps
            logger.warning(f"No specific implementation for Then step: {step_text}")
    
    def _determine_error_type(self, error_message: str) -> str:
        """
        Determine the type of error based on the error message.
        
        Args:
            error_message: Error message.
            
        Returns:
            Error type.
        """
        if "navigation" in error_message.lower() or "timeout" in error_message.lower():
            return "navigation"
        elif "element not found" in error_message.lower() or "no element" in error_message.lower():
            return "element_not_found"
        elif "popup" in error_message.lower() or "dialog" in error_message.lower():
            return "popup"
        else:
            return "unknown"
    
    def convert_browser_command_to_gherkin(self, command: str) -> str:
        """
        Convert a browser automation command to Gherkin format.
        
        Args:
            command: Browser automation command.
            
        Returns:
            Gherkin scenario text.
        """
        logger.info(f"Converting browser command to Gherkin: {command}")
        
        # Split the command into parts
        command_parts = [part.strip() for part in command.split(',')]
        
        # Create a natural language description
        description = f"Test for {command}"
        
        # Convert to Gherkin using the translator
        gherkin_text = self.gherkin_translator.translate_to_gherkin(description)
        
        # If the translator didn't produce valid Gherkin, create it manually
        if not gherkin_text or "Feature:" not in gherkin_text:
            feature_name = "Browser Automation Test"
            scenario_name = "Execute browser commands"
            
            gherkin_text = f"Feature: {feature_name}\n\n"
            gherkin_text += f"  Scenario: {scenario_name}\n"
            
            # Add steps based on command parts
            for i, part in enumerate(command_parts):
                if i == 0:
                    # First part is usually navigation
                    if part.startswith("open "):
                        url = part[5:].strip()
                        gherkin_text += f"    Given I am on {url}\n"
                    else:
                        gherkin_text += f"    Given I perform the action: {part}\n"
                else:
                    # Subsequent parts are usually actions
                    if "search for" in part:
                        search_term = part.split("search for")[1].strip()
                        gherkin_text += f'    When I search for "{search_term}"\n'
             
(Content truncated due to size limit. Use line ranges to read in chunks)
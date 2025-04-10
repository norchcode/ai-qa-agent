"""
Browser automation module for AI QA Agent.
This module provides functionality for automating browser interactions.
"""
import os
import logging
import json
import tempfile
from typing import Dict, Any, List
from playwright.sync_api import sync_playwright

logger = logging.getLogger(__name__)

class BrowserAutomation:
    """
    Automates browser interactions for testing.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the browser automation.
        
        Args:
            config: Configuration dictionary.
        """
        self.config = config or {}
        self.browser_type = self.config.get("browser_type", "chromium")
        self.headless = self.config.get("headless", False)
        
        # Parse resolution
        resolution = self.config.get("browser_resolution", "1920,1080")
        try:
            width, height = map(int, resolution.split(","))
            self.viewport_size = {"width": width, "height": height}
        except:
            self.viewport_size = {"width": 1920, "height": 1080}
        
        logger.info(f"Initialized browser automation with {self.browser_type} browser")
    
    def run(self, command: str) -> Dict[str, Any]:
        """
        Run a browser automation command.
        
        Args:
            command: The command to run.
            
        Returns:
            Dictionary containing the results.
        """
        logger.info(f"Running browser automation command: {command}")
        
        # Parse the command into steps
        steps = self._parse_command(command)
        
        # Execute the steps
        results = {
            "status": "success",
            "steps": [],
            "screenshots": []
        }
        
        with sync_playwright() as p:
            # Launch the browser
            browser_obj = getattr(p, self.browser_type.lower())
            browser = browser_obj.launch(headless=self.headless)
            
            # Create a new context with viewport size
            context = browser.new_context(viewport=self.viewport_size)
            
            # Create a new page
            page = context.new_page()
            
            # Create a directory for screenshots
            screenshot_dir = tempfile.mkdtemp()
            
            try:
                # Execute each step
                for i, step in enumerate(steps):
                    step_result = self._execute_step(page, step)
                    
                    # Take a screenshot after each step
                    screenshot_path = os.path.join(screenshot_dir, f"step_{i+1}.png")
                    page.screenshot(path=screenshot_path)
                    
                    # Add the step result and screenshot path to the results
                    results["steps"].append(step_result)
                    results["screenshots"].append(screenshot_path)
                    
                    # If the step failed, stop execution
                    if step_result["status"] == "failed":
                        results["status"] = "failed"
                        break
            
            except Exception as e:
                logger.error(f"Error executing browser automation: {e}")
                results["status"] = "failed"
                results["error"] = str(e)
            
            finally:
                # Close the browser
                browser.close()
        
        return results
    
    def _parse_command(self, command: str) -> List[Dict[str, str]]:
        """
        Parse a command into steps.
        
        Args:
            command: The command to parse.
            
        Returns:
            List of steps.
        """
        # Split the command by commas
        parts = [part.strip() for part in command.split(",")]
        
        steps = []
        for part in parts:
            # Identify the action and target
            if part.lower().startswith("open "):
                url = part[5:].strip()
                if not url.startswith(("http://", "https://")):
                    url = "https://" + url
                steps.append({"action": "open", "url": url})
            
            elif part.lower().startswith("search for "):
                query = part[11:].strip()
                steps.append({"action": "search", "query": query})
            
            elif part.lower().startswith("click on "):
                target = part[9:].strip()
                steps.append({"action": "click", "target": target})
            
            elif part.lower().startswith("sort "):
                # Handle various sort commands
                if "by" in part.lower():
                    field = part.lower().split("by")[1].strip()
                    steps.append({"action": "sort", "field": field})
                elif "the" in part.lower():
                    field = part.lower().split("the")[1].strip()
                    steps.append({"action": "sort", "field": field})
                else:
                    field = part[5:].strip()
                    steps.append({"action": "sort", "field": field})
            
            elif part.lower().startswith("fill "):
                # Handle fill commands
                if "with" in part.lower():
                    field, value = part[5:].split("with", 1)
                    steps.append({"action": "fill", "field": field.strip(), "value": value.strip()})
                else:
                    steps.append({"action": "fill", "field": part[5:].strip()})
            
            else:
                # Default to a generic command
                steps.append({"action": "custom", "command": part})
        
        return steps
    
    def _execute_step(self, page, step: Dict[str, str]) -> Dict[str, Any]:
        """
        Execute a single step.
        
        Args:
            page: The Playwright page object.
            step: The step to execute.
            
        Returns:
            Dictionary containing the step result.
        """
        action = step["action"]
        result = {
            "step": action,
            "command": json.dumps(step),
            "status": "passed",
            "details": ""
        }
        
        try:
            if action == "open":
                url = step["url"]
                page.goto(url)
                result["details"] = f"Opened {url}"
            
            elif action == "search":
                query = step["query"]
                # Look for a search input
                search_input = page.query_selector('input[type="search"], input[name="q"], input[name="search"], input[placeholder*="search" i]')
                if search_input:
                    search_input.fill(query)
                    search_input.press("Enter")
                    result["details"] = f"Searched for {query}"
                else:
                    result["status"] = "warning"
                    result["details"] = "Could not find search input"
            
            elif action == "click":
                target = step["target"]
                # Try to find the element by text
                element = page.query_selector(f'text="{target}"')
                if element:
                    element.click()
                    result["details"] = f"Clicked on {target}"
                else:
                    # Try to find by other common attributes
                    selectors = [
                        f'[aria-label*="{target}" i]',
                        f'[title*="{target}" i]',
                        f'[alt*="{target}" i]',
                        f'button:has-text("{target}")',
                        f'a:has-text("{target}")'
                    ]
                    
                    found = False
                    for selector in selectors:
                        try:
                            element = page.query_selector(selector)
                            if element:
                                element.click()
                                result["details"] = f"Clicked on {target} using selector {selector}"
                                found = True
                                break
                        except:
                            continue
                    
                    if not found:
                        result["status"] = "warning"
                        result["details"] = f"Could not find element {target}"
            
            elif action == "sort":
                field = step["field"]
                # Try to find sort options
                selectors = [
                    f'[aria-label*="sort" i][aria-label*="{field}" i]',
                    f'button:has-text("sort")',
                    f'select[name*="sort" i]',
                    f'a:has-text("sort")',
                    f'[data-testid*="sort" i]'
                ]
                
                found = False
                for selector in selectors:
                    try:
                        element = page.query_selector(selector)
                        if element:
                            element.click()
                            result["details"] = f"Clicked sort option for {field}"
                            found = True
                            break
                    except:
                        continue
                
                if not found:
                    # Try to find the field name in any clickable element
                    try:
                        page.click(f'text="{field}"')
                        result["details"] = f"Clicked on {field} text"
                        found = True
                    except:
                        pass
                
                if not found:
                    result["status"] = "warning"
                    result["details"] = f"Could not find sort option for {field}"
            
            elif action == "fill":
                field = step["field"]
                value = step.get("value", "")
                
                # Try to find the input field
                selectors = [
                    f'input[name*="{field}" i]',
                    f'input[placeholder*="{field}" i]',
                    f'input[aria-label*="{field}" i]',
                    f'textarea[name*="{field}" i]',
                    f'textarea[placeholder*="{field}" i]',
                    f'textarea[aria-label*="{field}" i]',
                    f'label:has-text("{field}") input',
                    f'label:has-text("{field}") textarea'
                ]
                
                found = False
                for selector in selectors:
                    try:
                        element = page.query_selector(selector)
                        if element:
                            element.fill(value)
                            result["details"] = f"Filled {field} with {value}"
                            found = True
                            break
                    except:
                        continue
                
                if not found:
                    result["status"] = "warning"
                    result["details"] = f"Could not find input field {field}"
            
            elif action == "custom":
                command = step["command"]
                result["details"] = f"Executed custom command: {command}"
                result["status"] = "warning"
                result["details"] = "Custom commands are not fully implemented"
        
        except Exception as e:
            logger.error(f"Error executing step {action}: {e}")
            result["status"] = "failed"
            result["details"] = f"Error: {str(e)}"
        
        return result

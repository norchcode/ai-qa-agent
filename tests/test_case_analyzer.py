"""
Test Case Analyzer module for AI QA Agent.
This module provides functionality for analyzing and improving test cases.
"""
import os
import logging
import json
from typing import Dict, List, Any, Optional, Union
import re

from llm_integration import get_llm_integration

logger = logging.getLogger(__name__)

class TestCaseAnalyzer:
    """Analyzer for test cases to identify issues and suggest improvements."""
    
    def __init__(self, llm_provider: str = "groq"):
        """
        Initialize the Test Case Analyzer.
        
        Args:
            llm_provider: The LLM provider to use for analysis.
        """
        self.llm = get_llm_integration(llm_provider)
        logger.info(f"Initialized Test Case Analyzer with LLM provider: {llm_provider}")
    
    def parse_gherkin(self, gherkin_text: str) -> Dict[str, Any]:
        """
        Parse Gherkin text into a structured format.
        
        Args:
            gherkin_text: The Gherkin text to parse.
            
        Returns:
            Dictionary containing the parsed Gherkin structure.
        """
        result = {
            "feature": "",
            "scenarios": []
        }
        
        current_scenario = None
        current_step_type = None
        
        for line in gherkin_text.split('\n'):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
                
            # Feature
            if line.startswith('Feature:'):
                result['feature'] = line[8:].strip()
            
            # Scenario or Scenario Outline
            elif line.startswith('Scenario:') or line.startswith('Scenario Outline:'):
                if current_scenario:
                    result['scenarios'].append(current_scenario)
                
                scenario_type = 'outline' if line.startswith('Scenario Outline:') else 'normal'
                title = line[line.index(':') + 1:].strip()
                
                current_scenario = {
                    'title': title,
                    'type': scenario_type,
                    'given': [],
                    'when': [],
                    'then': [],
                    'and': [],
                    'but': [],
                    'examples': []
                }
            
            # Steps
            elif line.startswith('Given '):
                current_step_type = 'given'
                current_scenario[current_step_type].append(line[6:].strip())
            elif line.startswith('When '):
                current_step_type = 'when'
                current_scenario[current_step_type].append(line[5:].strip())
            elif line.startswith('Then '):
                current_step_type = 'then'
                current_scenario[current_step_type].append(line[5:].strip())
            elif line.startswith('And ') and current_step_type:
                current_scenario[current_step_type].append(line[4:].strip())
            elif line.startswith('But ') and current_step_type:
                current_scenario[current_step_type].append(line[4:].strip())
            
            # Examples
            elif line.startswith('Examples:'):
                current_step_type = 'examples'
            elif current_step_type == 'examples' and '|' in line:
                current_scenario['examples'].append(line.strip())
        
        # Add the last scenario
        if current_scenario:
            result['scenarios'].append(current_scenario)
            
        return result
    
    def analyze_test_case(self, test_case: str) -> Dict[str, Any]:
        """
        Analyze a test case to identify issues and improvement opportunities.
        
        Args:
            test_case: The test case to analyze, in Gherkin format.
            
        Returns:
            Dictionary containing analysis results.
        """
        logger.info("Analyzing test case")
        
        # Parse the Gherkin structure
        parsed_test_case = self.parse_gherkin(test_case)
        
        # Use LLM to analyze the test case
        llm_analysis = self.llm.analyze_test_case(test_case)
        
        # Perform additional rule-based analysis
        rule_based_analysis = self._rule_based_analysis(parsed_test_case)
        
        # Combine the analyses
        combined_analysis = {
            "llm_analysis": llm_analysis,
            "rule_based_analysis": rule_based_analysis,
            "parsed_structure": parsed_test_case
        }
        
        return combined_analysis
    
    def _rule_based_analysis(self, parsed_test_case: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform rule-based analysis on a parsed test case.
        
        Args:
            parsed_test_case: The parsed test case structure.
            
        Returns:
            Dictionary containing rule-based analysis results.
        """
        issues = []
        warnings = []
        suggestions = []
        
        # Check for empty sections
        for scenario in parsed_test_case.get('scenarios', []):
            if not scenario.get('given', []):
                warnings.append(f"Scenario '{scenario['title']}' has no Given steps")
            if not scenario.get('when', []):
                warnings.append(f"Scenario '{scenario['title']}' has no When steps")
            if not scenario.get('then', []):
                issues.append(f"Scenario '{scenario['title']}' has no Then steps (no assertions)")
            
            # Check for scenario outline without examples
            if scenario['type'] == 'outline' and not scenario.get('examples', []):
                issues.append(f"Scenario Outline '{scenario['title']}' has no Examples")
            
            # Check for assertions in Then steps
            for then_step in scenario.get('then', []):
                if not any(word in then_step.lower() for word in ['should', 'expect', 'verify', 'check', 'assert', 'validate', 'confirm']):
                    warnings.append(f"Then step '{then_step}' may not contain an assertion")
            
            # Check for UI locators in steps
            for step_type in ['given', 'when', 'then']:
                for step in scenario.get(step_type, []):
                    if re.search(r'(id|class|xpath|css|selector)=[\'"]', step, re.IGNORECASE):
                        warnings.append(f"Step '{step}' contains hardcoded locators which may be fragile")
        
        # Check for feature description
        if not parsed_test_case.get('feature', ''):
            warnings.append("Test case has no Feature description")
        
        return {
            "issues": issues,
            "warnings": warnings,
            "suggestions": suggestions
        }
    
    def suggest_improvements(self, test_case: str, execution_results: Optional[Dict[str, Any]] = None) -> List[str]:
        """
        Suggest improvements for a test case.
        
        Args:
            test_case: The test case in Gherkin format.
            execution_results: Optional dictionary containing test execution results.
            
        Returns:
            List of suggested improvements.
        """
        logger.info("Suggesting improvements for test case")
        
        # If execution results are provided, use them for more targeted suggestions
        if execution_results:
            return self.llm.suggest_test_improvements(test_case, execution_results)
        
        # Otherwise, analyze the test case and generate suggestions based on the analysis
        analysis = self.analyze_test_case(test_case)
        
        suggestions = []
        
        # Add suggestions from rule-based analysis
        for issue in analysis['rule_based_analysis']['issues']:
            suggestions.append(f"Fix issue: {issue}")
        
        for warning in analysis['rule_based_analysis']['warnings']:
            suggestions.append(f"Address warning: {warning}")
        
        for suggestion in analysis['rule_based_analysis']['suggestions']:
            suggestions.append(suggestion)
        
        # Add suggestions from LLM analysis
        if 'improvement_suggestions' in analysis['llm_analysis']:
            if isinstance(analysis['llm_analysis']['improvement_suggestions'], list):
                suggestions.extend(analysis['llm_analysis']['improvement_suggestions'])
            else:
                suggestions.append(str(analysis['llm_analysis']['improvement_suggestions']))
        
        if 'missing_validations' in analysis['llm_analysis']:
            if isinstance(analysis['llm_analysis']['missing_validations'], list):
                for validation in analysis['llm_analysis']['missing_validations']:
                    suggestions.append(f"Add missing validation: {validation}")
            else:
                suggestions.append(f"Add missing validation: {analysis['llm_analysis']['missing_validations']}")
        
        return suggestions
    
    def optimize_test_case(self, test_case: str) -> str:
        """
        Optimize a test case based on analysis and suggestions.
        
        Args:
            test_case: The test case in Gherkin format.
            
        Returns:
            Optimized test case in Gherkin format.
        """
        logger.info("Optimizing test case")
        
        # Analyze the test case
        analysis = self.analyze_test_case(test_case)
        
        # Generate suggestions
        suggestions = self.suggest_improvements(test_case)
        
        # Use LLM to optimize the test case based on analysis and suggestions
        system_prompt = """
        You are a QA expert specialized in optimizing test cases. Your goal is to improve test cases
        based on analysis and suggestions. Focus on making the test case more reliable, efficient, and effective.
        Always return the complete optimized test case in Gherkin format.
        """
        
        prompt = f"""
        Here is a test case:
        
        ```gherkin
        {test_case}
        ```
        
        Here is the analysis of the test case:
        
        ```json
        {json.dumps(analysis, indent=2)}
        ```
        
        Here are suggestions for improvement:
        
        {json.dumps(suggestions, indent=2)}
        
        Please optimize this test case based on the analysis and suggestions.
        Focus on:
        1. Fixing identified issues
        2. Addressing warnings
        3. Implementing suggested improvements
        4. Making the test case more reliable and maintainable
        
        Return the complete optimized test case in Gherkin format.
        """
        
        optimized_test_case = self.llm.generate_completion(prompt, system_prompt)
        
        # Extract the Gherkin content from the response
        gherkin_pattern = r'```gherkin\s*(.*?)\s*```'
        match = re.search(gherkin_pattern, optimized_test_case, re.DOTALL)
        if match:
            optimized_test_case = match.group(1).strip()
        
        return optimized_test_case
    
    def analyze_error(self, error_message: str, test_step: str, screenshot_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze an error that occurred during test execution.
        
        Args:
            error_message: The error message from the test execution.
            test_step: The test step that failed.
            screenshot_path: Optional path to a screenshot taken at the time of the error.
            
        Returns:
            Dictionary containing error analysis and suggested fixes.
        """
        logger.info(f"Analyzing error for test step: {test_step}")
        
        return self.llm.analyze_error(error_message, test_step, screenshot_path)
    
    def suggest_alternative_steps(self, failed_step: str, error_message: str) -> List[str]:
        """
        Suggest alternative steps when a test step fails.
        
        Args:
            failed_step: The test step that failed.
            error_message: The error message from the test execution.
            
        Returns:
            List of alternative steps that might work.
        """
        logger.info(f"Suggesting alternative steps for failed step: {failed_step}")
        
        system_prompt = """
        You are a QA expert specialized in fixing failing test steps. Your goal is to suggest
        alternative steps that might work when a test step fails. Focus on practical, actionable
        alternatives that address the underlying issues.
        """
        
        prompt = f"""
        A test step failed during execution:
        
        Failed Step: {failed_step}
        
        Error Message: {error_message}
        
        Please suggest 3-5 alternative steps that might work instead of the failing step.
        Consider different approaches to achieve the same goal, such as:
        1. Using different selectors or locators
        2. Breaking the step into multiple smaller steps
        3. Adding explicit waits or synchronization
        4. Using alternative UI interactions
        5. Working around potential timing issues
        
        Return a list of specific, executable alternative steps in Gherkin format.
        """
        
        result = self.llm.generate_completion(prompt, system_prompt)
        
        # Extract steps from the result
        alternative_steps = []
        for line in result.split('\n'):
            line = line.strip()
            if line and (line.startswith('Given ') or line.startswith('When ') or line.startswith('Then ') or 
                         line.startswith('And ') or line.startswith('But ')):
                alternative_steps.append(line)
            elif line and (line.startswith('- Given ') or line.startswith('- When ') or line.startswith('- Then ') or 
                           line.startswith('- And ') or line.startswith('- But ')):
                alternative_steps.append(line[2:])  # Remove the leading "- "
        
        # If no steps were extracted, try to extract numbered items
        if not alternative_steps:
            numbered_pattern = r'\d+\.\s+(.*)'
            matches = re.findall(numbered_pattern, result)
            alternative_steps = matches
        
        # If still no steps, return the whole result split by lines
        if not alternative_steps:
            alternative_steps = [line.strip() for line in result.split('\n') if line.strip()]
        
        return alternative_steps

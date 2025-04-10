"""
Gherkin translator module for AI QA Agent.
This module provides functionality for translating between Gherkin and natural language.
"""
import os
import logging
import re
from typing import Dict, List, Any, Optional, Union
import json

from src.core.llm_integration import LLMProvider

logger = logging.getLogger(__name__)

class GherkinTranslator:
    """
    Translates between Gherkin and natural language.
    """
    
    def __init__(self, llm_provider):
        """
        Initialize the Gherkin translator.
        
        Args:
            llm_provider: LLM provider for translation.
        """
        self.llm_provider = llm_provider
        logger.info("Gherkin translator initialized")
    
    def translate_to_gherkin(self, natural_language: str) -> str:
        """
        Translate natural language test steps to Gherkin format.
        
        Args:
            natural_language: Natural language test steps.
            
        Returns:
            Gherkin format test case.
        """
        # Placeholder implementation
        # In a real implementation, this would use the LLM to translate
        
        # Simple pattern matching for demo purposes
        lines = natural_language.strip().split('\n')
        
        # Extract a feature name from the first line or use a default
        feature_name = "Automated Test"
        if lines and not lines[0].startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.')):
            feature_name = lines[0]
            lines = lines[1:]
        
        # Start building the Gherkin
        gherkin = f"Feature: {feature_name}\n\n"
        gherkin += "  Scenario: Automated test scenario\n"
        
        # Process each line
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # Remove numbering if present
            if re.match(r'^\d+\.', line):
                line = re.sub(r'^\d+\.', '', line).strip()
            
            # Determine the step type
            if i == 0:
                step_type = "Given"
            elif i == len(lines) - 1:
                step_type = "Then"
            else:
                step_type = "When"
            
            gherkin += f"    {step_type} {line}\n"
        
        return gherkin
    
    def translate_from_gherkin(self, gherkin: str) -> str:
        """
        Translate Gherkin format test case to natural language.
        
        Args:
            gherkin: Gherkin format test case.
            
        Returns:
            Natural language test steps.
        """
        # Placeholder implementation
        # In a real implementation, this would use the LLM to translate
        
        # Simple pattern matching for demo purposes
        lines = gherkin.strip().split('\n')
        
        natural_language = ""
        step_number = 1
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines and non-step lines
            if not line or not any(line.startswith(prefix) for prefix in ["Given ", "When ", "Then ", "And ", "But "]):
                continue
            
            # Extract the step text
            step_text = re.sub(r'^(Given|When|Then|And|But)\s+', '', line)
            
            # Add to natural language
            natural_language += f"{step_number}. {step_text}\n"
            step_number += 1
        
        return natural_language
    
    def generate_from_description(self, description: str) -> str:
        """
        Generate Gherkin test cases from a feature description.
        
        Args:
            description: Feature description.
            
        Returns:
            Gherkin format test cases.
        """
        # Placeholder implementation
        # In a real implementation, this would use the LLM to generate
        
        # Simple pattern matching for demo purposes
        feature_name = "Generated Test"
        
        # Try to extract a feature name from the first line
        lines = description.strip().split('\n')
        if lines:
            feature_name = lines[0]
        
        # Generate a simple Gherkin test
        gherkin = f"Feature: {feature_name}\n\n"
        gherkin += "  Scenario: Basic functionality test\n"
        gherkin += "    Given the application is open\n"
        gherkin += "    When I perform the main action\n"
        gherkin += "    Then I should see the expected result\n\n"
        
        gherkin += "  Scenario: Edge case test\n"
        gherkin += "    Given the application is in a special state\n"
        gherkin += "    When I perform an unusual action\n"
        gherkin += "    Then the system should handle it gracefully\n"
        
        return gherkin

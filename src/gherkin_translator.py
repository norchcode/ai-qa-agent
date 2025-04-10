"""
Gherkin Translator module for AI QA Agent.
This module provides functionality for translating natural language test steps into Gherkin format.
"""
import os
import logging
import json
from typing import Dict, List, Any, Optional, Union
import re

from llm_integration import get_llm_integration

logger = logging.getLogger(__name__)

class GherkinTranslator:
    """Translator for converting natural language test steps into Gherkin format."""
    
    def __init__(self, llm_provider: str = "groq"):
        """
        Initialize the Gherkin Translator.
        
        Args:
            llm_provider: The LLM provider to use for translation.
        """
        self.llm = get_llm_integration(llm_provider)
        logger.info(f"Initialized Gherkin Translator with LLM provider: {llm_provider}")
    
    def translate_to_gherkin(self, test_steps: str) -> str:
        """
        Translate natural language test steps into Gherkin format.
        
        Args:
            test_steps: Natural language test steps, one per line.
            
        Returns:
            Test steps in Gherkin format.
        """
        logger.info("Translating test steps to Gherkin format")
        
        system_prompt = """
        You are a QA expert specialized in translating natural language test steps into Gherkin format.
        Your goal is to convert plain English test steps into proper Gherkin syntax with Given, When, Then, And, and But steps.
        
        Follow these rules:
        1. Start with a Feature description that summarizes the functionality being tested
        2. Create one or more Scenarios based on the test steps
        3. Use Given for preconditions, When for actions, Then for expected outcomes
        4. Use And to extend a Given, When, or Then step
        5. Use proper indentation in the Gherkin output
        6. Be specific and clear in the step descriptions
        7. Ensure the Gherkin is syntactically correct
        
        Always return only the Gherkin format without any additional explanations or markdown formatting.
        """
        
        prompt = f"""
        Please translate the following natural language test steps into Gherkin format:
        
        {test_steps}
        
        Convert these steps into a complete Gherkin feature file with proper Feature, Scenario, Given, When, Then, And structure.
        """
        
        gherkin_result = self.llm.generate_completion(prompt, system_prompt)
        
        # Clean up the result to ensure it's valid Gherkin
        gherkin_result = self._clean_gherkin(gherkin_result)
        
        return gherkin_result
    
    def _clean_gherkin(self, gherkin_text: str) -> str:
        """
        Clean up the generated Gherkin to ensure it's valid.
        
        Args:
            gherkin_text: The raw Gherkin text from the LLM.
            
        Returns:
            Cleaned Gherkin text.
        """
        # Remove any markdown code block formatting
        gherkin_text = re.sub(r'```gherkin\s*', '', gherkin_text)
        gherkin_text = re.sub(r'```\s*', '', gherkin_text)
        
        # Ensure Feature is at the start
        if not gherkin_text.strip().startswith('Feature:'):
            # Try to find a Feature line
            feature_match = re.search(r'Feature:', gherkin_text)
            if feature_match:
                # Remove everything before the Feature line
                gherkin_text = gherkin_text[feature_match.start():]
            else:
                # Add a generic Feature line
                gherkin_text = f"Feature: Automated Test\n{gherkin_text}"
        
        # Ensure proper indentation
        lines = gherkin_text.split('\n')
        indented_lines = []
        
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('Feature:'):
                indented_lines.append(stripped)
            elif stripped.startswith('Scenario:') or stripped.startswith('Scenario Outline:'):
                indented_lines.append(f"  {stripped}")
            elif stripped.startswith('Given ') or stripped.startswith('When ') or stripped.startswith('Then ') or \
                 stripped.startswith('And ') or stripped.startswith('But '):
                indented_lines.append(f"    {stripped}")
            elif stripped.startswith('Examples:'):
                indented_lines.append(f"    {stripped}")
            elif stripped.startswith('|'):
                indented_lines.append(f"      {stripped}")
            elif stripped:
                indented_lines.append(stripped)
        
        return '\n'.join(indented_lines)
    
    def translate_from_gherkin(self, gherkin_text: str) -> str:
        """
        Translate Gherkin format into natural language test steps.
        
        Args:
            gherkin_text: Test steps in Gherkin format.
            
        Returns:
            Natural language test steps.
        """
        logger.info("Translating Gherkin to natural language test steps")
        
        system_prompt = """
        You are a QA expert specialized in translating Gherkin format into natural language test steps.
        Your goal is to convert Gherkin syntax with Given, When, Then, And, and But steps into plain English test steps.
        
        Follow these rules:
        1. Convert each Gherkin step into a clear, natural language instruction
        2. Maintain the logical flow and sequence of the steps
        3. Include all the details from the original Gherkin
        4. Make the steps easy to understand for non-technical stakeholders
        5. Number each step sequentially
        6. Start with a brief summary of what is being tested
        
        Always return only the natural language steps without any additional explanations or markdown formatting.
        """
        
        prompt = f"""
        Please translate the following Gherkin format into natural language test steps:
        
        {gherkin_text}
        
        Convert these Gherkin steps into clear, numbered test steps in plain English that anyone could follow.
        """
        
        natural_language_result = self.llm.generate_completion(prompt, system_prompt)
        
        # Clean up the result
        natural_language_result = self._clean_natural_language(natural_language_result)
        
        return natural_language_result
    
    def _clean_natural_language(self, text: str) -> str:
        """
        Clean up the generated natural language to ensure it's well-formatted.
        
        Args:
            text: The raw natural language text from the LLM.
            
        Returns:
            Cleaned natural language text.
        """
        # Remove any markdown formatting
        text = re.sub(r'```.*?\s*', '', text)
        text = re.sub(r'```\s*', '', text)
        
        # Ensure steps are numbered
        lines = text.split('\n')
        numbered_lines = []
        step_number = 1
        
        for line in lines:
            stripped = line.strip()
            if not stripped:
                numbered_lines.append(stripped)
                continue
                
            # Check if the line is already numbered
            if re.match(r'^\d+\.', stripped):
                numbered_lines.append(stripped)
                # Extract the number to continue numbering correctly
                match = re.match(r'^(\d+)\.', stripped)
                if match:
                    step_number = int(match.group(1)) + 1
            else:
                # Add numbering to lines that look like steps
                if len(stripped) > 5 and not stripped.startswith('#') and not stripped.startswith('Test') and not stripped.startswith('Summary'):
                    numbered_lines.append(f"{step_number}. {stripped}")
                    step_number += 1
                else:
                    numbered_lines.append(stripped)
        
        return '\n'.join(numbered_lines)
    
    def suggest_improvements(self, gherkin_text: str) -> List[str]:
        """
        Suggest improvements for Gherkin test steps.
        
        Args:
            gherkin_text: Test steps in Gherkin format.
            
        Returns:
            List of suggested improvements.
        """
        logger.info("Suggesting improvements for Gherkin test steps")
        
        system_prompt = """
        You are a QA expert specialized in improving Gherkin test scenarios.
        Your goal is to suggest specific improvements to make the Gherkin more effective, maintainable, and clear.
        
        Focus on these aspects:
        1. Clarity and specificity of steps
        2. Proper use of Given/When/Then structure
        3. Avoiding technical implementation details in steps
        4. Making steps reusable and maintainable
        5. Ensuring proper assertions in Then steps
        6. Proper use of scenario outlines and examples
        7. Avoiding ambiguity and vagueness
        
        Return a numbered list of specific, actionable suggestions.
        """
        
        prompt = f"""
        Please review the following Gherkin test steps and suggest improvements:
        
        {gherkin_text}
        
        Provide specific, actionable suggestions to improve the quality, maintainability, and effectiveness of these Gherkin steps.
        """
        
        suggestions_result = self.llm.generate_completion(prompt, system_prompt)
        
        # Extract suggestions into a list
        suggestions = []
        for line in suggestions_result.split('\n'):
            stripped = line.strip()
            if re.match(r'^\d+\.', stripped):
                suggestions.append(stripped)
            elif stripped and suggestions:
                # Append to the last suggestion if it's a continuation
                suggestions[-1] += f" {stripped}"
        
        return suggestions
    
    def generate_gherkin_from_description(self, test_description: str) -> str:
        """
        Generate Gherkin test steps from a high-level test description.
        
        Args:
            test_description: High-level description of what needs to be tested.
            
        Returns:
            Test steps in Gherkin format.
        """
        logger.info("Generating Gherkin from test description")
        
        system_prompt = """
        You are a QA expert specialized in creating Gherkin test scenarios from high-level descriptions.
        Your goal is to create comprehensive, well-structured Gherkin feature files based on test requirements.
        
        Follow these rules:
        1. Create a clear Feature description
        2. Include multiple Scenarios to cover different aspects
        3. Use Given for preconditions, When for actions, Then for expected outcomes
        4. Be specific and detailed in the steps
        5. Include edge cases and negative scenarios
        6. Use Scenario Outlines with Examples for data-driven tests when appropriate
        7. Ensure the Gherkin is syntactically correct and well-indented
        
        Always return only the Gherkin format without any additional explanations or markdown formatting.
        """
        
        prompt = f"""
        Please create a comprehensive Gherkin feature file based on the following test description:
        
        {test_description}
        
        Generate a complete Gherkin feature with multiple scenarios that thoroughly test the described functionality.
        Include both happy path and edge cases.
        """
        
        gherkin_result = self.llm.generate_completion(prompt, system_prompt)
        
        # Clean up the result to ensure it's valid Gherkin
        gherkin_result = self._clean_gherkin(gherkin_result)
        
        return gherkin_result

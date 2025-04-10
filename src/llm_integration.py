"""
LLM integration for the AI QA Agent.
This module provides integration with various LLM providers for AI-powered features.
"""
import os
import logging
import json
from typing import Dict, List, Any, Optional, Union

logger = logging.getLogger(__name__)

class LLMProvider:
    """
    LLM Provider integration for the AI QA Agent.
    
    This class handles integration with various LLM providers and provides a unified
    interface for making LLM requests.
    """
    
    def __init__(self, provider_name: str, config: Dict[str, Any]):
        """
        Initialize the LLM Provider with the given configuration.
        
        Args:
            provider_name: Name of the LLM provider (e.g., "groq", "openai").
            config: Configuration dictionary for the provider.
        """
        self.provider_name = provider_name
        self.config = config
        self.api_key = config.get("api_key", "")
        self.model = config.get("model", "")
        
        # Initialize the appropriate client based on provider
        self._init_client()
        
        logger.info(f"Initialized LLM Provider: {provider_name}")
    
    def _init_client(self):
        """Initialize the appropriate client based on the provider name."""
        if self.provider_name == "groq":
            self._init_groq_client()
        elif self.provider_name == "openai":
            self._init_openai_client()
        elif self.provider_name == "anthropic":
            self._init_anthropic_client()
        else:
            logger.warning(f"Unknown provider: {self.provider_name}, falling back to groq")
            self.provider_name = "groq"
            self._init_groq_client()
    
    def _init_groq_client(self):
        """Initialize the Groq client."""
        try:
            import groq
            self.client = groq.Client(api_key=self.api_key)
            logger.info("Groq client initialized")
        except ImportError:
            logger.error("Failed to import groq package. Please install it with: pip install groq")
            self.client = None
        except Exception as e:
            logger.error(f"Failed to initialize Groq client: {e}")
            self.client = None
    
    def _init_openai_client(self):
        """Initialize the OpenAI client."""
        try:
            import openai
            self.client = openai.OpenAI(api_key=self.api_key)
            logger.info("OpenAI client initialized")
        except ImportError:
            logger.error("Failed to import openai package. Please install it with: pip install openai")
            self.client = None
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            self.client = None
    
    def _init_anthropic_client(self):
        """Initialize the Anthropic client."""
        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=self.api_key)
            logger.info("Anthropic client initialized")
        except ImportError:
            logger.error("Failed to import anthropic package. Please install it with: pip install anthropic")
            self.client = None
        except Exception as e:
            logger.error(f"Failed to initialize Anthropic client: {e}")
            self.client = None
    
    def generate_text(self, prompt: str, max_tokens: int = 1000, temperature: float = 0.7) -> str:
        """
        Generate text using the configured LLM provider.
        
        Args:
            prompt: The prompt to send to the LLM.
            max_tokens: Maximum number of tokens to generate.
            temperature: Temperature parameter for generation.
            
        Returns:
            Generated text as a string.
        """
        if not self.client:
            logger.error(f"No client available for provider: {self.provider_name}")
            return "Error: LLM provider not available"
        
        try:
            if self.provider_name == "groq":
                return self._generate_text_groq(prompt, max_tokens, temperature)
            elif self.provider_name == "openai":
                return self._generate_text_openai(prompt, max_tokens, temperature)
            elif self.provider_name == "anthropic":
                return self._generate_text_anthropic(prompt, max_tokens, temperature)
            else:
                logger.error(f"Unknown provider: {self.provider_name}")
                return "Error: Unknown LLM provider"
        except Exception as e:
            logger.error(f"Error generating text: {e}")
            return f"Error generating text: {e}"
    
    def _generate_text_groq(self, prompt: str, max_tokens: int, temperature: float) -> str:
        """Generate text using Groq."""
        try:
            response = self.client.chat.completions.create(
                model=self.model or "llama3-70b-8192",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating text with Groq: {e}")
            raise
    
    def _generate_text_openai(self, prompt: str, max_tokens: int, temperature: float) -> str:
        """Generate text using OpenAI."""
        try:
            response = self.client.chat.completions.create(
                model=self.model or "gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating text with OpenAI: {e}")
            raise
    
    def _generate_text_anthropic(self, prompt: str, max_tokens: int, temperature: float) -> str:
        """Generate text using Anthropic."""
        try:
            response = self.client.messages.create(
                model=self.model or "claude-3-opus-20240229",
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        except Exception as e:
            logger.error(f"Error generating text with Anthropic: {e}")
            raise
    
    def process_unified_prompt(self, prompt: str, files: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Process a unified prompt that can handle any type of request and determine the appropriate action.
        
        Args:
            prompt: The user's prompt/request
            files: Optional list of file paths that were uploaded with the prompt
            
        Returns:
            Dictionary containing the response and any additional data
        """
        # Create a system prompt that helps the LLM understand how to process the unified prompt
        system_prompt = """
        You are an AI QA Agent assistant that helps with various testing tasks. 
        Analyze the user's request and determine which of the following actions to take:
        
        1. Test Case Analysis - Analyze a test case for quality, coverage, and potential issues
        2. Test Case Optimization - Improve a test case for better quality and effectiveness
        3. Gherkin Translation - Convert between natural language and Gherkin format
        4. Visual Testing - Analyze screenshots or compare visual elements
        5. Mobile Testing - Help with mobile app testing tasks
        6. Test Generation - Generate test cases from requirements or descriptions
        7. General Question - Answer a general question about testing
        
        For each request, identify:
        1. The primary action category
        2. Any specific sub-tasks needed
        3. How to use any attached files
        4. What additional information might be needed
        
        Respond with a JSON structure containing your analysis and plan.
        """
        
        # Create a prompt that includes information about any attached files
        files_info = ""
        if files and len(files) > 0:
            files_info = "Attached files:\n"
            for i, file_path in enumerate(files):
                file_name = os.path.basename(file_path)
                files_info += f"{i+1}. {file_name} ({file_path})\n"
        
        full_prompt = f"{system_prompt}\n\nUser Request: {prompt}\n\n{files_info}"
        
        # Get the LLM's analysis of what to do with this prompt
        try:
            response_text = self.generate_text(full_prompt, max_tokens=2000, temperature=0.3)
            
            # Try to parse the JSON response
            try:
                # Extract JSON if it's wrapped in markdown code blocks
                if "```json" in response_text:
                    json_text = response_text.split("```json")[1].split("```")[0].strip()
                    analysis = json.loads(json_text)
                else:
                    analysis = json.loads(response_text)
            except json.JSONDecodeError:
                # If not valid JSON, create a structured response
                analysis = {
                    "action": "general_question",
                    "response": response_text,
                    "confidence": 0.7
                }
            
            # Now process the request based on the analysis
            result = self._process_based_on_analysis(analysis, prompt, files)
            return result
            
        except Exception as e:
            logger.error(f"Error processing unified prompt: {e}")
            return {
                "error": f"Error processing request: {str(e)}",
                "raw_response": "An error occurred while processing your request."
            }
    
    def _process_based_on_analysis(self, analysis: Dict[str, Any], prompt: str, files: Optional[List[str]]) -> Dict[str, Any]:
        """
        Process the request based on the LLM's analysis.
        
        Args:
            analysis: The LLM's analysis of the request
            prompt: The original prompt
            files: Optional list of file paths
            
        Returns:
            Dictionary with the processed result
        """
        # This would normally call the appropriate controller methods
        # For now, we'll just return the analysis with a placeholder response
        action = analysis.get("action", "unknown")
        
        result = {
            "analysis": analysis,
            "action_taken": action,
            "response": f"Processed request as {action}",
            "files_used": files
        }
        
        # In a real implementation, this would call the appropriate controller methods
        # based on the action type. For now, we'll just return the analysis.
        return result

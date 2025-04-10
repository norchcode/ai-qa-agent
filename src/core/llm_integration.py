"""
LLM integration module for AI QA Agent.
"""
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class LLMProvider:
    """
    Provides integration with various LLM providers.
    """
    
    def __init__(self, provider_name: str, config: Dict[str, Any]):
        """
        Initialize the LLM provider.
        
        Args:
            provider_name: Name of the LLM provider (groq, openai, anthropic).
            config: Configuration dictionary.
        """
        self.provider_name = provider_name
        self.config = config
        self._initialize_client()
        logger.info(f"LLM provider initialized: {provider_name}")
    
    def _initialize_client(self):
        """Initialize the appropriate client based on the provider."""
        if self.provider_name == "groq":
            self._initialize_groq()
        elif self.provider_name == "openai":
            self._initialize_openai()
        elif self.provider_name == "anthropic":
            self._initialize_anthropic()
        else:
            logger.warning(f"Unknown LLM provider: {self.provider_name}, defaulting to groq")
            self.provider_name = "groq"
            self._initialize_groq()
    
    def _initialize_groq(self):
        """Initialize the Groq client."""
        try:
            import groq
            self.client = groq.Client(api_key=self.config.get("api_key", ""))
            self.model = self.config.get("model", "llama-3-70b-8192")
            logger.info(f"Groq client initialized with model: {self.model}")
        except ImportError:
            logger.error("Failed to import groq. Please install it with: pip install groq")
            self.client = None
    
    def _initialize_openai(self):
        """Initialize the OpenAI client."""
        try:
            import openai
            self.client = openai.OpenAI(api_key=self.config.get("api_key", ""))
            self.model = self.config.get("model", "gpt-4")
            logger.info(f"OpenAI client initialized with model: {self.model}")
        except ImportError:
            logger.error("Failed to import openai. Please install it with: pip install openai")
            self.client = None
    
    def _initialize_anthropic(self):
        """Initialize the Anthropic client."""
        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=self.config.get("api_key", ""))
            self.model = self.config.get("model", "claude-3-opus-20240229")
            logger.info(f"Anthropic client initialized with model: {self.model}")
        except ImportError:
            logger.error("Failed to import anthropic. Please install it with: pip install anthropic")
            self.client = None
    
    def process_unified_prompt(self, prompt: str, files: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Process a unified prompt to determine the appropriate action.
        
        Args:
            prompt: The user's prompt/request text.
            files: Optional list of file paths that were uploaded with the prompt.
            
        Returns:
            Dictionary containing the analysis and response.
        """
        logger.info(f"Processing unified prompt: {prompt[:100]}...")
        
        # Construct a system prompt to guide the LLM
        system_prompt = """
        You are an AI QA Agent assistant that helps with testing tasks. Analyze the user's request and determine the most appropriate action to take.
        Possible actions:
        - test_case_analysis: Analyze a test case for quality and coverage
        - test_case_optimization: Optimize a test case to improve quality
        - gherkin_translation: Translate between Gherkin and natural language (sub_task: to_gherkin or from_gherkin)
        - visual_testing: Analyze or compare screenshots
        - mobile_testing: Perform mobile app testing
        - test_generation: Generate test cases from requirements
        - general_question: Answer a general question about testing
        
        Return a JSON object with the following fields:
        - action_taken: The action you determined is most appropriate
        - sub_task: Any sub-task within the action (if applicable)
        - reasoning: Why you chose this action
        - response: A response to the user's request
        """
        
        # Construct the user message
        user_message = prompt
        if files:
            user_message += f"\n\nFiles attached: {', '.join(files)}"
        
        # This is a placeholder implementation
        # In a real implementation, we would call the LLM API to process the prompt
        
        # Determine the action based on keywords in the prompt
        action = "general_question"
        sub_task = ""
        
        if "analyze" in prompt.lower() and "test case" in prompt.lower():
            action = "test_case_analysis"
        elif "optimize" in prompt.lower() and "test case" in prompt.lower():
            action = "test_case_optimization"
        elif "translate" in prompt.lower() and "gherkin" in prompt.lower():
            action = "gherkin_translation"
            if "to gherkin" in prompt.lower():
                sub_task = "to_gherkin"
            elif "from gherkin" in prompt.lower():
                sub_task = "from_gherkin"
        elif "screenshot" in prompt.lower() or "image" in prompt.lower() or "visual" in prompt.lower():
            action = "visual_testing"
        elif "mobile" in prompt.lower() or "app" in prompt.lower() or "android" in prompt.lower() or "ios" in prompt.lower():
            action = "mobile_testing"
        elif "generate" in prompt.lower() and "test" in prompt.lower():
            action = "test_generation"
        
        # Check if files are attached and adjust action accordingly
        if files:
            for file_path in files:
                if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                    action = "visual_testing"
                    break
                elif file_path.lower().endswith('.feature'):
                    action = "test_case_analysis"
                    break
        
        # Generate a response based on the action
        response = ""
        if action == "test_case_analysis":
            response = "I'll analyze this test case for quality and coverage."
        elif action == "test_case_optimization":
            response = "I'll optimize this test case to improve its quality and effectiveness."
        elif action == "gherkin_translation":
            if sub_task == "to_gherkin":
                response = "I'll translate these natural language steps to Gherkin format."
            elif sub_task == "from_gherkin":
                response = "I'll translate this Gherkin scenario to natural language steps."
            else:
                response = "I'll handle this Gherkin translation task for you."
        elif action == "visual_testing":
            response = "I'll analyze these screenshots for you."
        elif action == "mobile_testing":
            response = "I'll help you with mobile app testing."
        elif action == "test_generation":
            response = "I'll generate test cases based on your requirements."
        else:  # general_question
            response = "I'll answer your question about testing."
        
        # Construct the result
        result = {
            "action_taken": action,
            "sub_task": sub_task,
            "reasoning": f"Based on the keywords in your request, I determined that you want me to perform {action}.",
            "response": response
        }
        
        return result

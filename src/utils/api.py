"""
Enhanced API for AI QA Agent with file and image processing support.
This module provides a unified API for accessing all AI QA Agent functionality.
"""
import os
import logging
from typing import Dict, List, Any, Optional, Union, Tuple

from .controller import Controller
from .llm_integration_enhanced import FileProcessor, ImageProcessor

logger = logging.getLogger(__name__)

class AIQA:
    """
    Unified API for AI QA Agent.
    
    This class provides a simple, consistent interface for accessing all AI QA Agent functionality.
    """
    
    def __init__(self, llm_provider: str = "groq", api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize the AI QA Agent API.
        
        Args:
            llm_provider: Name of the LLM provider to use (default: "groq").
            api_key: Optional API key for the LLM provider.
            model: Optional model name for the LLM provider.
        """
        self.controller = Controller(llm_provider=llm_provider, api_key=api_key, model=model)
        logger.info(f"Initialized AI QA Agent API with {llm_provider} provider")
    
    # Core functionality
    
    def analyze_test_case(self, test_case: str) -> Dict[str, Any]:
        """
        Analyze a test case using the LLM provider.
        
        Args:
            test_case: The test case to analyze, in Gherkin format.
            
        Returns:
            Dictionary containing analysis results.
        """
        return self.controller.llm_provider.analyze_test_case(test_case)
    
    def suggest_test_improvements(self, test_case: str, execution_results: Dict[str, Any]) -> List[str]:
        """
        Suggest improvements for a test case based on execution results.
        
        Args:
            test_case: The test case in Gherkin format.
            execution_results: Dictionary containing test execution results.
            
        Returns:
            List of suggested improvements.
        """
        return self.controller.llm_provider.suggest_test_improvements(test_case, execution_results)
    
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
        return self.controller.llm_provider.analyze_error(error_message, test_step, screenshot_path)
    
    def detect_visual_bugs(self, screenshot_description: str, expected_behavior: str) -> List[Dict[str, Any]]:
        """
        Detect visual bugs based on a screenshot description and expected behavior.
        
        Args:
            screenshot_description: Textual description of the screenshot.
            expected_behavior: Description of the expected visual behavior.
            
        Returns:
            List of detected visual bugs.
        """
        return self.controller.llm_provider.detect_visual_bugs(screenshot_description, expected_behavior)
    
    # File processing functionality
    
    def process_file(self, file_path: str, prompt: Optional[str] = None, 
                    system_prompt: Optional[str] = None) -> str:
        """
        Process a file using the LLM provider.
        
        Args:
            file_path: Path to the file to process.
            prompt: Optional prompt to provide context for processing the file.
            system_prompt: Optional system prompt to provide additional context.
            
        Returns:
            Generated text as a string.
        """
        return self.controller.llm_provider.process_file(file_path, prompt, system_prompt)
    
    def analyze_code_file(self, file_path: str) -> Dict[str, Any]:
        """
        Analyze a code file using the LLM provider.
        
        Args:
            file_path: Path to the code file to analyze.
            
        Returns:
            Dictionary containing analysis results.
        """
        return self.controller.llm_provider.analyze_code_file(file_path)
    
    def extract_test_cases_from_file(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Extract test cases from a file using the LLM provider.
        
        Args:
            file_path: Path to the file to extract test cases from.
            
        Returns:
            List of dictionaries containing extracted test cases.
        """
        return self.controller.llm_provider.extract_test_cases_from_file(file_path)
    
    def detect_file_type(self, file_path: str) -> str:
        """
        Detect the type of a file based on extension and content.
        
        Args:
            file_path: Path to the file.
            
        Returns:
            String indicating the file type.
        """
        return FileProcessor.detect_file_type(file_path)
    
    def extract_text_from_file(self, file_path: str) -> str:
        """
        Extract text content from a file.
        
        Args:
            file_path: Path to the file.
            
        Returns:
            Extracted text content.
        """
        return FileProcessor.extract_text_from_file(file_path)
    
    def extract_structured_data_from_file(self, file_path: str) -> Dict[str, Any]:
        """
        Extract structured data from a file (JSON, YAML, etc.).
        
        Args:
            file_path: Path to the file.
            
        Returns:
            Dictionary containing the structured data.
        """
        return FileProcessor.extract_structured_data_from_file(file_path)
    
    # Image processing functionality
    
    def analyze_image(self, image_path: str, prompt: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze an image using the LLM provider.
        
        Args:
            image_path: Path to the image to analyze.
            prompt: Optional prompt to provide context for analyzing the image.
            
        Returns:
            Dictionary containing analysis results.
        """
        return self.controller.llm_provider.analyze_image(image_path, prompt)
    
    def compare_ui_with_design(self, design_image_path: str, ui_screenshot_path: str) -> Dict[str, Any]:
        """
        Compare a UI design with an actual UI screenshot.
        
        Args:
            design_image_path: Path to the design image.
            ui_screenshot_path: Path to the UI screenshot.
            
        Returns:
            Dictionary containing comparison results.
        """
        return self.controller.llm_provider.compare_ui_with_design(design_image_path, ui_screenshot_path)
    
    def extract_text_from_image(self, image_path: str) -> str:
        """
        Extract text from an image using OCR.
        
        Args:
            image_path: Path to the image.
            
        Returns:
            Extracted text.
        """
        return ImageProcessor.extract_text_from_image(image_path)
    
    def compare_images(self, image1_path: str, image2_path: str) -> Tuple[float, Optional[str]]:
        """
        Compare two images and return a similarity score and difference visualization.
        
        Args:
            image1_path: Path to the first image.
            image2_path: Path to the second image.
            
        Returns:
            Tuple containing similarity score (0-1) and path to difference visualization image.
        """
        return ImageProcessor.compare_images(image1_path, image2_path)
    
    def detect_ui_elements(self, image_path: str) -> List[Dict[str, Any]]:
        """
        Detect UI elements in an image.
        
        Args:
            image_path: Path to the image.
            
        Returns:
            List of dictionaries containing detected UI elements.
        """
        return ImageProcessor.detect_ui_elements(image_path)
    
    # Web UI functionality
    
    def start_webui(self, port: int = 7860, share: bool = False) -> None:
        """
        Start the web UI.
        
        Args:
            port: Port to run the web UI on.
            share: Whether to create a public URL.
        """
        from .webui_enhanced import start_webui
        start_webui(self.controller, port=port, share=share)
    
    # Utility functions
    
    def change_llm_provider(self, provider_name: str, api_key: Optional[str] = None, model: Optional[str] = None) -> None:
        """
        Change the LLM provider.
        
        Args:
            provider_name: Name of the LLM provider to use.
            api_key: Optional API key for the LLM provider.
            model: Optional model name for the LLM provider.
        """
        self.controller.change_llm_provider(provider_name, api_key, model)
        logger.info(f"Changed LLM provider to {provider_name}")
    
    def get_available_providers(self) -> List[str]:
        """
        Get a list of available LLM providers.
        
        Returns:
            List of available LLM provider names.
        """
        return self.controller.get_available_providers()
    
    def get_current_provider(self) -> str:
        """
        Get the name of the current LLM provider.
        
        Returns:
            Name of the current LLM provider.
        """
        return self.controller.get_current_provider()


# Create a singleton instance for easy import
aiqa = AIQA()

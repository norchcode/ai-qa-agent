"""
Enhanced LLM Integration with File and Image Processing Support.
This module extends the LLM integration with capabilities for processing files and images.
"""
import os
import logging
import json
import time
import base64
import mimetypes
from typing import Dict, List, Any, Optional, Union, Tuple
from abc import ABC, abstractmethod
from pathlib import Path
import tempfile

# Import provider-specific modules
try:
    import groq
    from langchain_groq import ChatGroq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

# Import file processing libraries
try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False

try:
    import docx
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False

try:
    import chardet
    CHARDET_AVAILABLE = True
except ImportError:
    CHARDET_AVAILABLE = False

# Import image processing libraries
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

logger = logging.getLogger(__name__)

class FileProcessor:
    """Utility class for processing different file types."""
    
    @staticmethod
    def detect_file_type(file_path: str) -> str:
        """
        Detect the type of a file based on extension and content.
        
        Args:
            file_path: Path to the file.
            
        Returns:
            String indicating the file type.
        """
        # Get file extension
        ext = os.path.splitext(file_path)[1].lower()
        
        # Check if file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Detect file type based on extension
        if ext in ['.txt', '.md', '.log', '.csv']:
            return 'text'
        elif ext in ['.py', '.js', '.java', '.cpp', '.cs', '.html', '.css', '.php', '.rb', '.go', '.rs', '.ts']:
            return 'code'
        elif ext in ['.json', '.yaml', '.yml', '.xml', '.toml']:
            return 'structured'
        elif ext in ['.pdf']:
            return 'pdf'
        elif ext in ['.docx', '.doc']:
            return 'docx'
        elif ext in ['.feature']:
            return 'gherkin'
        elif ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff', '.svg']:
            return 'image'
        else:
            # Try to detect based on content
            try:
                with open(file_path, 'rb') as f:
                    content = f.read(1024)  # Read first 1KB
                
                # Check for binary file
                if b'\x00' in content:
                    # Check for image signatures
                    if content.startswith(b'\xff\xd8\xff'):  # JPEG
                        return 'image'
                    elif content.startswith(b'\x89PNG\r\n\x1a\n'):  # PNG
                        return 'image'
                    elif content.startswith(b'GIF87a') or content.startswith(b'GIF89a'):  # GIF
                        return 'image'
                    elif content.startswith(b'%PDF'):  # PDF
                        return 'pdf'
                    else:
                        return 'binary'
                else:
                    # Assume it's a text file
                    return 'text'
            except Exception as e:
                logger.error(f"Error detecting file type: {e}")
                return 'unknown'
    
    @staticmethod
    def extract_text_from_file(file_path: str) -> str:
        """
        Extract text content from a file.
        
        Args:
            file_path: Path to the file.
            
        Returns:
            Extracted text content.
        """
        file_type = FileProcessor.detect_file_type(file_path)
        
        try:
            if file_type == 'text' or file_type == 'code' or file_type == 'gherkin':
                # Try to detect encoding
                if CHARDET_AVAILABLE:
                    with open(file_path, 'rb') as f:
                        raw_data = f.read()
                    detected = chardet.detect(raw_data)
                    encoding = detected['encoding'] or 'utf-8'
                else:
                    encoding = 'utf-8'
                
                # Read text file with detected encoding
                with open(file_path, 'r', encoding=encoding, errors='replace') as f:
                    return f.read()
            
            elif file_type == 'structured':
                # Read structured file as text
                with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                    return f.read()
            
            elif file_type == 'pdf':
                if not PYPDF2_AVAILABLE:
                    raise ImportError("PyPDF2 is required for PDF processing. Install it with 'pip install PyPDF2'.")
                
                # Extract text from PDF
                text = ""
                with open(file_path, 'rb') as f:
                    pdf_reader = PyPDF2.PdfReader(f)
                    for page_num in range(len(pdf_reader.pages)):
                        page = pdf_reader.pages[page_num]
                        text += page.extract_text() + "\n\n"
                return text
            
            elif file_type == 'docx':
                if not DOCX_AVAILABLE:
                    raise ImportError("python-docx is required for DOCX processing. Install it with 'pip install python-docx'.")
                
                # Extract text from DOCX
                doc = docx.Document(file_path)
                return "\n".join([para.text for para in doc.paragraphs])
            
            elif file_type == 'image':
                # For images, use OCR if available
                if TESSERACT_AVAILABLE and PIL_AVAILABLE:
                    return ImageProcessor.extract_text_from_image(file_path)
                else:
                    return f"[Image file: {os.path.basename(file_path)}]"
            
            else:
                return f"[Unsupported file type: {file_type}]"
        
        except Exception as e:
            logger.error(f"Error extracting text from file: {e}")
            return f"[Error extracting text: {str(e)}]"
    
    @staticmethod
    def extract_code_from_file(file_path: str) -> str:
        """
        Extract code content from a file.
        
        Args:
            file_path: Path to the file.
            
        Returns:
            Extracted code content.
        """
        file_type = FileProcessor.detect_file_type(file_path)
        
        if file_type == 'code':
            # For code files, just return the content
            return FileProcessor.extract_text_from_file(file_path)
        else:
            # For non-code files, try to extract code blocks
            content = FileProcessor.extract_text_from_file(file_path)
            
            # Look for code blocks (markdown style)
            code_blocks = []
            in_code_block = False
            current_block = []
            
            for line in content.split('\n'):
                if line.strip().startswith('```'):
                    if in_code_block:
                        # End of code block
                        code_blocks.append('\n'.join(current_block))
                        current_block = []
                    in_code_block = not in_code_block
                elif in_code_block:
                    current_block.append(line)
            
            if code_blocks:
                return '\n\n'.join(code_blocks)
            else:
                # If no code blocks found, return the original content
                return content
    
    @staticmethod
    def extract_structured_data_from_file(file_path: str) -> Dict[str, Any]:
        """
        Extract structured data from a file (JSON, YAML, etc.).
        
        Args:
            file_path: Path to the file.
            
        Returns:
            Dictionary containing the structured data.
        """
        file_type = FileProcessor.detect_file_type(file_path)
        ext = os.path.splitext(file_path)[1].lower()
        
        try:
            if ext == '.json':
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            
            elif ext in ['.yaml', '.yml']:
                try:
                    import yaml
                    with open(file_path, 'r', encoding='utf-8') as f:
                        return yaml.safe_load(f)
                except ImportError:
                    raise ImportError("PyYAML is required for YAML processing. Install it with 'pip install PyYAML'.")
            
            elif ext == '.xml':
                try:
                    import xmltodict
                    with open(file_path, 'r', encoding='utf-8') as f:
                        return xmltodict.parse(f.read())
                except ImportError:
                    raise ImportError("xmltodict is required for XML processing. Install it with 'pip install xmltodict'.")
            
            elif ext == '.toml':
                try:
                    import toml
                    with open(file_path, 'r', encoding='utf-8') as f:
                        return toml.load(f)
                except ImportError:
                    raise ImportError("toml is required for TOML processing. Install it with 'pip install toml'.")
            
            else:
                # For unsupported structured data formats, return the raw text
                return {"raw_content": FileProcessor.extract_text_from_file(file_path)}
        
        except Exception as e:
            logger.error(f"Error extracting structured data from file: {e}")
            return {"error": str(e)}


class ImageProcessor:
    """Utility class for processing images."""
    
    @staticmethod
    def extract_text_from_image(image_path: str) -> str:
        """
        Extract text from an image using OCR.
        
        Args:
            image_path: Path to the image.
            
        Returns:
            Extracted text.
        """
        if not TESSERACT_AVAILABLE:
            raise ImportError("pytesseract is required for OCR. Install it with 'pip install pytesseract'.")
        
        if not PIL_AVAILABLE:
            raise ImportError("PIL is required for image processing. Install it with 'pip install Pillow'.")
        
        try:
            # Open the image
            image = Image.open(image_path)
            
            # Perform OCR
            text = pytesseract.image_to_string(image)
            
            return text
        
        except Exception as e:
            logger.error(f"Error extracting text from image: {e}")
            return f"[Error extracting text from image: {str(e)}]"
    
    @staticmethod
    def encode_image_to_base64(image_path: str) -> str:
        """
        Encode an image to base64 for API requests.
        
        Args:
            image_path: Path to the image.
            
        Returns:
            Base64-encoded image string.
        """
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        
        except Exception as e:
            logger.error(f"Error encoding image to base64: {e}")
            raise
    
    @staticmethod
    def compare_images(image1_path: str, image2_path: str) -> Tuple[float, Optional[str]]:
        """
        Compare two images and return a similarity score and difference visualization.
        
        Args:
            image1_path: Path to the first image.
            image2_path: Path to the second image.
            
        Returns:
            Tuple containing similarity score (0-1) and path to difference visualization image.
        """
        if not CV2_AVAILABLE:
            raise ImportError("OpenCV is required for image comparison. Install it with 'pip install opencv-python'.")
        
        try:
            # Read images
            img1 = cv2.imread(image1_path)
            img2 = cv2.imread(image2_path)
            
            # Resize images to same dimensions if needed
            if img1.shape != img2.shape:
                img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
            
            # Convert images to grayscale
            gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
            gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
            
            # Calculate structural similarity index
            (score, diff) = cv2.compareSSIM(gray1, gray2, full=True)
            
            # Create visualization of differences
            diff = (diff * 255).astype("uint8")
            thresh = cv2.threshold(diff, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
            
            # Find contours
            contours = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            contours = contours[0] if len(contours) == 2 else contours[1]
            
            # Create difference visualization
            diff_vis = img1.copy()
            for c in contours:
                area = cv2.contourArea(c)
                if area > 40:  # Filter small differences
                    x, y, w, h = cv2.boundingRect(c)
                    cv2.rectangle(diff_vis, (x, y), (x + w, y + h), (0, 0, 255), 2)
            
            # Save difference visualization
            diff_path = tempfile.mktemp(suffix='.png')
            cv2.imwrite(diff_path, diff_vis)
            
            return score, diff_path
        
        except Exception as e:
            logger.error(f"Error comparing images: {e}")
            return 0.0, None
    
    @staticmethod
    def detect_ui_elements(image_path: str) -> List[Dict[str, Any]]:
        """
        Detect UI elements in an image.
        
        Args:
            image_path: Path to the image.
            
        Returns:
            List of dictionaries containing detected UI elements.
        """
        if not CV2_AVAILABLE:
            raise ImportError("OpenCV is required for UI element detection. Install it with 'pip install opencv-python'.")
        
        try:
            # Read image
            img = cv2.imread(image_path)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Detect edges
            edges = cv2.Canny(gray, 50, 150)
            
            # Find contours
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Filter and classify contours
            ui_elements = []
            for i, contour in enumerate(contours):
                area = cv2.contourArea(contour)
                if area < 100:  # Filter out small contours
                    continue
                
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = float(w) / h
                
                # Extract region of interest
                roi = img[y:y+h, x:x+w]
                
                # Classify element type based on shape and size
                element_type = "unknown"
                if 0.9 <= aspect_ratio <= 1.1 and area < 10000:
                    element_type = "button"
                elif aspect_ratio > 3:
                    element_type = "text_field"
                elif aspect_ratio < 0.5:
                    element_type = "sidebar"
                
                # Extract text if possible
                text = ""
                if TESSERACT_AVAILABLE:
                    # Convert ROI to PIL Image
                    roi_rgb = cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)
                    pil_roi = Image.fromarray(roi_rgb)
                    text = pytesseract.image_to_string(pil_roi).strip()
                
                ui_elements.append({
                    "id": i,
                    "type": element_type,
                    "position": {"x": x, "y": y, "width": w, "height": h},
                    "text": text,
                    "confidence": 0.8  # Placeholder confidence score
                })
            
            return ui_elements
        
        except Exception as e:
            logger.error(f"Error detecting UI elements: {e}")
            return []


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    @abstractmethod
    def generate_completion(self, prompt: str, system_prompt: Optional[str] = None, 
                           temperature: float = 0.7, max_tokens: int = 1024) -> str:
        """
        Generate a completion using the LLM provider.
        
        Args:
            prompt: The prompt to generate a completion for.
            system_prompt: Optional system prompt to provide context.
            temperature: Sampling temperature, between 0 and 1.
            max_tokens: Maximum number of tokens to generate.
            
        Returns:
            Generated text as a string.
        """
        pass
    
    @abstractmethod
    def analyze_test_case(self, test_case: str) -> Dict[str, Any]:
        """
        Analyze a test case using the LLM provider.
        
        Args:
            test_case: The test case to analyze, in Gherkin format.
            
        Returns:
            Dictionary containing analysis results.
        """
        pass
    
    @abstractmethod
    def suggest_test_improvements(self, test_case: str, execution_results: Dict[str, Any]) -> List[str]:
        """
        Suggest improvements for a test case based on execution results.
        
        Args:
            test_case: The test case in Gherkin format.
            execution_results: Dictionary containing test execution results.
            
        Returns:
            List of suggested improvements.
        """
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
    def detect_visual_bugs(self, screenshot_description: str, expected_behavior: str) -> List[Dict[str, Any]]:
        """
        Detect visual bugs based on a screenshot description and expected behavior.
        
        Args:
            screenshot_description: Textual description of the screenshot.
            expected_behavior: Description of the expected visual behavior.
            
        Returns:
            List of detected visual bugs.
        """
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
    def analyze_code_file(self, file_path: str) -> Dict[str, Any]:
        """
        Analyze a code file using the LLM provider.
        
        Args:
            file_path: Path to the code file to analyze.
            
        Returns:
            Dictionary containing analysis results.
        """
        pass
    
    @abstractmethod
    def extract_test_cases_from_file(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Extract test cases from a file using the LLM provider.
        
        Args:
            file_path: Path to the file to extract test cases from.
            
        Returns:
            List of dictionaries containing extracted test cases.
        """
        pass
    
    @abstractmethod
    def analyze_image(self, image_path: str, prompt: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze an image using the LLM provider.
        
        Args:
            image_path: Path to the image to analyze.
            prompt: Optional prompt to provide context for analyzing the image.
            
        Returns:
            Dictionary containing analysis results.
        """
        pass
    
    @abstractmethod
    def compare_ui_with_design(self, design_image_path: str, ui_screenshot_path: str) -> Dict[str, Any]:
        """
        Compare a UI design with an actual UI screenshot.
        
        Args:
            design_image_path: Path to the design image.
            ui_screenshot_path: Path to the UI screenshot.
            
        Returns:
            Dictionary containing comparison results.
        """
        pass


class GroqProvider(LLMProvider):
    """Integration with Groq LLM API."""
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize Groq LLM integration.
        
        Args:
            api_key: Groq API key. If not provided, will be read from environment variable.
            model: Groq model to use. If not provided, will be read from environment variable.
        """
        if not GROQ_AVAILABLE:
            raise ImportError("Groq integration requires the groq package. Install it with 'pip install groq'.")
        
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("Groq API key not provided and GROQ_API_KEY environment variable not set")
        
        self.model = model or os.getenv("GROQ_MODEL", "llama3-70b-8192")
        logger.info(f"Initializing Groq LLM integration with model: {self.model}")
        
        # Initialize Groq client
        self.client = groq.Client(api_key=self.api_key)
        
        # Initialize LangChain integration for more complex chains
        try:
            from langchain_groq import ChatGroq
            from langchain_core.messages import HumanMessage, SystemMessage
            from langchain_core.output_parsers import StrOutputParser
            from langchain_core.prompts import ChatPromptTemplate
            
            self.chat_model = ChatGroq(
                groq_api_key=self.api_key,
                model_name=self.model
            )
            self.langchain_available = True
        except ImportError:
            logger.warning("LangChain not available, some features may be limited")
            self.langchain_available = False
        
        # Check if model supports multimodal inputs
        self.supports_multimodal = self.model in [
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229"
        ]
        
        logger.info(f"Model {self.model} multimodal support: {self.supports_multimodal}")
    
    def generate_completion(self, prompt: str, system_prompt: Optional[str] = None, 
                           temperature: float = 0.7, max_tokens: int = 1024) -> str:
        """
        Generate a completion using Groq API directly.
        
        Args:
            prompt: The prompt to generate a completion for.
            system_prompt: Optional system prompt to provide context.
            temperature: Sampling temperature, between 0 and 1.
            max_tokens: Maximum number of tokens to generate.
            
        Returns:
            Generated text as a string.
        """
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating completion with Groq: {e}")
            raise
    
    def analyze_test_case(self, test_case: str) -> Dict[str, Any]:
        """
        Analyze a test case using Groq LLM.
        
        Args:
            test_case: The test case to analyze, in Gherkin format.
            
        Returns:
            Dictionary containing analysis results.
        """
        system_prompt = """
        You are a QA expert specialized in analyzing test cases. Your goal is to identify issues, 
        redundancies, and opportunities for improvement in test cases. Provide specific, actionable feedback.
        
        Analyze the test case and return a JSON object with the following structure:
        {
            "quality_score": <score from 1-10>,
            "issues": [<list of issues found>],
            "redundancies": [<list of redundant steps>],
            "missing_validations": [<list of missing validations>],
            "improvement_suggestions": [<list of suggestions>]
        }
        """
        
        prompt = f"""
        Analyze the following test case:
        
        ```gherkin
        {test_case}
        ```
        
        Identify:
        1. Redundant or unnecessary steps
        2. Missing validations or assertions
        3. Potential edge cases not covered
        4. Opportunities to improve reliability
        5. Suggestions for optimization
        
        Return your analysis as a JSON object.
        """
        
        try:
            if self.langchain_available:
                # Use LangChain for structured output
                from langchain_core.prompts import ChatPromptTemplate
                from langchain_core.output_parsers import StrOutputParser
                
                prompt_template = ChatPromptTemplate.from_messages([
                    ("system", system_prompt),
                    ("human", prompt)
                ])
                
                chain = prompt_template | self.chat_model | StrOutputParser()
                result = chain.invoke({})
            else:
                # Use direct API call
                result = self.generate_completion(prompt, system_prompt)
            
            # Convert string result to dictionary (assuming it's valid JSON)
            try:
                return json.loads(result)
            except json.JSONDecodeError:
                logger.warning("Failed to parse LLM output as JSON, returning raw output")
                return {"raw_output": result}
                
        except Exception as e:
            logger.error(f"Error analyzing test case with Groq: {e}")
            return {"error": str(e)}
    
    def suggest_test_improvements(self, test_case: str, execution_results: Dict[str, Any]) -> List[str]:
        """
        Suggest improvements for a test case based on execution results.
        
        Args:
            test_case: The test case in Gherkin format.
            execution_results: Dictionary containing test execution results.
            
        Returns:
            List of suggested improvements.
        """
        system_prompt = """
        You are a QA expert specialized in improving test cases based on execution results.
        Your goal is to suggest specific improvements to make tests more reliable, efficient, and effective.
        Focus on practical, actionable suggestions that address the issues found during test execution.
        """
        
        prompt = f"""
        Here is a test case:
        
        ```gherkin
        {test_case}
        ```
        
        And here are the execution results:
        
        ```json
        {execution_results}
        ```
        
        Based on these results, suggest specific improvements to make the test more reliable, efficient, and effective.
        Focus on:
        1. Fixing failing steps
        2. Adding missing validations
        3. Improving selectors or locators
        4. Handling timing or synchronization issues
        5. Adding error recovery mechanisms
        
        Return a list of specific, actionable suggestions.
        """
        
        try:
            result = self.generate_completion(prompt, system_prompt)
            
            # Extract suggestions from the result
            # This is a simple implementation; in practice, you might want to use more structured parsing
            suggestions = [line.strip() for line in result.split('\n') if line.strip().startswith('-') or line.strip().startswith('*')]
            if not suggestions:
                # If no bullet points found, return the whole result
                return [result]
            return suggestions
            
        except Exception as e:
            logger.error(f"Error suggesting test improvements with Groq: {e}")
            return [f"Error suggesting improvements: {str(e)}"]
    
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
        system_prompt = """
        You are a QA expert specialized in analyzing test failures and suggesting fixes.
        Your goal is to identify the root cause of test failures and suggest specific fixes.
        Focus on practical, actionable suggestions that address the underlying issues.
        """
        
        if screenshot_path and self.supports_multimodal:
            # For multimodal models, include the screenshot in the prompt
            try:
                # Encode image to base64
                base64_image = ImageProcessor.encode_image_to_base64(screenshot_path)
                
                # Create multimodal message
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": [
                        {"type": "text", "text": f"""
                        A test step failed during execution:
                        
                        Test Step: {test_step}
                        
                        Error Message: {error_message}
                        
                        I've attached a screenshot taken at the time of the error. Based on this information, please:
                        1. Identify the most likely root cause of the failure
                        2. Suggest specific fixes or workarounds
                        3. Recommend changes to make the test more robust
                        
                        Return your analysis as a structured response with sections for "Root Cause", "Suggested Fixes", and "Robustness Improvements".
                        """},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}
                    ]}
                ]
                
                # Call API with multimodal message
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=1024
                )
                
                result = response.choices[0].message.content
            except Exception as e:
                logger.error(f"Error processing image for error analysis: {e}")
                # Fall back to text-only analysis
                prompt = f"""
                A test step failed during execution:
                
                Test Step: {test_step}
                
                Error Message: {error_message}
                
                Based on this information, please:
                1. Identify the most likely root cause of the failure
                2. Suggest specific fixes or workarounds
                3. Recommend changes to make the test more robust
                
                Return your analysis as a structured response with sections for "Root Cause", "Suggested Fixes", and "Robustness Improvements".
                """
                result = self.generate_completion(prompt, system_prompt)
        else:
            # Text-only analysis
            prompt = f"""
            A test step failed during execution:
            
            Test Step: {test_step}
            
            Error Message: {error_message}
            
            Based on this information, please:
            1. Identify the most likely root cause of the failure
            2. Suggest specific fixes or workarounds
            3. Recommend changes to make the test more robust
            
            Return your analysis as a structured response with sections for "Root Cause", "Suggested Fixes", and "Robustness Improvements".
            """
            
            result = self.generate_completion(prompt, system_prompt)
        
        # Parse the result into sections
        sections = {}
        current_section = None
        
        for line in result.split('\n'):
            line = line.strip()
            if not line:
                continue
            
            if line.startswith('Root Cause'):
                current_section = 'root_cause'
                sections[current_section] = []
            elif line.startswith('Suggested Fixes'):
                current_section = 'suggested_fixes'
                sections[current_section] = []
            elif line.startswith('Robustness Improvements'):
                current_section = 'robustness_improvements'
                sections[current_section] = []
            elif current_section:
                sections[current_section].append(line)
        
        # If parsing failed, return the raw result
        if not sections:
            return {
                "raw_output": result,
                "error_message": error_message,
                "test_step": test_step
            }
        
        # Join the lines in each section
        for section in sections:
            sections[section] = '\n'.join(sections[section])
        
        # Add the original error information
        sections["error_message"] = error_message
        sections["test_step"] = test_step
        
        return sections
    
    def detect_visual_bugs(self, screenshot_description: str, expected_behavior: str) -> List[Dict[str, Any]]:
        """
        Detect visual bugs based on a screenshot description and expected behavior.
        
        Args:
            screenshot_description: Textual description of the screenshot.
            expected_behavior: Description of the expected visual behavior.
            
        Returns:
            List of detected visual bugs.
        """
        system_prompt = """
        You are a QA expert specialized in detecting visual bugs in web applications.
        Your goal is to identify visual issues based on descriptions of screenshots and expected behavior.
        Focus on identifying specific visual bugs that affect the user experience.
        """
        
        prompt = f"""
        Screenshot Description: {screenshot_description}
        
        Expected Behavior: {expected_behavior}
        
        Based on this information, identify any potential visual bugs or UI issues.
        For each issue, provide:
        1. A description of the issue
        2. The severity (Low, Medium, High)
        3. The potential impact on user experience
        4. A suggestion for fixing the issue
        
        Return your analysis as a list of issues in JSON format.
        """
        
        try:
            result = self.generate_completion(prompt, system_prompt)
            
            # Attempt to parse the result as JSON
            try:
                return json.loads(result)
            except json.JSONDecodeError:
                # If parsing fails, extract issues manually
                issues = []
                current_issue = {}
                
                for line in result.split('\n'):
                    line = line.strip()
                    if not line:
                        continue
                    
                    if line.startswith('Issue') or line.startswith('Bug') or line.startswith('-'):
                        if current_issue and 'description' in current_issue:
                            issues.append(current_issue)
                        current_issue = {'description': line}
                    elif 'severity' in line.lower():
                        for severity in ['low', 'medium', 'high']:
                            if severity in line.lower():
                                current_issue['severity'] = severity.capitalize()
                                break
                    elif 'impact' in line.lower():
                        current_issue['impact'] = line
                    elif 'fix' in line.lower() or 'suggestion' in line.lower():
                        current_issue['suggestion'] = line
                
                if current_issue and 'description' in current_issue:
                    issues.append(current_issue)
                
                return issues if issues else [{"description": result}]
                
        except Exception as e:
            logger.error(f"Error detecting visual bugs with Groq: {e}")
            return [{"error": str(e)}]
    
    def process_file(self, file_path: str, prompt: Optional[str] = None, 
                    system_prompt: Optional[str] = None) -> str:
        """
        Process a file using Groq API.
        
        Args:
            file_path: Path to the file to process.
            prompt: Optional prompt to provide context for processing the file.
            system_prompt: Optional system prompt to provide additional context.
            
        Returns:
            Generated text as a string.
        """
        # Extract text from file
        file_content = FileProcessor.extract_text_from_file(file_path)
        
        # Create prompt with file content
        file_prompt = prompt or "Analyze the following file content:"
        full_prompt = f"{file_prompt}\n\n```\n{file_content}\n```"
        
        # Generate completion
        return self.generate_completion(full_prompt, system_prompt)
    
    def analyze_code_file(self, file_path: str) -> Dict[str, Any]:
        """
        Analyze a code file using Groq API.
        
        Args:
            file_path: Path to the code file to analyze.
            
        Returns:
            Dictionary containing analysis results.
        """
        # Extract code from file
        code_content = FileProcessor.extract_code_from_file(file_path)
        
        # Create system prompt for code analysis
        system_prompt = """
        You are a code analysis expert. Analyze the provided code and return a JSON object with the following structure:
        {
            "summary": "Brief summary of what the code does",
            "complexity": "Assessment of code complexity (Low, Medium, High)",
            "issues": ["List of potential issues or bugs"],
            "suggestions": ["List of improvement suggestions"],
            "test_coverage": "Assessment of test coverage or testability"
        }
        """
        
        # Create prompt with code content
        prompt = f"Analyze the following code:\n\n```\n{code_content}\n```"
        
        # Generate completion
        result = self.generate_completion(prompt, system_prompt)
        
        # Parse result as JSON
        try:
            return json.loads(result)
        except json.JSONDecodeError:
            logger.warning("Failed to parse LLM output as JSON, returning raw output")
            return {"raw_output": result}
    
    def extract_test_cases_from_file(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Extract test cases from a file using Groq API.
        
        Args:
            file_path: Path to the file to extract test cases from.
            
        Returns:
            List of dictionaries containing extracted test cases.
        """
        # Extract text from file
        file_content = FileProcessor.extract_text_from_file(file_path)
        
        # Create system prompt for test case extraction
        system_prompt = """
        You are a QA expert. Extract test cases from the provided content and return them as a JSON array with the following structure:
        [
            {
                "title": "Test case title",
                "description": "Test case description",
                "steps": ["Step 1", "Step 2", ...],
                "expected_results": ["Expected result 1", "Expected result 2", ...],
                "priority": "Priority level (Low, Medium, High)"
            },
            ...
        ]
        """
        
        # Create prompt with file content
        prompt = f"Extract test cases from the following content:\n\n```\n{file_content}\n```"
        
        # Generate completion
        result = self.generate_completion(prompt, system_prompt)
        
        # Parse result as JSON
        try:
            return json.loads(result)
        except json.JSONDecodeError:
            logger.warning("Failed to parse LLM output as JSON, returning raw output")
            return [{"raw_output": result}]
    
    def analyze_image(self, image_path: str, prompt: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze an image using Groq API.
        
        Args:
            image_path: Path to the image to analyze.
            prompt: Optional prompt to provide context for analyzing the image.
            
        Returns:
            Dictionary containing analysis results.
        """
        if not self.supports_multimodal:
            # For non-multimodal models, use OCR and then analyze the text
            try:
                # Extract text from image
                image_text = ImageProcessor.extract_text_from_image(image_path)
                
                # Detect UI elements
                ui_elements = ImageProcessor.detect_ui_elements(image_path)
                
                # Create system prompt for image analysis
                system_prompt = """
                You are a UI/UX expert. Analyze the provided UI description and elements to identify potential issues,
                assess usability, and suggest improvements. Focus on user experience, accessibility, and design consistency.
                """
                
                # Create prompt with image information
                analysis_prompt = prompt or "Analyze this UI:"
                full_prompt = f"""
                {analysis_prompt}
                
                Extracted Text:
                {image_text}
                
                Detected UI Elements:
                {json.dumps(ui_elements, indent=2)}
                
                Please provide a comprehensive analysis including:
                1. Overall assessment of the UI
                2. Potential usability issues
                3. Accessibility concerns
                4. Design consistency evaluation
                5. Improvement suggestions
                
                Return your analysis as a structured JSON object.
                """
                
                # Generate completion
                result = self.generate_completion(full_prompt, system_prompt)
                
                # Parse result as JSON
                try:
                    analysis = json.loads(result)
                except json.JSONDecodeError:
                    logger.warning("Failed to parse LLM output as JSON, returning raw output")
                    analysis = {"raw_output": result}
                
                # Add extracted information
                analysis["extracted_text"] = image_text
                analysis["detected_elements"] = ui_elements
                
                return analysis
            
            except Exception as e:
                logger.error(f"Error analyzing image with non-multimodal model: {e}")
                return {"error": str(e)}
        else:
            # For multimodal models, include the image directly in the prompt
            try:
                # Encode image to base64
                base64_image = ImageProcessor.encode_image_to_base64(image_path)
                
                # Create system prompt for image analysis
                system_prompt = """
                You are a UI/UX expert. Analyze the provided UI image to identify potential issues,
                assess usability, and suggest improvements. Focus on user experience, accessibility, and design consistency.
                """
                
                # Create multimodal message
                analysis_prompt = prompt or "Analyze this UI image:"
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": [
                        {"type": "text", "text": f"""
                        {analysis_prompt}
                        
                        Please provide a comprehensive analysis including:
                        1. Overall assessment of the UI
                        2. Potential usability issues
                        3. Accessibility concerns
                        4. Design consistency evaluation
                        5. Improvement suggestions
                        
                        Return your analysis as a structured JSON object.
                        """},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}
                    ]}
                ]
                
                # Call API with multimodal message
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=1024
                )
                
                result = response.choices[0].message.content
                
                # Parse result as JSON
                try:
                    return json.loads(result)
                except json.JSONDecodeError:
                    logger.warning("Failed to parse LLM output as JSON, returning raw output")
                    return {"raw_output": result}
            
            except Exception as e:
                logger.error(f"Error analyzing image with multimodal model: {e}")
                return {"error": str(e)}
    
    def compare_ui_with_design(self, design_image_path: str, ui_screenshot_path: str) -> Dict[str, Any]:
        """
        Compare a UI design with an actual UI screenshot.
        
        Args:
            design_image_path: Path to the design image.
            ui_screenshot_path: Path to the UI screenshot.
            
        Returns:
            Dictionary containing comparison results.
        """
        if not self.supports_multimodal:
            # For non-multimodal models, use image comparison and then analyze the results
            try:
                # Compare images
                similarity_score, diff_path = ImageProcessor.compare_images(design_image_path, ui_screenshot_path)
                
                # Extract text from both images
                design_text = ImageProcessor.extract_text_from_image(design_image_path)
                ui_text = ImageProcessor.extract_text_from_image(ui_screenshot_path)
                
                # Detect UI elements in both images
                design_elements = ImageProcessor.detect_ui_elements(design_image_path)
                ui_elements = ImageProcessor.detect_ui_elements(ui_screenshot_path)
                
                # Create system prompt for comparison analysis
                system_prompt = """
                You are a UI/UX expert. Compare the design specification with the actual implementation to identify
                discrepancies, assess implementation quality, and suggest improvements. Focus on visual consistency,
                layout accuracy, and functional equivalence.
                """
                
                # Create prompt with comparison information
                prompt = f"""
                Compare the design specification with the actual UI implementation:
                
                Design Specification:
                - Extracted Text: {design_text}
                - Detected Elements: {json.dumps(design_elements, indent=2)}
                
                Actual UI Implementation:
                - Extracted Text: {ui_text}
                - Detected Elements: {json.dumps(ui_elements, indent=2)}
                
                Similarity Score: {similarity_score:.2f} (0-1 scale, where 1 is identical)
                
                Please provide a comprehensive comparison including:
                1. Overall assessment of implementation fidelity
                2. Specific discrepancies identified
                3. Missing or additional elements
                4. Text content differences
                5. Layout and positioning issues
                6. Improvement suggestions
                
                Return your analysis as a structured JSON object.
                """
                
                # Generate completion
                result = self.generate_completion(prompt, system_prompt)
                
                # Parse result as JSON
                try:
                    comparison = json.loads(result)
                except json.JSONDecodeError:
                    logger.warning("Failed to parse LLM output as JSON, returning raw output")
                    comparison = {"raw_output": result}
                
                # Add comparison information
                comparison["similarity_score"] = similarity_score
                comparison["diff_image_path"] = diff_path
                comparison["design_text"] = design_text
                comparison["ui_text"] = ui_text
                comparison["design_elements"] = design_elements
                comparison["ui_elements"] = ui_elements
                
                return comparison
            
            except Exception as e:
                logger.error(f"Error comparing UI with design using non-multimodal model: {e}")
                return {"error": str(e)}
        else:
            # For multimodal models, include both images directly in the prompt
            try:
                # Encode images to base64
                design_base64 = ImageProcessor.encode_image_to_base64(design_image_path)
                ui_base64 = ImageProcessor.encode_image_to_base64(ui_screenshot_path)
                
                # Create system prompt for comparison analysis
                system_prompt = """
                You are a UI/UX expert. Compare the design specification with the actual implementation to identify
                discrepancies, assess implementation quality, and suggest improvements. Focus on visual consistency,
                layout accuracy, and functional equivalence.
                """
                
                # Create multimodal message
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": [
                        {"type": "text", "text": """
                        Compare these two images:
                        1. The first image is the design specification
                        2. The second image is the actual UI implementation
                        
                        Please provide a comprehensive comparison including:
                        1. Overall assessment of implementation fidelity
                        2. Specific discrepancies identified
                        3. Missing or additional elements
                        4. Text content differences
                        5. Layout and positioning issues
                        6. Improvement suggestions
                        
                        Return your analysis as a structured JSON object.
                        """},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{design_base64}"}},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{ui_base64}"}}
                    ]}
                ]
                
                # Call API with multimodal message
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=1024
                )
                
                result = response.choices[0].message.content
                
                # Parse result as JSON
                try:
                    comparison = json.loads(result)
                except json.JSONDecodeError:
                    logger.warning("Failed to parse LLM output as JSON, returning raw output")
                    comparison = {"raw_output": result}
                
                # Add comparison information from image processing
                try:
                    similarity_score, diff_path = ImageProcessor.compare_images(design_image_path, ui_screenshot_path)
                    comparison["similarity_score"] = similarity_score
                    comparison["diff_image_path"] = diff_path
                except Exception as e:
                    logger.warning(f"Error generating image comparison data: {e}")
                
                return comparison
            
            except Exception as e:
                logger.error(f"Error comparing UI with design using multimodal model: {e}")
                return {"error": str(e)}


# Factory function to create LLM provider instances
def create_llm_provider(provider_name: str, api_key: Optional[str] = None, model: Optional[str] = None) -> LLMProvider:
    """
    Create an LLM provider instance based on the provider name.
    
    Args:
        provider_name: Name of the LLM provider.
        api_key: Optional API key for the provider.
        model: Optional model name for the provider.
        
    Returns:
        LLMProvider instance.
    """
    if provider_name.lower() == "groq":
        return GroqProvider(api_key, model)
    elif provider_name.lower() == "hyperbolic":
        from hyperbolic_provider import HyperbolicProvider
        return HyperbolicProvider(api_key, model)
    elif provider_name.lower() == "ollama":
        from ollama_provider import OllamaProvider
        return OllamaProvider(model=model)
    elif provider_name.lower() == "lmstudio":
        from lmstudio_provider import LMStudioProvider
        return LMStudioProvider(api_key, model)
    else:
        raise ValueError(f"Unsupported LLM provider: {provider_name}")

"""
Visual Testing module for AI QA Agent.
This module provides functionality for detecting visual bugs and UI/UX issues.
"""
import os
import logging
import json
import base64
from typing import Dict, List, Any, Optional, Union, Tuple
from pathlib import Path
import re
import cv2
import numpy as np
import pytesseract
from PIL import Image
from skimage.metrics import structural_similarity as ssim
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from io import BytesIO

from llm_integration import get_llm_integration

logger = logging.getLogger(__name__)

class VisualTesting:
    """Visual testing functionality for detecting UI/UX bugs."""
    
    def __init__(self, llm_provider: str = "groq"):
        """
        Initialize the Visual Testing module.
        
        Args:
            llm_provider: The LLM provider to use for analysis.
        """
        self.llm = get_llm_integration(llm_provider)
        logger.info(f"Initialized Visual Testing module with LLM provider: {llm_provider}")
    
    def analyze_screenshot(self, screenshot_path: str, expected_state: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Analyze a screenshot to detect visual bugs.
        
        Args:
            screenshot_path: Path to the screenshot image.
            expected_state: Optional dictionary describing the expected visual state.
            
        Returns:
            Dictionary containing analysis results.
        """
        logger.info(f"Analyzing screenshot: {screenshot_path}")
        
        # Check if the file exists
        if not os.path.exists(screenshot_path):
            logger.warning(f"Screenshot file not found: {screenshot_path}")
            return {"error": "Screenshot file not found"}
        
        # Extract text using OCR
        extracted_text = self.extract_text_from_image(screenshot_path)
        
        # Detect UI elements
        ui_elements = self.detect_ui_elements_cv(screenshot_path)
        
        # Generate a description of the screenshot
        screenshot_description = self._describe_screenshot(screenshot_path, extracted_text, ui_elements)
        
        # Convert expected state to a text description
        expected_description = ""
        if expected_state:
            expected_description = json.dumps(expected_state, indent=2)
        
        # Use LLM to detect visual bugs
        visual_bugs = self.llm.detect_visual_bugs(screenshot_description, expected_description)
        
        return {
            "screenshot_path": screenshot_path,
            "screenshot_description": screenshot_description,
            "extracted_text": extracted_text,
            "ui_elements": ui_elements,
            "expected_state": expected_state,
            "visual_bugs": visual_bugs
        }
    
    def _describe_screenshot(self, screenshot_path: str, extracted_text: str = "", ui_elements: List[Dict[str, Any]] = None) -> str:
        """
        Generate a textual description of a screenshot.
        
        Args:
            screenshot_path: Path to the screenshot image.
            extracted_text: Text extracted from the image using OCR.
            ui_elements: List of detected UI elements.
            
        Returns:
            Textual description of the screenshot.
        """
        # Check if the file exists
        if not os.path.exists(screenshot_path):
            logger.warning(f"Screenshot file not found: {screenshot_path}")
            return "Screenshot file not found"
        
        # Get basic information about the file
        file_info = os.stat(screenshot_path)
        file_size = file_info.st_size
        file_extension = Path(screenshot_path).suffix.lower()
        
        # Get image dimensions
        img = cv2.imread(screenshot_path)
        if img is not None:
            height, width, channels = img.shape
            dimensions_info = f"dimensions: {width}x{height} pixels, {channels} channels"
        else:
            dimensions_info = "dimensions: unknown (failed to read image)"
        
        # Compile the description
        description = f"Screenshot file: {os.path.basename(screenshot_path)}, size: {file_size} bytes, type: {file_extension}, {dimensions_info}"
        
        if extracted_text:
            description += f"\n\nExtracted text:\n{extracted_text}"
        
        if ui_elements:
            ui_elements_desc = "\n".join([f"- {elem.get('type', 'Element')}: {elem.get('description', 'Unknown')}" for elem in ui_elements[:10]])
            description += f"\n\nDetected UI elements:\n{ui_elements_desc}"
            if len(ui_elements) > 10:
                description += f"\n... and {len(ui_elements) - 10} more elements"
        
        return description
    
    def compare_screenshots(self, baseline_path: str, current_path: str, output_diff_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Compare two screenshots to detect visual differences.
        
        Args:
            baseline_path: Path to the baseline screenshot.
            current_path: Path to the current screenshot.
            output_diff_path: Optional path to save the difference visualization.
            
        Returns:
            Dictionary containing comparison results.
        """
        logger.info(f"Comparing screenshots: {baseline_path} vs {current_path}")
        
        # Check if both files exist
        if not os.path.exists(baseline_path):
            logger.warning(f"Baseline screenshot file not found: {baseline_path}")
            return {"error": "Baseline screenshot file not found"}
        
        if not os.path.exists(current_path):
            logger.warning(f"Current screenshot file not found: {current_path}")
            return {"error": "Current screenshot file not found"}
        
        # Read images
        baseline_img = cv2.imread(baseline_path)
        current_img = cv2.imread(current_path)
        
        if baseline_img is None or current_img is None:
            logger.error("Failed to read one or both images")
            return {"error": "Failed to read one or both images"}
        
        # Resize images to match dimensions if needed
        if baseline_img.shape != current_img.shape:
            logger.info("Resizing images to match dimensions")
            current_img = cv2.resize(current_img, (baseline_img.shape[1], baseline_img.shape[0]))
        
        # Convert images to grayscale
        baseline_gray = cv2.cvtColor(baseline_img, cv2.COLOR_BGR2GRAY)
        current_gray = cv2.cvtColor(current_img, cv2.COLOR_BGR2GRAY)
        
        # Compute SSIM between the two images
        (score, diff) = ssim(baseline_gray, current_gray, full=True)
        logger.info(f"SSIM Score: {score}")
        
        # The diff image contains the actual image differences between the two images
        # and is represented as a floating point data type in the range [0,1]
        # so we must convert the array to 8-bit unsigned integers in the range
        # [0,255] before we can use it with OpenCV
        diff = (diff * 255).astype("uint8")
        
        # Threshold the difference image, followed by finding contours to
        # obtain the regions of the two input images that differ
        thresh = cv2.threshold(diff, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
        contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Create a copy of the current image to draw differences on
        diff_img = current_img.copy()
        
        # Draw contours around the differences
        cv2.drawContours(diff_img, contours, -1, (0, 0, 255), 2)
        
        # Count the number of differences
        num_differences = len(contours)
        
        # Calculate the percentage of different pixels
        total_pixels = baseline_gray.shape[0] * baseline_gray.shape[1]
        different_pixels = np.sum(thresh > 0)
        percent_diff = (different_pixels / total_pixels) * 100
        
        # Save the difference visualization if requested
        if output_diff_path:
            cv2.imwrite(output_diff_path, diff_img)
            logger.info(f"Saved difference visualization to {output_diff_path}")
        
        # Extract text from both images
        baseline_text = self.extract_text_from_image(baseline_path)
        current_text = self.extract_text_from_image(current_path)
        
        # Generate descriptions of both screenshots
        baseline_description = self._describe_screenshot(baseline_path, baseline_text)
        current_description = self._describe_screenshot(current_path, current_text)
        
        # Use LLM to analyze the differences
        system_prompt = """
        You are a QA expert specialized in detecting visual differences between screenshots.
        Your goal is to identify specific visual differences that might indicate bugs or regressions.
        Focus on practical, actionable findings that affect the user experience.
        """
        
        prompt = f"""
        Baseline Screenshot Description: {baseline_description}
        
        Current Screenshot Description: {current_description}
        
        Technical Comparison Results:
        - SSIM Score: {score} (1.0 means identical images, 0.0 means completely different)
        - Number of difference regions: {num_differences}
        - Percentage of different pixels: {percent_diff:.2f}%
        
        Based on these descriptions and technical results, identify any potential visual differences that might indicate bugs or regressions.
        For each difference, provide:
        1. A description of the difference
        2. The severity (Low, Medium, High)
        3. The potential impact on user experience
        4. A suggestion for fixing the issue
        
        Return your analysis as a list of differences in JSON format.
        """
        
        result = self.llm.generate_completion(prompt, system_prompt)
        
        # Attempt to parse the result as JSON
        try:
            differences = json.loads(result)
        except json.JSONDecodeError:
            # If parsing fails, extract differences manually
            differences = self._extract_differences_from_text(result)
        
        return {
            "baseline_path": baseline_path,
            "current_path": current_path,
            "ssim_score": score,
            "num_differences": num_differences,
            "percent_diff": percent_diff,
            "baseline_description": baseline_description,
            "current_description": current_description,
            "differences": differences,
            "output_diff_path": output_diff_path
        }
    
    def _extract_differences_from_text(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract differences from text output when JSON parsing fails.
        
        Args:
            text: The text output from the LLM.
            
        Returns:
            List of differences extracted from the text.
        """
        differences = []
        current_diff = {}
        
        for line in text.split('\n'):
            line = line.strip()
            if not line:
                continue
            
            if line.startswith('Difference') or line.startswith('Issue') or line.startswith('-'):
                if current_diff and 'description' in current_diff:
                    differences.append(current_diff)
                current_diff = {'description': line}
            elif 'severity' in line.lower():
                for severity in ['low', 'medium', 'high']:
                    if severity in line.lower():
                        current_diff['severity'] = severity.capitalize()
                        break
            elif 'impact' in line.lower():
                current_diff['impact'] = line
            elif 'fix' in line.lower() or 'suggestion' in line.lower():
                current_diff['suggestion'] = line
        
        if current_diff and 'description' in current_diff:
            differences.append(current_diff)
        
        return differences if differences else [{"description": text}]
    
    def extract_text_from_image(self, image_path: str) -> str:
        """
        Extract text from an image using OCR.
        
        Args:
            image_path: Path to the image.
            
        Returns:
            Extracted text.
        """
        logger.info(f"Extracting text from image: {image_path}")
        
        # Check if the file exists
        if not os.path.exists(image_path):
            logger.warning(f"Image file not found: {image_path}")
            return ""
        
        try:
            # Read the image
            img = cv2.imread(image_path)
            if img is None:
                logger.error(f"Failed to read image: {image_path}")
                return ""
            
            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Apply thresholding to preprocess the image
            thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
            
            # Apply dilation and erosion to remove noise
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
            opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)
            
            # Use pytesseract to extract text
            text = pytesseract.image_to_string(opening)
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"Error extracting text from image: {e}")
            return ""
    
    def detect_ui_elements(self, screenshot_path: str) -> Dict[str, Any]:
        """
        Detect UI elements in a screenshot.
        
        Args:
            screenshot_path: Path to the screenshot image.
            
        Returns:
            Dictionary containing detected UI elements.
        """
        logger.info(f"Detecting UI elements in screenshot: {screenshot_path}")
        
        # Check if the file exists
        if not os.path.exists(screenshot_path):
            logger.warning(f"Screenshot file not found: {screenshot_path}")
            return {"error": "Screenshot file not found"}
        
        # Detect UI elements using computer vision
        ui_elements = self.detect_ui_elements_cv(screenshot_path)
        
        # Extract text from the image
        extracted_text = self.extract_text_from_image(screenshot_path)
        
        # Generate a description of the screenshot
        screenshot_description = self._describe_screenshot(screenshot_path, extracted_text, ui_elements)
        
        # Use LLM to enhance the UI element detection
        system_prompt = """
        You are a QA expert specialized in identifying UI elements in web applications.
        Your goal is to identify specific UI elements that might be present in a screenshot.
        Focus on common UI elements like buttons, links, forms, inputs, dropdowns, etc.
        """
        
        prompt = f"""
        Screenshot Description: {screenshot_description}
        
        Based on this description and the detected UI elements, identify potential UI elements that might be present in the screenshot.
        For each element, provide:
        1. The element type (button, link, input, dropdown, etc.)
        2. A description of the element
        3. The potential purpose or function of the element
        
        Return your analysis as a list of UI elements in JSON format.
        """
        
        result = self.llm.generate_completion(prompt, system_prompt)
        
        # Attempt to parse the result as JSON
        try:
            llm_ui_elements = json.loads(result)
            # Merge with the CV-detected elements
            for elem in llm_ui_elements:
                if elem not in ui_elements:
                    ui_elements.append(elem)
        except json.JSONDecodeError:
            # If parsing fails, extract UI elements manually
            llm_ui_elements = self._extract_ui_elements_from_text(result)
            # Merge with the CV-detected elements
            for elem in llm_ui_elements:
                if elem not in ui_elements:
                    ui_elements.append(elem)
        
        return {
            "screenshot_path": screenshot_path,
            "screenshot_description": screenshot_description,
            "extracted_text": extracted_text,
            "ui_elements": ui_elements
        }
    
    def detect_ui_elements_cv(self, screenshot_path: str) -> List[Dict[str, Any]]:
        """
        Detect UI elements in a screenshot using computer vision techniques.
        
        Args:
            screenshot_path: Path to the screenshot image.
            
        Returns:
            List of detected UI elements.
        """
        logger.info(f"Detecting UI elements using CV in screenshot: {screenshot_path}")
        
        # Check if the file exists
        if not os.path.exists(screenshot_path):
            logger.warning(f"Screenshot file not found: {screenshot_path}")
            return []
        
        try:
            # Read the image
            img = cv2.imread(screenshot_path)
            if img is None:
                logger.error(f"Failed to read image: {screenshot_path}")
                return []
            
            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Apply thresholding
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
            
            # Find contours
            contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            
            # Filter contours by size
            min_area = 100  # Minimum area to consider
            filtered_contours = [cnt for cnt in contours if cv2.contourArea(cnt) > min_area]
            
            ui_elements = []
            
            # Process each contour
            for i, contour in enumerate(filtered_contours):
                # Get bounding box
                x, y, w, h = cv2.boundingRect(contour)
                
                # Skip if too small
                if w < 10 or h < 10:
                    continue
                
                # Determine element type based on aspect ratio and size
                aspect_ratio = w / h
                
                if aspect_ratio > 3:
                    element_type = "text_field"
                elif aspect_ratio < 0.5:
                    element_type = "scrollbar"
                elif w < 50 and h < 50 and aspect_ratio > 0.8 and aspect_ratio < 1.2:
                    element_type = "button"
                else:
                    element_type = "container"
                
                # Extract the region of interest
                roi = img[y:y+h, x:x+w]
                
                # Try to extract text from this element
                roi_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
                _, roi_thresh = cv2.threshold(roi_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                roi_text = pytesseract.image_to_string(roi_thresh).strip()
                
                # If text was found, refine the element type
                if roi_text:
                    if "submit" in roi_text.lower() or "login" in roi_text.lower() or "sign" in roi_text.lower():
                        element_type = "button"
                    elif "search" in roi_text.lower():
                        element_type = "search_field"
                    elif "@" in roi_text:
                        element_type = "email_field"
                    elif "password" in roi_text.lower():
                        element_type = "password_field"
                    elif "menu" in roi_text.lower():
                        element_type = "menu"
                
                ui_elements.append({
                    "type": element_type,
                    "description": roi_text if roi_text else f"{element_type} at ({x}, {y})",
                    "position": {"x": x, "y": y, "width": w, "height": h},
                    "text": roi_text
                })
            
            return ui_elements
            
        except Exception as e:
            logger.error(f"Error detecting UI elements: {e}")
            return []
    
    def _extract_ui_elements_from_text(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract UI elements from text output when JSON parsing fails.
        
        Args:
            text: The text output from the LLM.
            
        Returns:
            List of UI elements extracted from the text.
        """
        ui_elements = []
        current_element = {}
        
        for line in text.split('\n'):
            line = line.strip()
            if not line:
                continue
            
            if line.startswith('Element') or line.startswith('UI Element') or line.startswith('-'):
                if current_element and 'description' in current_element:
                    ui_elements.append(current_element)
                current_element = {'description': line}
            elif 'type' in line.lower():
                for element_type in ['button', 'link', 'input', 'dropdown', 'form', 'checkbox', 'radio', 'text', 'image']:
                    if element_type in line.lower():
                        current_element['type'] = element_type
                        break
            elif 'purpose' in line.lower() or 'function' in line.lower():
                current_element['purpose'] = line
        
        if current_element and 'description' in current_element:
            ui_elements.append(current_element)
        
        return ui_elements if ui_elements else [{"description": text}]
    
    def generate_heatmap(self, screenshot_path: str, interaction_data: List[Dict[str, Any]], 
                        output_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a heatmap visualization of user interactions.
        
        Args:
            screenshot_path: Path to the screenshot image.
            interaction_data: List of user interactions (clicks, scrolls, etc.).
                Each interaction should have 'x', 'y', and 'weight' keys.
            output_path: Optional path to save the heatmap visualization.
            
        Returns:
            Dictionary containing heatmap generation results.
        """
        logger.info(f"Generating heatmap for screenshot: {screenshot_path}")
        
        # Check if the file exists
        if not os.path.exists(screenshot_path):
            logger.warning(f"Screenshot file not found: {screenshot_path}")
            return {"error": "Screenshot file not found"}
        
        try:
            # Read the image
            img = cv2.imread(screenshot_path)
            if img is None:
                logger.error(f"Failed to read image: {screenshot_path}")
                return {"error": "Failed to read image"}
            
            # Get image dimensions
            height, width, _ = img.shape
            
            # Create a blank heatmap
            heatmap = np.zeros((height, width), dtype=np.float32)
            
            # Add each interaction to the heatmap
            for interaction in interaction_data:
                x = interaction.get('x', 0)
                y = interaction.get('y', 0)
                weight = interaction.get('weight', 1.0)
                
                # Skip if coordinates are out of bounds
                if x < 0 or x >= width or y < 0 or y >= height:
                    continue
                
                # Add a Gaussian blob at the interaction point
                radius = int(50 * weight)  # Scale radius by weight
                cv2.circle(heatmap, (x, y), radius, weight, -1)
            
            # Apply Gaussian blur to smooth the heatmap
            heatmap = cv2.GaussianBlur(heatmap, (51, 51), 0)
            
            # Normalize the heatmap
            heatmap = cv2.normalize(heatmap, None, 0, 1, cv2.NORM_MINMAX)
            
            # Convert the heatmap to a colormap
            heatmap_colored = cv2.applyColorMap((heatmap * 255).astype(np.uint8), cv2.COLORMAP_JET)
            
            # Blend the heatmap with the original image
            result = cv2.addWeighted(img, 0.7, heatmap_colored, 0.3, 0)
            
            # Save the result if output path is provided
            if output_path:
                cv2.imwrite(output_path, result)
                logger.info(f"Saved heatmap visualization to {output_path}")
            
            # Convert the result to a base64-encoded string
            _, buffer = cv2.imencode('.png', result)
            result_base64 = base64.b64encode(buffer).decode('utf-8')
            
            return {
                "screenshot_path": screenshot_path,
                "interaction_count": len(interaction_data),
                "output_path": output_path,
                "heatmap_base64": result_base64
            }
            
        except Exception as e:
            logger.error(f"Error generating heatmap: {e}")
            return {"error": f"Error generating heatmap: {e}"}
    
    def analyze_ui_ux_issues(self, screenshot_path: str, user_flow: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Analyze UI/UX issues in a screenshot within the context of a user flow.
        
        Args:
            screenshot_path: Path to the screenshot image.
            user_flow: Optional list of steps in the user flow.
            
        Returns:
            Dictionary containing UI/UX analysis results.
        """
        logger.info(f"Analyzing UI/UX issues in screenshot: {screenshot_path}")
        
        # Check if the file exists
        if not os.path.exists(screenshot_path):
            logger.warning(f"Screenshot file not found: {screenshot_path}")
            return {"error": "Screenshot file not found"}
        
        # Extract text from the image
        extracted_text = self.extract_text_from_image(screenshot_path)
        
        # Detect UI elements
        ui_elements = self.detect_ui_elements_cv(screenshot_path)
        
        # Generate a description of the screenshot
        screenshot_description = self._describe_screenshot(screenshot_path, extracted_text, ui_elements)
        
        # Use LLM to analyze UI/UX issues
        system_prompt = """
        You are a UX expert specialized in identifying UI/UX issues in web applications.
        Your goal is to identify specific UI/UX issues that might affect the user experience.
        Focus on usability, accessibility, consistency, and clarity.
        """
        
        user_flow_text = ""
        if user_flow:
            user_flow_text = "User Flow:\n" + "\n".join([f"{i+1}. {step}" for i, step in enumerate(user_flow)])
        
        prompt = f"""
        Screenshot Description: {screenshot_description}
        
        {user_flow_text}
        
        Based on this information, identify potential UI/UX issues that might affect the user experience.
        Consider the following aspects:
        1. Usability: Is the interface easy to use and navigate?
        2. Accessibility: Is the interface accessible to users with disabilities?
        3. Consistency: Is the interface consistent with design patterns and standards?
        4. Clarity: Is the interface clear and understandable?
        5. Efficiency: Can users accomplish tasks efficiently?
        
        For each issue, provide:
        1. A description of the issue
        2. The severity (Low, Medium, High)
        3. The aspect affected (Usability, Accessibility, Consistency, Clarity, Efficiency)
        4. A suggestion for fixing the issue
        
        Return your analysis as a list of UI/UX issues in JSON format.
        """
        
        result = self.llm.generate_completion(prompt, system_prompt)
        
        # Attempt to parse the result as JSON
        try:
            ui_ux_issues = json.loads(result)
        except json.JSONDecodeError:
            # If parsing fails, extract UI/UX issues manually
            ui_ux_issues = self._extract_ui_ux_issues_from_text(result)
        
        return {
            "screenshot_path": screenshot_path,
            "screenshot_description": screenshot_description,
            "extracted_text": extracted_text,
            "ui_elements": ui_elements,
            "user_flow": user_flow,
            "ui_ux_issues": ui_ux_issues
        }
    
    def _extract_ui_ux_issues_from_text(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract UI/UX issues from text output when JSON parsing fails.
        
        Args:
            text: The text output from the LLM.
            
        Returns:
            List of UI/UX issues extracted from the text.
        """
        ui_ux_issues = []
        current_issue = {}
        
        for line in text.split('\n'):
            line = line.strip()
            if not line:
                continue
            
            if line.startswith('Issue') or line.startswith('UI/UX Issue') or line.startswith('-'):
                if current_issue and 'description' in current_issue:
                    ui_ux_issues.append(current_issue)
                current_issue = {'description': line}
            elif 'severity' in line.lower():
                for severity in ['low', 'medium', 'high']:
                    if severity in line.lower():
                        current_issue['severity'] = severity.capitalize()
                        break
            elif 'aspect' in line.lower() or 'affected' in line.lower():
                for aspect in ['usability', 'accessibility', 'consistency', 'clarity', 'efficiency']:
                    if aspect in line.lower():
                        current_issue['aspect'] = aspect.capitalize()
                        break
            elif 'fix' in line.lower() or 'suggestion' in line.lower():
                current_issue['suggestion'] = line
        
        if current_issue and 'description' in current_issue:
            ui_ux_issues.append(current_issue)
        
        return ui_ux_issues if ui_ux_issues else [{"description": text}]

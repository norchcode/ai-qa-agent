import os
import sys
import unittest
import tempfile
from PIL import Image
import numpy as np

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.llm_integration_enhanced import FileProcessor, ImageProcessor, GroqProvider

class TestFileAndImageProcessing(unittest.TestCase):
    """Test cases for file and image processing capabilities."""
    
    def setUp(self):
        """Set up test environment."""
        # Create test files
        self.test_dir = tempfile.mkdtemp()
        
        # Create text file
        self.text_file = os.path.join(self.test_dir, "test.txt")
        with open(self.text_file, "w") as f:
            f.write("This is a test file.\nIt contains multiple lines.\nFor testing file processing.")
        
        # Create code file
        self.code_file = os.path.join(self.test_dir, "test.py")
        with open(self.code_file, "w") as f:
            f.write("""
def test_function():
    \"\"\"This is a test function.\"\"\"
    print("Hello, world!")
    return True

class TestClass:
    \"\"\"This is a test class.\"\"\"
    def __init__(self):
        self.value = 42
    
    def get_value(self):
        \"\"\"Return the value.\"\"\"
        return self.value
""")
        
        # Create JSON file
        self.json_file = os.path.join(self.test_dir, "test.json")
        with open(self.json_file, "w") as f:
            f.write("""
{
    "name": "Test",
    "value": 42,
    "items": [1, 2, 3],
    "nested": {
        "key": "value"
    }
}
""")
        
        # Create test images
        self.image_file = os.path.join(self.test_dir, "test.png")
        img = Image.new('RGB', (100, 100), color='white')
        img.save(self.image_file)
        
        self.ui_image_file = os.path.join(self.test_dir, "ui.png")
        ui_img = Image.new('RGB', (300, 200), color='white')
        # Add some UI elements (rectangles of different colors)
        pixels = np.array(ui_img)
        # Blue rectangle (button)
        pixels[50:80, 50:150] = [0, 0, 255]
        # Green rectangle (text field)
        pixels[100:130, 50:250] = [0, 255, 0]
        # Red rectangle (header)
        pixels[10:40, 10:290] = [255, 0, 0]
        ui_img = Image.fromarray(pixels)
        ui_img.save(self.ui_image_file)
        
        self.design_image_file = os.path.join(self.test_dir, "design.png")
        design_img = Image.new('RGB', (300, 200), color='white')
        # Add similar UI elements with slight differences
        pixels = np.array(design_img)
        # Blue rectangle (button) - slightly different position
        pixels[55:85, 55:155] = [0, 0, 255]
        # Green rectangle (text field) - same position
        pixels[100:130, 50:250] = [0, 255, 0]
        # Red rectangle (header) - same position
        pixels[10:40, 10:290] = [255, 0, 0]
        # Yellow rectangle (new element not in UI)
        pixels[150:180, 100:200] = [255, 255, 0]
        design_img = Image.fromarray(pixels)
        design_img.save(self.design_image_file)
        
        # Initialize Groq provider if API key is available
        api_key = os.getenv("GROQ_API_KEY")
        if api_key:
            self.groq_provider = GroqProvider(api_key=api_key)
            self.groq_available = True
        else:
            self.groq_available = False
    
    def tearDown(self):
        """Clean up test environment."""
        # Remove test files
        for file_path in [self.text_file, self.code_file, self.json_file, 
                         self.image_file, self.ui_image_file, self.design_image_file]:
            if os.path.exists(file_path):
                os.remove(file_path)
        
        # Remove test directory
        if os.path.exists(self.test_dir):
            os.rmdir(self.test_dir)
    
    def test_file_type_detection(self):
        """Test file type detection."""
        self.assertEqual(FileProcessor.detect_file_type(self.text_file), "text")
        self.assertEqual(FileProcessor.detect_file_type(self.code_file), "code")
        self.assertEqual(FileProcessor.detect_file_type(self.json_file), "structured")
        self.assertEqual(FileProcessor.detect_file_type(self.image_file), "image")
    
    def test_text_extraction(self):
        """Test text extraction from files."""
        text = FileProcessor.extract_text_from_file(self.text_file)
        self.assertIn("This is a test file.", text)
        self.assertIn("multiple lines", text)
        
        code = FileProcessor.extract_text_from_file(self.code_file)
        self.assertIn("def test_function():", code)
        self.assertIn("class TestClass:", code)
        
        json_text = FileProcessor.extract_text_from_file(self.json_file)
        self.assertIn('"name": "Test"', json_text)
    
    def test_code_extraction(self):
        """Test code extraction from files."""
        code = FileProcessor.extract_code_from_file(self.code_file)
        self.assertIn("def test_function():", code)
        self.assertIn("class TestClass:", code)
    
    def test_structured_data_extraction(self):
        """Test structured data extraction from files."""
        try:
            data = FileProcessor.extract_structured_data_from_file(self.json_file)
            self.assertEqual(data["name"], "Test")
            self.assertEqual(data["value"], 42)
            self.assertEqual(data["items"], [1, 2, 3])
            self.assertEqual(data["nested"]["key"], "value")
        except ImportError:
            self.skipTest("Required libraries not available")
    
    @unittest.skipIf(not os.path.exists("/usr/bin/tesseract"), "Tesseract not installed")
    def test_image_text_extraction(self):
        """Test text extraction from images."""
        try:
            # Create an image with text
            text_image_file = os.path.join(self.test_dir, "text_image.png")
            img = Image.new('RGB', (200, 50), color='white')
            # We can't easily add text to the image in this test environment
            # So we'll just test that the function runs without error
            img.save(text_image_file)
            
            # Extract text
            ImageProcessor.extract_text_from_image(text_image_file)
            
            # Clean up
            os.remove(text_image_file)
        except ImportError:
            self.skipTest("Required libraries not available")
    
    def test_image_comparison(self):
        """Test image comparison."""
        try:
            score, diff_path = ImageProcessor.compare_images(self.ui_image_file, self.design_image_file)
            
            # Check that score is between 0 and 1
            self.assertGreaterEqual(score, 0.0)
            self.assertLessEqual(score, 1.0)
            
            # Check that diff image was created
            self.assertTrue(os.path.exists(diff_path))
            
            # Clean up
            os.remove(diff_path)
        except ImportError:
            self.skipTest("Required libraries not available")
    
    def test_ui_element_detection(self):
        """Test UI element detection."""
        try:
            elements = ImageProcessor.detect_ui_elements(self.ui_image_file)
            
            # Check that elements were detected
            self.assertGreater(len(elements), 0)
            
            # Check element structure
            for element in elements:
                self.assertIn("id", element)
                self.assertIn("type", element)
                self.assertIn("position", element)
                self.assertIn("x", element["position"])
                self.assertIn("y", element["position"])
                self.assertIn("width", element["position"])
                self.assertIn("height", element["position"])
        except ImportError:
            self.skipTest("Required libraries not available")
    
    @unittest.skipIf(True, "Skipping Groq API tests to avoid API usage")
    def test_groq_file_processing(self):
        """Test file processing with Groq API."""
        if not self.groq_available:
            self.skipTest("Groq API key not available")
        
        # Test process_file
        result = self.groq_provider.process_file(self.text_file)
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)
        
        # Test analyze_code_file
        result = self.groq_provider.analyze_code_file(self.code_file)
        self.assertIsInstance(result, dict)
        
        # Test extract_test_cases_from_file
        result = self.groq_provider.extract_test_cases_from_file(self.text_file)
        self.assertIsInstance(result, list)
    
    @unittest.skipIf(True, "Skipping Groq API tests to avoid API usage")
    def test_groq_image_processing(self):
        """Test image processing with Groq API."""
        if not self.groq_available:
            self.skipTest("Groq API key not available")
        
        # Test analyze_image
        result = self.groq_provider.analyze_image(self.ui_image_file)
        self.assertIsInstance(result, dict)
        
        # Test compare_ui_with_design
        result = self.groq_provider.compare_ui_with_design(
            self.design_image_file, self.ui_image_file)
        self.assertIsInstance(result, dict)


if __name__ == "__main__":
    unittest.main()

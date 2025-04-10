"""
Test script for the implemented features of AI QA Agent.
This script tests the Visual Testing Enhancements, Reporting Enhancements, and LLM Provider Extensions.
"""
import os
import sys
import logging
import json
import time
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the modules to test
try:
    from visual_testing import VisualTester, ScreenshotComparator, OCRExtractor, HeatmapGenerator
    from report_generator import ReportGenerator
    from llm_integration import get_provider_manager, get_llm_integration
    
    # Optional import for UI testing
    try:
        from llm_provider_ui import start_ui_server
        UI_AVAILABLE = True
    except ImportError:
        UI_AVAILABLE = False
        logger.warning("LLM Provider UI not available, skipping UI tests")
    
    MODULES_AVAILABLE = True
except ImportError as e:
    MODULES_AVAILABLE = False
    logger.error(f"Failed to import modules: {e}")


class FeatureTester:
    """Test class for the implemented features."""
    
    def __init__(self, output_dir: str = "test_output"):
        """
        Initialize the feature tester.
        
        Args:
            output_dir: Directory to store test output files.
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Create subdirectories for different test outputs
        self.visual_dir = os.path.join(output_dir, "visual")
        self.report_dir = os.path.join(output_dir, "reports")
        self.llm_dir = os.path.join(output_dir, "llm")
        
        os.makedirs(self.visual_dir, exist_ok=True)
        os.makedirs(self.report_dir, exist_ok=True)
        os.makedirs(self.llm_dir, exist_ok=True)
        
        # Test data
        self.create_test_data()
    
    def create_test_data(self):
        """Create test data for the tests."""
        # Create test images for visual testing
        self.create_test_images()
        
        # Create test data for reporting
        self.test_results = {
            "test_suite": "Login Tests",
            "execution_date": "2025-04-10",
            "total_tests": 10,
            "passed": 8,
            "failed": 1,
            "skipped": 1,
            "duration": 45.2,
            "tests": [
                {
                    "name": "test_valid_login",
                    "status": "PASS",
                    "duration": 3.2,
                    "description": "Test login with valid credentials",
                    "steps": [
                        {"step": "Navigate to login page", "status": "PASS"},
                        {"step": "Enter valid username", "status": "PASS"},
                        {"step": "Enter valid password", "status": "PASS"},
                        {"step": "Click login button", "status": "PASS"},
                        {"step": "Verify dashboard is displayed", "status": "PASS"}
                    ]
                },
                {
                    "name": "test_invalid_password",
                    "status": "PASS",
                    "duration": 2.8,
                    "description": "Test login with invalid password",
                    "steps": [
                        {"step": "Navigate to login page", "status": "PASS"},
                        {"step": "Enter valid username", "status": "PASS"},
                        {"step": "Enter invalid password", "status": "PASS"},
                        {"step": "Click login button", "status": "PASS"},
                        {"step": "Verify error message is displayed", "status": "PASS"}
                    ]
                },
                {
                    "name": "test_empty_username",
                    "status": "PASS",
                    "duration": 2.5,
                    "description": "Test login with empty username",
                    "steps": [
                        {"step": "Navigate to login page", "status": "PASS"},
                        {"step": "Leave username field empty", "status": "PASS"},
                        {"step": "Enter valid password", "status": "PASS"},
                        {"step": "Click login button", "status": "PASS"},
                        {"step": "Verify username error message is displayed", "status": "PASS"}
                    ]
                },
                {
                    "name": "test_empty_password",
                    "status": "PASS",
                    "duration": 2.4,
                    "description": "Test login with empty password",
                    "steps": [
                        {"step": "Navigate to login page", "status": "PASS"},
                        {"step": "Enter valid username", "status": "PASS"},
                        {"step": "Leave password field empty", "status": "PASS"},
                        {"step": "Click login button", "status": "PASS"},
                        {"step": "Verify password error message is displayed", "status": "PASS"}
                    ]
                },
                {
                    "name": "test_password_masking",
                    "status": "PASS",
                    "duration": 3.0,
                    "description": "Test password masking functionality",
                    "steps": [
                        {"step": "Navigate to login page", "status": "PASS"},
                        {"step": "Enter password", "status": "PASS"},
                        {"step": "Verify password is masked", "status": "PASS"},
                        {"step": "Click show password icon", "status": "PASS"},
                        {"step": "Verify password is visible", "status": "PASS"}
                    ]
                },
                {
                    "name": "test_remember_me",
                    "status": "PASS",
                    "duration": 5.1,
                    "description": "Test remember me functionality",
                    "steps": [
                        {"step": "Navigate to login page", "status": "PASS"},
                        {"step": "Enter valid credentials", "status": "PASS"},
                        {"step": "Check remember me checkbox", "status": "PASS"},
                        {"step": "Click login button", "status": "PASS"},
                        {"step": "Verify login successful", "status": "PASS"},
                        {"step": "Logout", "status": "PASS"},
                        {"step": "Navigate to login page again", "status": "PASS"},
                        {"step": "Verify username is pre-filled", "status": "PASS"}
                    ]
                },
                {
                    "name": "test_forgot_password",
                    "status": "PASS",
                    "duration": 4.2,
                    "description": "Test forgot password functionality",
                    "steps": [
                        {"step": "Navigate to login page", "status": "PASS"},
                        {"step": "Click forgot password link", "status": "PASS"},
                        {"step": "Verify forgot password page is displayed", "status": "PASS"},
                        {"step": "Enter email address", "status": "PASS"},
                        {"step": "Click submit button", "status": "PASS"},
                        {"step": "Verify confirmation message is displayed", "status": "PASS"}
                    ]
                },
                {
                    "name": "test_account_lockout",
                    "status": "PASS",
                    "duration": 12.5,
                    "description": "Test account lockout after multiple failed attempts",
                    "steps": [
                        {"step": "Navigate to login page", "status": "PASS"},
                        {"step": "Enter valid username", "status": "PASS"},
                        {"step": "Enter invalid password (attempt 1)", "status": "PASS"},
                        {"step": "Click login button", "status": "PASS"},
                        {"step": "Verify error message is displayed", "status": "PASS"},
                        {"step": "Enter invalid password (attempt 2)", "status": "PASS"},
                        {"step": "Click login button", "status": "PASS"},
                        {"step": "Verify error message is displayed", "status": "PASS"},
                        {"step": "Enter invalid password (attempt 3)", "status": "PASS"},
                        {"step": "Click login button", "status": "PASS"},
                        {"step": "Verify account lockout message is displayed", "status": "PASS"}
                    ]
                },
                {
                    "name": "test_login_api_integration",
                    "status": "FAIL",
                    "duration": 6.5,
                    "description": "Test login API integration",
                    "steps": [
                        {"step": "Navigate to login page", "status": "PASS"},
                        {"step": "Enter valid username", "status": "PASS"},
                        {"step": "Enter valid password", "status": "PASS"},
                        {"step": "Intercept API call", "status": "PASS"},
                        {"step": "Verify API request format", "status": "PASS"},
                        {"step": "Verify API response handling", "status": "FAIL", 
                         "error": "Expected token in response, but received null"}
                    ],
                    "error": "API response validation failed: Expected token in response, but received null",
                    "screenshot": "login_api_failure.png"
                },
                {
                    "name": "test_oauth_login",
                    "status": "SKIP",
                    "duration": 0,
                    "description": "Test OAuth login integration",
                    "skip_reason": "OAuth provider not available in test environment"
                }
            ]
        }
        
        # Create test data for LLM testing
        self.test_case = """
Feature: Shopping Cart
  As a customer
  I want to add items to my shopping cart
  So that I can purchase them

  Scenario: Add item to empty cart
    Given I am on the product page
    When I click the "Add to Cart" button
    Then the item should be added to my cart
    And the cart count should display "1"
    And the cart subtotal should be updated

  Scenario: Add multiple quantities of an item
    Given I am on the product page
    When I set the quantity to "3"
    And I click the "Add to Cart" button
    Then the item should be added to my cart with quantity 3
    And the cart count should display "3"
    And the cart subtotal should be updated
        """
    
    def create_test_images(self):
        """Create test images for visual testing."""
        # Create baseline image
        baseline_img = Image.new('RGB', (400, 300), color=(255, 255, 255))
        draw = self._get_image_draw(baseline_img)
        draw.rectangle([50, 50, 350, 100], fill=(200, 200, 200), outline=(0, 0, 0))
        draw.text((100, 65), "Login", fill=(0, 0, 0))
        draw.rectangle([100, 120, 300, 160], fill=(240, 240, 240), outline=(0, 0, 0))
        draw.text((110, 130), "Username", fill=(0, 0, 0))
        draw.rectangle([100, 180, 300, 220], fill=(240, 240, 240), outline=(0, 0, 0))
        draw.text((110, 190), "Password", fill=(0, 0, 0))
        draw.rectangle([150, 240, 250, 270], fill=(0, 120, 255), outline=(0, 0, 0))
        draw.text((180, 250), "Login", fill=(255, 255, 255))
        
        baseline_path = os.path.join(self.visual_dir, "baseline.png")
        baseline_img.save(baseline_path)
        self.baseline_image_path = baseline_path
        
        # Create current image with differences
        current_img = Image.new('RGB', (400, 300), color=(255, 255, 255))
        draw = self._get_image_draw(current_img)
        draw.rectangle([50, 50, 350, 100], fill=(200, 200, 200), outline=(0, 0, 0))
        draw.text((100, 65), "Login", fill=(0, 0, 0))
        draw.rectangle([100, 120, 300, 160], fill=(240, 240, 240), outline=(0, 0, 0))
        draw.text((110, 130), "Username", fill=(0, 0, 0))
        draw.rectangle([100, 180, 300, 220], fill=(240, 240, 240), outline=(0, 0, 0))
        draw.text((110, 190), "Password", fill=(0, 0, 0))
        # Changed button color and position
        draw.rectangle([130, 240, 270, 270], fill=(255, 0, 0), outline=(0, 0, 0))
        draw.text((180, 250), "Login", fill=(255, 255, 255))
        # Added error message
        draw.text((110, 220), "Invalid credentials", fill=(255, 0, 0))
        
        current_path = os.path.join(self.visual_dir, "current.png")
        current_img.save(current_path)
        self.current_image_path = current_path
        
        # Create image with text for OCR testing
        ocr_img = Image.new('RGB', (400, 300), color=(255, 255, 255))
        draw = self._get_image_draw(ocr_img)
        draw.text((50, 50), "Username: testuser", fill=(0, 0, 0))
        draw.text((50, 100), "Password: ********", fill=(0, 0, 0))
        draw.text((50, 150), "Login Status: Failed", fill=(255, 0, 0))
        draw.text((50, 200), "Error: Invalid credentials", fill=(255, 0, 0))
        
        ocr_path = os.path.join(self.visual_dir, "ocr_test.png")
        ocr_img.save(ocr_path)
        self.ocr_image_path = ocr_path
        
        # Create heatmap data
        heatmap_data = np.zeros((300, 400))
        # Add click points
        for _ in range(50):
            x = int(np.random.normal(200, 30))
            y = int(np.random.normal(255, 10))
            if 0 <= x < 400 and 0 <= y < 300:
                heatmap_data[y, x] += 1
        
        # Save heatmap data
        heatmap_path = os.path.join(self.visual_dir, "heatmap_data.npy")
        np.save(heatmap_path, heatmap_data)
        self.heatmap_data_path = heatmap_path
    
    def _get_image_draw(self, img):
        """Get a draw object for an image."""
        try:
            from PIL import ImageDraw
            return ImageDraw.Draw(img)
        except ImportError:
            logger.error("PIL.ImageDraw not available")
            return None
    
    def test_visual_testing_enhancements(self):
        """Test the Visual Testing Enhancements."""
        logger.info("Testing Visual Testing Enhancements...")
        
        if not MODULES_AVAILABLE:
            logger.error("Modules not available, skipping test")
            return False
        
        try:
            # Test screenshot comparison
            logger.info("Testing screenshot comparison...")
            comparator = ScreenshotComparator()
            comparison_result = comparator.compare_screenshots(
                self.baseline_image_path,
                self.current_image_path,
                os.path.join(self.visual_dir, "diff.png")
            )
            
            logger.info(f"Comparison result: {comparison_result}")
            assert comparison_result['similarity_score'] < 1.0, "Expected differences between images"
            assert comparison_result['similarity_score'] > 0.5, "Images should still be somewhat similar"
            assert os.path.exists(os.path.join(self.visual_dir, "diff.png")), "Diff image should be created"
            
            # Test OCR extraction
            logger.info("Testing OCR extraction...")
            ocr_extractor = OCRExtractor()
            ocr_result = ocr_extractor.extract_text(self.ocr_image_path)
            
            logger.info(f"OCR result: {ocr_result}")
            assert "Username" in ocr_result, "OCR should extract username text"
            assert "Password" in ocr_result, "OCR should extract password text"
            assert "Failed" in ocr_result, "OCR should extract status text"
            assert "Invalid credentials" in ocr_result, "OCR should extract error text"
            
            # Test heatmap generation
            logger.info("Testing heatmap generation...")
            heatmap_generator = HeatmapGenerator()
            heatmap_path = os.path.join(self.visual_dir, "heatmap.png")
            heatmap_generator.generate_heatmap(
                np.load(self.heatmap_data_path),
                self.baseline_image_path,
                heatmap_path
            )
            
            assert os.path.exists(heatmap_path), "Heatmap image should be created"
            
            # Test the full VisualTester class
            logger.info("Testing VisualTester class...")
            visual_tester = VisualTester()
            visual_test_result = visual_tester.analyze_visual_changes(
                self.baseline_image_path,
                self.current_image_path,
                os.path.join(self.visual_dir, "visual_analysis")
            )
            
            logger.info(f"Visual test result: {visual_test_result}")
            assert 'similarity_score' in visual_test_result, "Result should include similarity score"
            assert 'differences' in visual_test_result, "Result should include differences"
            assert 'text_changes' in visual_test_result, "Result should include text changes"
            
            logger.info("Visual Testing Enhancements tests passed!")
            return True
        except Exception as e:
            logger.error(f"Visual Testing Enhancements test failed: {e}")
            return False
    
    def test_reporting_enhancements(self):
        """Test the Reporting Enhancements."""
        logger.info("Testing Reporting Enhancements...")
        
        if not MODULES_AVAILABLE:
            logger.error("Modules not available, skipping test")
            return False
        
        try:
            # Initialize the report generator
            report_generator = ReportGenerator(output_dir=self.report_dir)
            
            # Test PDF report generation
            logger.info("Testing PDF report generation...")
            pdf_path = report_generator.generate_pdf_report(
                self.test_results,
                "Detailed Test Report",
                os.path.join(self.report_dir, "detailed_report.pdf")
            )
            
            assert os.path.exists(pdf_path), "PDF report should be created"
            assert os.path.getsize(pdf_path) > 0, "PDF report should not be empty"
            
            # Test HTML report generation
            logger.info("Testing HTML report generation...")
            html_path = report_generator.generate_html_report(
                self.test_results,
                "Interactive Test Report",
                os.path.join(self.report_dir, "interactive_report.html")
            )
            
            assert os.path.exists(html_path), "HTML report should be created"
            assert os.path.getsize(html_path) > 0, "HTML report should not be empty"
            
            # Test executive summary generation
            logger.info("Testing executive summary generation...")
            summary_path = report_generator.generate_executive_summary(
                self.test_results,
                "Executive Summary",
                os.path.join(self.report_dir, "executive_summary.pdf")
            )
            
            assert os.path.exists(summary_path), "Executive summary should be created"
            assert os.path.getsize(summary_path) > 0, "Executive summary should not be empty"
            
            logger.info("Reporting Enhancements tests passed!")
            return True
        except Exception as e:
            logger.error(f"Reporting Enhancements test failed: {e}")
            return False
    
    def test_llm_provider_extensions(self):
        """Test the LLM Provider Extensions."""
        logger.info("Testing LLM Provider Extensions...")
        
        if not MODULES_AVAILABLE:
            logger.error("Modules not available, skipping test")
            return False
        
        try:
            # Get the provider manager
            provider_manager = get_provider_manager()
            
            # Test getting available providers
            logger.info("Testing getting available providers...")
            available_providers = provider_manager.get_available_providers()
            
            logger.info(f"Available providers: {available_providers}")
            assert isinstance(available_providers, list), "Available providers should be a list"
            
            # Test provider comparison (mock if no real providers available)
            logger.info("Testing provider comparison...")
            if available_providers:
                # Use real providers if available
                comparison_result = provider_manager.compare_providers(
                    "Analyze this test case for potential issues.",
                    "You are a QA expert.",
                    available_providers[:1]  # Use only the first provider to avoid rate limits
                )
                
                logger.info(f"Comparison result: {comparison_result}")
                assert isinstance(comparison_result, dict), "Comparison result should be a dictionary"
                assert len(comparison_result) > 0, "Comparison result should not be empty"
            else:
                # Mock comparison result if no providers available
                logger.warning("No providers available, mocking comparison result")
                comparison_result = {
                    "mock_provider": {
                        "response": "This is a mock response for testing purposes.",
                        "time_taken": 0.5,
                        "success": True
                    }
                }
            
            # Test the UI server if available
            if UI_AVAILABLE:
                logger.info("Testing LLM Provider UI...")
                # Start the UI server without opening a browser
                server = start_ui_server(open_browser=False)
                
                # Wait a moment for the server to start
                time.sleep(1)
                
                # Shutdown the server
                server.shutdown()
                logger.info("LLM Provider UI test passed!")
            
            logger.info("LLM Provider Extensions tests passed!")
            return True
        except Exception as e:
            logger.error(f"LLM Provider Extensions test failed: {e}")
            return False
    
    def run_all_tests(self):
        """Run all tests and return the results."""
        results = {
            "visual_testing": self.test_visual_testing_enhancements(),
            "reporting": self.test_reporting_enhancements(),
            "llm_provider": self.test_llm_provider_extensions()
        }
        
        # Print summary
        logger.info("\n=== Test Results Summary ===")
        for test, result in results.items():
            logger.info(f"{test}: {'PASS' if result else 'FAIL'}")
        
        return results


if __name__ == "__main__":
    # Run the tests
    tester = FeatureTester()
    results = tester.run_all_tests()
    
    # Exit with appropriate status code
    sys.exit(0 if all(results.values()) else 1)

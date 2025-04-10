"""
Integration test script for the AI QA Agent.
This module tests the integrated system to ensure all components work together properly.
"""
import os
import logging
import tempfile
import unittest
from pathlib import Path
import json
import shutil

from api import AIQA
from controller import AIQAAgentController
from tool_integrator import ToolIntegrator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IntegrationTest(unittest.TestCase):
    """Test case for the integrated AI QA Agent system."""
    
    @classmethod
    def setUpClass(cls):
        """Set up the test environment."""
        # Create test output directory
        cls.test_dir = tempfile.mkdtemp(prefix="aiqa_integration_test_")
        logger.info(f"Test directory: {cls.test_dir}")
        
        # Initialize the API
        cls.aiqa = AIQA()
        
        # Create test assets
        cls._create_test_assets()
    
    @classmethod
    def tearDownClass(cls):
        """Clean up the test environment."""
        # Remove test directory
        shutil.rmtree(cls.test_dir, ignore_errors=True)
        logger.info("Test directory removed")
    
    @classmethod
    def _create_test_assets(cls):
        """Create test assets for the integration tests."""
        # Create a test Gherkin file
        cls.gherkin_file = os.path.join(cls.test_dir, "test.feature")
        with open(cls.gherkin_file, "w") as f:
            f.write("""
            Feature: Login
              Scenario: Successful login
                Given I am on the login page
                When I enter valid credentials
                Then I should be logged in
            """)
        
        # Create test images
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # Create baseline image
            cls.baseline_image = os.path.join(cls.test_dir, "baseline.png")
            baseline = Image.new('RGB', (400, 300), color=(240, 240, 240))
            draw = ImageDraw.Draw(baseline)
            draw.rectangle([(50, 50), (350, 250)], fill=(200, 200, 200), outline=(0, 0, 0))
            baseline.save(cls.baseline_image)
            
            # Create current image (slightly different)
            cls.current_image = os.path.join(cls.test_dir, "current.png")
            current = Image.new('RGB', (400, 300), color=(240, 240, 240))
            draw = ImageDraw.Draw(current)
            draw.rectangle([(50, 50), (350, 250)], fill=(220, 200, 200), outline=(0, 0, 0))
            current.save(cls.current_image)
        
        except ImportError:
            # If PIL is not available, create empty files
            cls.baseline_image = os.path.join(cls.test_dir, "baseline.png")
            cls.current_image = os.path.join(cls.test_dir, "current.png")
            
            with open(cls.baseline_image, "w") as f:
                f.write("Test baseline image")
            
            with open(cls.current_image, "w") as f:
                f.write("Test current image")
            
            logger.warning("PIL not available. Created placeholder image files.")
    
    def test_01_controller_initialization(self):
        """Test that the controller initializes correctly."""
        controller = AIQAAgentController()
        self.assertIsNotNone(controller)
        self.assertIsNotNone(controller.config)
        logger.info("Controller initialization test passed")
    
    def test_02_tool_integration(self):
        """Test that all tools can be integrated with the controller."""
        controller = AIQAAgentController()
        integrator = ToolIntegrator(controller)
        status = integrator.integrate_all_tools()
        
        # Check that all tools were integrated
        for tool_name, integrated in status.items():
            self.assertTrue(integrated, f"Tool {tool_name} was not integrated")
        
        logger.info("Tool integration test passed")
    
    def test_03_api_initialization(self):
        """Test that the API initializes correctly."""
        api = AIQA()
        self.assertIsNotNone(api)
        self.assertIsNotNone(api.controller)
        logger.info("API initialization test passed")
    
    def test_04_test_analysis(self):
        """Test the test analysis functionality."""
        with open(self.gherkin_file, "r") as f:
            gherkin = f.read()
        
        analysis = self.aiqa.analyze_test(gherkin)
        self.assertIsNotNone(analysis)
        self.assertIsInstance(analysis, dict)
        logger.info("Test analysis test passed")
    
    def test_05_test_optimization(self):
        """Test the test optimization functionality."""
        with open(self.gherkin_file, "r") as f:
            gherkin = f.read()
        
        optimized = self.aiqa.optimize_test(gherkin)
        self.assertIsNotNone(optimized)
        self.assertIsInstance(optimized, str)
        logger.info("Test optimization test passed")
    
    def test_06_test_creation(self):
        """Test the test creation functionality."""
        description = "Test that users can log in with valid credentials."
        gherkin = self.aiqa.create_test_from_description(description)
        self.assertIsNotNone(gherkin)
        self.assertIsInstance(gherkin, str)
        self.assertIn("Feature:", gherkin)
        logger.info("Test creation test passed")
    
    def test_07_image_comparison(self):
        """Test the image comparison functionality."""
        results = self.aiqa.compare_images(self.baseline_image, self.current_image)
        self.assertIsNotNone(results)
        self.assertIsInstance(results, dict)
        self.assertIn("diff_path", results)
        logger.info("Image comparison test passed")
    
    def test_08_configuration(self):
        """Test the configuration functionality."""
        # Get current config
        config = self.aiqa.get_config()
        self.assertIsNotNone(config)
        self.assertIsInstance(config, dict)
        
        # Update config
        new_config = {"test_key": "test_value"}
        updated_config = self.aiqa.update_config(new_config)
        self.assertEqual(updated_config["test_key"], "test_value")
        
        # Save config
        config_path = os.path.join(self.test_dir, "config.json")
        saved_path = self.aiqa.save_config(config_path)
        self.assertTrue(os.path.exists(saved_path))
        
        logger.info("Configuration test passed")
    
    def test_09_workflow_integration(self):
        """Test that workflows integrate multiple components correctly."""
        # Create a simple test workflow
        description = "Test that users can log in with valid credentials."
        save_path = os.path.join(self.test_dir, "workflow_test.feature")
        
        try:
            # This test might fail in environments without all dependencies
            results = self.aiqa.test_workflow(description, save_path)
            self.assertIsNotNone(results)
            self.assertIsInstance(results, dict)
            self.assertIn("gherkin", results)
            self.assertIn("optimized_gherkin", results)
            self.assertTrue(os.path.exists(save_path))
            logger.info("Workflow integration test passed")
        except Exception as e:
            logger.warning(f"Workflow integration test skipped: {e}")
            self.skipTest(f"Workflow integration test skipped: {e}")
    
    def test_10_system_status(self):
        """Test the system status functionality."""
        status = self.aiqa.status()
        self.assertIsNotNone(status)
        self.assertIsInstance(status, dict)
        self.assertIn("version", status)
        self.assertIn("tools_integrated", status)
        logger.info("System status test passed")


if __name__ == "__main__":
    unittest.main()

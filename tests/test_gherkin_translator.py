import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add the parent directory to the path so we can import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from test_analyzer.gherkin_translator import GherkinTranslator

class TestGherkinTranslator(unittest.TestCase):
    """Test cases for the GherkinTranslator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a mock LLM integration
        self.mock_llm = MagicMock()
        
        # Create a mock for the get_llm_integration function
        self.patcher = patch('test_analyzer.gherkin_translator.get_llm_integration')
        self.mock_get_llm = self.patcher.start()
        self.mock_get_llm.return_value = self.mock_llm
        
        # Create an instance of GherkinTranslator with the mock LLM
        self.translator = GherkinTranslator(llm_provider="groq")
    
    def tearDown(self):
        """Tear down test fixtures."""
        self.patcher.stop()
    
    def test_translate_to_gherkin(self):
        """Test translating natural language to Gherkin format."""
        # Set up the mock LLM to return a Gherkin feature
        self.mock_llm.generate_completion.return_value = """
Feature: Login Functionality
  Scenario: Successful login
    Given I am on the login page
    When I enter valid credentials
    And I click the login button
    Then I should be logged in successfully
"""
        
        # Test input
        test_steps = """
1. Navigate to the login page
2. Enter valid username and password
3. Click the login button
4. Verify that login is successful
"""
        
        # Call the method
        result = self.translator.translate_to_gherkin(test_steps)
        
        # Verify the result
        self.assertIn("Feature:", result)
        self.assertIn("Scenario:", result)
        self.assertIn("Given", result)
        self.assertIn("When", result)
        self.assertIn("Then", result)
        
        # Verify the mock was called correctly
        self.mock_llm.generate_completion.assert_called_once()
    
    def test_translate_from_gherkin(self):
        """Test translating Gherkin format to natural language."""
        # Set up the mock LLM to return natural language steps
        self.mock_llm.generate_completion.return_value = """
1. Navigate to the login page
2. Enter valid username and password
3. Click the login button
4. Verify that login is successful
"""
        
        # Test input
        gherkin_text = """
Feature: Login Functionality
  Scenario: Successful login
    Given I am on the login page
    When I enter valid credentials
    And I click the login button
    Then I should be logged in successfully
"""
        
        # Call the method
        result = self.translator.translate_from_gherkin(gherkin_text)
        
        # Verify the result
        self.assertIn("1.", result)
        self.assertIn("Navigate", result)
        self.assertIn("login", result)
        
        # Verify the mock was called correctly
        self.mock_llm.generate_completion.assert_called_once()
    
    def test_suggest_improvements(self):
        """Test suggesting improvements for Gherkin test steps."""
        # Set up the mock LLM to return suggestions
        self.mock_llm.generate_completion.return_value = """
1. Make the scenario title more specific by describing the exact functionality being tested
2. Add more specific details to the Given step to clarify the preconditions
3. Be more specific in the When step about what credentials are being entered
4. Add a more detailed assertion in the Then step
"""
        
        # Test input
        gherkin_text = """
Feature: Login
  Scenario: login
    Given user on login page
    When user enters credentials
    Then user is logged in
"""
        
        # Call the method
        result = self.translator.suggest_improvements(gherkin_text)
        
        # Verify the result
        self.assertIsInstance(result, list)
        self.assertTrue(len(result) > 0)
        
        # Verify the mock was called correctly
        self.mock_llm.generate_completion.assert_called_once()
    
    def test_generate_gherkin_from_description(self):
        """Test generating Gherkin from a high-level description."""
        # Set up the mock LLM to return a Gherkin feature
        self.mock_llm.generate_completion.return_value = """
Feature: User Authentication
  Scenario: Successful login with valid credentials
    Given I am on the login page
    When I enter valid username "user123" and password "pass123"
    And I click the login button
    Then I should be redirected to the dashboard
    And I should see a welcome message

  Scenario: Failed login with invalid credentials
    Given I am on the login page
    When I enter invalid username "wronguser" and password "wrongpass"
    And I click the login button
    Then I should see an error message
    And I should remain on the login page
"""
        
        # Test input
        description = "Test the login functionality with both valid and invalid credentials"
        
        # Call the method
        result = self.translator.generate_gherkin_from_description(description)
        
        # Verify the result
        self.assertIn("Feature:", result)
        self.assertIn("Scenario:", result)
        self.assertTrue("valid" in result and "invalid" in result)
        
        # Verify the mock was called correctly
        self.mock_llm.generate_completion.assert_called_once()
    
    def test_clean_gherkin(self):
        """Test cleaning up Gherkin text."""
        # Test input with markdown formatting
        gherkin_text = """```gherkin
Feature: Login
  Scenario: login
    Given user on login page
    When user enters credentials
    Then user is logged in
```"""
        
        # Call the method
        result = self.translator._clean_gherkin(gherkin_text)
        
        # Verify the result
        self.assertNotIn("```", result)
        self.assertIn("Feature:", result)
        self.assertIn("Scenario:", result)
    
    def test_clean_natural_language(self):
        """Test cleaning up natural language text."""
        # Test input with markdown formatting
        nl_text = """```
1. Navigate to the login page
2. Enter credentials
3. Click login
```"""
        
        # Call the method
        result = self.translator._clean_natural_language(nl_text)
        
        # Verify the result
        self.assertNotIn("```", result)
        self.assertIn("1.", result)
        self.assertIn("Navigate", result)

if __name__ == '__main__':
    unittest.main()

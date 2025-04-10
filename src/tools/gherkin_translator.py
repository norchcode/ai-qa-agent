"""
Gherkin translator module for AI QA Agent.
"""
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class GherkinTranslator:
    """
    Translates between Gherkin format and natural language test steps.
    """
    
    def __init__(self, llm_provider):
        """
        Initialize the Gherkin translator.
        
        Args:
            llm_provider: LLM provider for translation.
        """
        self.llm_provider = llm_provider
        logger.info("Gherkin translator initialized")
    
    def to_gherkin(self, natural_language: str) -> str:
        """
        Translate natural language test steps to Gherkin format.
        
        Args:
            natural_language: Test steps in natural language.
            
        Returns:
            Test steps in Gherkin format.
        """
        logger.info("Translating to Gherkin")
        
        # This is a placeholder implementation
        # In a real implementation, we would use the LLM to translate to Gherkin
        
        # Example translation
        if "1. Navigate to the login page" in natural_language:
            gherkin = """Feature: User Login
  Scenario: Successful login
    Given I am on the login page
    When I enter username "admin" and password "password123"
    And I click the login button
    Then I should see the dashboard"""
            return gherkin
        
        # Default translation for other cases
        lines = natural_language.strip().split('\n')
        gherkin_lines = ["Feature: Automated Test", "  Scenario: Test Scenario"]
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Remove numbering if present
            if line[0].isdigit() and '. ' in line:
                line = line.split('. ', 1)[1]
                
            if "navigate" in line.lower() or "go to" in line.lower() or "open" in line.lower():
                gherkin_lines.append(f"    Given {line}")
            elif "click" in line.lower() or "select" in line.lower() or "choose" in line.lower():
                gherkin_lines.append(f"    When {line}")
            elif "enter" in line.lower() or "type" in line.lower() or "input" in line.lower():
                gherkin_lines.append(f"    And {line}")
            elif "verify" in line.lower() or "check" in line.lower() or "assert" in line.lower() or "should" in line.lower():
                gherkin_lines.append(f"    Then {line}")
            else:
                gherkin_lines.append(f"    And {line}")
                
        return "\n".join(gherkin_lines)
    
    def from_gherkin(self, gherkin: str) -> str:
        """
        Translate Gherkin format to natural language test steps.
        
        Args:
            gherkin: Test steps in Gherkin format.
            
        Returns:
            Test steps in natural language.
        """
        logger.info("Translating from Gherkin")
        
        # This is a placeholder implementation
        # In a real implementation, we would use the LLM to translate from Gherkin
        
        # Example translation
        if "Feature: User Login" in gherkin and "Scenario: Successful login" in gherkin:
            nl_text = """1. Navigate to the login page
2. Enter username "admin" and password "password123"
3. Click the login button
4. Verify that the dashboard is displayed"""
            return nl_text
        
        # Default translation for other cases
        lines = gherkin.strip().split('\n')
        nl_lines = []
        step_num = 1
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith("Feature:") or line.startswith("Scenario:"):
                continue
                
            # Extract the step text
            parts = line.split(' ', 1)
            if len(parts) > 1 and parts[0] in ["Given", "When", "Then", "And", "But"]:
                nl_lines.append(f"{step_num}. {parts[1]}")
                step_num += 1
                
        return "\n".join(nl_lines)
    
    def generate_from_description(self, description: str) -> str:
        """
        Generate Gherkin scenarios from a test description.
        
        Args:
            description: Description of the test requirements.
            
        Returns:
            Generated Gherkin scenarios.
        """
        logger.info("Generating Gherkin from description")
        
        # This is a placeholder implementation
        # In a real implementation, we would use the LLM to generate Gherkin
        
        # Example generation for login functionality
        if "login" in description.lower():
            gherkin = """Feature: User Authentication
  As a registered user
  I want to log in to the system
  So that I can access my account

  Scenario: Successful login with valid credentials
    Given I am on the login page
    When I enter username "valid_user" in the username field
    And I enter password "valid_password" in the password field
    And I click the login button
    Then I should be redirected to the dashboard page
    And I should see a welcome message with my username

  Scenario: Failed login with invalid credentials
    Given I am on the login page
    When I enter username "invalid_user" in the username field
    And I enter password "invalid_password" in the password field
    And I click the login button
    Then I should see an error message "Invalid username or password"
    And I should remain on the login page

  Scenario: Failed login with empty credentials
    Given I am on the login page
    When I leave the username field empty
    And I leave the password field empty
    And I click the login button
    Then I should see validation messages for required fields
    And I should remain on the login page"""
            return gherkin
            
        # Example generation for registration form
        elif "registration" in description.lower() or "sign up" in description.lower() or "register" in description.lower():
            gherkin = """Feature: User Registration
  As a new user
  I want to register an account
  So that I can access the system

  Scenario: Successful registration with valid information
    Given I am on the registration page
    When I enter "John Doe" in the name field
    And I enter "john.doe@example.com" in the email field
    And I enter "Password123!" in the password field
    And I enter "Password123!" in the password confirmation field
    And I click the register button
    Then I should be redirected to the dashboard
    And I should see a welcome message

  Scenario: Failed registration with existing email
    Given I am on the registration page
    When I enter "Jane Smith" in the name field
    And I enter "existing@example.com" in the email field
    And I enter "Password123!" in the password field
    And I enter "Password123!" in the password confirmation field
    And I click the register button
    Then I should see an error message "Email already exists"
    And I should remain on the registration page

  Scenario: Failed registration with password mismatch
    Given I am on the registration page
    When I enter "John Doe" in the name field
    And I enter "john.doe@example.com" in the email field
    And I enter "Password123!" in the password field
    And I enter "DifferentPassword!" in the password confirmation field
    And I click the register button
    Then I should see an error message "Passwords do not match"
    And I should remain on the registration page"""
            return gherkin
            
        # Default generation for other cases
        return """Feature: Automated Test
  Scenario: Test Scenario
    Given I am on the application page
    When I perform the required actions
    Then I should see the expected results"""
    
    def suggest_improvements(self, gherkin: str) -> Dict[str, Any]:
        """
        Suggest improvements for Gherkin scenarios.
        
        Args:
            gherkin: Test steps in Gherkin format.
            
        Returns:
            Dictionary containing suggested improvements.
        """
        logger.info("Suggesting Gherkin improvements")
        
        # This is a placeholder implementation
        # In a real implementation, we would use the LLM to suggest improvements
        
        # Example suggestions
        suggestions = {
            "improvements": [
                {
                    "type": "clarity",
                    "message": "Use more specific step descriptions to improve clarity",
                    "example": "Change 'When I enter valid credentials' to 'When I enter username \"user123\" and password \"pass456\"'"
                },
                {
                    "type": "structure",
                    "message": "Add Feature description to provide context",
                    "example": "Add 'As a user, I want to... So that I can...'"
                },
                {
                    "type": "coverage",
                    "message": "Add scenarios for edge cases",
                    "example": "Add scenarios for invalid inputs, boundary conditions, etc."
                }
            ],
            "score": 75,
            "optimized_gherkin": gherkin  # In a real implementation, this would be an improved version
        }
        
        return suggestions

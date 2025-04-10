Feature: User Authentication
  As a user of the application
  I want to be able to log in and log out
  So that I can access my account securely

  Background:
    Given the application is running
    And I am on the login page

  Scenario: Successful login with valid credentials
    When I enter "valid_user" in the username field
    And I enter "correct_password" in the password field
    And I click the login button
    Then I should be redirected to the dashboard
    And I should see a welcome message with my username
    And the navigation menu should show authenticated user options

  Scenario: Failed login with invalid password
    When I enter "valid_user" in the username field
    And I enter "wrong_password" in the password field
    And I click the login button
    Then I should remain on the login page
    And I should see an error message indicating invalid credentials
    And the password field should be cleared

  Scenario: Failed login with non-existent username
    When I enter "nonexistent_user" in the username field
    And I enter "any_password" in the password field
    And I click the login button
    Then I should remain on the login page
    And I should see an error message indicating invalid credentials
    And both username and password fields should be cleared

  Scenario: Logout from dashboard
    Given I am logged in as "valid_user"
    And I am on the dashboard page
    When I click the logout button in the navigation menu
    Then I should be redirected to the login page
    And I should see a message confirming successful logout
    And I should not be able to access protected pages without logging in again

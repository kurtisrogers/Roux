Feature: Public website
  As a parent
  I want to browse the wraparound care website
  So that I can learn about sessions and register

  Background:
    Given the application is running

  Scenario: Homepage displays club information
    Given I am on the homepage
    Then I should see "Oakwood Wraparound Club"

  Scenario: Sessions page is accessible
    Given I visit "/sessions/"
    Then the page title should contain "Sessions"

  Scenario: Registration page loads
    Given I visit "/accounts/register/"
    Then I should see "Parent Registration"

Feature: Parent session discovery
  As a parent
  I want to find after-school sessions easily
  So that I can book wraparound care

  Background:
    Given the application is running
    And I am logged in as a parent

  Scenario: Sessions show pricing
    When I browse available sessions
    Then I should see "£"

  Scenario: Sessions show spaces remaining
    When I browse available sessions
    Then I should see "spaces left"

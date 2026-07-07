Feature: Activity catalogue management
  As an organisation admin
  I want to maintain a global activity library
  So that week packs can reference consistent activities

  Background:
    Given the application is running
    And I am logged in as admin

  Scenario: View seeded creative activity
    When I open the activities catalogue
    Then the activities table should list "Arts & crafts"

  Scenario: View seeded homework activity
    When I open the activities catalogue
    Then the activities table should list "Homework club"

  Scenario: Add a new sport activity
    When I open the activities catalogue
    And I add activity "Dodgeball" in category "Sport"
    Then I should see "Dodgeball"
    And the activities table should list "Dodgeball"

  Scenario: Add a new outdoor activity
    When I open the activities catalogue
    And I add activity "Nature walk" in category "Outdoor"
    Then the activities table should list "Nature walk"

  Scenario: Add a quiet activity
    When I open the activities catalogue
    And I add activity "Reading corner" in category "Quiet / homework"
    Then the activities table should list "Reading corner"

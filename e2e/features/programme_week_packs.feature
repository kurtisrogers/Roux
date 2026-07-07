Feature: Week pack management
  As an organisation admin
  I want to build and duplicate weekly timetables
  So that Week A and Week B are easy to maintain

  Background:
    Given the application is running
    And I am logged in as admin

  Scenario: View Week A pack with time slots
    When I open the week packs list
    And I open week pack "Week A"
    Then I should see heading "Week A"
    And the week pack grid should show "Football"

  Scenario: View Week B pack
    When I open the week packs list
    And I open week pack "Week B"
    Then I should see heading "Week B"
    And the week pack grid should show "Snack time"

  Scenario: Duplicate a week pack
    When I open the week packs list
    And I open week pack "Week A"
    And I duplicate the current week pack
    Then I should see "Week A (copy)"

  Scenario: Create a thematic week pack
    When I open the week packs list
    And I create week pack "Sports week"
    Then I should see heading "Sports week"

  Scenario: Add a block to a week pack
    When I open the week packs list
    And I create week pack "Test pack"
    And I add a Monday slot from 15:30 to 16:15 using activity "Football"
    Then the week pack grid should show "Football"

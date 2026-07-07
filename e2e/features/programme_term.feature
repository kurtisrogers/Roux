Feature: Programme term planning
  As an organisation admin
  I want to assign Week A and Week B to a term
  So that activities alternate automatically

  Background:
    Given the application is running
    And I am logged in as admin

  Scenario: View published summer programme
    When I open the programmes list
    And I open programme "Summer term after-school"
    Then I should see "Week A"
    And I should see "Week B"
    And I should see "Published"

  Scenario: Programme preview shows weekdays
    When I open the programmes list
    And I open programme "Summer term after-school"
    Then I should see "Preview"

  Scenario: Open programme calendar
    When I open the programmes list
    And I open programme "Summer term after-school"
    And I open the programme calendar
    Then I should see heading "Summer term after-school calendar"
    And I should see week label "Week A" on the calendar

  Scenario: Calendar shows edit links
    When I open the programmes list
    And I open programme "Summer term after-school"
    And I open the programme calendar
    Then I should see "Edit"

  Scenario: Start new programme wizard
    When I open the programmes list
    And I start creating a new programme
    Then I should see heading "New programme"
    And I should see "Week a pack"

  Scenario: Navigate from programme to week packs
    When I open the programmes list
    And I click "Week packs"
    Then I should see heading "Week packs"

Feature: Programme closures and overrides
  As an organisation admin
  I want to mark non-running periods and override individual days
  So that the run sheet reflects reality

  Background:
    Given the application is running
    And I am logged in as admin

  Scenario: Add organisation closure period
    When I open the closures page
    And I add closure from "2030-08-01" to "2030-08-08" labelled "Summer shutdown"
    Then I should see "Summer shutdown"
    And the table should contain "Aug 2030"

  Scenario: Add half-term closure
    When I open the closures page
    And I add closure from "2030-10-20" to "2030-10-24" labelled "Half term"
    Then I should see "Half term"

  Scenario: Open programme day editor
    When I open the programmes list
    And I open programme "Summer term after-school"
    And I open the programme calendar
    And I open the first programme day editor
    Then I should see "Resolved timetable"

  Scenario: Replace a programme day with a trip
    When I open the programmes list
    And I open programme "Summer term after-school"
    And I open the programme calendar
    And I open the first programme day editor
    And I replace the programme day with a trip
    And I open the first programme day editor
    Then I should see "Coach trip"

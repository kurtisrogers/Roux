Feature: Programme planner navigation
  As an organisation admin
  I want to reach all programme planning screens
  So that I can manage activities and term plans

  Background:
    Given the application is running
    And I am logged in as admin

  Scenario: Programme planner list loads
    When I open the programmes list
    Then I should see heading "Programmes"
    And I should see "Summer term after-school"

  Scenario: Activities catalogue loads
    When I open the activities catalogue
    Then I should see heading "Activities"
    And the table should contain "Football"
    And the table should contain "Snack time"

  Scenario: Week packs list shows Week A and Week B
    When I open the week packs list
    Then I should see heading "Week packs"
    And I should see "Week A"
    And I should see "Week B"

  Scenario: Closures page loads
    When I open the closures page
    Then I should see heading "Closures"
    And I should see heading "Add closure period"

  Scenario: Sidebar links to programme planner
    When I navigate to "/dashboard/"
    And I click "Programme Planner"
    Then I should see heading "Programmes"

  Scenario: Sidebar links to activities
    When I navigate to "/dashboard/"
    And I click "Activities"
    Then I should see heading "Activities"

  Scenario: Sidebar links to week packs
    When I navigate to "/dashboard/"
    And I click "Week Packs"
    Then I should see heading "Week packs"

  Scenario: Sidebar links to closures
    When I navigate to "/dashboard/"
    And I click "Closures"
    Then I should see heading "Closures"

Feature: Session register and programme integration
  As club staff
  I want the session register to show today's programme
  So that I know which activities to run

  Background:
    Given the application is running
    And I am logged in as admin

  Scenario: Open session register for after-school club
    When I open the after-school session register
    Then I should see heading "Session Register"
    And I should see "After School Club"

  Scenario: Register shows programme run sheet
    When I open the after-school session register
    Then I should see the programme run sheet

  Scenario: Register programme includes snack time
    When I open the after-school session register
    Then I should see snack time on the register programme

  Scenario: Session detail shows today's programme
    When I open the after-school session detail
    Then I should see today's programme on the session page

  Scenario: Walk-in booking form loads
    When I open the walk-in booking form for the first session
    Then I should see heading "Walk-in booking"

  Scenario: Register has check in all button
    When I open the after-school session register
    Then I should see "Check in all"

  Scenario: Register has export CSV link
    When I open the after-school session register
    Then I should see "Export CSV"

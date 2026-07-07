Feature: Operations sidebar navigation
  As an organisation admin
  I want quick access from the dashboard sidebar
  So that I can move between operational tasks

  Background:
    Given the application is running
    And I am logged in as admin

  Scenario: Navigate to waitlist from dashboard
    When I navigate to "/dashboard/"
    And I click "Waitlist"
    Then I should see heading "Waitlist"

  Scenario: Navigate to recurring bookings
    When I navigate to "/dashboard/"
    And I click "Recurring"
    Then I should see heading "Recurring bookings"

  Scenario: Navigate to childcare vouchers
    When I navigate to "/dashboard/"
    And I click "Childcare Vouchers"
    Then I should see heading "Childcare vouchers"

  Scenario: Navigate to analytics
    When I navigate to "/dashboard/"
    And I click "Analytics"
    Then I should see heading "Analytics"

  Scenario: Navigate to staff rota
    When I navigate to "/dashboard/"
    And I click "Staff Rota"
    Then I should see heading "Staff rota"

  Scenario: Navigate to visitors log
    When I navigate to "/dashboard/"
    And I click "Visitors"
    Then I should see heading "Visitors"

  Scenario: Navigate to medication log
    When I navigate to "/dashboard/"
    And I click "Medication Log"
    Then I should see heading "Medication log"

  Scenario: Navigate to bulk sessions
    When I navigate to "/dashboard/"
    And I click "Bulk Sessions"
    Then I should see heading "Bulk session generator"

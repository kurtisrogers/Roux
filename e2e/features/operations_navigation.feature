Feature: Operations dashboard navigation
  As an organisation admin
  I want to access all operations screens
  So that I can run wraparound care day to day

  Background:
    Given the application is running
    And I am logged in as admin

  Scenario: Waitlist page loads
    When I open the waitlist page
    Then I should see heading "Waitlist"

  Scenario: Recurring bookings page loads
    When I open the recurring bookings page
    Then I should see heading "Recurring bookings"

  Scenario: Childcare vouchers page loads
    When I open the childcare vouchers page
    Then I should see heading "Childcare vouchers"
    And the table should contain "EDEN-1001"

  Scenario: Voucher redeem page loads
    When I open the voucher redeem page
    Then I should see heading "Redeem voucher"

  Scenario: Subsidies page loads
    When I open the subsidies page
    Then I should see heading "Subsidy codes"

  Scenario: Payment plans page loads
    When I open the payment plans page
    Then I should see heading "Payment plans"

  Scenario: Analytics dashboard loads
    When I open the analytics dashboard
    Then I should see heading "Analytics"

  Scenario: Staff rota page loads
    When I open the staff rota page
    Then I should see heading "Staff rota"

  Scenario: Visitors log loads
    When I open the visitors log
    Then I should see heading "Visitors"

  Scenario: Medication log loads
    When I open the medication log
    Then I should see heading "Medication log"

  Scenario: Staff compliance page loads
    When I open staff compliance
    Then I should see heading "Staff compliance"

  Scenario: Safeguarding page loads
    When I open safeguarding cases
    Then I should see heading "Safeguarding"

  Scenario: Bulk session generator loads
    When I open bulk session generator
    Then I should see heading "Bulk session generator"

  Scenario: Booking calendar loads
    When I open the booking calendar
    Then I should see heading "Booking calendar"

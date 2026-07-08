Feature: Parent booking and programme visibility
  As a parent
  I want to see planned activities and payment options when booking
  So that I know what my child will do and how to pay

  Background:
    Given the application is running
    And I am logged in as a parent

  Scenario: Browse available sessions
    When I browse available sessions
    Then I should see heading "Available Sessions"
    And I should see "After School Club"

  Scenario: Parent booking calendar loads
    When I open the parent booking calendar
    Then I should see heading "Book a session"
    And I should see "After School Club"

  Scenario: After-school booking shows planned activities
    When I open the first after-school booking page
    Then I should see planned activities for the session
    And I should see "Homework club"

  Scenario: Booking page offers childcare voucher payment
    When I open the first after-school booking page
    Then I should see the childcare voucher payment option
    And I should see "Card (Stripe)"

  Scenario: Report absence page loads
    When I open the report absence page
    Then I should see the absence reporting form
    And I should see "Submit absence"

  Scenario: My bookings page loads
    When I open my bookings
    Then I should see heading "My Bookings"

  Scenario: Parent can add child link visible
    When I open my bookings
    Then I should see "Add a child"

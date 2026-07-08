Feature: Parent session discovery when logged out
  As a visitor
  I want to be prompted to log in before booking
  So that bookings are tied to my account

  Background:
    Given the application is running

  Scenario: Book now requires login when logged out
    Given I visit "/sessions/"
    When I click login to book on the first session
    Then I should see "Login"

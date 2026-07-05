Feature: Authentication
  As a user
  I want to log in and out
  So that I can access my account securely

  Background:
    Given the application is running

  Scenario: Login page loads
    Given I visit "/accounts/login/"
    Then I should see "Login"

  Scenario: Parent login redirects to public site
    Given I am logged in as "parent1" with password "parent123"
    When I navigate to "/my-bookings/"
    Then I should see "My Bookings"

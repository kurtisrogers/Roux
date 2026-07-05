Feature: Dashboard access
  As a staff member
  I want to access the operations dashboard
  So that I can manage wraparound care

  Background:
    Given the application is running

  Scenario: Admin can access dashboard
    Given I am logged in as "admin" with password "admin123"
    When I navigate to "/dashboard/"
    Then I should see "Dashboard"

  Scenario: Admin can view sessions list
    Given I am logged in as "admin" with password "admin123"
    When I navigate to "/dashboard/sessions/"
    Then I should see "Sessions"

  Scenario: Admin can access Ofsted compliance
    Given I am logged in as "admin" with password "admin123"
    When I navigate to "/dashboard/ofsted/"
    Then I should see "Ofsted"

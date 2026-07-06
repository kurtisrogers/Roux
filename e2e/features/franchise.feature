Feature: Franchise partner application
  As a prospective franchisee
  I want to apply online
  So that I can start my own wraparound care business on Roux

  Scenario: Submit a franchise application
    Given the application is running
    When I navigate to "/franchise/apply/"
    Then I should see "Run wraparound care under your own brand"
    When I fill in "Your name" with "Alex Partner"
    And I fill in "Email" with "alex@franchise.test"
    And I press "Continue"
    And I fill in "Business / club name" with "Bright Stars Clubs"
    And I fill in "UK region" with "Leeds"
    And I press "Review application"
    And I press "Submit application"
    Then I should see "Thank you"
    And I should see "Bright Stars Clubs"

  Scenario: Super admin reviews applications
    Given the application is running
    And I am logged in as "superadmin" with password "super123"
    When I navigate to "/dashboard/franchise-applications/"
    Then I should see "Franchise Applications"

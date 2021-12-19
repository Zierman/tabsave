@config_setup_test
Feature: Setup
The first time the program is executed it sets up everything it needs.

  Scenario: Alex runs tabsave for the first time
    Given tabsave had not been run before
    When Alex tries to create a backup
    And Alex is asked for a path to the save directory
    And Alex specifies a valid directory
    Then the system will save that in the configurations


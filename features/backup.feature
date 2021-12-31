Feature: Backup
Create backups of a game save.

  Scenario: Alex tries to backup a non-existing save
    Given there was no game save named "Alex1"
    When Alex tries to run `tabsave Alex1 -b`
    Then Alex should get an error

  Scenario: ALex performs implicit backup
    Given there was a game save named "Alex1"
    When Alex runs `tabsave Alex1`
    Then game save "Alex1" will have 1 backup which is a copy of the current save


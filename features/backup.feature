Feature: Backup
Create backups of a game save.

  Scenario: Alex tries to backup a non-existing save
    Given there was no game save named "Alex1"
    When Alex tries to run `tabsave backup Alex1`
    Then Alex should get an error

  Scenario: ALex performs valid backup
    Given there was a game save named "Alex1"
    When Alex runs `tabsave backup Alex1`
    Then game save "Alex1" will have 1 backup which is a copy of the current save

  Scenario: ALex performs valid backup using alias
    Given there was a game save named "Alex1"
    When Alex runs `tabsave b Alex1`
    Then game save "Alex1" will have 1 backup which is a copy of the current save


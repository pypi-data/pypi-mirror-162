# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html)[^1].

<!---
Types of changes

- Added for new features.
- Changed for changes in existing functionality.
- Deprecated for soon-to-be removed features.
- Removed for now removed features.
- Fixed for any bug fixes.
- Security in case of vulnerabilities.

-->

## [Unreleased]

## [2.0.7] - 2022-08-11

### Added

#### Edition

* A site now has an option to enable the creation of working copies in user workspaces. Workspaces are specified at the site scope (`user_working_dir`), and can be overriden in user profiles (`working_dir`). This is typically meant to prevent server overloads by allowing users to work locally on their machines.
* When creating a working copy, if it doesn't exist yet, the last revision of the `pack` folder of the same task is automatically copied into the user workspace.

#### Submission for validation

* The user can now submit the latest versions of the working files at the project scope. The tool lists all shots with the `H TO SEND` status in Kitsu for the selected task (`L&S KEY FRAME` or `L&S ANIMATION`), and for each, the take which is going to be created. If the take has already been delivered on the same day, but not yet received by the target site, the user can choose between creating a new take or replacing the last one. Otherwise, the user must create a new take.

### Changed

#### Edition

* Creating a working copy on a file `working_file` sets the status of the Kitsu task (`L&S KEY FRAME` if it's not `K APPROVED`, `L&S ANIMATION` otherwise) to `E Work In Progress`.
* The user cannot create a working copy on a `working_file` file if there is no `pack` folder in the task files.

#### Submission for validation

* The number of the take's file name has no more padding.

### Fixed

* Prevent from publishing when `Cancel` button is clicked

## [2.0.6] - 2022-07-29

### Changed

#### Edition

* The user can't create a working copy if the status of the `L&S ANIMATION` task is `K APPROVED`.

#### Publication

* Publishing now updates the status of the `L&S KEY FRAME` Kitsu task if it isn't `K APPROVED`; that of the `L&S ANIMATION` task otherwise.
* The user can choose the value of the Kitsu status between `WIP` and `To check`. If `To check` is selected, the user's working copy is deleted after publication.
* The `keep_editing` and `upload_after_publish` option have been hidden and disabled.

#### Submission for validation

* Make shot and file actions to send for validation available for `working_file` files.
* A `working_file` file can't be submitted for validation if the status of the selected task isn't `H TO SEND`.
* Set the Kitsu status comment with information about the submitted take (submitter, working file, original revision, task oid).

### Removed

* The `_fix` infix in the name of the key frame revision files.

## [2.0.5.1] - 2022-07-28

### Changed

* Default Kitsu source and target statutes in action to submit the lighting scene for check have been changed to `H TO SEND` and `I Waiting For Approval` respectively.

### Fixed

* Add missing `task_files` parameter in check submission action.

## [2.0.5] - 2022-07-28

### Added

* An action to submit a `lighting.plas` file for validation.
* An action to submit lighting scenes of all shots ready to send in Kitsu.

#### Visible tasks

* A working site now holds a list containing the names of the tasks to display when this site is the current one, and assignation for the given tasks is enabled.

### Changed

* The publication action now provides an option to update the status of a selected Kitsu task to submit the scene for check.

## [2.0.4] - 2022-07-21

### Changed

#### Authentication

* A user now logs in with a login defined in its profile. The password is that of the Kitsu account being used by the user.

## [2.0.3] - 2022-07-05

### Added

* A valid `.plas` file template

### Fixed

* Use CMD to launch PaLaS to fix display issue on Windows.

## [2.0.2] - 2022-06-30

### Added

* New runners to edit PaLaS and Houdoo scenes, and their associated file extensions in the list of supported extensions in the default applications.

### Removed

* The sequence level: shots are now lying right under a film.

## [2.0.1] - 2022-06-08

### Changed

* The existing types defining the main entities of the project (films, sequences, shots, tracked files and folders, revisions) have been redefined to integrate the last features provided in libreflow 2.1.0.
* Tracked files and folders are created by default with the path format specified in the contextual dictionary (in the `settings` context) of the project.

### Added

* Each shot now holds a list of tasks, which can be parameterised in the task manager available in the project settings.

## [2.0.0] - 2022-03-15

Setting up a basic project.
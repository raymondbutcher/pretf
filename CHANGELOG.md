# Pretf Changes

## [Unreleased]

# Added

* Add support for rendering Jinja2 templates.

### Changed

* Use python-hcl2 for parsing Terraform files (#65)

### Fixed

* Fixed parsing complex types in variable definitions (#29)
* Updated command line argument parsing and variable precedence logic, fixing some issues (#38, #54, #66)

### Removed

* Pretf no longer supports [passing a different configuration directory](https://www.terraform.io/docs/cli/commands/plan.html#passing-a-different-configuration-directory), bringing it in line with Terraform version v0.15 and above. Pretf currently has no specific handling or support for the [-chdir argument](https://www.terraform.io/docs/cli/commands/#switching-working-directory-with-chdir) but it does get passed through to the Terraform command if provided.

## 0.7.3

### Fixed

* Prevent simultaneous MFA prompts (#61)

## 0.7.2

### Added

* `aws.terraform_remote_state_s3()` function added.

## 0.7.1

### Changed

* Added `pytest` dependency which is required for `api.get_outputs()`.

## 0.7.0

### Added

* `api.get_outputs()` function added.
* `pretf.blocks` module added.
    * More human-friendly way to define Terraform blocks in Python.
* `workflow.delete_links()` function added.
* `workflow.link_files()` function added.
* `workflow.link_module()` function added.
* `workflow.load_parent()` function added.
    * More composable workflows.

### Changed

* Use multiple threads to render files.
    * Should fix rare race conditions with multiple files referring to each others' variables.
* `log.bad()` and `log.ok()` can now be raised as exceptions to display a message and then exit.

### Deprecated

* `workflow.mirror_files()` function deprecated.
    * Use the new `link` functions instead.

### Removed

* `workspaces` example removed.
    * It was too much effort to maintain it. I don't recommend using this project structure because the currently selected workspace is not obvious, and it can't have different S3 backends for different environments.

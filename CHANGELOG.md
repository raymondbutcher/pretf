# Pretf Changes

## [Unreleased]

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

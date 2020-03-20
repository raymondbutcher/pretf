# Pretf Changes

## [Unreleased]

### Added

* `api.get_outputs()` function added.
* `pretf.blocks` module added.
    * More human-friendly way to define Terraform blocks in Python.
* `workflow.delete_links()` function added.
* `workflow.link_files()` function added.
* `workflow.load_parent()` function added.
    * More composable workflows.

### Changed

* Use multiple threads to render files.
    * Should fix rare race conditions with multiple files referring to each others' variables.
* `path.module` now refers to the directory of the current Python file.
* `workflow.mirror_files()` function now accepts Path objects along with pattern strings.
* `workflow.mirror_files()` function now searches for files in parent directories if they don't contain a slash.

### Deprecated

* `workflow.mirror_files()` function deprecated.
    * Use the new `link` functions instead.

### Removed

* `workspaces` example removed.
    * It was too much effort to maintain it. I don't recommend using this project structure because the currently selected workspace is not obvious, and it can't have different S3 backends for different environments.

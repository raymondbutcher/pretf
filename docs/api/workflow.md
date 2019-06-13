## create_files

Creates `*.tf.json` and `*.tfvars.json` files in the current directory from `*.tf.py` and `*.tfvars.py` files in the source directories.

Uses the current directory as a source directory if none are specified. If multiple directories are specified, and there are duplicate file names, the files in the latter directories take precedence.

It is recommended to call create() only once. Pass in multiple source_dirs rather than calling it multiple times. Pretf parses variables from files in the current directory and the source_dirs. Calling it multiple times with different source_dirs could give Pretf a different set of files to parse each time it is called, resulting in different variables each time.

Signature:

```python
def create_files(*source_dirs: Union[Path, str], verbose: bool = True) -> List[Path]:

source_dirs:
    directories to use for source files
verbose:
    whether to print information

returns:
    created files
```

Example:

```python
from pretf import workflow


def pretf_workflow():
    workflow.create_files()
    return workflow.execute_terraform()
```

## custom

Calls the `pretf_workflow()` function from the specified Python file. This is useful for having a custom workflow that is used by multiple pretf.py files in different directories.

Signature:

```python
def custom(module_path: Union[PurePath, str]) -> int:

module_path:
    file path for the Python module

returns:
    exit code for when pretf finishes
```

Example:

```python
from pretf import workflow


def pretf_workflow():
    return workflow.custom("../src/pretf_workflow.py")
```

## default

This is the default Pretf workflow. This is automatically used when there is no pretf.py file in the current directory, or it can be called directly from a custom workflow function if it just needs to do something before or after the default workflow.

Signature:

```python
def default(verbose: bool = True) -> int:

verbose:
    whether to print information

returns:
    exit code for when pretf finishes
```

Example:

```python
from pretf import workflow


def pretf_workflow():
    workflow.create_files()
    return workflow.default()
```

## delete_files

Deletes matching files from the current directory. Defaults to deleting files normally created by the `create()` function. Optionally exclude files matching a specified pattern.

Signature:

```python
def delete_files(
    path_patterns: Sequence[str] = ["*.tf.json", "*.tfvars.json"],
    exclude_name_patterns: Sequence[str] = [],
    cwd: Optional[Union[Path, str]] = None,
    verbose: bool = True,
) -> List[Path]:

path_patterns:
    path glob patterns to mirror into the current directory
exclude_name_patterns:
    name glob patterns to exclude
cwd:
    current directory
verbose:
    whether to print information

returns:
    removed files
```

Example:

```python
from pretf import workflow


def pretf_workflow():
    workflow.delete_files()
    return workflow.execute_terraform()
```

## execute_terraform

Executes Terraform and waits for it to finish. Command line arguments are passed through to Terraform. Returns the exit code from Terraform.

Signature:

```python
def execute_terraform(verbose: bool = True) -> int:

verbose:
    whether to print the command

returns:
    exit code from the process
```

Example:

```python
from pretf import workflow


def pretf_workflow():
    return workflow.execute_terraform()
```

## mirror_files

Creates symlinks from all files and directories matching the source patterns into the current directory. Deletes all pre-existing symlinks in the current directory.

Signature:

```python
def mirror_files(
    *path_patterns: str,
    exclude_name_patterns: Sequence[str] = [".*", "_*"],
    include_directories: bool = True,
    cwd: Optional[Union[Path, str]] = None,
    verbose: bool = True,
) -> List[Path]:

path_patterns:
    path glob patterns to mirror into the current directory
exclude_name_patterns:
    name glob patterns to exclude
cwd:
    current directory
verbose:
    whether to print information

returns:
    created symlinks
```

Example:

```python
from pretf import workflow


def pretf_workflow():
    mirror_files("../src/*")
    return workflow.execute_terraform()
```

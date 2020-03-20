## clean_files

Deletes the specified files. Intended for use after `create_files()`. Use `delete_files()` if wildcards are required.

Signature:

```python
def clean_files(paths: Sequence[Path], verbose:bool=True) -> None:

paths:
    files to delete

verbose:
    whether to print information
```

Example:

```python
from pretf import workflow


def pretf_workflow():
    created = workflow.create_files()
    proc = workflow.execute_terraform()
    workflow.clean_files(created)
    return proc
```

## create_files

Creates `*.tf.json` and `*.tfvars.json` files in `target_dir` from `*.tf.py` and `*.tfvars.py` in source_dirs.

`target_dir` defaults to the current working directory and `source_dirs` defaults to a list containing `target_dir`.

If multiple source_dirs are specified, and there are duplicate file names, the files in the latter directories take precedence.

It is recommended to call create() only once. Pass in multiple source_dirs rather than calling it multiple times. Pretf parses variables from files in the current directory and the source_dirs. Calling it multiple times with different source_dirs could give Pretf a different set of files to parse each time it is called, resulting in different variables each time.

Signature:

```python
def create_files(
    target_dir: Union[Path, str] = "",
    source_dirs: Sequence[Union[Path, str]] = [],
    verbose: bool = True,
) -> List[Path]:
```

Example:

```python
from pretf import workflow


def pretf_workflow():
    workflow.create_files()
    return workflow.execute_terraform()
```

## custom

Calls the `pretf_workflow()` function from the specified Python file. This is useful for having a custom workflow that is used by multiple `pretf.workflow.py` files in different directories.

Signature:

```python
def custom(module_path: Union[PurePath, str], context: Optional[dict] = None) -> int:

module_path:
    file path for the Python module
context:
    dictionary to pass into the pretf_workflow() function

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

This is the default Pretf workflow. This is automatically used when there is no `pretf.workflow.py` file in the current directory, or it can be called directly from a custom workflow function if it just needs to do something before or after the default workflow.

Signature:

```python
def default(
    clean: bool = True,
    created: list = [],
    verbose: bool = True,
) -> CompletedProcess:

clean:
    whether to delete created files afterwards

created:
    extra files to delete afterwards

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
    *path_patterns: str,
    exclude_name_patterns: Sequence[str] = [],
    cwd: Optional[Union[Path, str]] = None,
    verbose: bool = True,
) -> List[Path]:

path_patterns:
    path glob patterns to mirror into the current directory
    defaults to ("*.tf.json", "*.tfvars.json")
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

## delete_links

Deletes symlinks from the current directory.

Signature:

```python
def delete_files(
    cwd: Optional[Union[Path, str]] = None,
    verbose: bool = True,
) -> List[Path]:

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
    workflow.delete_links()
    workflow.link_files("*.tf.py")
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

## load_parent

Looks for the closest `pretf.workflow.py` file in parent directories and calls the `pretf_workflow()` function. Errors if there are no `pretf.workflow.py` files in any parent directories.

Signature:

```python
def load_parent(**kwargs: Any) -> CompletedProcess:

kwargs:
    keyword arguments to pass into the pretf_workflow() function

returns:
    exit code for when pretf finishes
```

Example:

```python
from pretf import workflow


def pretf_workflow():
    workflow.require_files("terraform.tfvars")
    return workflow.load_parent()
```

## link_files

Creates symlinks from all files and directories matching the source patterns into the current directory.

Signature:

```python
def mirror_files(
    *path_patterns: Union[Path, str],
    exclude_name_patterns: Sequence[str] = [".*", "_*", "pretf.workflow.py"],
    cwd: Optional[Union[Path, str]] = None,
    verbose: bool = True,
) -> List[Path]:

path_patterns:
    paths or path glob patterns to mirror into the current directory
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
    workflow.delete_links()
    workflow.link_files("*.tf.py")
    return workflow.execute_terraform()
```

## link_module

Creates symlinks from all files and directories in a module into the current directory. Remote modules are first downloaded into a cache directory.

Signature:

```python
def link_module(
    source: Union[Path,str],
    version: Optional[str] = None,
    update: bool = False,
    cache_dir: Optional[Union[Path, str]] = None,
    cwd: Optional[Union[Path, str]] = None,
    verbose: bool = True,
) -> List[Path]:

source:
    location of module to mirror into the current directory
version:
    the module version (if using registry)
update:
    whether to fetch the module every time, or use a cached copy
cache_dir:
    location to use for caching modules
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
    workflow.delete_links()
    workflow.link_module("claranet/vpc-modules/aws", version="1.1.0")
    return workflow.execute_terraform()
```

## mirror_files

> This function will be removed in a future version. Use [delete_links](#delete_links) and [link_files](#link_files) instead.

Creates symlinks from all files and directories matching the source patterns into the current directory. Deletes all pre-existing symlinks in the current directory.

Signature:

```python
def mirror_files(
    *path_patterns: Union[Path, str],
    exclude_name_patterns: Sequence[str] = [".*", "_*", "pretf.workflow.py"],
    include_directories: bool = True,
    cwd: Optional[Union[Path, str]] = None,
    verbose: bool = True,
) -> List[Path]:

path_patterns:
    paths or path glob patterns to mirror into the current directory
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
    workflow.mirror_files("../src/*")
    return workflow.execute_terraform()
```

## require_files

Raises an exception if the specified files are not found in the current directory. Pretf will catch this exception, display an error message, and show other directories that do contain the files.

This can be used to restrict where Pretf/Terraform can run, while informing users where it can run if they make a mistake.

If multiple patterns are provided, the directory must contain files that match all patterns (performing an `AND` search).

```python
def require_files(*name_patterns: str) -> None:

name_patterns:
    name glob patterns to require
```

Example:

```python
from pretf import workflow


def pretf_workflow():
    workflow.require_files("*.tfvars")
    return workflow.default()
```

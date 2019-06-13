## execute

> Note: this is a lower level function than the simpler `pretf.workflow.execute_terraform()` function which is limited to executing only Terraform.

Executes a command and waits for it to finish.

If args are provided, then they will be used.

If args are not provided, and arguments were used to run this program,
then those arguments will be used.

If args are not provided, and no arguments were used to run this program,
and default args are provided, then they will be used.

Returns the exit code from the command that is run.

Signature:

```python
def execute(
    file: str,
    args: Sequence[str],
    env: Optional[dict] = None,
    verbose: bool = True
) -> int:

file:
    binary to execute
args:
    arguments
env:
    environment variables, defaults to those of the current process
verbose:
    whether to print the command

returns:
    exit code from the process
```

Example:

```python
from pretf.util import execute


def pretf_workflow():
    execute("terraform", ["terraform", "plan"])
```

## import_file

> Note: this is a lower level function than the simpler `pretf.workflow.custom()` function which is limited to calling custom workflows.

Imports a Python module from any local filesystem path. Temporarily alters sys.path to allow the imported module to import other modules in the same directory.

Signature:

```python
def import_file(path: Union[PurePath, str]) -> ModuleType:

path:
    file path of Python module to import

returns:
    context object with the imported module
```

Example:

```python
from pretf.util import import_file

def pretf_workflow():
    with import_file("../src/pretf_workflow.py") as module:
        return module.pretf_workflow()
```

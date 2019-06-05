## execute

```python
from pretf.util import execute


def run():
    execute("terraform", ["terraform", "plan"])
```

## import_file

```python
from pretf.util import import_file

def run():
    with import_file("../src/pretf_env.py") as pretf_env:
        pretf_env.run()
```

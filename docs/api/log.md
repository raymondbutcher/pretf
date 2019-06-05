## accept

```python
from pretf import log


def run():
    if log.accept("do you wish to continue?"):
        print("user accepted the prompt")
    else:
        print("user did not accept the prompt")
```

## bad

```python
from pretf import log


def run():
    log.bad("something bad happened")
```

## ok

```python
from pretf import log


def run():
    log.bad("something normal happened")
```

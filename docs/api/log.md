## accept

Prompts the user to enter "yes" or "no". Returns True if the response was "yes", otherwise False. Ctrl-c counts as "no".

Signature:

```python
log.accept(message)

message:
    required str

returns:
    bool
```

Example:

```python
from pretf import log


def run():
    if log.accept("do you wish to continue?"):
        print("user accepted the prompt")
    else:
        print("user did not accept the prompt")
```

## bad

Displays a message prefixed with `[pref]` in red.

Signature:

```python
log.bad(message)

message:
    required str

returns:
    None
```

Example:

```python
from pretf import log


def run():
    log.bad("something bad happened")
```

## ok

Displays a message prefixed with `[pref]` in cyan.

Signature:

```python
log.ok(message)

message:
    required str

returns:
    None
```

Example:

```python
from pretf import log


def run():
    log.bad("something normal happened")
```

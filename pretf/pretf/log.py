import sys
from functools import wraps
from typing import Any, Callable

import colorama


def colorama_init(func: Callable, state: dict = {}) -> Callable:
    @wraps(func)
    def wrapped(*args: Any, **kwargs: dict) -> Any:

        if not state:
            colorama.init()
            state["init"] = True

        return func(*args, **kwargs)

    return wrapped


@colorama_init
def accept(message: Any) -> bool:
    """
    Prompts the user to enter "yes" or "no". Returns True if the
    response was "yes", otherwise False. Ctrl-c counts as "no".

    """

    message = f"[pretf] {message} [yes/no]: "
    response = ""
    while response not in ("yes", "no"):
        try:
            response = input(message).lower()
        except KeyboardInterrupt:
            response = "no"
            print()
    return response == "yes"


@colorama_init
def bad(message: Any) -> None:
    """
    Displays a message prefixed with [pref] in red.

    """

    print(
        f"{colorama.Fore.RED}[pretf] {message}{colorama.Style.RESET_ALL}",
        file=sys.stderr,
    )


@colorama_init
def ok(message: Any) -> None:
    """
    Displays a message prefixed with [pref] in cyan.

    """

    print(
        f"{colorama.Fore.CYAN}[pretf] {message}{colorama.Style.RESET_ALL}",
        file=sys.stderr,
    )

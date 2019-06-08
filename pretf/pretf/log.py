from functools import wraps

import colorama


def uses_colorama(func, state={}):
    @wraps(func)
    def wrapped(*args, **kwargs):

        if not state:
            colorama.init()
            state["init"] = True

        return func(*args, **kwargs)

    return wrapped


@uses_colorama
def accept(message):
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


@uses_colorama
def bad(message):
    """
    Displays a message prefixed with [pref] in red.

    """

    print(f"{colorama.Fore.RED}[pretf] {message}{colorama.Style.RESET_ALL}")


@uses_colorama
def ok(message):
    """
    Displays a message prefixed with [pref] in cyan.

    """

    print(f"{colorama.Fore.CYAN}[pretf] {message}{colorama.Style.RESET_ALL}")

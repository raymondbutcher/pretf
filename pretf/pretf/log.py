import colorama


def _init(_cache=[]):
    if not _cache:
        colorama.init()
        _cache.append(True)


def accept(message):
    """
    Prompts the user to enter "yes" or "no". Returns True if the
    response was "yes", otherwise False. Ctrl-c counts as "no".

    """

    message = "[pretf] " + message + " [yes/no]: "
    response = ""
    while response not in ("yes", "no"):
        try:
            response = input(message).lower()
        except KeyboardInterrupt:
            response = "no"
            print()
    return response == "yes"


def bad(message):
    """
    Displays a message prefixed with [pref] in red.

    """

    _init()
    print(colorama.Fore.RED + "[pretf] " + message + colorama.Style.RESET_ALL)


def ok(message):
    """
    Displays a message prefixed with [pref] in cyan.

    """

    _init()
    print(colorama.Fore.CYAN + "[pretf] " + message + colorama.Style.RESET_ALL)

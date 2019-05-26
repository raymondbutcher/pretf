import colorama


def _init(_cache=[]):
    if not _cache:
        colorama.init()
        _cache.append(True)


def accept(question):
    """
    Prompt the user to enter "yes" or "no". Returns True if the
    response was "yes", otherwise False. Ctrl-c counts as "no".

    """

    question = "[pretf] " + question + " [yes/no]: "
    answer = ""
    while answer not in ("yes", "no"):
        try:
            answer = input(question).lower()
        except KeyboardInterrupt:
            answer = "no"
            print()
    return answer == "yes"


def bad(message):
    """
    Display a bad pretf message.

    """

    _init()
    print(colorama.Fore.RED + "[pretf] " + message + colorama.Style.RESET_ALL)


def ok(message):
    """
    Display a normal pretf message.

    """

    _init()
    print(colorama.Fore.CYAN + "[pretf] " + message + colorama.Style.RESET_ALL)

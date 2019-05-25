import colorama


def init(_cache=[]):
    if not _cache:
        colorama.init()
        _cache.append(True)


def accept(question):
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
    init()
    print(colorama.Fore.RED + "[pretf] " + message + colorama.Style.RESET_ALL)


def ok(message):
    init()
    print(colorama.Fore.CYAN + "[pretf] " + message + colorama.Style.RESET_ALL)

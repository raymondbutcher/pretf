import pretf.api
import pretf.cli


def run():
    pretf.api.mirror("../src/*", "../../src/*")
    return pretf.cli.run()

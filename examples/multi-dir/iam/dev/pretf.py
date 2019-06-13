from pretf import workflow


def run():
    workflow.mirror_files("../src/*", "../../src/*")
    return workflow.default()

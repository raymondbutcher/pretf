from pretf import workflow


def run():
    workflow.mirror_files("../../src/*")
    return workflow.default()

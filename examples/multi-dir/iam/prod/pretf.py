from pretf import workflow


def pretf_workflow():
    workflow.mirror_files("../src/*", "../../src/*")
    return workflow.default()

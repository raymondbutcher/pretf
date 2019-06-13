from pretf import workflow


def pretf_workflow():
    workflow.mirror_files("../../src/*")
    return workflow.default()
